
import os, sys
import numpy as np
import pandas as pd
import itertools as it
from sympy import Rational
from scipy import misc
import cPickle
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
from timeit import default_timer as timer

import EvalKeys as keys
import EvalFive, EvalSeven
from EvalGenerateHands import create_array_all_five_fast, create_array_all_seven_fast, all_n_cards_given_m_cards_fast

np.set_printoptions(linewidth=300)
pd.set_option('display.width', 300)

# face symbols
face_symbol = np.array(['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'], dtype=np.dtype('a1'))
face_symbol_to_no = dict(zip(face_symbol, np.arange(len(face_symbol))))
turn_on_red = '\033[31m'
turn_on_bold = '\033[30;1m'
turn_off_all = '\033[0m'

# suits symbols - clubs, diamonds, hearst, spades - in unicode
suit_symbol_terminal = [u'\u2663', u'\u2666', u'\u2665', u'\u2660']
suit_symbol = [suit_symbol_terminal[0],
				turn_on_red+suit_symbol_terminal[1]+turn_off_all,
				turn_on_red+suit_symbol_terminal[2]+turn_off_all,
				suit_symbol_terminal[3]]
suit_symbol_html = ['<span style="color:back; font-size:125%">&#x2663</span>',
						'<span style="color:red; font-size:125%">&#x2666</span>',
						'<span style="color:red; font-size:125%">&#x2665</span>',
						'<span style="color:back; font-size:125%">&#x2660</span>']

def choice(i, j, r):
	if (i>j):		return r[0]
	elif (i<j):	return r[1]
	else:		return r[2]

all_preflop_hands = [face_symbol[i]+face_symbol[j]+choice(i, j, ['s', 'o', 'o'])
								for i in range(len(face_symbol))[::-1]
								for j in range(len(face_symbol))[::-1]]
all_preflop_two_hands = list(it.combinations(all_preflop_hands, r=2)) + zip(all_preflop_hands, all_preflop_hands)


def C(n, p):
	return misc.comb(n, p, exact=True)

def A(n, p):
	return C(n, p)*misc.factorial(p, exact=True)

def card_no(f, s):
	return 4*f+s

def card_fs(no):
	s = no % 4
	f = (no-s)/4
	return [f, s]

def hand_str_to_no(hand):
	fs1, fs2, m = hand
	f1, f2 = face_symbol_to_no[fs1], face_symbol_to_no[fs2]
	if (m=='s'):
		s1, s2 = 3, 3
	else:
		s1, s2 = 3, 2
	return np.array([card_no(f1, s1), card_no(f2, s2)])

def card_fs_to_char(f, s):
	return turn_on_bold+face_symbol[f]+turn_off_all+suit_symbol[s]

def card_no_to_char(no):
	f, s = card_fs(no)
	return turn_on_bold+face_symbol[f]+turn_off_all+suit_symbol[s]

def one_hand_no_to_char(arr):
	f1, s1 = card_fs(arr[0])
	f2, s2 = card_fs(arr[1])
	return turn_on_bold+face_symbol[f1]+turn_off_all+suit_symbol[s1]+' '+turn_on_bold+face_symbol[f2]+turn_off_all+suit_symbol[s2]

def two_hand_no_to_char(arr):
	h1f1, h1s1 = card_fs(arr[0])
	h1f2, h1s2 = card_fs(arr[1])
	h2f1, h2s1 = card_fs(arr[2])
	h2f2, h2s2 = card_fs(arr[3])
	return turn_on_bold+face_symbol[h1f1]+turn_off_all+suit_symbol[h1s1]+' '+ turn_on_bold+face_symbol[h1f2]+turn_off_all+suit_symbol[h1s2]+' - '+ \
			turn_on_bold+face_symbol[h2f1]+turn_off_all+suit_symbol[h2s1]+' '+ turn_on_bold+face_symbol[h2f2]+turn_off_all+suit_symbol[h2s2]



nb_occurence_formula_hand_five = [
	['Straight Flush', r'\binom{4}{1} \binom{10}{1}-\binom{4}{1}'],
	['Four of a Kind', r'\binom{4}{1} \binom{12}{1} \binom{13}{1}'],
	['Full House', r'\binom{4}{2} \binom{4}{3} \binom{12}{1} \binom{13}{1}'],
	['Flush', r'\binom{4}{1} \binom{13}{5}-\binom{4}{1} \binom{10}{1}'],
	['Straight', r'\binom{4}{1}^5 \binom{10}{1}-\binom{4}{1} \binom{10}{1}'],
	['Three of a Kind', r'\binom{4}{1}^2 \binom{4}{3} \binom{12}{2} \binom{13}{1}'],
	['Two Pairs', r'\binom{4}{1} \binom{4}{2}^2 \binom{11}{1} \binom{13}{2}'],
	['One Pair', r'\binom{4}{1}^3 \binom{4}{2} \binom{12}{3} \binom{13}{1}'],
	['High Card', r'\left(\binom{4}{1}^5-4\right) (\binom{13}{5}-10)'],
	['All', r'\binom{52}{5}']
	]


def create_df_hand_five():
	"""create summary dataframe for all five card hands"""
	hand_type = EvalFive.hand_type

	uniq, idx = np.unique(hand_type, return_index=True)
	sorted_idx = np.sort(idx)[::-1]
	uniq_hand_type = hand_type[sorted_idx]
	min_rank = sorted_idx
	max_rank = np.r_[hand_type.size, sorted_idx[:-1]]-1
	nb_rank = max_rank-min_rank+1

	array_all_five_cards = create_array_all_five_fast()
	all_hand_rank = EvalFive.get_five_rank_fast(array_all_five_cards, keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, EvalFive.flush_rank, EvalFive.face_rank)
	bins = np.r_[sorted_idx[::-1], max_rank[0]]
	nb_occurence = np.histogram(all_hand_rank, bins)[0][::-1]
	proba = 1.0*nb_occurence/np.sum(nb_occurence)
	odd = 1.0/proba
	cum_proba = np.cumsum(proba)

	proba_exact = map(lambda x : Rational(x, array_all_five_cards.shape[0]), nb_occurence)

	df = pd.DataFrame(data=np.array([uniq_hand_type, nb_rank, min_rank, max_rank, nb_occurence, proba_exact, odd, proba, cum_proba]).T,
			columns=['HandType', 'NbHands', 'MinRank', 'MaxRank', 'NbOccurence', 'ProbaExact', 'Odd', 'ProbaApprox', 'CumulativeProba'])
	# df.ix[uniq.size] = ['All', hand_type.size, 0, max_rank[0],  array_all_five_cards.shape[0], 1.0, 1.0, 1.0, np.nan]
	s = pd.Series(data=['All', hand_type.size, 0, max_rank[0],  array_all_five_cards.shape[0], 1.0, 1.0, 1.0, np.nan],
			index=['HandType', 'NbHands', 'MinRank', 'MaxRank', 'NbOccurence', 'ProbaExact', 'Odd', 'ProbaApprox', 'CumulativeProba'], name=uniq.size)
	df = df.append(s)

	# df.to_pickle(os.path.join('Tables', 'df_hand_five.pd'))
	return df



nb_occurence_formula_hand_seven = [
	['Straight Flush', r'4 \binom{47}{2} + 36 \binom{46}{2}'],
	['Four of a Kind', r'\binom{13}{1} \binom{48}{3}'],

	['Full House - 1 Triple, 1 Pair, 2 Kickers', r'\binom{4}{1}^2 \binom{4}{2} \binom{4}{3} \binom{11}{2} \binom{12}{1} \binom{13}{1}'],
	['Full House - 1 Triple, 2 Pairs', r'\binom{4}{2}^2 \binom{4}{3} \binom{12}{2} \binom{13}{1}'],
	['Full House - 2 Triples, 1 Kicker', r'\binom{4}{1} \binom{4}{3}^2 \binom{11}{1} \binom{13}{2}'],

	['Flush - 7 cards same suit', r'\binom{4}{1} \binom{13}{7}'],
	['Flush - 6 cards same suit', r'\binom{4}{1} \binom{13}{6} \binom{39}{1}'],
	['Flush - 5 cards same suit', r'\binom{4}{1} \binom{13}{5} \binom{39}{2}'],

	['Straight - 7 distinct faces', r'\left(\binom{4}{1}^7-\binom{4}{1} \left(\binom{7}{5} \binom{3}{1}^2+\binom{7}{6} \binom{3}{1}+1\right)\right) (9 \binom{7}{2}+\binom{8}{2})'],
	['Straight - 6 distinct faces', r'\binom{4}{2} \left(\binom{4}{1}^5-\binom{4}{1}-\binom{2}{1} \binom{3}{1} \binom{5}{4}\right) \binom{6}{1} (9 \binom{7}{1}+\binom{8}{1})'],
	['Straight - 5 distinct faces, 1 Triple', r'\left(\binom{4}{1}^4-\binom{3}{1}\right) \binom{4}{3} \binom{5}{1} \binom{10}{1}'],
	['Straight - 5 distinct faces, 2 Triples', r'\left(\binom{4}{2} \binom{4}{1}^3+\left(\binom{4}{1}^3-2\right) \binom{4}{2}+\binom{2}{1}^2 \left(\binom{4}{1}^3-1\right) \binom{4}{2}\right) \binom{5}{2} \binom{10}{1}'],

	['Three of a Kind', r'\left(\binom{4}{1}^4-\binom{3}{1}\right) \binom{4}{3} \binom{5}{1} (\binom{13}{5}-10)'],

	['Two Pairs - 2 Pairs, 3 Kickers', r'\left(\binom{4}{2} \binom{4}{1}^3+\left(\binom{4}{1}^3-2\right) \binom{4}{2}+\binom{2}{1}^2 \left(\binom{4}{1}^3-1\right) \binom{4}{2}\right) \binom{5}{2} (\binom{13}{5}-10)'],
	['Two Pairs - 3 Pairs, 1 Kicker', r'\binom{4}{1}^2 \binom{4}{2}^3 \binom{13}{4}'],

	['One Pair', r'\binom{4}{2} \left(\binom{4}{1}^5-2 \binom{3}{1} \binom{5}{4}-4\right) \binom{6}{1} (-8 \binom{6}{1}-2 \binom{7}{1}+\binom{13}{6}-9)'],
	['High Card', r'\left(\binom{4}{1}^7-\binom{4}{1} \left(\binom{7}{5} \binom{3}{1}^2+\binom{7}{6} \binom{3}{1}+1\right)\right) (-7 \binom{5}{1}-2 \binom{6}{1}-8 \binom{6}{2}-2 \binom{7}{2}+\binom{13}{7}-8)'],
	['All', r'\binom{52}{7}']
	]


def create_df_hand_seven():
	"""create summary dataframe for all seven card hands"""
	hand_type = EvalFive.hand_type

	uniq, idx = np.unique(hand_type, return_index=True)
	sorted_idx = np.sort(idx)[::-1]
	uniq_hand_type = hand_type[sorted_idx]
	min_rank_5 = sorted_idx
	max_rank_5 = np.r_[hand_type.size, sorted_idx[:-1]]-1
	nb_rank_5 = max_rank_5-min_rank_5+1

	array_all_seven_cards = create_array_all_seven_fast()
	all_hand_rank = EvalSeven.get_seven_rank_fast(array_all_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, EvalSeven.flush_rank, EvalSeven.face_rank, EvalSeven.flush_suit)

	bins = np.r_[sorted_idx[::-1], max_rank_5[0]]
	nb_occurence = np.histogram(all_hand_rank, bins)[0][::-1]
	proba = 1.0*nb_occurence/np.sum(nb_occurence)
	odd = 1.0/proba
	cum_proba = np.cumsum(proba)

	bins = np.r_[sorted_idx[::-1], max_rank_5[0]+1][::-1]
	digitized = np.digitize(all_hand_rank, bins)
	min_rank_7 = np.zeros(uniq.size, dtype=np.int32)
	max_rank_7 = np.zeros(uniq.size, dtype=np.int32)
	nb_rank_7 = np.zeros(uniq.size, dtype=np.int32)
	for k in range(1, uniq.size+1):
		subset = all_hand_rank[digitized==k]
		min_rank_7[k-1] = subset.min()
		max_rank_7[k-1] = subset.max()
		nb_rank_7[k-1] = np.unique(subset).size

	proba_exact = map(lambda x : Rational(x, array_all_seven_cards.shape[0]), nb_occurence)

	df = pd.DataFrame(data=np.array([uniq_hand_type, nb_rank_5, nb_rank_7, min_rank_5, min_rank_7, max_rank_5, max_rank_7, nb_occurence, proba_exact, odd, proba, cum_proba]).T,
			columns=['HandType', 'NbHands_5', 'NbHands_7', 'MinRank_5', 'MinRank_7', 'MaxRank_5', 'MaxRank_7', 'NbOccurence', 'ProbaExact', 'Odd', 'ProbaApprox', 'CumulativeProba'])
	# df.loc[uniq.size] = ['All', nb_rank_5.sum(), nb_rank_7.sum(), min_rank_5.min(), min_rank_7.min(), max_rank_5.max(), max_rank_7.max(), array_all_seven_cards.shape[0], 1.0, 1.0, 1.0, np.nan]

	s = pd.Series(data=['All', nb_rank_5.sum(), nb_rank_7.sum(), min_rank_5.min(), min_rank_7.min(), max_rank_5.max(), max_rank_7.max(), array_all_seven_cards.shape[0], 1.0, 1.0, 1.0, np.nan],
			index=['HandType', 'NbHands_5', 'NbHands_7', 'MinRank_5', 'MinRank_7', 'MaxRank_5', 'MaxRank_7', 'NbOccurence', 'ProbaExact', 'Odd', 'ProbaApprox', 'CumulativeProba'], name=uniq.size)
	df = df.append(s)

	df.to_pickle(os.path.join('Tables', 'df_hand_seven.pd'))
	return df



def create_df_preflop_hand_distrib(save=False):
	"""returns df containing the hand rank distribution for all combinations of preflop hands"""
	global df_preflop_hand_distrib

	print "\n--------------- start create_df_preflop_hand_distrib"
	print 'all preflop hands = \nstart = {}\nend = {}\nnb of elements = {}'.format(all_preflop_hands[:10], all_preflop_hands[-10:], len(all_preflop_hands))

	print "\nhand rank distribution for all preflop hands"
	t0 = timer()
	preflop_hand_rank_distrib = np.zeros([1+len(all_preflop_hands), 7462], dtype=np.int32)

	sys.stdout.write('\rk=%3d / %3d' % (1, 1+len(all_preflop_hands)))
	sys.stdout.flush()
	N = C(52, 7)
	h1_array_all_seven_cards = create_array_all_seven_fast()
	h1_rank7 = EvalSeven.get_seven_rank_fast(h1_array_all_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, EvalSeven.flush_rank, EvalSeven.face_rank, EvalSeven.flush_suit)
	preflop_hand_rank_distrib[0, :] = np.bincount(h1_rank7)

	for k, hand in enumerate(all_preflop_hands):
		sys.stdout.write('\rk = %3d / %3d' % (2+k, 1+len(all_preflop_hands)))
		sys.stdout.flush()
		hand_no = hand_str_to_no(hand)
		N = C(52-2, 5)
		array_five_cards = all_n_cards_given_m_cards_fast(5, hand_no, N)
		h1_cards = np.ones([N, 2], dtype=np.int32)*hand_no
		h1_array_all_seven_cards = np.concatenate((h1_cards, array_five_cards), axis=1)
		h1_rank7 = EvalSeven.get_seven_rank_fast(h1_array_all_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, EvalSeven.flush_rank, EvalSeven.face_rank, EvalSeven.flush_suit)
		preflop_hand_rank_distrib[1+k, :] = np.bincount(h1_rank7)

	df = pd.DataFrame(data=preflop_hand_rank_distrib.T, columns=['NoHand']+all_preflop_hands, index=np.arange(7462))
	t1 = timer()
	print '\ndf_preflop_hand_distrib time = {:8.4f} s'.format(t1-t0)
	if (save):
		df.to_pickle(os.path.join('Tables', 'df_preflop_hand_distrib.pd'))
		print '{} saved to disk as {}'.format('df_preflop_hand_distrib', os.path.join('Tables', 'df_preflop_hand_distrib.pd'))
		df.to_csv(os.path.join('Tables', 'df_preflop_hand_distrib.csv'), index=False)
		print '{} saved to disk as {}'.format('df_preflop_hand_distrib', os.path.join('Tables', 'df_preflop_hand_distrib.csv'))

	print "--------------- end create_df_preflop_hand_distrib"
	return df



pfh_combin = ['suited - suited',
				'suited - offsuited (no pair)',
				'suited - offsuited (pair)',
				'offsuited (no pair) - suited',
				'offsuited (pair) - suited',
				'offsuited (no pair) - offsuited (no pair)',
				'offsuited (no pair) - offsuited (pair)',
				'offsuited (pair) - offsuited (pair)',]
# clubs=0, diamonds=1, hearst=2, spades=3
suit_combin = [[[3, 3, 2, 2], [3, 3, 3, 3]],
				[[3, 3, 2, 1], [3, 3, 2, 3], [3, 3, 3, 2]],
				[[3, 3, 2, 1], [3, 3, 2, 3]],
				[[2, 1, 3, 3], [2, 3, 3, 3], [3, 2, 3, 3]],
				[[2, 1, 3, 3], [2, 3, 3, 3]],
				[[3, 2, 1, 0], [3, 2, 1, 2], [3, 2, 1, 3], [3, 2, 2, 1], [3, 2, 2, 3], [3, 2, 3, 1], [3, 2, 3 ,2]],
				[[3, 2, 1, 0], [3, 2, 1, 2], [3, 2, 1, 3], [3, 2, 2, 3]],
				[[1, 0, 3, 2], [1, 2, 3, 2], [1, 3, 3, 2], [2, 3, 3, 2]],
				[[3, 2, 1, 0], [3, 2, 1, 3], [3, 2, 2, 3]]]

suit_combin_freq = [[A(4, 1)*A(3, 1), A(4, 1)],
						[A(4, 1)*A(3, 2), A(4, 1)*A(3, 1), A(4, 1)*C(3, 1)],
						[A(4, 1)*A(3, 2), A(4, 1)*A(3, 1)],
						[A(4, 1)*A(3, 2), A(4, 1)*A(3, 1), A(4, 1)*C(3, 1)],
						[A(4, 1)*A(3, 2), A(4, 1)*A(3, 1)],
						[A(4, 2)*A(2, 2), A(4, 2)*A(2, 1), A(4, 2)*A(2, 1), A(4, 2)*A(2, 1), A(4, 2)*A(1, 1), A(4, 2)*A(2, 1), A(4, 2)*A(1, 1)],
						[A(4, 2)*A(2, 2), A(4, 2)*A(2, 1), A(4, 2)*A(2, 1), A(4, 2)*A(1, 1)],
						[A(4, 2)*A(2, 2), A(4, 2)*A(2, 1), A(4, 2)*A(2, 1), A(4, 2)*A(1, 1)],
						[A(4, 2)*A(2, 2), A(4, 2)*A(2, 1), A(4, 2)*A(1, 1)]]


def card_combin(idx, h1f1, h1f2, h2f1, h2f2):
	global sel, freq, card
	suit_pair = suit_combin[idx]
	suit_pair_freq = suit_combin_freq[idx]
	n = len(suit_pair)
	card = np.zeros([n, 4], dtype=np.int32)
	freq = np.zeros([n], dtype=np.int32)

	for k in range(n):
		freq[k] = suit_pair_freq[k]
		card[k, 0] = card_no(h1f1, suit_pair[k][0])
		card[k, 1] = card_no(h1f2, suit_pair[k][1])
		card[k, 2] = card_no(h2f1, suit_pair[k][2])
		card[k, 3] = card_no(h2f2, suit_pair[k][3])

	sel = [np.unique(r).size==4 for r in card]
	card = np.array([r for r in card if np.unique(r).size==4])
	freq = np.array([f for k, f in enumerate(freq) if sel[k]])
	return [card, freq]


def two_hand_to_no(hand1, hand2):
	h1fs1, h1fs2, h1m = hand1
	h1f1, h1f2 = face_symbol_to_no[h1fs1], face_symbol_to_no[h1fs2]
	h2fs1, h2fs2, h2m = hand2
	h2f1, h2f2 = face_symbol_to_no[h2fs1], face_symbol_to_no[h2fs2]

	# suited - suited
	if ((h1m=='s') and (h2m=='s')):
		# print 'suited - suited'
		idx = 0
		card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
	# suited - offsuited
	elif ((h1m=='s') and (h2m=='o')):
		# suited - offsuited (no pair)
		if (h2f1!=h2f2):
			# print 'suited - offsuited (no pair)'
			idx = 1
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
		# suited - offsuited (pair)
		else:
			# print 'suited - offsuited (pair)'
			idx = 2
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
	# offsuited  - suited
	elif ((h1m=='o') and (h2m=='s')):
		# offsuited (no pair) - suited
		if (h1f1!=h1f2):
			# print 'offsuited (no pair) - suited'
			idx = 3
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
		# offsuited (pair) - suited
		else:
			# print 'offsuited (pair) - suited'
			idx = 4
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
	# offsuited - offsuited
	else:
		# offsuited (no pair) - offsuited (no pair)
		if ((h1f1!=h1f2) and (h2f1!=h2f2)):
			# print 'offsuited (no pair) - offsuited (no pair)'
			idx = 5
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
		# offsuited (no pair) - offsuited (pair)
		elif ((h1f1!=h1f2) and (h2f1==h2f2)):
			# print 'offsuited (no pair) - offsuited (pair)'
			idx = 6
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
		# offsuited (pair) - offsuited (no pair)
		elif ((h1f1==h1f2) and (h2f1!=h2f2)):
			# print 'offsuited (pair) - offsuited (no pair)'
			idx = 7
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
		# offsuited (pair) - offsuited (pair)
		else:
			# print 'offsuited (pair) - offsuited (pair)'
			idx = 8
			card, freq = card_combin(idx, h1f1, h1f2, h2f1, h2f2)
	return [card, freq]



def preflop_two_hand_equity((h1, h2), verbose=False):
	"""returns [h1 nb win, nb ties, h2 nb wins] for all suit combinations for 2 preflop hands h1, h2 input as 'Q6o', '52o'"""
	if (verbose):
		print 'preflop hands : {}'.format((h1, h2))
		t0 = timer()
	two_hand_no, freq = two_hand_to_no(h1, h2)
	equity = np.zeros([two_hand_no.shape[0], 4], dtype=np.int32)
	for k, p in enumerate(two_hand_no):

		N = C(52-4, 5)
		array_five_cards = all_n_cards_given_m_cards_fast(5, p, N)

		h1_cards = np.ones([N, 2], dtype=np.int32)*[p[0], p[1]]
		h1_array_all_seven_cards = np.concatenate((h1_cards, array_five_cards), axis=1)
		h1_rank7 = EvalSeven.get_seven_rank_fast(h1_array_all_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, EvalSeven.flush_rank, EvalSeven.face_rank, EvalSeven.flush_suit)
		h2_cards = np.ones([N, 2], dtype=np.int32)*[p[2], p[3]]
		h2_array_all_seven_cards = np.concatenate((h2_cards, array_five_cards), axis=1)
		h2_rank7 = EvalSeven.get_seven_rank_fast(h2_array_all_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, EvalSeven.flush_rank, EvalSeven.face_rank, EvalSeven.flush_suit)
		diff_rank7 = h1_rank7-h2_rank7
		h1_win, tie, h2_win = (diff_rank7>0).sum(), (diff_rank7==0).sum(), (diff_rank7<0).sum()
		equity[k, :] = np.array([h1_win, tie, h2_win, freq[k]])
		if (verbose):
			print 'suit combination #{}'.format(k)
			print '\t', two_hand_no_to_char(p)
			print '\tfrequency = {}'.format(freq[k])
			print '\t{}\t{}\t{}'.format('h1#wins', '#ties', 'h2#wins')
			print '\t{}\t{}\t{}'.format(h1_win, tie, h2_win)
			total = np.array([h1_win, tie, h2_win]).sum()
			print '\t{:5.3f}%\t{:5.3f}%\t{:5.3f}%'.format(100.0*h1_win/total, 100.0*tie/total, 100.0*h2_win/total)

	if (verbose):
		t1 = timer()
		print 'preflop_two_hand_equity time = {:8.4f} s'.format(t1-t0)

	return equity



def create_all_preflop_two_hand_equity(verbose=False, save=False, distributed=False, nb_process=4):
	"""returns preflop_two_hand_equity for all two hand preflop combinations"""
	global all_preflop_two_hands

	print '\n--------------- start create_all_preflop_two_hand_equity'
	print 'all preflop two hands = \nstart = {}\nend = {}\nnb of elements = {}'.format(all_preflop_two_hands[:5], all_preflop_two_hands[-5:], len(all_preflop_two_hands))

	t0 = timer()

	if (distributed):
		pool = ThreadPool(nb_process)
		equity = pool.map(preflop_two_hand_equity, all_preflop_two_hands[:])
		pool.close()
		pool.join()
	else:
		equity = []
		for k, p in enumerate(all_preflop_two_hands[:]):
			if (verbose):
				# print k,' - ', p
				sys.stdout.write('\rk=%5d / %5d : {}' % (k+1, len(all_preflop_two_hands)), p)
				sys.stdout.flush()
			equity.append(preflop_two_hand_equity(p))

	t1 = timer()
	print 'all_preflop_two_hand_equity time = {:9.4f} s'.format(t1-t0)
	print 'exact number of distinct (rankwise) pairs of preflop hands = {}'.format(np.array([len(e) for e in equity]).sum())
	if (save):
		cPickle.dump(equity, open(os.path.join('Tables', 'all_preflop_two_hand_equity.pk'), 'wb'))
		print '{} saved to disk as {}'.format('equity', os.path.join('Tables', 'all_preflop_two_hand_equity.pk'))
	return equity



def create_all_preflop_two_hand_equity_aggregate(all_preflop_two_hand_equity, save=False):
	"""returns 169x169 matrix of preflop two hands equity weighted averaged over frequency"""
	p = len(all_preflop_hands)
	n = len(all_preflop_two_hand_equity)
	N = (all_preflop_two_hand_equity[0][0, :3]).sum()
	equity = np.zeros([n, 3], dtype=np.float32)
	for i in xrange(n):
		arr = all_preflop_two_hand_equity[i]
		weights = 1.0*arr[:, 3]/np.sum(arr[:, 3])
		equity_one_combin = (arr[:, :3]*weights[np.newaxis].T)/N
		equity[i] = np.sum(equity_one_combin, axis=0)
	df = pd.DataFrame(data=equity, columns=['Hand1_Wins', 'Ties', 'Hand2_Wins'], index=np.arange(n))
	df.insert(0, 'HandA', [e[0] for e in all_preflop_two_hands])
	df.insert(1, 'HandA_no', df['HandA'].apply(lambda x : all_preflop_hands.index(x)))
	df.insert(2, 'HandB', [e[1] for e in all_preflop_two_hands])
	df.insert(3, 'HandB_no', df['HandB'].apply(lambda x : all_preflop_hands.index(x)))
	if (save):
		df.to_csv(os.path.join('Tables', 'df_two_hand_equity.csv'), index=False)

	return df



def preflop_hand_str_order(h, return_index=True):
	hfs1, hfs2, hm = h
	hf1, hf2 = face_symbol_to_no[hfs1], face_symbol_to_no[hfs2]

	if (((hf1<hf2) and (hm=='s')) or ((hf1>hf2) and (hm=='o'))):
		hf1, hf2 = hf2, hf1
		hfs1, hfs2 = hfs2, hfs1

	if (return_index):
		return all_preflop_hands.index(hfs1+hfs2+hm)
	else:
		return (hfs1+hfs2+hm)


def preflop_two_hand_str_order(p, return_index=True):
	h1fs1, h1fs2, h1m = p[0]
	h1f1, h1f2 = face_symbol_to_no[h1fs1], face_symbol_to_no[h1fs2]
	h2fs1, h2fs2, h2m = p[1]
	h2f1, h2f2 = face_symbol_to_no[h2fs1], face_symbol_to_no[h2fs2]

	if (((h1f1<h1f2) and (h1m=='s')) or ((h1f1>h1f2) and (h1m=='o'))):
		h1f1, h1f2 = h1f2, h1f1
		h1fs1, h1fs2 = h1fs2, h1fs1

	if (((h2f1<h2f2) and (h2m=='s')) or ((h2f1>h2f2) and (h2m=='o'))):
		h2f1, h2f2 = h2f2, h2f1
		h2fs1, h2fs2 = h2fs2, h2fs1

	if ((h1fs1+h1fs2+h1m, h2fs1+h2fs2+h2m) not in all_preflop_two_hands):
		h1fs1, h1fs2, h1m , h2fs1, h2fs2, h2m = h2fs1, h2fs2, h2m, h1fs1, h1fs2, h1m

	if (return_index):
		return all_preflop_two_hands.index((h1fs1+h1fs2+h1m, h2fs1+h2fs2+h2m))
	else:
		return (h1fs1+h1fs2+h1m, h2fs1+h2fs2+h2m)



# ------------------------ main
if __name__ == '__main__':


	# 5 card hands statistics
	t0 = timer()
	df_hand_five = create_df_hand_five()
	t1 = timer()
	print '\ndf_hand_five time = {:8.4f} s'.format(t1-t0)
	# df_hand_five = pd.read_pickle(os.path.join('Tables', 'df_hand_five.pd'))
	print df_hand_five


	# 7 card hands statistics
	t0 = timer()
	df_hand_seven = create_df_hand_seven()
	t1 = timer()
	print '\ndf_hand_seven time = {:8.4f} s'.format(t1-t0)
	# df_hand_seven = pd.read_pickle(os.path.join('Tables', 'df_hand_seven.pd'))
	print df_hand_seven


	# one pre flop hand display
	print '\none preflop hand'
	h = 'K5s'
	print h
	print one_hand_no_to_char(hand_str_to_no(h))


	# one pre flop hand pair display
	print '\none pair of preflop hands'
	h1, h2 = 'Q6o', '52o'
	print h1, h2
	print two_hand_no_to_char(np.concatenate((hand_str_to_no(h1), hand_str_to_no(h2))))


	# deck of 52 cards display
	print '\n deck of 52 cards'
	for f in range(13):
		for s in range(4):
			print card_fs_to_char(f, s), ',',
	print '\n'


	# all preflop hand equity distribution
	all_preflop_hands = [face_symbol[i]+face_symbol[j]+choice(i, j, ['s', 'o', 'o'])
									for i in range(len(face_symbol))[::-1]
									for j in range(len(face_symbol))[::-1]]
	print 'all preflop hands = \nstart = {}\nend = {}\nnb of elements = {}'.format(all_preflop_hands[:10], all_preflop_hands[-10:], len(all_preflop_hands))
	df_preflop_hand_distrib = create_df_preflop_hand_distrib(save=True)
	# df_preflop_hand_distrib = pd.read_pickle(os.path.join('Tables', 'df_preflop_hand_distrib.pd'))


	# one pair of preflop hand equity distributions, with all suit combinations and associated frequencies
	# h1, h2 = 'Q6o', '52o'
	# equ_h1_h2 = preflop_two_hand_equity((h1, h2), verbose=False)
	# print equ_h1_h2


	# all preflop hand pairs equity distribution, with all suit combinations and associated frequencies -  long  computation
	all_preflop_two_hands = list(it.combinations(all_preflop_hands, r=2)) + zip(all_preflop_hands, all_preflop_hands)
	print '\nall preflop two hands = \nstart = {}\nend = {}\nnb of elements = {}'.format(all_preflop_two_hands[:5], all_preflop_two_hands[-5:], len(all_preflop_two_hands))
	# all_preflop_two_hand_equity = create_all_preflop_two_hand_equity()
	all_preflop_two_hand_equity = cPickle.load(open(os.path.join('Tables', 'all_preflop_two_hand_equity_full.pk'), 'rb'))



	# equity distribution for one hand pair, with all suit combinations and associated frequencies
	p = ('89o', '98o')

	t0 = timer()
	print '\np = {}, idx(p)={}'.format(p, preflop_two_hand_str_order(p, return_index=True))
	t1 = timer()
	print 'time = {:8.4f} s'.format(t1-t0)

	print'\n'
	t0 = timer()
	print preflop_two_hand_equity(p, verbose=True)
	t1 = timer()
	print 'time = {:8.4f} s'.format(t1-t0)


	print'\n------------- creating df_equity_two_hands'
	t0 = timer()
	df_equity_two_hands = create_all_preflop_two_hand_equity_aggregate(all_preflop_two_hand_equity, save=False)
	t1 = timer()
	print df_equity_two_hands.head()
	print df_equity_two_hands.tail()
	print 'time = {:8.4f} s'.format(t1-t0)



