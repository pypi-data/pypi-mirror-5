""" Fast Fragment Seeker
Extracts recurring tree fragments from constituency treebanks.

NB: there is a known bug in multiprocessing which makes it impossible to detect
Ctrl-C or fatal errors like segmentation faults in child processes which causes
the master program to wait forever for output from its children. Therefore if
you want to abort, kill the program manually (e.g., press Ctrl-Z and issue
'kill %1'). If the program seems stuck, re-run without multiprocessing
(pass --numproc 1) to see if there might be a bug. """

from __future__ import division, print_function
import io
import os
import re
import sys
import logging
from multiprocessing import Pool, cpu_count, log_to_stderr, SUBDEBUG
from collections import defaultdict
from itertools import count
from getopt import gnu_getopt, GetoptError
from .treetransforms import binarize, introducepreterminals
from ._fragments import extractfragments, fastextractfragments, \
		exactcounts, readtreebank, getctrees, completebitsets, coverbitsets

USAGE = """Fast Fragment Seeker
usage: %s [options] treebank1 [treebank2]
If only one treebank is given, fragments occurring at least twice are sought.
If two treebanks are given, finds common fragments between first & second.
Input is in Penn treebank format (S-expressions), one tree per line.
Output contains lines of the form "tree<TAB>frequency".
Frequencies refer to the last treebank by default.
Output is sent to stdout; to save the results, redirect to a file.
--disc        work with discontinuous trees; input is in Negra export format.
              output: tree<TAB>sentence<TAB>frequency
              where "tree' has indices as leaves, referring to elements of
              "sentence", a space separated list of words.
--indices     report sets of indices instead of frequencies.
--cover       include `cover' fragments corresponding to single productions.
--complete    find complete matches of fragments from treebank1 (needle) in
              treebank2 (haystack).
--batch dir   enable batch mode; any number of treebanks > 1 can be given;
              first treebank will be compared to all others, frequencies refer
              to first treebank.
              Results are written to filenames of the form dir/A_B.
--numproc n   use n independent processes, to enable multi-core usage.
              The default is not to use multiprocessing; use 0 to use all CPUs.
--numtrees n  only read first n trees from first treebank
--encoding x  use x as treebank encoding, e.g. UTF-8, ISO-8859-1, etc.
--approx      report approximate frequencies (lower bound)
--nofreq      do not report frequencies.
--quadratic   use the slower, quadratic algorithm for finding fragments.
--alt         alternative output format: (NP (DT "a") NN)
              default: (NP (DT a) (NN ))
--debug       extra debug information, ignored when numproc > 1.
--quiet       disable all messages.""" % sys.argv[0]

FLAGS = ('approx', 'indices', 'nofreq', 'complete', 'complement',
		'disc', 'quiet', 'debug', 'quadratic', 'cover', 'alt')
OPTIONS = ('numproc=', 'numtrees=', 'encoding=', 'batch=')
PARAMS = {}
FRONTIERRE = re.compile(r"\(([^ ()]+) \)")
TERMRE = re.compile(r"\(([^ ()]+) ([^ ()]+)\)")


def main(argv=None):
	""" Command line interface to fragment extraction. """
	if argv is None:
		argv = sys.argv
	try:
		opts, args = gnu_getopt(argv[1:], '', FLAGS + OPTIONS)
	except GetoptError as err:
		print("%s\n%s" % (err, USAGE))
		return
	opts = dict(opts)

	for flag in FLAGS:
		PARAMS[flag] = '--' + flag in opts
	numproc = int(opts.get("--numproc", 1))
	if numproc == 0:
		numproc = cpu_count()
	limit = int(opts.get('--numtrees', 0))
	encoding = opts.get("--encoding", "UTF-8")
	batchdir = opts.get("--batch")

	if len(args) < 1:
		print("missing treebank argument")
	if batchdir is None and len(args) not in (1, 2):
		print("incorrect number of arguments:", args)
		print(USAGE)
		return
	if batchdir:
		assert numproc == 1, ("Batch mode only supported in single-process "
				"mode. Use the xargs command for multi-processing.")
	if args[0] == '-':
		args[0] = '/dev/stdin'
	for a in args:
		assert os.path.exists(a), "not found: %r" % a
	if PARAMS['complete']:
		assert len(args) == 2 or batchdir, (
				"need at least two treebanks with --complete.")
		assert not PARAMS['approx'] and not PARAMS['nofreq'], (
				"--complete is incompatible with --nofreq and --approx")

	level = logging.WARNING if PARAMS['quiet'] else logging.INFO
	logging.basicConfig(level=level, format='%(message)s')
	if PARAMS['debug'] and numproc > 1:
		logger = log_to_stderr()
		logger.setLevel(SUBDEBUG)

	logging.info("Fast Fragment Seeker")

	assert numproc
	logging.info("parameters:\n%s", "\n".join("    %s:\t%r" % kv
		for kv in sorted(PARAMS.items())))
	logging.info("\n".join("treebank%d: %s" % (n + 1, a)
		for n, a in enumerate(args)))

	if numproc == 1 and batchdir:
		batch(batchdir, args, limit, encoding)
	else:
		fragmentkeys, counts = regular(args, numproc, limit, encoding)
		printfragments(fragmentkeys, counts)


def regular(filenames, numproc, limit, encoding):
	""" non-batch processing. multiprocessing optional. """
	mult = 1
	if PARAMS['approx']:
		fragments = defaultdict(int)
	else:
		fragments = {}
	# detect corpus reading errors in this process (e.g., wrong encoding)
	initworker(filenames[0], filenames[1] if len(filenames) == 2 else None,
			limit, encoding)
	if numproc == 1:
		mymap = map
		myapply = lambda x, y: x(*y)
	else:  # multiprocessing, start worker processes
		pool = Pool(processes=numproc, initializer=initworker,
			initargs=(filenames[0],
				filenames[1] if len(filenames) == 2 else None, limit, encoding))
		mymap = pool.imap
		myapply = pool.apply
	numtrees = (PARAMS['trees1'].len if limit == 0
			else min(PARAMS['trees1'].len, limit))

	if PARAMS['complete']:
		fragments = completebitsets(PARAMS['trees1'], PARAMS['sents1'],
				PARAMS['labels'], PARAMS['disc'])
	else:
		if len(filenames) == 1:
			work = workload(numtrees, mult, numproc)
		else:
			chunk = numtrees // (mult * numproc) + 1
			work = [(a, a + chunk) for a in range(0, numtrees, chunk)]
		if numproc != 1:
			logging.info("work division:\n%s", "\n".join("    %s:\t%r" % kv
				for kv in sorted(dict(numchunks=len(work), mult=mult).items())))
		dowork = mymap(worker, work)
		for n, results in enumerate(dowork):
			if PARAMS['approx']:
				for frag, x in results.items():
					fragments[frag] += x
			else:
				fragments.update(results)
	if PARAMS['cover']:
		assert not PARAMS['trees2'], "only supported for single treebank."
		cover = myapply(coverfragworker, ()).get()
		if PARAMS['approx']:
			fragments.update(zip(cover.keys(),
					exactcounts(PARAMS['trees1'], PARAMS['trees1'],
					cover.values(), fast=not PARAMS['quadratic'])))
		else:
			fragments.update(cover)
		logging.info("merged %d cover fragments", len(cover))
	fragmentkeys = list(fragments.keys())
	if PARAMS['nofreq']:
		counts = None
	elif PARAMS['approx']:
		counts = [fragments[a] for a in fragmentkeys]
	else:
		task = "indices" if PARAMS['indices'] else "counts"
		logging.info("dividing work for exact %s", task)
		bitsets = [fragments[a] for a in fragmentkeys]
		countchunk = len(bitsets) // numproc + 1
		work = list(range(0, len(bitsets), countchunk))
		work = [(n, len(work), bitsets[a:a + countchunk])
				for n, a in enumerate(work)]
		counts = []
		logging.info("getting exact %s", task)
		for a in mymap(exactcountworker, work):
			counts.extend(a)
	if numproc != 1:
		pool.close()
		pool.join()
		del dowork, pool
	return fragmentkeys, counts


def batch(outputdir, filenames, limit, encoding):
	""" batch processing: three or more treebanks specified.
	The use case for this is when you have one big treebank which you want to
	compare to lots of smaller sets of trees, and get the results for each
	comparison in a separate file. """
	initworker(filenames[0], None, limit, encoding)
	trees1 = PARAMS['trees1']
	sents1 = PARAMS['sents1']
	if PARAMS['approx']:
		fragments = defaultdict(int)
	else:
		fragments = {}
	for filename in filenames[1:]:
		PARAMS.update(read2ndtreebank(filename, PARAMS['labels'],
			PARAMS['prods'], PARAMS['disc'], limit, encoding))
		trees2 = PARAMS['trees2']
		sents2 = PARAMS['sents2']
		if PARAMS['complete']:
			fragments = completebitsets(PARAMS['trees2'], sents2,
					PARAMS['labels'], PARAMS['disc'])
		elif PARAMS['quadratic']:
			fragments = extractfragments(trees2, sents2, 0, 0,
					PARAMS['labels'], trees1, sents1,
					discontinuous=PARAMS['disc'], debug=PARAMS['debug'],
					approx=PARAMS['approx'])
		else:
			fragments = fastextractfragments(trees2, sents2, 0, 0,
					PARAMS['labels'], trees1, sents1,
					discontinuous=PARAMS['disc'], debug=PARAMS['debug'],
					approx=PARAMS['approx'])
		counts = None
		fragmentkeys = list(fragments.keys())
		if PARAMS['approx'] or not fragments:
			counts = fragments.values()
		elif not PARAMS['nofreq']:
			bitsets = [fragments[a] for a in fragmentkeys]
			logging.info("getting %s for %d fragments",
					"indices of occurrence" if PARAMS['indices']
					else "exact counts", len(bitsets))
			counts = exactcounts(trees2, trees1, bitsets,
					indices=PARAMS['indices'], fast=not PARAMS['quadratic'])
		outputfilename = "%s/%s_%s" % (outputdir,
				os.path.basename(filenames[0]), os.path.basename(filename))
		out = io.open(outputfilename, "w", encoding=encoding)
		printfragments(fragmentkeys, counts, out=out)
		logging.info("wrote to %s", outputfilename)


def readtreebanks(treebank1, treebank2=None, discontinuous=False,
		limit=0, encoding="utf-8"):
	""" Read one or two treebanks.  """
	labels = []
	prods = {}
	trees1, sents1 = readtreebank(treebank1, labels, prods,
			not PARAMS['quadratic'], discontinuous, limit, encoding)
	trees2, sents2 = readtreebank(treebank2, labels, prods,
			not PARAMS['quadratic'], discontinuous, limit, encoding)
	trees1.indextrees(prods)
	if trees2:
		trees2.indextrees(prods)
	return dict(trees1=trees1, sents1=sents1, trees2=trees2, sents2=sents2,
		prods=prods, labels=labels)


def read2ndtreebank(treebank2, labels, prods, discontinuous=False,
	limit=0, encoding="utf-8"):
	""" Read a second treebank.  """
	trees2, sents2 = readtreebank(treebank2, labels, prods,
		not PARAMS['quadratic'], discontinuous, limit, encoding)
	logging.info("%r: %d trees; %d nodes (max %d). "
			"labels: %d, prods: %d",
			treebank2, len(trees2), trees2.numnodes, trees2.maxnodes,
			len(set(PARAMS['labels'])), len(PARAMS['prods']))
	return dict(trees2=trees2, sents2=sents2, prods=prods, labels=labels)


def initworker(treebank1, treebank2, limit, encoding):
	""" Read treebanks for this worker. We do this separately for each process
	under the assumption that this is advantageous with a NUMA architecture. """
	PARAMS.update(readtreebanks(treebank1, treebank2,
		limit=limit, discontinuous=PARAMS['disc'], encoding=encoding))
	if PARAMS['debug']:
		print("\nproductions:")
		for a, b in sorted(PARAMS['prods'].items(), key=lambda x: x[1]):
			print(b, a[0], '=>', ' '.join(a[1:]))
	trees1 = PARAMS['trees1']
	assert trees1
	m = "treebank1: %d trees; %d nodes (max: %d);" % (
		trees1.len, trees1.numnodes, trees1.maxnodes)
	if treebank2:
		trees2 = PARAMS['trees2']
		assert trees2
		m += " treebank2: %d trees; %d nodes (max %d);" % (
			trees2.len, trees2.numnodes, trees2.maxnodes)
	logging.info("%s labels: %d, prods: %d", m, len(set(PARAMS['labels'])),
		len(PARAMS['prods']))


def initworkersimple(trees, sents, trees2=None, sents2=None):
	""" A simpler initialization for a worker in which a treebank has already
	been loaded. """
	PARAMS.update(getctrees(trees, sents, trees2, sents2))
	assert PARAMS['trees1']


def worker(interval):
	""" Worker function that initiates the extraction of fragments
	in each process. """
	offset, end = interval
	trees1 = PARAMS['trees1']
	trees2 = PARAMS['trees2']
	sents1 = PARAMS['sents1']
	sents2 = PARAMS['sents2']
	assert offset < trees1.len
	result = {}
	if PARAMS['quadratic']:
		result = extractfragments(trees1, sents1, offset, end,
				PARAMS['labels'], trees2, sents2, approx=PARAMS['approx'],
				discontinuous=PARAMS['disc'], debug=PARAMS['debug'])
	else:
		result = fastextractfragments(trees1, sents1, offset, end,
				PARAMS['labels'], trees2, sents2, approx=PARAMS['approx'],
				discontinuous=PARAMS['disc'], complement=PARAMS['complement'],
				debug=PARAMS.get('debug'))
	logging.info("finished %d--%d", offset, end)
	return result


def exactcountworker(args):
	""" Worker function that initiates the counting of fragments
	in each process. """
	n, m, bitsets = args
	trees1 = PARAMS['trees1']
	results = exactcounts(trees1, PARAMS['trees2'] or trees1, bitsets,
			fast=not PARAMS['quadratic'], indices=PARAMS['indices'])
	if PARAMS['complete']:
		logging.info("complete matches %d of %d", n + 1, m)
	elif PARAMS['indices']:
		logging.info("exact indices %d of %d", n + 1, m)
	else:
		logging.info("exact counts %d of %d", n + 1, m)
	return results


def coverfragworker():
	""" Worker function that gets depth-1 fragments. Does not need
	multiprocessing but using it avoids reading the treebank again. """
	trees1 = PARAMS['trees1']
	trees2 = PARAMS['trees2']
	return coverbitsets(trees1, PARAMS['sents1'], PARAMS['labels'],
			max(trees1.maxnodes, (trees2 or trees1).maxnodes),
			PARAMS['disc'])


def workload(numtrees, mult, numproc):
	""" Get an even workload. When n trees are compared against themselves,
	n * (n - 1) total comparisons are made.
	Each tree m has to be compared to all trees x such that m < x < n.
	(meaning there are more comparisons for lower n).
	This function returns a sequence of (start, end) intervals such that
	the number of comparisons is approximately balanced. """
	# could base on number of nodes as well.
	if numproc == 1:
		return [(0, numtrees)]
	# here chunk is the number of tree pairs that will be compared
	goal = togo = total = 0.5 * numtrees * (numtrees - 1)
	chunk = total // (mult * numproc) + 1
	goal -= chunk
	result = []
	last = 0
	for n in range(1, numtrees):
		togo -= numtrees - n
		if togo <= goal:
			goal -= chunk
			result.append((last, n))
			last = n
	if last < numtrees:
		result.append((last, numtrees))
	return result


def getfragments(trees, sents, numproc=1, iterate=False, complement=False,
		indices=False):
	""" Get recurring fragments with exact counts in a single treebank. """
	if numproc == 0:
		numproc = cpu_count()
	numtrees = len(trees)
	assert numtrees
	mult = 1  # 3 if numproc > 1 else 1
	fragments = {}
	trees = trees[:]
	work = workload(numtrees, mult, numproc)
	PARAMS.update(disc=True, indices=indices, approx=False, complete=False,
			quadratic=False, complement=complement)
	if numproc == 1:
		initworkersimple(trees, list(sents))
		mymap = map
		myapply = lambda x, y: x(*y)
	else:
		logging.info("work division:\n%s", "\n".join("    %s: %r" % kv
			for kv in sorted(dict(numchunks=len(work),
				numproc=numproc).items())))
		# start worker processes
		pool = Pool(processes=numproc, initializer=initworkersimple,
			initargs=(trees, list(sents)))
		mymap = pool.map
		myapply = pool.apply
	# collect recurring fragments
	logging.info("extracting recurring fragments")
	for a in mymap(worker, work):
		fragments.update(a)
	# add 'cover' fragments corresponding to single productions
	cover = myapply(coverfragworker, ())
	before = len(fragments)
	fragments.update(cover)
	logging.info("merged %d unseen cover fragments", len(fragments) - before)
	fragmentkeys = list(fragments.keys())
	bitsets = [fragments[a] for a in fragmentkeys]
	countchunk = len(bitsets) // numproc + 1
	work = list(range(0, len(bitsets), countchunk))
	work = [(n, len(work), bitsets[a:a + countchunk])
			for n, a in enumerate(work)]
	logging.info("getting exact counts for %d fragments", len(bitsets))
	counts = []
	for a in mymap(exactcountworker, work):
		counts.extend(a)
	if numproc != 1:
		pool.close()
		pool.join()
		del pool
	if iterate:  # optionally collect fragments of fragments
		from .tree import Tree
		logging.info("extracting fragments of recurring fragments")
		PARAMS['complement'] = False  # needs to be turned off if it was on
		newfrags = fragments
		trees, sents = None, None
		ids = count()
		for _ in range(10):  # up to 10 iterations
			newtrees = [binarize(
					introducepreterminals(Tree.parse(tree, parse_leaf=int),
					ids=ids), childchar="}") for tree, _ in newfrags]
			newsents = [["#%d" % next(ids) if word is None else word
					for word in sent] for _, sent in newfrags]
			newfrags, newcounts = iteratefragments(
					fragments, newtrees, newsents, trees, sents, numproc)
			if len(newfrags) == 0:
				break
			if trees is None:
				trees = []
				sents = []
			trees.extend(newtrees)
			sents.extend(newsents)
			fragmentkeys.extend(newfrags)
			counts.extend(newcounts)
			fragments.update(zip(newfrags, newcounts))
	logging.info("found %d fragments", len(fragmentkeys))
	return dict(zip(fragmentkeys, counts))


def iteratefragments(fragments, newtrees, newsents, trees, sents, numproc):
	""" Get fragments of fragments. """
	numtrees = len(newtrees)
	assert numtrees
	if numproc == 1:  # set fragments as input
		initworkersimple(newtrees, newsents, trees, sents)
		mymap = map
	else:
		# since the input trees change, we need a new pool each time
		pool = Pool(processes=numproc, initializer=initworkersimple,
			initargs=(newtrees, newsents, trees, sents))
		mymap = pool.imap
	newfragments = {}
	for a in mymap(worker, workload(numtrees, 1, numproc)):
		newfragments.update(a)
	logging.info("before: %d, after: %d, difference: %d",
		len(fragments), len(set(fragments) | set(newfragments)),
		len(set(newfragments) - set(fragments)))
	# we have to get counts for these separately because they're not coming
	# from the same set of trees
	newkeys = list(set(newfragments) - set(fragments))
	bitsets = [newfragments[a] for a in newkeys]
	countchunk = len(bitsets) // numproc + 1
	if countchunk == 0:
		return newkeys, []
	work = list(range(0, len(bitsets), countchunk))
	work = [(n, len(work), bitsets[a:a + countchunk])
			for n, a in enumerate(work)]
	logging.info("getting exact counts for %d fragments", len(bitsets))
	counts = []
	for a in mymap(exactcountworker, work):
		counts.extend(a)
	if numproc != 1:
		pool.close()
		pool.join()
		del pool
	return newkeys, counts


def altrepr(a):
	""" Alternative format
	Replace double quotes with double single quotes: " -> ''
	Quote terminals with double quotes terminal: -> "terminal"
	Remove parentheses around frontier nodes: (NN ) -> NN

	>>> altrepr("(NP (DT a) (NN ))")
	'(NP (DT "a") NN)'
	"""
	return FRONTIERRE.sub(r'\1', TERMRE.sub(r'(\1 "\2")', a.replace('"', "''")))


def printfragments(fragments, counts, out=sys.stdout):
	""" Dump fragments to standard output or some other file object. """
	if PARAMS['complete']:
		logging.info("total number of matches: %d", sum(counts))
	else:
		logging.info("number of fragments: %d", len(fragments))
	if PARAMS['nofreq']:
		for a in fragments:
			if PARAMS['alt']:
				a = altrepr(a)
			out.write("%s\n" % (("%s\t%s" % (a[0],
					" ".join("%s" % x if x else "" for x in a[1])))
					if PARAMS['disc'] else a.decode('utf-8')))
		return
	# when comparing two treebanks, a frequency of 1 is normal;
	# otherwise, raise alarm.
	if PARAMS.get('trees2') or PARAMS['cover'] or PARAMS['complement']:
		threshold = 0
	else:
		threshold = 1
	if PARAMS['indices']:
		for a, theindices in zip(fragments, counts):
			if PARAMS['alt']:
				a = altrepr(a)
			if len(theindices) > threshold:
				out.write("%s\t%r\n" % (("%s\t%s" % (a[0],
					" ".join("%s" % x if x else "" for x in a[1])))
					if PARAMS['disc'] else a.decode('utf-8'),
					list(sorted(theindices.elements()))))
			elif threshold:
				raise ValueError("invalid fragment--frequency=1: %r" % a)
				#logging.warning("invalid fragment--frequency=1: %r", a)
		return
	for a, freq in zip(fragments, counts):
		if freq > threshold:
			if PARAMS['alt']:
				a = altrepr(a)
			out.write("%s\t%d\n" % (("%s\t%s" % (a[0],
				" ".join("%s" % x if x else "" for x in a[1])))
				if PARAMS['disc'] else a, freq))
		elif threshold:
			raise ValueError("invalid fragment--frequency=1: %r" % a)
			#logging.warning("invalid fragment--frequency=1: %r", a)


def test():
	""" Simple test. """
	main("fragments.py --disc --encoding iso-8859-1 sample2.export".split())

if __name__ == '__main__':
	main()
