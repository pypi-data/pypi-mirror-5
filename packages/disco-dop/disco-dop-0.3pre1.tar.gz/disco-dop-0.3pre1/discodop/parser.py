""" Simple command line interface to parse with grammar(s) in text format.  """
from __future__ import print_function
import io
import os
import re
import sys
import time
import gzip
import codecs
import logging
import tempfile
import string  # pylint: disable=W0402
from math import log
from getopt import gnu_getopt, GetoptError
from operator import itemgetter
from itertools import count
from subprocess import Popen, PIPE
import numpy as np
from discodop import plcfrs, pcfg
from discodop.grammar import FORMAT, defaultparse
from discodop._grammar import Grammar
from discodop.containers import CFGChartItem
from discodop.coarsetofine import prunechart, whitelistfromposteriors
from discodop.disambiguation import marginalize, doprerank
from discodop.tree import Tree
from discodop.lexicon import replaceraretestwords, getunknownwordfun, UNK
from discodop.treebank import saveheads, TERMINALSRE
from discodop.treebanktransforms import reversetransform, rrbacktransform
from discodop.treetransforms import mergediscnodes, unbinarize, \
		removefanoutmarkers

USAGE = """
usage: %s [options] <rules> <lexicon> [input [output]]
or:    %s [options] --ctf k <coarserules> <coarselex>
          <finerules> <finelex> [input [output]]

Grammars need to be binarized, and are in bitpar or PLCFRS format.
When no file is given, output is written to standard output;
when additionally no input is given, it is read from standard input.
Files must be encoded in UTF-8.
Input should contain one token per line, with sentences delimited by two
newlines. Output consists of bracketed trees, with discontinuities indicated
through indices pointing to words in the original sentence.

Options:
  -b k          Return the k-best parses instead of just 1.
  -s x          Use "x" as start symbol instead of default "TOP".
  -z            Input is one sentence per line, space-separated tokens.
  --ctf=k       Use k-best coarse-to-fine; prune items not in top k derivations
  --prob        Print probabilities as well as parse trees.
  --mpd         In coarse-to-fine mode, produce the most probable
                derivation (MPD) instead of the most probable parse (MPP).

%s
""" % (sys.argv[0], sys.argv[0], FORMAT)

DEFAULTSTAGE = dict(
		name='stage1',  # identifier, used for filenames
		mode='plcfrs',  # use the agenda-based PLCFRS parser
		prune=False,  # whether to use previous chart to prune this stage
		split=False,  # split disc. nodes VP_2[101] as { VP*[100], VP*[001] }
		splitprune=False,  # treat VP_2[101] as {VP*[100], VP*[001]} for pruning
		markorigin=False,  # mark origin of split nodes: VP_2 => {VP*1, VP*2}
		k=50,  # no. of coarse pcfg derivations to prune with; k=0: filter only
		neverblockre=None,  # do not prune nodes with label that match regex
		getestimates=None,  # compute & store estimates
		useestimates=None,  # load & use estimates
		dop=False,  # enable DOP mode (DOP reduction / double DOP)
		packedgraph=False,  # use packed graph encoding for DOP reduction
		usedoubledop=False,  # when False, use DOP reduction instead
		iterate=False,  # for double dop, whether to add fragments of fragments
		complement=False,  # for double dop, whether to include fragments which
			# form the complement of the maximal recurring fragments extracted
		sample=False, kbest=True,
		m=10,  # number of derivations to sample/enumerate
		estimator='ewe',  # choices: dop1, ewe
		objective='mpp',  # choices: mpp, mpd, shortest, sl-dop[-simple]
			# NB: w/shortest derivation, estimator only affects tie breaking.
		sldop_n=7)


def main():
	""" Handle command line arguments. """
	print('PLCFRS parser - Andreas van Cranenburgh', file=sys.stderr)
	options = 'ctf= prob mpd'.split()
	try:
		opts, args = gnu_getopt(sys.argv[1:], 'u:b:s:z', options)
		assert 2 <= len(args) <= 6, 'incorrect number of arguments'
	except (GetoptError, AssertionError) as err:
		print(err, USAGE)
		return
	for n, filename in enumerate(args):
		assert os.path.exists(filename), (
				'file %d not found: %r' % (n + 1, filename))
	opts = dict(opts)
	k = int(opts.get('-b', 1))
	top = opts.get('-s', 'TOP')
	threshold = int(opts.get('--ctf', 0))
	prob = '--prob' in opts
	oneline = '-z' in opts
	rules = (gzip.open if args[0].endswith('.gz') else open)(args[0]).read()
	lexicon = codecs.getreader('utf-8')((gzip.open if args[1].endswith('.gz')
			else open)(args[1])).read()
	bitpar = rules[0] in string.digits
	coarse = Grammar(rules, lexicon, start=top, bitpar=bitpar)
	stages = []
	stage = DEFAULTSTAGE.copy()
	stage.update(
			name='coarse',
			mode='pcfg' if bitpar else 'plcfrs',
			grammar=coarse,
			backtransform=None,
			m=k)
	stages.append(DictObj(stage))
	if 4 <= len(args) <= 6 and threshold:
		rules = (gzip.open if args[2].endswith('.gz') else open)(args[2]).read()
		lexicon = codecs.getreader('utf-8')((gzip.open
				if args[3].endswith('.gz') else open)(args[3])).read()
		# detect bitpar format
		bitpar = rules[0] in string.digits
		fine = Grammar(rules, lexicon, start=top, bitpar=bitpar)
		fine.getmapping(coarse, striplabelre=re.compile(b'@.+$'))
		stage = DEFAULTSTAGE.copy()
		stage.update(
				name='fine',
				mode='pcfg' if bitpar else 'plcfrs',
				grammar=fine,
				backtransform=None,
				m=k,
				prune=True,
				k=threshold,
				objective='mpd' if '--mpd' in opts else 'mpp')
		stages.append(DictObj(stage))
		infile = (io.open(args[4], encoding='utf-8')
				if len(args) >= 5 else sys.stdin)
		out = (io.open(args[5], 'w', encoding='utf-8')
				if len(args) == 6 else sys.stdout)
	else:
		infile = (io.open(args[2], encoding='utf-8')
				if len(args) >= 3 else sys.stdin)
		out = (io.open(args[3], 'w', encoding='utf-8')
				if len(args) == 4 else sys.stdout)
	doparsing(Parser(stages), infile, out, prob, oneline)


def doparsing(parser, infile, out, printprob, oneline):
	""" Parse sentences from file and write results to file, log to stdout. """
	times = [time.clock()]
	unparsed = 0
	if not oneline:
		infile = infile.read().split('\n\n')
	for n, line in enumerate(infile):
		if not line.strip():
			continue
		sent = line.split() if oneline else line.splitlines()
		lexicon = parser.stages[0].grammar.lexicalbyword
		assert not set(sent) - set(lexicon), (
			'unknown words and no open class tags supplied: %r' % (
			list(set(sent) - set(lexicon))))
		print('parsing %d: %s' % (n, ' '.join(sent)), file=sys.stderr)
		sys.stdout.flush()
		result = list(parser.parse(sent))[-1]
		if result.noparse:
			unparsed += 1
			out.writelines('No parse for "%s"\n' % ' '.join(sent))
		elif printprob:
			out.writelines('prob=%.16g\n%s\n' % (prob, tree)
					for tree, prob in sorted(result.parsetrees.items(),
						key=itemgetter(1), reverse=True))
		else:
			out.writelines('%s\n' % tree
					for tree in sorted(result.parsetrees,
						key=result.parsetrees.get, reverse=True))
		out.flush()
		times.append(time.clock())
		print(times[-1] - times[-2], 's', file=sys.stderr)
	times = [a - b for a, b in zip(times[1::2], times[::2])]
	print('raw cpu time', time.clock() - times[0],
			'\naverage time per sentence', sum(times) / len(times),
			'\nunparsed sentences:', unparsed,
			'\nfinished',
			file=sys.stderr)
	out.close()


class Parser(object):
	""" An object to parse sentences following parameters given as a sequence
	of coarse-to-fine stages.

	:param stages: a list of coarse-to-fine stages containing grammars and
		parameters.
	:param transformations: treebank transformations to reverse on parses.
	:param tailmarker: if heads have been marked with a symbol, use this to
		mark heads in the output.
	:param postagging: if given, an unknown word model is used, consisting of a
		dictionary with three items:
		- unknownwordfun: function to produces signatures for unknown words.
		- lexicon: the set of known words in the grammar.
		- sigs: the set of word signatures occurring in the grammar.
	:param relationalrealizational: whether to reverse the RR-transform. """
	def __init__(self, stages, transformations=None, tailmarker=None,
			relationalrealizational=None, postagging=None):
		self.stages = stages
		self.transformations = transformations
		self.tailmarker = tailmarker
		self.postagging = postagging
		self.relationalrealizational = relationalrealizational

	def parse(self, sent, tags=None):
		""" Parse a sentence and yield a dictionary from parse trees to
		probabilities for each stage.

		:param tags: if given, will be given to the parser instead of trying
			all possible tags. """
		if self.postagging:
			sent = replaceraretestwords(sent,
					self.postagging['unknownwordfun'],
					self.postagging['lexicon'], self.postagging['sigs'])
		sent = list(sent)
		if tags is not None:
			tags = list(tags)
		chart = {}
		start = inside = outside = None
		for n, stage in enumerate(self.stages):
			begin = time.clock()
			noparse = False
			parsetrees = fragments = None
			msg = '%s:\t' % stage.name.upper()
			model = u'default'
			if stage.dop:
				if (stage.estimator == 'ewe'
						or stage.objective.startswith('sl-dop')):
					model = u'ewe'
				elif stage.estimator == 'bon':
					model = u'bon'
				if stage.objective == 'shortest':
					model = u'shortest'
			x = stage.grammar.currentmodel
			stage.grammar.switch(model, logprob=stage.mode != 'pcfg-posterior')
			if stage.mode == 'pcfg-bitpar' and (
					not hasattr(stage, 'rulesfile')
					or x != stage.grammar.currentmodel):
				exportbitpargrammar(stage)
			if not stage.prune or start:
				if n != 0 and stage.prune and stage.mode != 'dop-rerank':
					if self.stages[n - 1].mode == 'pcfg-posterior':
						(whitelist, sentprob, unfiltered,
							numitems, numremain) = whitelistfromposteriors(
								inside, outside, start,
								self.stages[n - 1].grammar, stage.grammar,
								stage.k, stage.splitprune,
								self.stages[n - 1].markorigin,
								stage.mode.startswith('pcfg'))
						msg += ('coarse items before pruning=%d; filtered: %d;'
								' pruned: %d; sentprob=%g\n\t' % (
								unfiltered, numitems, numremain, sentprob))
					else:
						whitelist, items = prunechart(
								chart, start, self.stages[n - 1].grammar,
								stage.grammar, stage.k, stage.splitprune,
								self.stages[n - 1].markorigin,
								stage.mode.startswith('pcfg'),
								self.stages[n - 1].mode == 'pcfg-bitpar')
						msg += 'coarse items before pruning: %d; ' % (
								sum(len(a) for x in chart for a in x if a)
								if self.stages[n - 1].mode == 'pcfg'
								else len(chart))
						msg += 'after: %d\n\t' % (items)
				else:
					whitelist = None
				if stage.mode == 'pcfg':
					chart, start, msg1 = pcfg.parse(
							sent, stage.grammar, tags=tags,
							chart=whitelist if stage.prune else None)
				elif stage.mode == 'pcfg-symbolic':
					chart, start, msg1 = pcfg.parse_symbolic(
							sent, stage.grammar, tags=tags)
				elif stage.mode == 'pcfg-posterior':
					inside, outside, start, msg1 = pcfg.doinsideoutside(
							sent, stage.grammar, tags=tags)
				elif stage.mode == 'pcfg-bitpar':
					chart, start, msg1 = parse_bitpar(
							stage.rulesfile.name, stage.lexiconfile.name,
							sent, stage.m, stage.grammar.start,
							stage.grammar.toid[stage.grammar.start], tags=tags)
					msg1 += '%d derivations' % (len(chart) if start else 0)
				elif stage.mode == 'plcfrs':
					chart, start, msg1 = plcfrs.parse(
							sent, stage.grammar, tags=tags,
							exhaustive=stage.dop or (n + 1 != len(self.stages)
								and self.stages[n + 1].prune),
							whitelist=whitelist,
							splitprune=stage.splitprune
								and self.stages[n - 1].split,
							markorigin=self.stages[n - 1].markorigin,
							estimates=(stage.useestimates, stage.outside)
								if stage.useestimates in ('SX', 'SXlrgaps')
								else None)
				elif stage.mode == 'dop-rerank':
					if start:
						parsetrees = doprerank(chart, start, sent, stage.k,
								self.stages[n - 1].grammar, stage.grammar)
						msg1 = 're-ranked %d parse trees. ' % len(parsetrees)
				else:
					raise ValueError('unknown mode specified.')
				msg += '%s\n\t' % msg1
				if (n != 0 and not start and not noparse
						and stage.split == self.stages[n - 1].split):
					logging.error('ERROR: expected successful parse. '
							'sent: %s\nstage: %s.', ' '.join(sent), stage.name)
					#raise ValueError('ERROR: expected successful parse. '
					#		'sent %s, %s.' % (nsent, stage.name))
			if start and stage.mode not in ('pcfg-posterior', 'dop-rerank'
					) and not (self.relationalrealizational and stage.split):
				begindisamb = time.clock()
				if stage.objective == 'shortest':
					stage.grammar.switch('ewe' if stage.estimator == 'ewe'
							else 'default', True)
				parsetrees, derivs, msg1 = marginalize(stage.objective
						if stage.dop else 'mpd',
						chart, start, stage.grammar, stage.m,
						sample=stage.sample, kbest=stage.kbest,
						sent=sent, tags=tags,
						sldop_n=stage.sldop_n,
						backtransform=stage.backtransform,
						bitpar=stage.mode == 'pcfg-bitpar')
				msg += 'disambiguation: %s, %gs\n\t' % (
						msg1, time.clock() - begindisamb)
			if parsetrees:
				resultstr, prob = max(parsetrees.items(), key=itemgetter(1))
				try:
					parsetree, fragments, noparse = self.postprocess(
							resultstr, n, derivs)
				except ValueError as err:
					logging.error("something's amiss: %r", err)
					parsetree, prob, fragments, noparse = self.noparse(
							stage, sent, tags)
				msg += probstr(prob) + ' '
			else:
				parsetree, prob, fragments, noparse = self.noparse(
						stage, sent, tags)
			elapsedtime = time.clock() - begin
			msg += '%.2fs cpu time elapsed\n' % (elapsedtime)
			yield DictObj(name=stage.name, parsetree=parsetree, prob=prob,
					parsetrees=parsetrees, fragments=fragments,
					noparse=noparse, elapsedtime=elapsedtime, msg=msg)

	def postprocess(self, treestr, stage=-1, derivs=None):
		""" Take parse tree and apply postprocessing. """
		parsetree = Tree.parse(treestr, parse_leaf=int)
		if self.stages[stage].split:
			mergediscnodes(unbinarize(parsetree, childchar=':'))
		saveheads(parsetree, self.tailmarker)
		unbinarize(parsetree)
		removefanoutmarkers(parsetree)
		if self.relationalrealizational:
			parsetree = rrbacktransform(parsetree,
					self.relationalrealizational['adjunctionlabel'])
		if self.transformations:
			reversetransform(parsetree, self.transformations)
		fragments = derivs.get(treestr) if derivs else None
		return parsetree, fragments, False

	def noparse(self, stage, sent, tags):
		""" Produce a dummy parse for evaluation purposes. """
		parsetree = defaultparse([(n, t)
				for n, t in enumerate(tags or (len(sent) * ['NONE']))])
		parsetree = Tree.parse('(%s %s)' % (stage.grammar.start,
				parsetree), parse_leaf=int)
		return parsetree, 0.0, None, True


def readgrammars(resultdir, stages, postagging=None, top='ROOT'):
	""" Read the grammars from a previous experiment.
	Expects a directory 'resultdir' which contains the relevant grammars and
	the parameter file 'params.prm', as produced by runexp. """
	for n, stage in enumerate(stages):
		logging.info('reading: %s', stage.name)
		rules = gzip.open('%s/%s.rules.gz' % (resultdir, stage.name))
		lexicon = codecs.getreader('utf-8')(gzip.open('%s/%s.lex.gz' % (
				resultdir, stage.name)))
		grammar = Grammar(rules.read(), lexicon.read(),
				start=top, bitpar=stage.mode.startswith('pcfg'))
		backtransform = None
		if stage.dop:
			assert stage.useestimates is None, 'not supported'
			if stage.usedoubledop:
				backtransform = gzip.open('%s/%s.backtransform.gz' % (
						resultdir, stage.name)).read().splitlines()
				if n and stage.prune:
					_ = grammar.getmapping(stages[n - 1].grammar,
						striplabelre=re.compile(b'@.+$'),
						neverblockre=re.compile(b'^#[0-9]+|.+}<'),
						splitprune=stage.splitprune and stages[n - 1].split,
						markorigin=stages[n - 1].markorigin)
				else:
					# recoverfragments() relies on this mapping to identify
					# binarization nodes
					_ = grammar.getmapping(None,
						neverblockre=re.compile(b'.+}<'))
			elif n and stage.prune:  # dop reduction
				_ = grammar.getmapping(stages[n - 1].grammar,
					striplabelre=re.compile(b'@[-0-9]+$'),
					neverblockre=re.compile(stage.neverblockre)
						if stage.neverblockre else None,
					splitprune=stage.splitprune and stages[n - 1].split,
					markorigin=stages[n - 1].markorigin)
				if stage.mode == 'dop-rerank':
					grammar.getrulemapping(stages[n - 1].grammar)
			probmodels = np.load('%s/%s.probs.npz' % (resultdir, stage.name))
			for name in probmodels.files:
				if name != 'default':
					grammar.register(unicode(name), probmodels[name])
		else:  # not stage.dop
			if n and stage.prune:
				_ = grammar.getmapping(stages[n - 1].grammar,
					neverblockre=re.compile(stage.neverblockre)
						if stage.neverblockre else None,
					splitprune=stage.splitprune and stages[n - 1].split,
					markorigin=stages[n - 1].markorigin)
		if stage.mode == 'pcfg-bitpar':
			assert grammar.maxfanout == 1
		grammar.testgrammar()
		stage.update(grammar=grammar, backtransform=backtransform, outside=None)
	if postagging and postagging['method'] == 'unknownword':
		postagging['unknownwordfun'] = getunknownwordfun(postagging['model'])
		postagging['lexicon'] = {w for w in stages[0].grammar.lexicalbyword
				if not w.startswith(UNK)}
		postagging['sigs'] = {w for w in stages[0].grammar.lexicalbyword
				if w.startswith(UNK)}


def exportbitpargrammar(stage):
	""" (re-)export bitpar grammar with current weights. """
	if not hasattr(stage, 'rulesfile'):
		stage.rulesfile = tempfile.NamedTemporaryFile()
		stage.lexiconfile = tempfile.NamedTemporaryFile()
	stage.rulesfile.seek(0)
	stage.rulesfile.truncate()
	if stage.grammar.currentmodel == 0:
		stage.rulesfile.write(stage.grammar.origrules)
	else:
		stage.rulesfile.writelines(
				'%g\t%s\n' % (weight, line.split(None, 1)[1])
				for weight, line in
				zip(stage.grammar.models[stage.grammar.currentmodel],
					stage.grammar.origrules.splitlines()))
	stage.rulesfile.flush()

	stage.lexiconfile.seek(0)
	stage.lexiconfile.truncate()
	lexicon = stage.grammar.origlexicon.replace(
			'(', '-LRB-').replace(')', '-RRB-')
	lexiconfile = codecs.getwriter('utf-8')(stage.lexiconfile)
	if stage.grammar.currentmodel == 0:
		lexiconfile.writelines(lexicon)
	else:
		weights = iter(stage.grammar.models[stage.grammar.currentmodel,
				stage.grammar.numrules:])
		lexiconfile.writelines('%s\t%s\n' % (line.split(None, 1)[0],
				'\t'.join('%s %g' % (tag, next(weights))
					for tag in line.split()[1::2]))
				for line in lexicon.splitlines())
	stage.lexiconfile.flush()


class DictObj(object):
	""" Trivial class to wrap a dictionary for reasons of syntactic sugar. """

	def __init__(self, *a, **kw):
		self.__dict__.update(*a, **kw)

	def update(self, *a, **kw):
		""" Update/add more attributes. """
		self.__dict__.update(*a, **kw)

	def __getattr__(self, name):
		""" This is only called when the normal mechanism fails, so in practice
		should never be called. It is only provided to satisfy pylint that it
		is okay not to raise E1101 errors in the client code. """
		raise AttributeError('%r instance has no attribute %r' % (
				self.__class__.__name__, name))

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__,
			',\n'.join('%s=%r' % a for a in self.__dict__.items()))


def probstr(prob):
	""" Render probability / number of subtrees as string. """
	if isinstance(prob, tuple):
		return 'subtrees=%d, p=%.4g ' % (abs(prob[0]), prob[1])
	return 'p=%.4g' % prob


BITPARUNESCAPE = re.compile(r"\\([#{}\[\]<>\^$'])")
BITPARPARSES = re.compile(r'(?:^|\n)vitprob=(.*)\n(\(.*\))\n')
BITPARPARSESLOG = re.compile(r'(?:^|\n)logvitprob=(.*)\n(\(.*\))\n')


def parse_bitpar(rulesfile, lexiconfile, sent, n,
		startlabel, startid, tags=None):
	""" Parse a single sentence with bitpar, given filenames of rules and
	lexicon. n is the number of derivations to ask for (max 1000).
	Result is a dictionary of derivations with their probabilities. """
	# TODO: get full viterbi parse forest, turn into chart w/ChartItems
	assert 1 <= n <= 1000
	if tags:
		tmp = tempfile.NamedTemporaryFile()
		tmp.writelines('%s\t%s 1\n' % (t, t) for t in set(tags))
		lexiconfile = tmp.name
	tokens = [word.replace('(', '-LRB-').replace(')', '-RRB-').encode('utf8')
			for word in (tags or sent)]
	proc = Popen(['bitpar', '-q', '-vp', '-b', str(n), '-s', startlabel,
			rulesfile, lexiconfile],
			shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)
	results, msg = proc.communicate('\n'.join(tokens) + '\n')
	# decode results or not?
	if not results or results.startswith('No parse'):
		return {}, None, '%s\n%s' % (results, msg)
	start = CFGChartItem(startid, 0, len(sent))
	lines = BITPARUNESCAPE.sub(r'\1', results).replace(')(', ') (')
	derivs = {renumber(deriv): -float(prob)
			for prob, deriv in BITPARPARSESLOG.findall(lines)}
	if not derivs:
		derivs = {renumber(deriv): -log(float(prob))
				for prob, deriv in BITPARPARSES.findall(lines)}
	return derivs, start, msg


def renumber(deriv):
	""" Replace terminals of CF-derivation (string) with indices. """
	it = count()
	return TERMINALSRE.sub(lambda _: ' %s)' % next(it), deriv)


if __name__ == '__main__':
	main()
