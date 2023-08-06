# -*- coding: UTF-8 -*-
""" Functions related to dealing with unknown words
and smoothing of lexical probabilities.

Rare words in the training set are replaced with word signatures, such that
unknown words can receive similar tags. Given a function to produce such
signatures from words, the flow is as follows:

Simple lexical smoothing:
	getunknownwordmodel (get statistics)
	replaceraretrainwords (adjust trees)
	[ read off grammar ]
	simplesmoothlexicon (add extra lexical productions)

Non-simple (untested):
	getunknownwordmodel
	getlexmodel
	replaceraretrainwords
	[ read off grammar ]
	smoothlexicon

During parsing:
	replaceraretestwords (only give known words and signatures to parser)
"""
from __future__ import division, print_function, unicode_literals
import re
from collections import defaultdict, Counter as multiset
from fractions import Fraction

UNK = '_UNK'


def getunknownwordmodel(tagged_sents, unknownword,
		unknownthreshold, openclassthreshold):
	""" Compute an unknown word model that smooths lexical probabilities
	for unknown & rare words.

	:param tagged_sents: the sentences from the training set with the gold POS
			tags from the treebank.
	:param unknownword: a function that returns a signature for a given word;
			e.g., "eschewed" => "_UNK-L-d".
	:param unknownthreshold: words with frequency lower than or equal to this
			are replaced by their signature.
	:param openclassthreshold: tags that rewrite to at least this much word
			types are considered to be open class categories. """
	wordsfortag = defaultdict(set)
	tags = multiset()
	wordtags = multiset()
	sigs = multiset()
	sigtag = multiset()
	words = multiset(word for sent in tagged_sents for word, tag in sent)
	lexicon = {word for word, freq in words.items() if freq > unknownthreshold}
	wordsig = {}
	for sent in tagged_sents:
		for n, (word, tag) in enumerate(sent):
			wordsfortag[tag].add(word)
			tags[tag] += 1
			wordtags[word, tag] += 1
			sig = unknownword(word, n, lexicon)
			wordsig[word] = sig  # NB: sig may also depend on n and lexicon
			sigtag[sig, tag] += 1
	if openclassthreshold:
		openclasstags = {tag: len({w.lower() for w in ws})
				for tag, ws in wordsfortag.items()
				if len({w.lower() for w in ws}) >= openclassthreshold}
		closedclasstags = set(tags) - set(openclasstags)
		closedclasswords = {word for tag in closedclasstags
				for word in wordsfortag[tag]}
		openclasswords = lexicon - closedclasswords
		# add rare closed-class words back to lexicon
		lexicon.update(closedclasswords)
	else:
		openclasstags = {}
		openclasswords = {}
	for sent in tagged_sents:
		for n, (word, _) in enumerate(sent):
			if word not in lexicon:
				sig = unknownword(word, n, lexicon)
				sigs[sig] += 1
	msg = "known words: %d, signature types seen: %d\n" % (
			len(lexicon), len(sigs))
	msg += "open class tags: {%s}\n" % ", ".join(
			"%s:%d" % a for a in openclasstags.items())
	msg += "closed class tags: {%s}" % ", ".join(a for a in closedclasstags)
	return (sigs, words, lexicon, wordsfortag, openclasstags,
			openclasswords, tags, wordtags,
			wordsig, sigtag), msg


def replaceraretrainwords(tagged_sents, unknownword, lexicon):
	""" Given a training set, replace all terminals not part of the lexicon
	with a signature of features as returned by unknownword(),
	before a grammar is read of from the training set. """
	return [[word if word in lexicon else unknownword(word, n, lexicon)
			for n, (word, _) in enumerate(sent)]
			for sent in tagged_sents]


def replaceraretestwords(sent, unknownword, lexicon, sigs):
	""" Given a test sentence, replace words not part of the lexicon
	with a signature of features as returned by unknownword(),
	if that signature is part of the grammar. """
	for n, word in enumerate(sent):
		if word in lexicon:
			yield word
		else:
			sig = unknownword(word, n, lexicon)
			if sig in sigs:
				yield sig
			else:
				yield UNK


def simplesmoothlexicon(lexmodel, epsilon=Fraction(1, 100)):
	""" introduce lexical productions for unobserved
	combinations of known open class words and tags, as well as for unobserved
	signatures which are mapped to ``'_UNK'``.

	:param epsilon: 'frequency' of productions for unseen tag, word pair. """
	(lexicon, wordsfortag, openclasstags,
			openclasswords, tags, wordtags) = lexmodel
	newrules = []
	# rare words as signature AND as word:
	for word, tag in wordtags:
		if word not in lexicon:  # and word in openclasswords:
			# needs to be normalized later
			newrules.append((((tag, 'Epsilon'), (word, )),
					Fraction(wordtags[word, tag], tags[tag])))
			#print(>> sys.stderr, newrules[-1])
	for tag in openclasstags:  # open class tag-word pairs
		epsilon1 = epsilon / tags[tag]
		for word in openclasswords - wordsfortag[tag] - {UNK}:
			newrules.append((((tag, 'Epsilon'), (word, )), epsilon1))
	for tag in tags:  # catch all unknown signature
		epsilon1 = epsilon / tags[tag]
		newrules.append((((tag, 'Epsilon'), (UNK, )), epsilon1))
	return newrules


def getlexmodel(sigs, words, _lexicon, wordsfortag, openclasstags,
			openclasswords, tags, wordtags, wordsig, sigtag,
			openclassoffset=1, kappa=1):
	""" Compute a smoothed lexical model.

	:returns: a dictionary giving P(word_or_sig | tag).
	:param openclassoffset: for words that only appear with open class tags,
		add unseen combinations of open class (tag, word) with this count.
	:param kappa: FIXME; cf. Klein & Manning (2003). """
	for tag in openclasstags:
		for word in openclasswords - wordsfortag[tag]:
			wordtags[word, tag] += openclassoffset
			words[word] += openclassoffset
			tags[tag] += openclassoffset
		# unseen signatures
		sigs[UNK] += 1
		sigtag[UNK, tag] += 1
	# Compute P(tag|sig)
	tagtotal = sum(tags.values())
	wordstotal = sum(words.values())
	sigstotal = sum(sigs.values())
	P_tag = {}
	for tag in tags:
		P_tag[tag] = Fraction(tags[tag], tagtotal)
	P_word = defaultdict(int)
	for word in words:
		P_word[word] = Fraction(words[word], wordstotal)
	P_tagsig = defaultdict(Fraction)  # ??
	for sig in sigs:
		P_tagsig[tag, sig] = Fraction(P_tag[tag],
				Fraction(sigs[sig], sigstotal))
		#print(>> sys.stderr, "P(%s | %s) = %s " % ()
		#		tag, sig, P_tagsig[tag, sig])
	# Klein & Manning (2003) Accurate unlexicalized parsing
	# P(tag|word) = [count(tag, word) + kappa * P(tag|sig)]
	#		/ [count(word) + kappa]
	P_tagword = defaultdict(int)
	for word, tag in wordtags:
		P_tagword[tag, word] = Fraction(wordtags[word, tag]
				+ kappa * P_tagsig[tag, wordsig[word]],
				words[word] + kappa)
		#print(>> sys.stderr, "P(%s | %s) = %s " % ()
		#		tag, word, P_tagword[tag, word])
	# invert with Bayes theorem to get P(word|tag)
	P_wordtag = defaultdict(int)
	for tag, word in P_tagword:
		#wordorsig = word if word in lexicon else wordsig[word]
		wordorsig = word
		P_wordtag[wordorsig, tag] += Fraction((P_tagword[tag, word]
				* P_word[word]), P_tag[tag])
		#print(>> sys.stderr, "P(%s | %s) = %s " % ()
		#		word, tag, P_wordtag[wordorsig, tag])
	msg = "(word, tag) pairs in model: %d" % len(P_tagword)
	return P_wordtag, msg


def smoothlexicon(grammar, P_wordtag):
	""" Replace lexical probabilities using given unknown word model.
	Ignores lexical productions of known subtrees (tag contains '@')
	introduced by DOP, i.e., we only modify lexical depth 1 subtrees. """
	newrules = []
	for (rule, yf), w in grammar:
		if rule[1] == 'Epsilon' and '@' not in rule[0]:
			wordorsig = yf[0]
			tag = rule[0]
			newrule = (((tag, 'Epsilon'), (wordorsig, )),
					P_wordtag[wordorsig, tag])
			newrules.append(newrule)
		else:
			newrules.append(((rule, yf), w))
	return newrules


# === functions for unknown word signatures ============
# resolve name to function assigning unknown word signatures
def getunknownwordfun(model):
	""" Resolve name of unknown word model into function for that model. """
	return {"4": unknownword4,
		"6": unknownword6,
		"base": unknownwordbase,
		"ftb": unknownwordftb,
		}[model]

hasdigit = re.compile(r"\d", re.UNICODE)
hasnondigit = re.compile(r"\D", re.UNICODE)
#NB: includes '-', hyphen, non-breaking hyphen
# does NOT include: figure-dash, em-dash, en-dash (these are punctuation,
# not word-combining) u2012-u2015; nb: these are hex values.
hasdash = re.compile(u"[-\u2010\u2011]", re.UNICODE)
# FIXME: exclude accented characters for model 6?
haslower = re.compile(u'[a-z\xe7\xe9\xe0\xec\xf9\xe2\xea\xee\xf4\xfb\xeb'
		u'\xef\xfc\xff\u0153\xe6]', re.UNICODE)
hasupper = re.compile(u'[A-Z\xc7\xc9\xc0\xcc\xd9\xc2\xca\xce\xd4\xdb\xcb'
		u'\xcf\xdc\u0178\u0152\xc6]', re.UNICODE)
hasletter = re.compile(u'[A-Za-z\xe7\xe9\xe0\xec\xf9\xe2\xea\xee\xf4\xfb'
		u'\xeb\xef\xfc\xff\u0153\xe6\xc7\xc9\xc0\xcc\xd9\xc2\xca\xce\xd4'
		u'\xdb\xcb\xcf\xdc\u0178\u0152\xc6]', re.UNICODE)
# Cf. http://en.wikipedia.org/wiki/French_alphabet
LOWER = (u'abcdefghijklmnopqrstuvwxyz\xe7\xe9\xe0\xec\xf9\xe2\xea\xee\xf4\xfb'
		u'\xeb\xef\xfc\xff\u0153\xe6')
UPPER = (u'ABCDEFGHIJKLMNOPQRSTUVWXYZ\xc7\xc9\xc0\xcc\xd9\xc2\xca\xce\xd4\xdb'
		u'\xcb\xcf\xdc\u0178\u0152\xc6')
LOWERUPPER = LOWER + UPPER


def unknownword6(word, loc, lexicon):
	""" Model 6 of the Stanford parser (for WSJ treebank). """
	wlen = len(word)
	numcaps = 0
	sig = UNK
	numcaps = len(hasupper.findall(word))
	lowered = word.lower()
	if numcaps > 1:
		sig += "-CAPS"
	elif numcaps > 0:
		if loc == 0:
			sig += "-INITC"
			if lowered in lexicon:
				sig += "-KNOWNLC"
		else:
			sig += "-CAP"
	elif haslower.search(word):
		sig += "-LC"
	if hasdigit.search(word):
		sig += "-NUM"
	if hasdash.search(word):
		sig += "-DASH"
	if lowered.endswith("s") and wlen >= 3:
		if lowered[-2] not in "siu":
			sig += "-s"
	elif wlen >= 5 and not hasdash.search(word) and not (
			hasdigit.search(word) and numcaps > 0):
		suffixes = ("ed", "ing", "ion", "er", "est", "ly", "ity", "y", "al")
		for a in suffixes:
			if lowered.endswith(a):
				sig += "-%s" % a
	return sig


def unknownword4(word, loc, _):
	""" Model 4 of the Stanford parser. Relatively language agnostic. """
	sig = UNK

	# letters
	if word[0] in UPPER:
		if not haslower:
			sig += "-AC"
		elif loc == 0:
			sig += "-SC"
		else:
			sig += "-C"
	elif haslower.search(word):
		sig += "-L"
	elif hasletter.search(word):
		sig += "-U"
	else:
		sig += "-S"  # no letter

	# digits
	if hasdigit.search(word):
		if hasnondigit.search(word):
			sig += "-n"
		else:
			sig += "-N"

	# punctuation
	if "-" in word:
		sig += "-H"
	if "." in word:
		sig += "-P"
	if "," in word:
		sig += "-C"
	if len(word) > 3:
		if word[-1] in LOWERUPPER:
			sig += "-%s" % word[-1].lower()
	return sig


def unknownwordbase(word, _loc, _lexicon):
	""" BaseUnknownWordModel of the Stanford parser.
	Relatively language agnostic. """
	sig = UNK

	# letters
	if word[0] in UPPER:
		sig += "-C"
	else:
		sig += "-c"

	# digits
	if hasdigit.search(word):
		if hasnondigit.search(word):
			sig += "-n"
		else:
			sig += "-N"

	# punctuation
	if "-" in word:
		sig += "-H"
	if word == ".":
		sig += "-P"
	if word == ",":
		sig += "-C"
	if len(word) > 3:
		if word[-1] in LOWERUPPER:
			sig += "-%s" % word[-2].lower()
	return sig

nounsuffix = re.compile(u"(ier|ière|ité|ion|ison|isme|ysme|iste|esse|eur|euse"
		u"|ence|eau|erie|ng|ette|age|ade|ance|ude|ogue|aphe|ate|duc|anthe"
		u"|archie|coque|érèse|ergie|ogie|lithe|mètre|métrie|odie|pathie|phie"
		u"|phone|phore|onyme|thèque|scope|some|pole|ôme|chromie|pie)s?$")
adjsuffix = re.compile(u"(iste|ième|uple|issime|aire|esque|atoire|ale|al|able"
		u"|ible|atif|ique|if|ive|eux|aise|ent|ois|oise|ante|el|elle|ente|oire"
		u"|ain|aine)s?$")
possibleplural = re.compile(u"(s|ux)$")
verbsuffix = re.compile(u"(ir|er|re|ez|ont|ent|ant|ais|ait|ra|era|eras"
		u"|é|és|ées|isse|it)$")
advsuffix = re.compile("(iment|ement|emment|amment)$")
haspunc = re.compile(u"([\u0021-\u002F\u003A-\u0040\u005B\u005C\u005D"
		u"\u005E-\u0060\u007B-\u007E\u00A1-\u00BF\u2010-\u2027\u2030-\u205E"
		u"\u20A0-\u20B5])+")
ispunc = re.compile(u"([\u0021-\u002F\u003A-\u0040\u005B\u005C\u005D"
		u"\u005E-\u0060\u007B-\u007E\u00A1-\u00BF\u2010-\u2027\u2030-\u205E"
		u"\u20A0-\u20B5])+$")


def unknownwordftb(word, loc, _):
	""" Model 2 for French of the Stanford parser. """
	sig = UNK

	if advsuffix.search(word):
		sig += "-ADV"
	elif verbsuffix.search(word):
		sig += "-VB"
	elif nounsuffix.search(word):
		sig += "-NN"

	if adjsuffix.search(word):
		sig += "-ADV"
	if hasdigit.search(word):
		sig += "-NUM"
	if possibleplural.search(word):
		sig += "-PL"

	if ispunc.search(word):
		sig += "-ISPUNC"
	elif haspunc.search(word):
		sig += "-HASPUNC"

	if loc > 0 and len(word) > 0 and word[0] in UPPER:
		sig += "-UP"

	return sig


def test():
	""" Not implemented. """

if __name__ == '__main__':
	test()
