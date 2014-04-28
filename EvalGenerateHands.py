
import numpy as np
from scipy import misc
from timeit import default_timer as timer
from numba import jit, int32


def create_array_all_seven():
	"""c1, c2, c3, c4, c5, c6, c7 are distincts integers from 0 to 51, each one card of the deck"""
	N =133784560	# import scipy.misc; scipy.misc.comb(52, 7, exact=True)
	deckSize = 52
	array_seven_cards = np.zeros([N, 7], dtype=np.int32)
	k = 0
	for c1 in xrange(0, deckSize):
		for c2 in xrange(0, c1):
			for c3 in xrange(0, c2):
				for c4 in xrange(0, c3):
					for c5 in xrange(0, c4):
						for c6 in xrange(0, c5):
							for c7 in xrange(0, c6):
								array_seven_cards[k, 0] = c1
								array_seven_cards[k, 1] = c2
								array_seven_cards[k, 2] = c3
								array_seven_cards[k, 3] = c4
								array_seven_cards[k, 4] = c5
								array_seven_cards[k, 5] = c6
								array_seven_cards[k, 6] = c7
								k += 1
	return array_seven_cards

create_array_all_seven_fast = jit(int32[:, :]())(create_array_all_seven)



def create_array_all_five():
	"""c1, c2, c3, c4, c5 are distincts integers from 0 to 51, each one card of the deck"""
	N =2598960	# import scipy.misc; scipy.misc.comb(52, 5, exact=True)
	deckSize = 52
	array_five_cards = np.zeros([N, 5], dtype=np.int32)
	k = 0
	for c1 in range(0, deckSize):
		for c2 in range(0, c1):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					for c5 in range(0, c4):
						array_five_cards[k, 0] = c1
						array_five_cards[k, 1] = c2
						array_five_cards[k, 2] = c3
						array_five_cards[k, 3] = c4
						array_five_cards[k, 4] = c5
						k += 1
	return array_five_cards

create_array_all_five_fast = jit(int32[:, :]())(create_array_all_five)



def table_cards_given_two(array_two_cards):
	card1 = array_two_cards[0]
	card2 = array_two_cards[1]

	N =2118760	# import scipy.misc; scipy.misc.comb(50-2, 5, exact=True)
	deckSize = 52
	array_five_cards = np.zeros([N, 5], dtype=np.int32)
	deck = np.zeros(deckSize-2, dtype=np.int32)
	k=0
	for c in range(deckSize):
		if ((c!=card1) and (c!=card2)):
			deck[k] = c
			k += 1
	# print deck

	k = 0
	for idx1 in range(deckSize-2):
		for idx2 in range(idx1):
			for idx3 in range(idx2):
				for idx4 in range(idx3):
					for idx5 in range(idx4):
							array_five_cards[k, 0] = deck[idx1]
							array_five_cards[k, 1] = deck[idx2]
							array_five_cards[k, 2] = deck[idx3]
							array_five_cards[k, 3] = deck[idx4]
							array_five_cards[k, 4] = deck[idx5]
							k += 1
	return array_five_cards

table_cards_given_two_fast = jit(int32[:, :](int32[:]))(table_cards_given_two)



def table_cards_given_four(array_four_cards):
	card1 = array_four_cards[0]
	card2 = array_four_cards[1]
	card3 = array_four_cards[2]
	card4 = array_four_cards[3]

	N =1712304	# import scipy.misc; scipy.misc.comb(52-4, 5, exact=True)
	deckSize = 52
	array_five_cards = np.zeros([N, 5], dtype=np.int32)
	deck = np.zeros(deckSize-4, dtype=np.int32)
	k=0
	for c in range(deckSize):
		if ((c!=card1) and (c!=card2) and (c!=card3) and (c!=card4)):
			deck[k] = c
			k += 1
	k = 0
	for idx1 in range(deckSize-4):
		for idx2 in range(idx1):
			for idx3 in range(idx2):
				for idx4 in range(idx3):
					for idx5 in range(idx4):
							array_five_cards[k, 0] = deck[idx1]
							array_five_cards[k, 1] = deck[idx2]
							array_five_cards[k, 2] = deck[idx3]
							array_five_cards[k, 3] = deck[idx4]
							array_five_cards[k, 4] = deck[idx5]
							k += 1
	return array_five_cards

table_cards_given_four_fast = jit(int32[:, :](int32[:]))(table_cards_given_four)



def all_n_cards_given_m_cards(n, array_m_cards, N):
	""" n must be in [7, 5, 3, 2, 1] all practical cases
	nb_combin contains scipy.misc.comb(52-m, n, exact=True) for for m in range(9*2+4+1) for n in [7, 5, 3, 2, 1]"""
	array_n_cards = np.zeros([N, n], dtype=np.int32)
	m = array_m_cards.size

	deck = np.zeros([52-m], dtype=np.int32)
	k=0
	for c in xrange(52):
		cand = 1
		for idx in xrange(m):
			if (c==array_m_cards[idx]):
				cand = 0
		if (cand==1):
			deck[k] = c
			k += 1

	k=0
	if (n==7):
		for idx1 in xrange(52-m):
			for idx2 in xrange(idx1):
				for idx3 in xrange(idx2):
					for idx4 in xrange(idx3):
						for idx5 in xrange(idx4):
							for idx6 in xrange(idx5):
								for idx7 in xrange(idx6):
									array_n_cards[k, 0] = deck[idx1]
									array_n_cards[k, 1] = deck[idx2]
									array_n_cards[k, 2] = deck[idx3]
									array_n_cards[k, 3] = deck[idx4]
									array_n_cards[k, 4] = deck[idx5]
									array_n_cards[k, 5] = deck[idx6]
									array_n_cards[k, 6] = deck[idx6]
									k += 1
	elif (n==5):
		for idx1 in xrange(52-m):
			for idx2 in xrange(idx1):
				for idx3 in xrange(idx2):
					for idx4 in xrange(idx3):
						for idx5 in xrange(idx4):
							array_n_cards[k, 0] = deck[idx1]
							array_n_cards[k, 1] = deck[idx2]
							array_n_cards[k, 2] = deck[idx3]
							array_n_cards[k, 3] = deck[idx4]
							array_n_cards[k, 4] = deck[idx5]
							k += 1

	elif (n==3):
		for idx1 in xrange(52-m):
			for idx2 in xrange(idx1):
				for idx3 in xrange(idx2):
					array_n_cards[k, 0] = deck[idx1]
					array_n_cards[k, 1] = deck[idx2]
					array_n_cards[k, 2] = deck[idx3]
					k += 1

	elif (n==2):
		for idx1 in xrange(52-m):
			for idx2 in xrange(idx1):
				array_n_cards[k, 0] = deck[idx1]
				array_n_cards[k, 1] = deck[idx2]
				k += 1

	elif (n==1):
		for idx1 in xrange(52-m):
			array_n_cards[k, 0] = deck[idx1]
			k += 1

	else:
		array_n_cards =  np.zeros([1, 1], dtype=np.int32)

	return array_n_cards

all_n_cards_given_m_cards_fast = jit(int32[:, :](int32, int32[:], int32))(all_n_cards_given_m_cards)


# ------------------------ main
if __name__ == '__main__':

	t0 = timer()
	tc1 = create_array_all_five_fast()
	t1 = timer()
	print '\ncreate_array_all_five time = {:8.4f} s'.format(t1-t0)
	print tc1.shape

	t0 = timer()
	tc2 = create_array_all_seven_fast()
	t1 = timer()
	print '\ncreate_array_all_seven_fast time = {:8.4f} s'.format(t1-t0)
	print tc2.shape

	t0 = timer()
	tc3 = table_cards_given_two_fast(np.array([10, 18]))
	t1 = timer()
	print '\ntable_cards_given_two_fast time = {:8.4f} s'.format(t1-t0)
	print tc3.shape

	t0 = timer()
	tc4 = table_cards_given_four_fast(np.array([10, 18, 28, 50]))
	t1 = timer()
	print '\ntable_cards_given_four_fast time = {:8.4f} s'.format(t1-t0)
	print tc4.shape

	t0 = timer()
	n, m = 7, 0
	known_cards_m = np.random.choice(52, m, replace=False)
	N = misc.comb(52-m, n, exact=True)
	print '\nm={}, m={}, N={}'.format(n, m, N)
	print 'known_cards_m={}'.format(known_cards_m)
	tc5 = all_n_cards_given_m_cards_fast(n, known_cards_m, N)
	t1 = timer()
	print 'all_n_cards_given_m_cards_fast time = {:8.4f} s'.format(t1-t0)
	print tc5.shape

	t0 = timer()
	n, m = 5, 5*2+0
	known_cards_m = np.random.choice(52, m, replace=False)
	N = misc.comb(52-m, n, exact=True)
	print '\nm={}, m={}, N={}'.format(n, m, N)
	print 'known_cards_m={}'.format(known_cards_m)
	tc6 = all_n_cards_given_m_cards_fast(n, known_cards_m, N)
	t1 = timer()
	print 'all_n_cards_given_m_cards_fast time = {:8.4f} s'.format(t1-t0)
	print tc6.shape



