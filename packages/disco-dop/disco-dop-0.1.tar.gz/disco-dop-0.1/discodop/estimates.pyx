""" Implementation of outside estimates:
- PCFG A* estimate (Klein & Manning 2003),
- PLCFRS LR context-summary estimate (Kallmeyer & Maier 2010).
The latter ported almost directly from rparse
(except for sign reversal of log probs). """

from __future__ import print_function
from math import exp
from containers cimport Grammar, Rule, LexicalRule, SmallChartItem as ChartItem
from containers cimport UInt, ULLong, new_ChartItem
from agenda cimport Agenda, Entry
cimport numpy as np
from bit cimport nextset, nextunset, bitcount, bitlength, testbit, testbitint
import numpy as np
np.import_array()
infinity = float('infinity')

cdef extern from "math.h":
	bint isnan(double x)
	bint isfinite(double x)

cdef class Item:
	cdef int state, length, lr, gaps
	def __hash__(Item self):
		return self.state * 1021 + self.length * 571 + self.lr * 311 + self.gaps
	def __richcmp__(Item self, Item other, op):
		if op == 2:
			return (self.state == other.state and self.length == other.length
				and self.lr == other.lr and self.gaps == other.gaps)
		a = (self.state, self.length, self.lr, self.gaps)
		b = (other.state, other.length, other.lr, other.gaps)
		if op == 0:
			return a < b
		elif op == 1:
			return a <= b
		elif op == 3:
			return a != b
		elif op == 4:
			return a > b
		elif op == 5:
			return a >= b
	def __repr__(Item self):
		return "%s(%4d, %2d, %2d, %2d)" % (self.__class__.__name__,
			self.state, self.length, self.lr, self.gaps)

cdef inline Item new_Item(int state, int length, int lr, int gaps):
	cdef Item item = Item.__new__(Item)
	item.state = state
	item.length = length
	item.lr = lr
	item.gaps = gaps
	return item

cdef inline double getoutside(np.ndarray[np.double_t, ndim=4] outside,
		UInt maxlen, UInt slen, UInt label, ULLong vec):
	""" Query for outside estimate. NB: if this would be used, it should be in
	a .pxd with `inline.' However, passing the numpy array is slow. """
	cdef UInt length = bitcount(vec)
	cdef UInt left = nextset(vec, 0)
	cdef UInt gaps = bitlength(vec) - length - left
	cdef UInt right = slen - length - left - gaps
	cdef UInt lr = left + right
	if slen > maxlen or length + lr + gaps > maxlen:
		return 0.0
	return outside[label, length, lr, gaps]

def simpleinside(Grammar grammar, UInt maxlen,
		np.ndarray[np.double_t, ndim=2] insidescores):
	""" Compute simple inside estimate in bottom-up fashion.
	Here vec is actually the length (number of terminals in the yield of
	the constituent)
	insidescores is a 2-dimensional matrix initialized with NaN to indicate
	values that have yet to be computed. """
	cdef ChartItem I
	cdef Entry entry
	cdef Rule rule
	cdef LexicalRule lexrule
	cdef Agenda agenda = Agenda()
	cdef np.double_t x
	cdef size_t i
	cdef ULLong vec

	for i in grammar.lexicalbylhs:
		agenda[new_ChartItem(i, 1)] = min([lexrule.prob
			for lexrule in grammar.lexicalbylhs[i]])

	while agenda.length:
		entry = agenda.popentry()
		I = entry.key
		x = entry.value

		# This comparison catches the case when insidescores has a higher
		# value than x, but also when it is NaN, because all comparisons
		# against NaN are false.
		#if not x >= insidescores[I.label, I.vec]:
		# Mory explicitly:
		if (isnan(insidescores[I.label, I.vec])
			or x < insidescores[I.label, I.vec]):
			insidescores[I.label, I.vec] = x

		for i in range(grammar.nonterminals):
			rule = grammar.unary[I.label][i]
			if rule.rhs1 != I.label:
				break
			elif isnan(insidescores[rule.lhs, I.vec]):
				agenda.setifbetter(
						new_ChartItem(rule.lhs, I.vec), rule.prob + x)

		for i in range(grammar.nonterminals):
			rule = grammar.lbinary[I.label][i]
			if rule.rhs1 != I.label:
				break
			for vec in range(1, maxlen - I.vec + 1):
				if (isfinite(insidescores[rule.rhs2, vec])
					and isnan(insidescores[rule.lhs, I.vec + vec])):
					agenda.setifbetter(new_ChartItem(rule.lhs, I.vec + vec),
						rule.prob + x + insidescores[rule.rhs2, vec])

		for i in range(grammar.nonterminals):
			rule = grammar.rbinary[I.label][i]
			if rule.rhs2 != I.label:
				break
			for vec in range(1, maxlen - I.vec + 1):
				if (isfinite(insidescores[rule.rhs1, vec])
					and isnan(insidescores[rule.lhs, vec + I.vec])):
					agenda.setifbetter(new_ChartItem(rule.lhs, vec + I.vec),
						rule.prob + insidescores[rule.rhs1, vec] + x)

	# anything not reached so far gets probability zero:
	insidescores[np.isnan(insidescores)] = np.inf

def inside(Grammar grammar, UInt maxlen, dict insidescores):
	""" Compute inside estimate in bottom-up fashion, with
	full bit vectors (not used)."""
	cdef ChartItem I
	cdef Entry entry
	cdef LexicalRule lexrule
	cdef size_t i
	agenda = Agenda()

	for i in grammar.lexicalbylhs:
		agenda[new_ChartItem(i, 1)] = min([lexrule.prob
			for lexrule in grammar.lexicalbylhs[i]])

	while agenda.length:
		entry = agenda.popentry()
		I = entry.key
		x = entry.value
		if I.label not in insidescores:
			insidescores[I.label] =  {}
		if x < insidescores[I.label].get(I.vec, infinity):
			insidescores[I.label][I.vec] = x

		for i in range(grammar.nonterminals):
			rule = grammar.unary[I.label][i]
			if rule.rhs1 != I.label:
				break
			elif (rule.lhs not in insidescores
				or I.vec not in insidescores[rule.lhs]):
				agenda.setifbetter(
					new_ChartItem(rule.lhs, I.vec), rule.prob + x)

		for i in range(grammar.nonterminals):
			rule = grammar.lbinary[I.label][i]
			if rule.rhs1 != I.label:
				break
			elif rule.rhs2 not in insidescores:
				continue
			for vec in insidescores[rule.rhs2]:
				left = insideconcat(I.vec, vec, rule, grammar, maxlen)
				if left and (rule.lhs not in insidescores
					or left not in insidescores[rule.lhs]):
					agenda.setifbetter(new_ChartItem(rule.lhs, left),
						rule.prob + x + insidescores[rule.rhs2][vec])

		for i in range(grammar.nonterminals):
			rule = grammar.rbinary[I.label][i]
			if rule.rhs2 != I.label:
				break
			elif rule.rhs1 not in insidescores:
				continue
			for vec in insidescores[rule.rhs1]:
				right = insideconcat(vec, I.vec, rule, grammar, maxlen)
				if right and (rule.lhs not in insidescores
					or right not in insidescores[rule.lhs]):
					agenda.setifbetter(new_ChartItem(rule.lhs, right),
						rule.prob + insidescores[rule.rhs1][vec] + x)

	return insidescores

cdef inline ULLong insideconcat(ULLong a, ULLong b, Rule rule, Grammar grammar,
		UInt maxlen):
	if grammar.fanout[rule.lhs] + bitcount(a) + bitcount(b) > maxlen + 1:
		return 0
	result = resultpos = l = r = 0
	for x in range(bitlength(rule.lengths)):
		if testbitint(rule.args, x) == 0:
			subarg = nextunset(a, l) - l
			result |= (1 << subarg) - 1 << resultpos
			resultpos += subarg
			l = subarg + 1
		else:
			subarg = nextunset(b, r) - r
			result |= (1 << subarg) - 1 << resultpos
			resultpos += subarg
			r = subarg + 1
		if testbitint(rule.lengths, x):
			resultpos += 1
			result &= ~(1 << resultpos)
	return result


def outsidelr(Grammar grammar, np.ndarray[np.double_t, ndim=2] insidescores,
		UInt maxlen, UInt goal, np.ndarray[np.double_t, ndim=4] outside):
	""" Compute the outside SX simple LR estimate in top down fashion. """
	cdef Agenda agenda = Agenda()
	cdef np.double_t current, score
	cdef Entry entry
	cdef Item I
	cdef Rule rule
	cdef LexicalRule lexrule
	cdef double x, insidescore
	cdef int m, n, totlen, addgaps, addright, leftfanout, rightfanout
	cdef int lenA, lenB, lr, ga
	cdef size_t i
	cdef bint stopaddleft, stopaddright

	for n in range(1, maxlen + 1):
		agenda[new_Item(goal, n, 0, 0)] = 0.0
		outside[goal, n, 0, 0] = 0.0
	print("initialized")

	while agenda.length:
		entry = agenda.popentry()
		I = entry.key
		x = entry.value
		if agenda.length % 1000 == 0:
			print("agenda size: %dk top: %r, %g %s" % (
				agenda.length / 1000, I, exp(-x), grammar.tolabel[I.state].decode('ascii')))
		totlen = I.length + I.lr + I.gaps
		i = 0
		rule = grammar.bylhs[I.state][i]
		while rule.lhs == I.state:
			# X -> A
			if rule.rhs2 == 0:
				score = rule.prob + x
				if score < outside[rule.rhs1, I.length, I.lr, I.gaps]:
					agenda.setitem(
						new_Item(rule.rhs1, I.length, I.lr, I.gaps), score)
					outside[rule.rhs1, I.length, I.lr, I.gaps] = score
				i += 1
				rule = grammar.bylhs[I.state][i]
				continue
			# X -> A B
			addgaps = addright = 0
			stopaddright = False
			for n in range(bitlength(rule.lengths) - 1, -1, -1):
				if testbitint(rule.args, n):
					if stopaddright:
						addgaps += 1
					else:
						addright += 1
				elif not stopaddright:
					stopaddright = True

			leftfanout = grammar.fanout[rule.rhs1]
			rightfanout = grammar.fanout[rule.rhs2]

			# binary-left (A is left)
			for lenA in range(leftfanout, I.length - rightfanout + 1):
				lenB = I.length - lenA
				insidescore = insidescores[rule.rhs2, lenB]
				for lr in range(I.lr, I.lr + lenB + 2): #FIXME: why 2?
					if addright == 0 and lr != I.lr:
						continue
					for ga in range(leftfanout - 1, totlen + 1):
						if (lenA + lr + ga == I.length + I.lr + I.gaps
							and ga >= addgaps):
							score = rule.prob + x + insidescore
							current = outside[rule.rhs1, lenA, lr, ga]
							if score < current:
								agenda.setitem(
									new_Item(rule.rhs1, lenA, lr, ga), score)
								outside[rule.rhs1, lenA, lr, ga] = score

			# X -> B A
			addgaps = addright = 0
			stopaddleft = False
			for n in range(bitlength(rule.lengths)):
				if not stopaddleft and testbitint(rule.args, n):
					stopaddleft = True
				if not testbitint(rule.args, n):
					if stopaddleft:
						addgaps += 1

			stopaddright = False
			for n in range(bitlength(rule.lengths) - 1, -1, -1):
				if not stopaddright and testbitint(rule.args, n):
					stopaddright = True
				if not testbitint(rule.args, n) and not stopaddright:
					addright += 1
			addgaps -= addright

			# binary-right (A is right)
			for lenA in range(rightfanout, I.length - leftfanout + 1):
				lenB = I.length - lenA
				insidescore = insidescores[rule.rhs1, lenB]
				for lr in range(I.lr, I.lr + lenB + 2): #FIXME: why 2?
					for ga in range(rightfanout - 1, totlen + 1):
						if (lenA + lr + ga == I.length + I.lr + I.gaps
							and ga >= addgaps):
							score = rule.prob + insidescore + x
							current = outside[rule.rhs2, lenA, lr, ga]
							if score < current:
								agenda.setitem(
									new_Item(rule.rhs2, lenA, lr, ga), score)
								outside[rule.rhs2, lenA, lr, ga] = score
			i += 1
			rule = grammar.bylhs[I.state][i]
		#end while rule.lhs == I.state:
	#end while agenda.length:

cpdef getestimates(Grammar grammar, UInt maxlen, UInt goal):
	print("allocating outside matrix:",
		(8 * grammar.nonterminals * (maxlen + 1) * (maxlen + 1)
			* (maxlen + 1) / 1024 ** 2), 'MB')
	insidescores = np.empty((grammar.nonterminals, (maxlen + 1)), dtype='d')
	outside = np.empty((grammar.nonterminals, ) + 3 * (maxlen + 1, ), dtype='d')
	insidescores.fill(np.NAN)
	outside.fill(np.inf)
	print("getting inside estimates")
	simpleinside(grammar, maxlen, insidescores)
	print("getting outside estimates")
	outsidelr(grammar, insidescores, maxlen, goal, outside)
	return outside

cdef inline double getpcfgoutside(dict outsidescores,
		UInt maxlen, UInt slen, UInt label, ULLong vec):
	""" Query for a PCFG A* estimate. For documentation purposes. """
	cdef UInt length = bitcount(vec)
	cdef UInt left = nextset(vec, 0)
	cdef UInt right = slen - length - left
	cdef UInt lr = left + right
	if slen > maxlen or length + left + right > maxlen:
		return 0.0
	return outsidescores[label, left, right]

cpdef getpcfgestimates(Grammar grammar, UInt maxlen, UInt goal,
		bint debug=False):
	insidescores = pcfginsidesx(grammar, maxlen)
	outside = pcfgoutsidesx(grammar, insidescores, goal, maxlen)
	if debug:
		print('inside:')
		for span in range(1, maxlen + 1):
			for k, v in sorted(insidescores[span].items()):
				if v < infinity:
					print("%s[%d] %g" % (grammar.tolabel[k].decode('ascii'), span, exp(-v)))
		print('infinite:', end='')
		for span in range(1, maxlen + 1):
			for k, v in sorted(insidescores[span].items()):
				if v == infinity:
					print("%s[%d]" % (grammar.tolabel[k].decode('ascii'), span), end='')
		print('\n\noutside:')
		for lspan in range(maxlen + 1):
			for rspan in range(maxlen - lspan + 1):
				for lhs in range(grammar.nonterminals):
					if outside[lhs, lspan, rspan] < infinity:
						print("%s[%d-%d] %g" % (grammar.tolabel[lhs].decode('ascii'),
								lspan, rspan, exp(-outside[lhs, lspan, rspan])))
	return outside

cdef pcfginsidesx(Grammar grammar, UInt maxlen):
	""" insideSX estimate for a PCFG using agenda. Adapted from:
	Klein & Manning (2003), A* parsing: Fast Exact Viterbi Parse Selection. """
	cdef size_t n, split
	cdef ULLong vec
	cdef ChartItem I
	cdef Entry entry
	cdef Rule rule
	cdef LexicalRule lexrule
	cdef Agenda agenda = Agenda()
	cdef double x
	cdef list insidescores = [{} for n in range(maxlen + 1)]
	for n in grammar.lexicalbylhs:
		x = min([lexrule.prob for lexrule in grammar.lexicalbylhs[n]])
		agenda[new_ChartItem(n, 1)] = x
	while agenda.length:
		entry = agenda.popentry()
		I = entry.key
		x = entry.value
		if (I.label not in insidescores[I.vec]
				or x < insidescores[I.vec][I.label]):
			insidescores[I.vec][I.label] = x

		for i in range(grammar.nonterminals):
			rule = grammar.unary[I.label][i]
			if rule.rhs1 != I.label:
				break
			elif rule.lhs not in insidescores[I.vec]:
				agenda.setifbetter(
						new_ChartItem(rule.lhs, I.vec), rule.prob + x)

		for i in range(grammar.nonterminals):
			rule = grammar.lbinary[I.label][i]
			if rule.rhs1 != I.label:
				break
			for vec in range(1, maxlen - I.vec + 1):
				if (rule.rhs2 in insidescores[vec]
					and rule.lhs not in insidescores[I.vec + vec]):
					agenda.setifbetter(new_ChartItem(rule.lhs, I.vec + vec),
						rule.prob + x + insidescores[vec][rule.rhs2])

		for i in range(grammar.nonterminals):
			rule = grammar.rbinary[I.label][i]
			if rule.rhs2 != I.label:
				break
			for vec in range(1, maxlen - I.vec + 1):
				if (rule.rhs1 in insidescores[vec]
					and rule.lhs not in insidescores[vec + I.vec]):
					agenda.setifbetter(new_ChartItem(rule.lhs, vec + I.vec),
						rule.prob + insidescores[vec][rule.rhs1] + x)
	return insidescores

cdef pcfgoutsidesx(Grammar grammar, list insidescores, UInt goal, UInt maxlen):
	""" outsideSX estimate for a PCFG, agenda-based version. """
	cdef Agenda agenda = Agenda()
	cdef Entry entry
	cdef tuple I
	cdef Rule rule
	cdef LexicalRule lexrule
	cdef np.double_t current, score
	cdef double x, insidescore
	cdef int m, n, state, left, right
	cdef size_t i, sibsize
	cdef np.ndarray[np.double_t, ndim=4] outside = np.empty(
				(grammar.nonterminals, maxlen + 1, maxlen + 1, 1), dtype='d')
	outside.fill(np.inf)

	agenda[goal, 0, 0] = outside[goal, 0, 0, 0] = 0.0
	while agenda.length:
		entry = agenda.popentry()
		I = entry.key
		x = entry.value
		state, left, right = I
		if agenda.length % 1000 == 0:
			print("agenda size: %dk top: %r, %g %s" % (
				agenda.length / 1000, I, exp(-x), grammar.tolabel[state].decode('ascii')))
		i = 0
		rule = grammar.bylhs[state][i]
		while rule.lhs == state:
			# X -> A
			if rule.rhs2 == 0:
				score = rule.prob + x
				if score < outside[rule.rhs1, left, right, 0]:
					agenda.setitem((rule.rhs1, left, right), score)
					outside[rule.rhs1, left, right, 0] = score
				i += 1
				rule = grammar.bylhs[state][i]
				continue

			# item is on the left: X -> A B.
			for sibsize in range(1, maxlen - left - right):
				insidescore = insidescores[sibsize].get(rule.rhs2, infinity)
				score = rule.prob + x + insidescore
				current = outside[rule.rhs1, left, right + sibsize, 0]
				if score < current:
					agenda.setitem((rule.rhs1, left, right + sibsize), score)
					outside[rule.rhs1, left, right + sibsize, 0] = score

			# item is on the right: X -> B A
			for sibsize in range(1, maxlen - left - right):
				insidescore = insidescores[sibsize].get(rule.rhs1, infinity)
				score = rule.prob + insidescore + x
				current = outside[rule.rhs2, left + sibsize, right, 0]
				if score < current:
					agenda.setitem((rule.rhs2, left + sibsize, right), score)
					outside[rule.rhs2, left + sibsize, right, 0] = score

			i += 1
			rule = grammar.bylhs[state][i]
		#end while rule.lhs == state:
	#end while agenda.length:
	return outside

cpdef getpcfgestimatesrec(Grammar grammar, UInt maxlen, UInt goal,
	bint debug=False):
	insidescores = [{} for _ in range(maxlen + 1)]
	outsidescores = {}
	for span in range(1, maxlen + 1):
		insidescores[span][goal] = pcfginsidesxrec(
			grammar, insidescores, goal, span)
	for lspan in range(maxlen + 1):
		for rspan in range(maxlen - lspan + 1):
			for lhs in grammar.lexicalbylhs:
				if (lhs, lspan, rspan) in outsidescores:
					continue
				outsidescores[lhs, lspan, rspan] = pcfgoutsidesxrec(grammar,
						insidescores, outsidescores, goal, lhs, lspan, rspan)
	if debug:
		print('inside:')
		for span in range(1, maxlen + 1):
			for k, v in sorted(insidescores[span].items()):
				if v < infinity:
					print("%s[%d] %g" % (grammar.tolabel[k].decode('ascii'), span, exp(-v)))
		print('infinite:', end='')
		for span in range(1, maxlen + 1):
			for k, v in sorted(insidescores[span].items()):
				if v == infinity:
					print("%s[%d]" % (grammar.tolabel[k].decode('ascii'), span), end='')

		print('\n\noutside:')
		for k, v in sorted(outsidescores.items()):
			if v < infinity:
				print("%s[%d-%d] %g" % (
						grammar.tolabel[k[0]].decode('ascii'), k[1], k[2], exp(-v)))
		print('infinite:', end='')
		for k, v in sorted(outsidescores.items()):
			if v == infinity:
				print("%s[%d-%d]" % (
						grammar.tolabel[k[0]].decode('ascii'), k[1], k[2]), end='')
	outside = np.empty((grammar.nonterminals, maxlen + 1, maxlen + 1, 1),
			dtype='d')
	outside.fill(np.inf)
	#convert sparse dictionary to dense numpy array
	for (state, lspan, rspan), prob in outsidescores.items():
		outside[state, lspan, rspan, 0] = prob
	return outside

cdef pcfginsidesxrec(Grammar grammar, list insidescores, UInt state, int span):
	""" insideSX estimate for a PCFG. Straight from Klein & Manning (2003),
	A* parsing: Fast Exact Viterbi Parse Selection. """
	# NB: does not deal correctly with unary rules.
	cdef size_t n, split
	cdef Rule rule
	cdef LexicalRule lexrule
	if span == 0:
		return 0 if state == 0 else infinity
	if span == 1 and state in grammar.lexicalbylhs:
		score =  min([lexrule.prob for lexrule in grammar.lexicalbylhs[state]])
	else:
		score = infinity
	for split in range(1, span + 1):
		n = 0
		rule = grammar.bylhs[state][n]
		while rule.lhs == state:
			if rule.rhs1 in insidescores[split]:
				inleft = insidescores[split][rule.rhs1]
				if inleft == -1:
					n += 1
					rule = grammar.bylhs[state][n]
			else:
				insidescores[split][rule.rhs1] = -1 # mark to avoid cycles.
				inleft = pcfginsidesxrec(
					grammar, insidescores, rule.rhs1, split)
				insidescores[split][rule.rhs1] = inleft
			if rule.rhs2 == 0:
				if split == span:
					inright = 0
				else:
					n += 1
					rule = grammar.bylhs[state][n]
					continue
			elif rule.rhs2 in insidescores[span - split]:
				inright = insidescores[span - split][rule.rhs2]
			else:
				inright = pcfginsidesxrec(
					grammar, insidescores, rule.rhs2, span - split)
				insidescores[span - split][rule.rhs2] = inright
			cost = inleft + inright + rule.prob
			if cost < score:
				score = cost
			n += 1
			rule = grammar.bylhs[state][n]
	return score

cdef pcfgoutsidesxrec(Grammar grammar, list insidescores, dict outsidescores,
		UInt goal, UInt state, int lspan, int rspan):
	""" outsideSX estimate for a PCFG. """
	# NB: does not deal correctly with unary rules.
	cdef size_t n, sibsize
	cdef Rule rule
	cdef tuple item
	if lspan + rspan == 0:
		return 0 if state == goal else infinity
	score = infinity
	# unary productions: no sibling
	n = 0
	rule = grammar.unary[state][n]
	while rule.rhs1 == state:
		item = (rule.lhs, lspan, rspan)
		if item in outsidescores:
			out = outsidescores[item]
			if out == -1:
				n += 1
				rule = grammar.unary[state][n]
				continue
		else:
			outsidescores[item] = -1 # mark to avoid cycles
			outsidescores[item] = out = pcfgoutsidesxrec(grammar,
				insidescores, outsidescores, goal, rule.lhs, lspan, rspan)
		cost = out + rule.prob
		if cost < score:
			score = cost
		n += 1
		rule = grammar.unary[state][n]
	# could have a left sibling
	for sibsize in range(1, lspan + 1):
		n = 0
		rule = grammar.rbinary[state][n]
		while rule.rhs2 == state:
			item = (rule.lhs, lspan - sibsize, rspan)
			if item in outsidescores:
				out = outsidescores[item]
			else:
				outsidescores[item] = out = pcfgoutsidesxrec(grammar,
						insidescores, outsidescores, goal, rule.lhs,
						lspan - sibsize, rspan)
			cost = (insidescores[sibsize].get(rule.rhs1, infinity)
					+ out + rule.prob)
			if cost < score:
				score = cost
			n += 1
			rule = grammar.rbinary[state][n]
	# could have a right sibling
	for sibsize in range(1, rspan + 1):
		n = 0
		rule = grammar.lbinary[state][n]
		while rule.rhs1 == state:
			item = (rule.lhs, lspan, rspan - sibsize)
			if item in outsidescores:
				out = outsidescores[item]
			else:
				out = pcfgoutsidesxrec(grammar, insidescores,
					outsidescores, goal, rule.lhs, lspan, rspan - sibsize)
				outsidescores[item] = out
			cost = (insidescores[sibsize].get(rule.rhs2, infinity)
					+ out + rule.prob)
			if cost < score:
				score = cost
			n += 1
			rule = grammar.lbinary[state][n]
	return score

cpdef testestimates(Grammar grammar, UInt maxlen, UInt goal):
	print("getting inside")
	insidescores = inside(grammar, maxlen, {})
	for a in insidescores:
		for b in insidescores[a]:
			assert 0 <= a < grammar.nonterminals
			assert 0 <= bitlength(b) <= maxlen
			#print(a, b)
			#print("%s[%d] =" % (grammar.tolabel[a].decode('ascii'), b), exp(insidescores[a][b]))
	print(len(insidescores) * sum(map(len, insidescores.values())), '\n')
	insidescores = np.empty((grammar.nonterminals, (maxlen + 1)), dtype='d')
	insidescores.fill(np.NAN)
	simpleinside(grammar, maxlen, insidescores)
	print("inside")
	for an, a in enumerate(insidescores):
		for bn, b in enumerate(a):
			if b < np.inf:
				print("%s len %d = %g" % (grammar.tolabel[an].decode('ascii'), bn, exp(-b)))
	#print(insidescores)
	#for a in range(maxlen):
	#	print(grammar.tolabel[goal].decode('ascii'), "len", a, "=", exp(-insidescores[goal, a]))

	print("getting outside")
	outside = np.empty((grammar.nonterminals, ) + 3 * (maxlen + 1, ), dtype='d')
	outside.fill(np.inf)
	outsidelr(grammar, insidescores, maxlen, goal, outside)
	#print(outside)
	cnt = 0
	for an, a in enumerate(outside):
		for bn, b in enumerate(a):
			for cn, c in enumerate(b):
				for dn, d in enumerate(c):
					if d < np.inf:
						print("%s length %d lr %d gaps %d = %g" % (
								grammar.tolabel[an].decode('ascii'), bn, cn, dn, exp(-d)))
						cnt += 1
	print(cnt)
	print("done")
	return outside

def main():
	from treebank import NegraCorpusReader
	from grammar import induce_plcfrs
	import plcfrs
	from containers import Grammar
	from treetransforms import addfanoutmarkers, binarize
	from tree import Tree
	corpus = NegraCorpusReader(".", "sample2.export", encoding="iso-8859-1")
	trees = list(corpus.parsed_sents().values())
	for a in trees:
		binarize(a, vertmarkov=1, horzmarkov=1)
		addfanoutmarkers(a)
	grammar = Grammar(induce_plcfrs(trees, list(corpus.sents().values())))
	trees = [Tree.parse("(ROOT (A (a 0) (b 1)))", parse_leaf=int),
			Tree.parse("(ROOT (B (a 0) (c 2)) (b 1))", parse_leaf=int),
			Tree.parse("(ROOT (B (a 0) (c 2)) (b 1))", parse_leaf=int),
			Tree.parse("(ROOT (C (a 0) (c 2)) (b 1))", parse_leaf=int),
			]
	sents =[["a", "b"],
			["a", "b", "c"],
			["a", "b", "c"],
			["a", "b", "c"]]
	print("treebank:")
	for a in trees:
		print(a)
	print("\ngrammar:")
	grammar = Grammar(induce_plcfrs(trees, sents))
	print(grammar, '\n')
	testestimates(grammar, 4, grammar.toid[b"ROOT"])
	outside = getestimates(grammar, 4, grammar.toid[b"ROOT"])
	sent = ["a", "b", "c"]
	print("\nwithout estimates")
	chart, start, msg = plcfrs.parse(sent, grammar, estimates=None)
	print(msg)
	plcfrs.pprint_chart(chart, sent, grammar.tolabel)
	print("\nwith estimates")
	estchart, start, msg = plcfrs.parse(sent, grammar,
			estimates=('SXlrgaps', outside))
	print(msg)
	plcfrs.pprint_chart(estchart, sent, grammar.tolabel)
	print('items avoided:')
	print(list(chart.keys()))
	print()
	print(list(estchart.keys()))
	for item in set(chart) - set(estchart):
		print(item)
	print()

	trees = [Tree.parse("(ROOT (A (a 0) (b 1)))", parse_leaf=int),
			Tree.parse("(ROOT (A (B (A (B (a 0) (b 1))))) (c 2))", parse_leaf=int),
			Tree.parse("(ROOT (A (B (A (B (a 0) (b 1))))) (c 2))", parse_leaf=int),
			Tree.parse("(ROOT (A (B (A (B (a 0) (b 1))))) (c 2))", parse_leaf=int),
			Tree.parse("(ROOT (A (B (A (B (a 0) (b 1))))) (c 2))", parse_leaf=int),
			Tree.parse("(ROOT (A (B (A (B (a 0) (b 1))))) (c 2))", parse_leaf=int),
			Tree.parse("(ROOT (C (a 0) (b 1)) (c 2))", parse_leaf=int),
			]
	sents =[["a", "b"],
			["a", "b", "c"],
			["a", "b", "c"],
			["a", "b", "c"],
			["a", "b", "c"],
			["a", "b", "c"],
			["a", "b", "c"]]
	print("treebank:")
	for a in trees:
		print(a)
	print("\npcfg grammar:")
	grammar = Grammar(induce_plcfrs(trees, sents))
	print(grammar, '\n')
	outside = getpcfgestimates(grammar, 4, grammar.toid[b"ROOT"], debug=True)
	sent = ["a", "b", "c"]
	print("\nwithout estimates")
	chart, start, msg = plcfrs.parse(sent, grammar, estimates=None)
	print(msg)
	plcfrs.pprint_chart(chart, sent, grammar.tolabel)
	print("\nwith estimates")
	estchart, start, msg = plcfrs.parse(sent, grammar, estimates=('SX', outside))
	print(msg)
	plcfrs.pprint_chart(estchart, sent, grammar.tolabel)
	print('items avoided:')
	for item in set(chart) - set(estchart):
		print(item)

if __name__ == '__main__':
	main()
