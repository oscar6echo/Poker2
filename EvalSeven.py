"""
Texas Hold'em fast hand evaluator for 7 card hands
"""

import numpy as np
import os
from scipy import sparse, misc
from timeit import default_timer as timer
from numba import autojit, jit, int32, uint32

import EvalKeys as keys
import EvalFive
from EvalFive import save_vector_to_csv_as_sparse, load_vector_from_sparse_csv
from EvalGenerateHands import create_array_all_seven_fast

np.set_printoptions(linewidth=500)


# Init all tables
flush_rank = np.zeros(keys.MAX_FLUSH_KEY_SEVEN+1, dtype=np.int32)
face_rank = np.zeros(keys.MAX_FACE_KEY_SEVEN+1, dtype=np.int32)
flush_suit = np.ones(keys.MAX_SUIT_KEY+1, dtype=np.int32)*(-2)



def compute_tables():
	"""compute all EvalSeven tables: flush_rank, face_rank, flush_suit"""
	global flush_rank, face_rank, flush_suit

	print "\n--------------- start EvalSeven.compute_tables"

	# local names
	face_key_seven = keys.FACE_KEY_SEVEN
	flush_key_seven = keys.FLUSH_KEY_SEVEN
	suit_key = keys.SUIT_KEY
	nb_face = keys.NB_FACE
	nb_suit = keys.NB_SUIT

	t0 = timer()

	# compute face_rank
	print 'start face_rank'
	for c1 in range(0, nb_face):
		for c2 in range(0, c1+1):
			for c3 in range(0, c2+1):
				for c4 in range(0, c3+1):
					for c5 in range(0, c4+1):
						for c6 in range(0, c5+1):
							for c7 in range(0, c6+1):
								# No 5, or more, same faces
								if ((c1-c5>0) and (c2-c6>0) and (c3-c7>0)):
									hand_key = face_key_seven[c1]+face_key_seven[c2]+face_key_seven[c3]+face_key_seven[c4]+face_key_seven[c5]+face_key_seven[c6]+face_key_seven[c7]
									face_rank[hand_key] = EvalFive.get_seven_rank_fast(np.array([[4*c1, 4*c2, 4*c3, 4*c4, 4*c5+1, 4*c6+1, 4*c7+1]]), keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, EvalFive.flush_rank, EvalFive.face_rank)[0]

	# compute flush_rank
	# Flush 7 cards
	print 'start flush_rank: 7 cards'
	for c1 in range(6, nb_face):
		for c2 in range(0, c1):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					for c5 in range(0, c4):
						for c6 in range(0, c5):
							for c7 in range(0, c6):
								hand_key = flush_key_seven[c1]+flush_key_seven[c2]+flush_key_seven[c3]+flush_key_seven[c4]+flush_key_seven[c5]+flush_key_seven[c6]+flush_key_seven[c7]
								flush_rank[hand_key] = EvalFive.get_seven_rank_fast(np.array([[4*c1, 4*c2, 4*c3, 4*c4, 4*c5, 4*c6, 4*c7]]), keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, EvalFive.flush_rank, EvalFive.face_rank)[0]

	# Flush 6 cards
	print 'start flush_rank: 6 cards'
	for c1 in range(5, nb_face):
		for c2 in range(0, c1):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					for c5 in range(0, c4):
						for c6 in range(0, c5):
							hand_key = flush_key_seven[c1]+flush_key_seven[c2]+flush_key_seven[c3]+flush_key_seven[c4]+flush_key_seven[c5]+flush_key_seven[c6]
							flush_rank[hand_key] = EvalFive.get_seven_rank_fast(np.array([[4*c1, 4*c2, 4*c3, 4*c4, 4*c5, 4*c6, 1]]), keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, EvalFive.flush_rank, EvalFive.face_rank)[0]

	# Flush 5 cards
	print 'start flush_rank: 5 cards'
	for c1 in range(4, nb_face):
		for c2 in range(0, c1):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					for c5 in range(0, c4):
						hand_key = flush_key_seven[c1]+flush_key_seven[c2]+flush_key_seven[c3]+flush_key_seven[c4]+flush_key_seven[c5]
						flush_rank[hand_key] = EvalFive.get_five_rank_fast(np.array([[4*c1, 4*c2, 4*c3, 4*c4, 4*c5]]), keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, EvalFive.flush_rank, EvalFive.face_rank)[0]

	# Flush Suit table
	print 'start flush_suit'
	for c1 in range(0, nb_suit):
		for c2 in range(0, c1+1):
			for c3 in range(0, c2+1):
				for c4 in range(0, c3+1):
					for c5 in range(0, c4+1):
						for c6 in range(0, c5+1):
							for c7 in range(0, c6+1):
								hand_suit_key = (suit_key[c1]+suit_key[c2]+suit_key[c3]+suit_key[c4]+suit_key[c5]+suit_key[c6]+suit_key[c7])
								flush_suit[hand_suit_key] = -1
								for cand_suit in range(0, nb_suit):
									suit_count = ((c1==cand_suit)+(c2==cand_suit)+(c3==cand_suit)+(c4==cand_suit)+(c5==cand_suit)+(c6==cand_suit)+(c7==cand_suit))
									if (suit_count>=5):
										flush_suit[hand_suit_key] = cand_suit

	t1 = timer()
	print 'compute_tables time = {:8.4f} s'.format(t1-t0)
	print '--------------- end EvalSeven.compute_tables'



def save_tables():
	"""save all EvalSeven tables on disk: flush_rank, face_rank, flush_suit"""
	print '\n--------------- start EvalSeven.save_tables'
	table_dir = 'Tables'
	if not os.path.exists(table_dir):
		os.makedirs(table_dir)
		print 'directory {} created'.format(table_dir)
	save_vector_to_csv_as_sparse(flush_rank, table_dir, 'sparse_flush_rank_seven')
	save_vector_to_csv_as_sparse(face_rank, table_dir, 'sparse_face_rank_seven')
	np.savetxt(os.path.join(table_dir, 'flush_suit.txt'), flush_suit, delimiter=',', fmt='%d')
	for f in ['sparse_flush_rank_seven.csv', 'sparse_face_rank_seven.csv', 'flush_suit.txt']:
		print '{} saved to disk as {}'.format(f[:-4], os.path.join(table_dir, f))



def load_tables():
	"""load all EvalSeven tables from disk: flush_rank, face_rank, flush_suit"""
	global flush_rank, face_rank, flush_suit
	print '\n--------------- EvalSeven.load_tables'
	table_dir = 'Tables'
	if os.path.exists(table_dir):
		flush_rank = load_vector_from_sparse_csv(table_dir, 'sparse_flush_rank_seven')
		face_rank = load_vector_from_sparse_csv(table_dir, 'sparse_face_rank_seven')
		flush_suit = np.loadtxt(os.path.join(table_dir, 'flush_suit.txt'), dtype=np.int32)
		for f in ['sparse_flush_rank_seven.csv', 'sparse_face_rank_seven.csv', 'flush_suit.txt']:
			print '{} loaded from file {}'.format(f[:-4], os.path.join(table_dir, f))
	else:
		print 'No tables on disk'



def get_seven_rank_simple(array_seven_cards):
	"""array_seven_cards is an array of Nx7 distincts integers from 0 to 51, each one card of the deck"""
	c1, c2, c3, c4, c5, c6, c7 = array_seven_cards
	hand_rank = -1
	hand_key = keys.CARD_FACE_KEY[c1]+ \
			keys.CARD_FACE_KEY[c2]+ \
			keys.CARD_FACE_KEY[c3]+ \
			keys.CARD_FACE_KEY[c4]+ \
			keys.CARD_FACE_KEY[c5]+ \
			keys.CARD_FACE_KEY[c6]+ \
			keys.CARD_FACE_KEY[c7]
	hand_suit_key = hand_key & keys.SUIT_MASK
	hand_suit = flush_suit[hand_suit_key]
	if (hand_suit == -1):
		hand_face_key = hand_key >> keys.SUIT_BIT_SHIFT
		hand_rank = face_rank[hand_face_key]
	else:
		hand_flush_key = (keys.CARD_FLUSH_KEY[c1]*(keys.CARD_SUIT[c1]==hand_suit)+ \
				keys.CARD_FLUSH_KEY[c2]*(keys.CARD_SUIT[c2]==hand_suit)+ \
				keys.CARD_FLUSH_KEY[c3]*(keys.CARD_SUIT[c3]==hand_suit)+ \
				keys.CARD_FLUSH_KEY[c4]*(keys.CARD_SUIT[c4]==hand_suit)+ \
				keys.CARD_FLUSH_KEY[c5]*(keys.CARD_SUIT[c5]==hand_suit)+ \
				keys.CARD_FLUSH_KEY[c6]*(keys.CARD_SUIT[c6]==hand_suit)+ \
				keys.CARD_FLUSH_KEY[c7]*(keys.CARD_SUIT[c7]==hand_suit))
		hand_rank = flush_rank[hand_flush_key]
	return hand_rank



def get_seven_rank_full(array_seven_cards, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit):
	"""array_seven_cards is an array of Nx7 distincts integers from 0 to 51, each one card of the deck"""
	N = array_seven_cards.shape[0]
	hand_rank = np.zeros(N, dtype=np.int32)
	for i in xrange(N):
		hand_rank[i] = -1
		c1 = array_seven_cards[i, 0]
		c2 = array_seven_cards[i, 1]
		c3 = array_seven_cards[i, 2]
		c4 = array_seven_cards[i, 3]
		c5 = array_seven_cards[i, 4]
		c6 = array_seven_cards[i, 5]
		c7 = array_seven_cards[i, 6]
		hand_key = card_face_key[c1]+card_face_key[c2]+card_face_key[c3]+card_face_key[c4]+card_face_key[c5]+card_face_key[c6]+card_face_key[c7]
		hand_suit_key = hand_key & suit_mask
		hand_suit = flush_suit[hand_suit_key]
		if (hand_suit == -1):
			hand_face_key = hand_key >> suit_bit_shift
			hand_rank [i] = face_rank[hand_face_key]
		else:
			hand_flush_key = (card_flush_key[c1]*(card_suit[c1]==hand_suit)+
				card_flush_key[c2]*(card_suit[c2]==hand_suit)+
				card_flush_key[c3]*(card_suit[c3]==hand_suit)+
				card_flush_key[c4]*(card_suit[c4]==hand_suit)+
				card_flush_key[c5]*(card_suit[c5]==hand_suit)+
				card_flush_key[c6]*(card_suit[c6]==hand_suit)+
				card_flush_key[c7]*(card_suit[c7]==hand_suit))
			hand_rank[i] = flush_rank[hand_flush_key]
	return hand_rank

get_seven_rank_fast = jit(int32[:](int32[:, :], int32[:], uint32[:], int32[:], int32, int32, int32[:], int32[:], int32[:]))(get_seven_rank_full)



def test():
	"""display all EvalSeven tables, run getSevenRank_ evaluators on sample hands, compare getSevenRank_ with EvalFive.getSevenRank_"""
	global seven_cards, array_seven_cards, hr1, hr2, hr3, N, rank7, rank5, sparse_flush_rank, sparse_face_rank
	print '\n--------------- start EvalSeven.test'

	print '-------- EvalSeven tables'
	sparse_flush_rank = sparse.csc_matrix(flush_rank)
	print 'flush_rank = \n{}\n{}\nnb of nonzero elements = {}'.format(sparse_flush_rank.nonzero()[1], sparse_flush_rank.data, sparse_flush_rank.nonzero()[1].size)
	sparse_face_rank = sparse.csc_matrix(face_rank)
	print 'face_rank = \n{}\n{}\nnb of nonzero elements = {}'.format(sparse_face_rank.nonzero()[1], sparse_face_rank.data, sparse_face_rank.nonzero()[1].size)
	print 'flush_suit = \n{}'.format(flush_suit)
	print 'nb of elements different from -2 = {}'.format(np.array(flush_suit[flush_suit!=-2].size))

	print '-------- EvalSeven getSevenRank_ evaluators sample runs'
	np.random.seed(99)
	array_seven_cards = np.array([np.random.choice(keys.DECK_SIZE, 7, replace=False) for k in xrange(10)])
	print 'array_seven_cards=\n{}'.format(array_seven_cards)
	seven_cards = array_seven_cards[0]
	print 'seven_cards={}'.format(seven_cards)

	hr1 = get_seven_rank_simple(seven_cards)
	print '\nget_seven_rank_simple(seven_cards)={}'.format(hr1)

	hr2 = get_seven_rank_full(array_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, flush_rank, face_rank, flush_suit)
	print 'get_seven_rank_full(array_seven_cards)={}'.format(hr2)

	hr3 = get_seven_rank_fast(array_seven_cards, keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, flush_rank, face_rank, flush_suit)
	print 'get_seven_rank_fast(array_seven_cards)={}'.format(hr3)

	print '-------- compare getSevenRank_ with EvalFive.get_seven_rank_ on all hands'
	t0 = timer()
	array_all_seven_cards = create_array_all_seven_fast()
	t1 = timer()
	print 'array_all_seven_cards time = {:8.4f} s'.format(t1-t0)

	t0 = timer()

	rank7 = get_seven_rank_fast(array_all_seven_cards[:], keys.CARD_FLUSH_KEY, keys.CARD_FACE_KEY, keys.CARD_SUIT, keys.SUIT_MASK, keys.SUIT_BIT_SHIFT, flush_rank, face_rank, flush_suit)
	t1 = timer()
	print 'EvalSeven.get_seven_rank_fast time = {:8.4f} s'.format(t1-t0)

	N = 1000000*140
	t0 = timer()
	rank5 = EvalFive.get_seven_rank_fast(array_all_seven_cards[:N], keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, EvalFive.flush_rank, EvalFive.face_rank)
	t1 = timer()
	print 'EvalFive.get_seven_rank_fast time = {:8.4f} s'.format(t1-t0)

	print 'result(EvalSeven.get_seven_rank_fast)==result(EvalFive.get_seven_rank_fast) ? {}'.format((rank5==rank7).all())

	print '--------------- end EvalSeven.test'


# ------------------------ main
if __name__ == '__main__':
	compute_tables()
	save_tables()
	test()

else:
	load_tables()
	# test()



