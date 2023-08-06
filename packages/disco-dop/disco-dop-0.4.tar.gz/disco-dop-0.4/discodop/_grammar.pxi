""" Objects for grammars and grammar rules. """
import re
import logging
import numpy as np

# This regex should match exactly the set of valid yield functions,
# i.e., comma-separated strings of alternating occurrences from the set {0,1},
YFBINARY = re.compile(
		br'^(?:0|1|1?(?:01)+|0?(?:10)+)(?:,(?:0|1|1?(?:01)+|0?(?:10)+))*$')
YFUNARYRE = re.compile(br'^0(?:,0)*$')
# Match when non-integral weights are present
LCFRS_NONINT = re.compile(b'\t[0-9]+[./][0-9]+\n')
BITPAR_NONINT = re.compile(b'(?:^|\n)[0-9]+\.[0-9]+[ \t]')
LEXICON_NONINT = re.compile('[ \t][0-9]+[./][0-9]+[ \t\n]')

# comparison functions for sorting rules on LHS/RHS labels.
cdef int cmp0(const void *p1, const void *p2) nogil:
	cdef Rule *a = <Rule *>p1, *b = <Rule *>p2
	if a.lhs == b.lhs:
		return (a.no > b.no) - (a.no < b.no)
	return (a.lhs > b.lhs) - (a.lhs < b.lhs)
cdef int cmp1(const void *p1, const void *p2) nogil:
	cdef Rule *a = <Rule *>p1, *b = <Rule *>p2
	if a.rhs1 == b.rhs1:
		return (a.prob < b.prob) - (a.prob > b.prob)
	return (a.rhs1 > b.rhs1) - (a.rhs1 < b.rhs1)
cdef int cmp2(const void *p1, const void *p2) nogil:
	cdef Rule *a = <Rule *>p1, *b = <Rule *>p2
	if a.rhs2 == b.rhs2:
		return (a.prob < b.prob) - (a.prob > b.prob)
	return (a.rhs2 > b.rhs2) - (a.rhs2 < b.rhs2)


cdef class Grammar:
	""" A grammar object which stores rules compactly, indexed in various ways.

	:param rule_tuples_or_bytes: either a sequence of tuples containing both
		phrasal & lexical rules, or a bytes string containing the phrasal
		rules in text format; in the latter case ``lexicon`` should be given.
		The text format allows for more efficient loading and is used
		internally.
	:param start: a string identifying the unique start symbol of this grammar,
		which will be used by default when parsing with this grammar
	:param bitpar: whether to expect and use the bitpar grammar format

	By default the grammar is in logprob mode;
	invoke ``grammar.switch('default', logprob=False)`` to switch.
	If the grammar only contains integral weights (frequencies), they will
	be normalized into relative frequencies; if the grammar contains any
	non-integral weights, weights will be left unchanged. """
	def __cinit__(self):
		self.fanout = self.unary = self.mapping = self.splitmapping = NULL

	def __init__(self, rule_tuples_or_bytes, lexicon=None, start=b'ROOT',
			bitpar=False):
		cdef LexicalRule lexrule
		cdef double [:] weights
		cdef int n
		self.mapping = self.splitmapping = self.bylhs = NULL
		if not isinstance(start, bytes):
			start = start.encode('ascii')
		self.start = start
		self.bitpar = bitpar
		self.numunary = self.numbinary = self.currentmodel = 0
		self.modelnames = [u'default']
		self.logprob = False

		if rule_tuples_or_bytes and isinstance(rule_tuples_or_bytes, bytes):
			assert isinstance(lexicon, unicode), 'expected lexicon'
			self.origrules = rule_tuples_or_bytes
			self.origlexicon = lexicon
		elif rule_tuples_or_bytes and isinstance(
				rule_tuples_or_bytes[0], tuple):
			# convert tuples to strings with text format
			from discodop.grammar import write_lcfrs_grammar
			self.origrules, self.origlexicon = write_lcfrs_grammar(
					rule_tuples_or_bytes, bitpar=bitpar)
		else:
			raise ValueError(
					'expected non-empty sequence of tuples or bytes string.')

		# collect non-terminal labels; count number of rules in each category
		# for allocation purposes.
		rulelines = self.origrules.splitlines()
		fanoutdict = self._countrules(rulelines)
		self._convertlexicon(fanoutdict)
		self.tolabel = sorted(self.toid, key=self.toid.get)
		self.nonterminals = len(self.toid)
		self._allocate()
		self._convertrules(rulelines, fanoutdict)
		for n in range(self.nonterminals):
			self.fanout[n] = fanoutdict[self.tolabel[n]]
		del rulelines, fanoutdict
		# index & filter phrasal rules in different ways
		self._indexrules(self.bylhs, 0, 0)
		self._indexrules(self.unary, 1, 2)
		self._indexrules(self.lbinary, 1, 3)
		self._indexrules(self.rbinary, 2, 3)
		# if the grammar only contains integral values (frequencies),
		# normalize them into relative frequencies.
		nonint = BITPAR_NONINT if self.bitpar else LCFRS_NONINT
		if not (nonint.search(self.origrules)
				or LEXICON_NONINT.search(self.origlexicon)):
			self._normalize()
		# store 'default' weights
		weights = self.models[0]
		for n in range(self.numrules):
			weights[self.bylhs[0][n].no] = self.bylhs[0][n].prob
		for n, lexrule in enumerate(self.lexical, self.numrules):
			weights[n] = lexrule.prob
		self.switch('default', True)  # enable log probabilities

	@cython.wraparound(True)
	def _countrules(self, list rulelines):
		""" Count unary & binary rules; make a canonical list of all
		non-terminal labels and assign them unique IDs """
		Epsilon = b'Epsilon'
		# Epsilon gets ID 0, only occurs implicitly in RHS of lexical rules.
		self.toid = {Epsilon: 0}
		fanoutdict = {Epsilon: 0}  # temporary mapping of labels to fan-outs
		for line in rulelines:
			if not line.strip():
				continue
			fields = line.split()
			if self.bitpar:
				rule = fields[1:]
				yf = b'0' if len(rule) == 2 else b'01'
			else:
				rule = fields[:-2]
				yf = fields[-2]
			assert Epsilon not in rule, ('Epsilon symbol may only occur '
						'in RHS of lexical rules.')
			assert self.start not in rule[1:], (
					'Start symbol should only occur on LHS.')
			if len(rule) == 2:
				assert YFUNARYRE.match(yf), ('yield function refers to '
						'non-existent second non-terminal: %r\t%r' % (rule, yf))
				self.numunary += 1
			elif len(rule) == 3:
				assert YFBINARY.match(yf), 'illegal yield function: %s' % yf
				assert b'0' in yf and b'1' in yf, ('mismatch between '
						'non-terminals and yield function: %r\t%r' % (rule, yf))
				self.numbinary += 1
			else:
				raise ValueError('grammar not binarized:\n%s' % line)
			if rule[0] not in self.toid:
				self.toid[rule[0]] = len(self.toid)
				fanout = yf.count(b',') + 1
				fanoutdict[rule[0]] = fanout
				if fanout > self.maxfanout:
					self.maxfanout = fanout

		assert self.start in self.toid, ('Start symbol %r not in set of '
				'non-terminal labels extracted from grammar rules.' % self.start)
		self.numrules = self.numunary + self.numbinary
		self.phrasalnonterminals = len(self.toid)
		assert self.numrules, 'no rules found'
		return fanoutdict

	def _convertlexicon(self, fanoutdict):
		""" Make objects for lexical rules. """
		cdef int x
		self.lexical = []
		self.lexicalbyword = {}
		self.lexicalbylhs = {}
		for line in self.origlexicon.splitlines():
			if not line.strip():
				continue
			x = line.index('\t')
			word = line[:x]
			fields = line[x + 1:].encode('ascii').split()
			assert word not in self.lexicalbyword, (
					'word %r appears more than once in lexicon file' % word)
			self.lexicalbyword[word] = []
			for tag, w in zip(fields[::2], fields[1::2]):
				if tag not in self.toid:
					self.toid[tag] = len(self.toid)
					fanoutdict[tag] = 1
					# disabled because we add ids for labels on the fly:
					#logging.warning('POS tag %r for word %r '
					#		'not used in any phrasal rule', tag, word)
					#continue
				else:
					assert fanoutdict[tag] == 1, (
							'POS tag %r has fan-out %d, may only be 1.' % (
							fanoutdict[tag], tag))
				# convert fraction to float
				x = w.find(b'/')
				w = float(w[:x]) / float(w[x + 1:]) if x > 0 else float(w)
				assert w > 0, (
						'weights should be positive and non-zero:\n%r' % line)
				lexrule = LexicalRule(self.toid[tag], word, w)
				if lexrule.lhs not in self.lexicalbylhs:
					self.lexicalbylhs[lexrule.lhs] = {}
				self.lexical.append(lexrule)
				self.lexicalbyword[word].append(lexrule)
				self.lexicalbylhs[lexrule.lhs][word] = lexrule
			assert self.lexical and self.lexicalbyword and self.lexicalbylhs, (
					'no lexical rules found.')

	def _allocate(self):
		""" Allocate memory to store rules. """
		# store all non-lexical rules in a contiguous array
		# the other arrays will contain pointers to relevant parts thereof
		# (indexed on lhs, rhs1, and rhs2 of rules)
		self.bylhs = <Rule **>malloc(sizeof(Rule *) * self.nonterminals * 4)
		assert self.bylhs is not NULL
		self.bylhs[0] = NULL
		self.unary = &(self.bylhs[1 * self.nonterminals])
		self.lbinary = &(self.bylhs[2 * self.nonterminals])
		self.rbinary = &(self.bylhs[3 * self.nonterminals])
		# allocate the actual contiguous array that will contain the rules
		# (plus sentinels)
		self.bylhs[0] = <Rule *>malloc(sizeof(Rule) *
			(self.numrules + (2 * self.numbinary) + self.numunary + 4))
		assert self.bylhs[0] is not NULL
		self.unary[0] = &(self.bylhs[0][self.numrules + 1])
		self.lbinary[0] = &(self.unary[0][self.numunary + 1])
		self.rbinary[0] = &(self.lbinary[0][self.numbinary + 1])
		self.fanout = <UChar *>malloc(sizeof(UChar) * self.nonterminals)
		assert self.fanout is not NULL
		self.models = np.empty((1, self.numrules + len(self.lexical)), dtype='d')

	@cython.wraparound(True)
	cdef _convertrules(Grammar self, list rulelines, dict fanoutdict):
		""" Auxiliary function to create Grammar objects. Copies grammar
		rules from a text file to a contiguous array of structs. """
		cdef UInt n = 0, m
		cdef Rule *cur
		self.rulenos = {}
		for line in rulelines:
			if not line.strip():
				continue
			fields = line.split()
			if self.bitpar:
				rule = fields[1:]
				yf = b'0' if len(rule) == 2 else b'01'
				w = fields[0]
			else:
				rule = fields[:-2]
				yf = fields[-2]
				w = fields[-1]
			# check whether RHS labels have been seen as LHS and check fanout
			for m, nt in enumerate(rule):
				assert nt in self.toid, ('symbol %r has not been seen as LHS '
						'in any rule: %s' % (nt, line))
				fanout = yf.count(b',01'[m:m + 1]) + (m == 0)
				assert fanoutdict[nt] == fanout, (
						"conflicting fanouts for symbol '%s'.\n"
						"previous: %d; this non-terminal: %d.\nrule: %r" % (
						nt, fanoutdict[nt], fanout, rule))
			# convert fraction to float
			x = w.find(b'/')
			w = float(w[:x]) / float(w[x + 1:]) if x > 0 else float(w)
			assert w > 0, 'weights should be positive and non-zero:\n%r' % line
			# n is the rule index in the array, and will be the ID for the rule
			cur = &(self.bylhs[0][n])
			cur.no = n
			cur.lhs = self.toid[rule[0]]
			cur.rhs1 = self.toid[rule[1]]
			cur.rhs2 = self.toid[rule[2]] if len(rule) == 3 else 0
			cur.prob = w
			cur.lengths = cur.args = m = 0
			for a in yf.decode('ascii'):
				if a == ',':
					cur.lengths |= 1 << (m - 1)
					continue
				elif a == '1':
					cur.args += 1 << m
				elif a != '0':
					raise ValueError('expected: %r; got: %r' % ('0', a))
				m += 1
			cur.lengths |= 1 << (m - 1)
			assert m < (8 * sizeof(cur.args)), (m, (8 * sizeof(cur.args)))
			self.rulenos[(yf, ) + tuple(rule)] = n
			n += 1
		assert n == self.numrules, (n, self.numrules)

	def _normalize(self):
		""" Optionally normalize frequencies to relative frequencies.
		Should be run during initialization. """
		cdef double mass = 0
		cdef UInt n = 0, lhs
		cdef LexicalRule lexrule
		for lhs in range(self.nonterminals):
			mass = 0
			n = 0
			while self.bylhs[lhs][n].lhs == lhs:
				mass += self.bylhs[lhs][n].prob
				n += 1
			for lexrule in self.lexicalbylhs.get(lhs, {}).values():
				mass += lexrule.prob
			n = 0
			while self.bylhs[lhs][n].lhs == lhs:
				self.bylhs[lhs][n].prob /= mass
				n += 1
			for lexrule in self.lexicalbylhs.get(lhs, {}).values():
				lexrule.prob /= mass

	cdef _indexrules(Grammar self, Rule **dest, int idx, int filterlen):
		""" Auxiliary function to create Grammar objects. Copies certain
		grammar rules and sorts them on the given index.
		Resulting array is ordered by lhs, rhs1, or rhs2 depending on the value
		of `idx` (0, 1, or 2); filterlen can be 0, 2, or 3 to get all, only
		unary, or only binary rules, respectively.
		A separate array has a pointer for each non-terminal into this array;
		e.g.: dest[NP][0] == the first rule with an NP in the idx position. """
		cdef UInt prev = self.nonterminals, idxlabel = 0, n, m = 0
		cdef Rule *cur
		#need to set dest even when there are no rules for that idx
		for n in range(self.nonterminals):
			dest[n] = dest[0]
		if dest is self.bylhs:
			m = self.numrules
		else:
			for n in range(self.numrules):
				if (filterlen == 2) == (self.bylhs[0][n].rhs2 == 0):
					# copy this rule
					dest[0][m] = self.bylhs[0][n]
					assert dest[0][m].no < self.numrules
					m += 1
		if filterlen == 2:
			assert m == self.numunary, (m, self.numunary)
		elif filterlen == 3:
			assert m == self.numbinary, (m, self.numbinary)
		# sort rules by idx (NB: qsort is not stable, use appropriate cmp func)
		if idx == 0:
			qsort(dest[0], m, sizeof(Rule), &cmp0)
		elif idx == 1:
			qsort(dest[0], m, sizeof(Rule), &cmp1)
		elif idx == 2:
			qsort(dest[0], m, sizeof(Rule), &cmp2)
		# make index: dest[NP] points to first rule with NP in index position
		for n in range(m):
			cur = &(dest[0][n])
			if idx == 0:
				idxlabel = cur.lhs
			elif idx == 1:
				idxlabel = cur.rhs1
			elif idx == 2:
				idxlabel = cur.rhs2
			if idxlabel != prev:
				dest[idxlabel] = cur
			prev = idxlabel
			assert cur.no < self.numrules
		# sentinel rule
		dest[0][m].lhs = dest[0][m].rhs1 = dest[0][m].rhs2 = self.nonterminals

	def register(self, unicode name, weights):
		""" Register a probabilistic model given a name, and a sequence of
		floats ``weights``, with weights  in the same order as
		``self.origrules`` and ``self.origlexicon`` (which is an arbitrary
		order except that tags for each word are clustered together). """
		cdef int n, m = len(self.modelnames)
		cdef double [:] tmp
		assert name not in self.modelnames, 'model %r already exists' % name
		assert len(self.modelnames) <= 255, (
				'256 probabilistic models should be enough for anyone.')
		assert len(weights) == self.numrules + len(self.lexical), (
				'length mismatch: %d grammar rules, %d weights given.' % (
					self.numrules + len(self.lexical), len(weights)))
		self.models.resize(m + 1, self.numrules + len(self.lexical))
		self.modelnames.append(name)
		tmp = self.models[m]
		for n in range(self.numrules):
			tmp[n] = weights[n]
		for n in range(self.numrules, self.numrules + len(self.lexical)):
			tmp[n] = weights[n]

	def switch(self, name, bint logprob=True):
		""" Switch to a different probabilistic model;
		use 'default' to swith back to model given during initialization. """
		cdef int n, m = self.modelnames.index(name)
		cdef double [:] tmp
		cdef LexicalRule lexrule
		if self.currentmodel == m and self.logprob == logprob:
			return
		tmp = -np.log(self.models[m]) if logprob else self.models[m]
		for n in range(self.numrules):
			self.bylhs[0][n].prob = tmp[self.bylhs[0][n].no]
		for n in range(self.numbinary):
			self.lbinary[0][n].prob = tmp[self.lbinary[0][n].no]
			self.rbinary[0][n].prob = tmp[self.rbinary[0][n].no]
		for n in range(self.numunary):
			self.unary[0][n].prob = tmp[self.unary[0][n].no]
		for n, lexrule in enumerate(self.lexical, self.numrules):
			lexrule.prob = tmp[n]
		self.logprob = logprob
		self.currentmodel = m

	def buildchainvec(self):
		""" Build a boolean matrix representing the unary (chain) rules. """
		cdef UInt n
		cdef Rule *rule
		self.chainvec = <ULong *>calloc(self.nonterminals
				* BITNSLOTS(self.nonterminals), sizeof(ULong))
		assert self.chainvec is not NULL
		for n in range(self.numunary):
			rule = self.unary[n]
			SETBIT(self.chainvec, rule.rhs1 * self.nonterminals + rule.lhs)

	def testgrammar(self, epsilon=np.finfo(np.double).eps):  # machine epsilon
		""" Report whether all left-hand sides sum to 1 +/-epsilon for the
		currently selected weights. """
		cdef Rule *rule
		cdef LexicalRule lexrule
		cdef UInt n
		cdef list sums = [[] for _ in self.toid]
		cdef double [:] tmp = self.models[self.currentmodel, :]
		#We could be strict about separating POS tags and phrasal categories,
		#but Negra contains at least one tag (--) used for both.
		for n in range(self.numrules):
			rule = &(self.bylhs[0][n])
			sums[rule.lhs].append(tmp[rule.no])
		for n, lexrule in enumerate(self.lexical, self.numrules):
			sums[lexrule.lhs].append(tmp[n])
		for lhs, weights in enumerate(sums[1:], 1):
			mass = fsum(weights)
			if abs(mass - 1.0) > epsilon:
				logging.error("Weights of rules with LHS '%s' "
						"do not sum to 1 +/- %g: sum = %g; diff = %g",
						self.tolabel[lhs], epsilon, mass, mass - 1.0)
				return False
		logging.info('All left hand sides sum to 1 +/- epsilon=%s', epsilon)
		return True

	def getmapping(Grammar self, Grammar coarse, striplabelre=None,
			neverblockre=None, bint splitprune=False, bint markorigin=False):
		""" Construct a mapping of fine non-terminal IDs to coarse non-terminal
		IDs, by applying the regex ``striplabelre`` to the fine labels, used
		for coarse-to-fine pruning. A secondary regex neverblockre is for items
		that should never be pruned.
		The regexes should be compiled objects, i.e., ``re.compile(regex)``,
		or ``None`` to leave labels unchanged. ``coarse`` may be ``None``, in
		which case only ``neverblockre`` is effective, which is also used for
		non-pruning purposes.

		- use ``|<`` to ignore nodes introduced by binarization;
			useful if coarse and fine stages employ different kinds of
			markovization; e.g., ``NP`` and ``VP`` may be blocked,
			but not ``NP|<DT-NN>``.
		- ``_[0-9]+`` to ignore discontinuous nodes ``X_n`` where ``X`` is a
			label and *n* is a fanout. """
		cdef int n, m, components = 0
		cdef set seen = {0}
		if coarse is None:
			coarse = self
		if self.mapping is not NULL:
			free(self.mapping)
		self.mapping = <UInt *>malloc(sizeof(UInt) * self.nonterminals)
		if splitprune and markorigin:
			if self.splitmapping is not NULL:
				if self.splitmapping[0] is not NULL:
					free(self.splitmapping[0])
				free(self.splitmapping)
			self.splitmapping = <UInt **>malloc(sizeof(UInt *)
					* self.nonterminals)
			for n in range(self.nonterminals):
				self.splitmapping[n] = NULL
			self.splitmapping[0] = <UInt *>malloc(sizeof(UInt) *
				sum([self.fanout[n] for n in range(self.nonterminals)
					if self.fanout[n] > 1]))
		for n in range(self.nonterminals):
			if not neverblockre or neverblockre.search(self.tolabel[n]) is None:
				strlabel = self.tolabel[n]
				if striplabelre is not None:
					strlabel = striplabelre.sub(b'', strlabel, 1)
				if self.fanout[n] > 1 and splitprune:
					strlabel += b'*'
				if self.fanout[n] > 1 and splitprune and markorigin:
					self.mapping[n] = self.nonterminals  # sentinel value
					self.splitmapping[n] = &(self.splitmapping[0][components])
					components += self.fanout[n]
					for m in range(self.fanout[n]):
						self.splitmapping[n][m] = coarse.toid[
								strlabel + str(m).encode('ascii')]
						seen.add(self.splitmapping[n][m])
				else:
					self.mapping[n] = coarse.toid[strlabel]
					seen.add(self.mapping[n])
			else:
				self.mapping[n] = 0
		if seen == set(range(coarse.nonterminals)):
			msg = 'label sets are equal'
		else:
			# NB: ALL fine symbols are mapped to some coarse symbol;
			# we only check if all coarse symbols have received a mapping.
			l = sorted([coarse.tolabel[a].decode('ascii') for a in
					set(range(coarse.nonterminals)) - seen])
			diff = ', '.join(l[:10]) + (', ...' if len(l) > 10 else '')
			if coarse.nonterminals > self.nonterminals:
				msg = ('grammar is not a superset of coarse grammar:\n'
						'coarse labels without mapping: {%s}' % diff)
			elif coarse.nonterminals < self.nonterminals:
				msg = 'grammar is a proper superset of coarse grammar.'
			else:
				msg = ('equal number of nodes, but not equivalent:\n'
						'coarse labels without mapping: {%s}' % diff)
		return msg

	def getrulemapping(Grammar self, Grammar coarse):
		""" Produce a mapping of coarse rules to sets of fine rules;
		e.g., ``mapping[12] == [34, 56, 78, ...]``.
		For use with ``dopparseprob()``. """
		cdef list mapping = [[] for _ in range(coarse.numrules)]
		cdef Rule *rule
		for ruleno in range(self.numrules):
			rule = &(self.bylhs[0][ruleno])
			key = (self.yfstr(rule[0]),
					self.tolabel[rule.lhs].rsplit('@', 1)[0],
					self.tolabel[rule.rhs1].rsplit('@', 1)[0])
			if rule.rhs2:
				key += (self.tolabel[rule.rhs2].rsplit('@', 1)[0], )
			mapping[coarse.rulenos[key]].append(ruleno)
		self.rulemapping = mapping

	cdef rulestr(self, Rule rule):
		left = '%.2f %s => %s%s' % (
			exp(-rule.prob) if self.logprob else rule.prob,
			self.tolabel[rule.lhs].decode('ascii'),
			self.tolabel[rule.rhs1].decode('ascii'),
			' %s' % self.tolabel[rule.rhs2].decode('ascii')
				if rule.rhs2 else '')
		return '%s %s [%d]' % (left.ljust(40), self.yfstr(rule), rule.no)

	cdef yfstr(self, Rule rule):
		cdef int n, m = 0
		cdef result = ''
		for n in range(8 * sizeof(rule.args)):
			result += '1' if (rule.args >> n) & 1 else '0'
			if (rule.lengths >> n) & 1:
				m += 1
				if m == self.fanout[rule.lhs]:
					return result
				else:
					result += ','
		raise ValueError('illegal yield function expected %d components.\n'
				'args: %s; lengths: %s' % (self.fanout[rule.lhs],
				bin(rule.args), bin(rule.lengths)))

	def __str__(self):
		cdef LexicalRule lexrule
		cdef size_t n
		rules = '\n'.join(filter(None,
			[self.rulestr(self.bylhs[0][n]) for n in range(self.numrules)]))
		lexical = '\n'.join(['%.2f %s => %s' % (
				exp(-lexrule.prob) if self.logprob else lexrule.prob,
				self.tolabel[lexrule.lhs].decode('ascii'),
				lexrule.word.encode('unicode-escape').decode('ascii'))
			for word in sorted(self.lexicalbyword)
			for lexrule in sorted(self.lexicalbyword[word],
			key=lambda lexrule: (<LexicalRule>lexrule).lhs)])
		labels = ', '.join(['%s=%d' % (a.decode('ascii'), b)
				for a, b in sorted(self.toid.items())])
		return 'rules:\n%s\nlexicon:\n%s\nlabels:\n%s' % (
				rules, lexical, labels)

	def __repr__(self):
		return '%s(\n%s,\n%s\n)' % (self.__class__.__name__,
				self.origrules, self.origlexicon)

	def __reduce__(self):
		""" Helper function for pickling. """
		return (Grammar, (self.origrules, self.origlexicon,
				self.start, self.logprob, self.bitpar))

	def __dealloc__(self):
		if self.bylhs is NULL:
			return
		free(self.bylhs[0])
		self.bylhs[0] = NULL
		free(self.bylhs)
		self.bylhs = NULL
		free(self.fanout)
		self.fanout = NULL
		if self.chainvec is not NULL:
			free(self.chainvec)
			self.chainvec = NULL
		if self.mapping is not NULL:
			free(self.mapping)
			self.mapping = NULL
		if self.splitmapping is not NULL:
			free(self.splitmapping[0])
			free(self.splitmapping)
			self.splitmapping = NULL
