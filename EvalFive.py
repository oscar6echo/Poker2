"""
Texas Hold'em hand evaluators
	a fast one for 5 cards
	a slow one for 7 cards: It goes through the C(7, 5)=21 5-card possible hands
"""

import numpy as np
from scipy import sparse
import os
from timeit import default_timer as timer
from numba import autojit, jit, int32, uint32

import EvalKeys as keys

np.set_printoptions(linewidth=300)


# Init all tables
flush_rank = np.zeros(keys.MAX_FLUSH_KEY_FIVE+1, dtype=np.int32)
face_rank = np.zeros(keys.MAX_FACE_KEY_FIVE+1, dtype=np.int32)
hand_faces = np.zeros([7462, 5], dtype=np.int32)	# we know the solution in advance :-)
hand_type = np.array(['']*7462, dtype=np.dtype('a16'))



def compute_tables():
	"""compute all EvalFive tables: flush_rank, face_rank, hand_faces, hand_type"""
	global flush_rank, face_rank, hand_faces, hand_type

	print "\n--------------- start EvalFive.compute_tables"

	# local names
	face_key_five = keys.FACE_KEY_FIVE
	flush_key_five = keys.FLUSH_KEY_FIVE
	nb_face = keys.NB_FACE
	nb_suit = keys.NB_SUIT

	t0 = timer()

	# compute hand ranks from all distinctly ranked 5 card hands
	hand_rank = 0

	# High Card
	print 'start High Card'
	for c1 in range(4, nb_face):
		for c2 in range(0, c1):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					for c5 in range(0, c4):
						# No straights, including A2345
						if not ((c1 - c5 ==4) or (c1 == 12 and c2 == 3)):
							hand_key = face_key_five[c1]+face_key_five[c2]+face_key_five[c3]+face_key_five[c4]+face_key_five[c5]
							face_rank[hand_key] = hand_rank
							hand_faces[hand_rank] = [c1, c2, c3, c4, c5]
							hand_type[hand_rank] = "High Card"
							hand_rank += 1

	# One Pair
	print 'start One Pair'
	for c1 in range(0, nb_face):
		for c2 in range(0, nb_face):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					# No Three of a Kind
					if not ((c1 == c2 ) or (c1 == c3) or (c1 == c4)):
						hand_key = 2*face_key_five[c1]+face_key_five[c2]+face_key_five[c3]+face_key_five[c4]
						face_rank[hand_key] = hand_rank
						hand_faces[hand_rank] = [c1, c1, c3, c4, c5]
						hand_type[hand_rank] = 'One Pair'
						hand_rank += 1

	# Two Pairs
	print 'start Two Pairs'
	for c1 in range(0, nb_face):
		for c2 in range(0, c1):
			for c3 in range(0, nb_face):
				# No Three of a Kind
				if not ((c1 == c3 ) or (c2 == c3)):
					hand_key = 2*face_key_five[c1]+2*face_key_five[c2]+face_key_five[c3]
					face_rank[hand_key] = hand_rank
					hand_faces[hand_rank] = [c1, c1, c2, c2, c5]
					hand_type[hand_rank] = 'Two Pairs'
					hand_rank += 1

	# Three of a kind
	print 'start Three of a Kind'
	for c1 in range(0, nb_face):
		for c2 in range(0, nb_face):
			for c3 in range(0, c2):
				# No Four of a Kind
				if not ((c1 == c2 ) or (c1 == c3)):
					hand_key = 3*face_key_five[c1]+face_key_five[c2]+face_key_five[c3]
					face_rank[hand_key] = hand_rank
					hand_faces[hand_rank] = [c1, c1, c1, c2, c3]
					hand_type[hand_rank] = 'Three of a Kind'
					hand_rank += 1

	# Low Straight
	print 'start Low Straight'
	c1 = 3
	c5 = 12
	hand_key = face_key_five[c1]+face_key_five[c1-1]+face_key_five[c1-2]+face_key_five[c1-3]+face_key_five[c5]
	face_rank[hand_key] = hand_rank
	hand_faces[hand_rank] = [c1, c1-1, c1-2, c1-3, c5]
	hand_type[hand_rank] = 'Straight'
	hand_rank += 1

	# Usual Straights
	print 'start Usual Straight'
	for c1 in range(4, nb_face):
		hand_key = face_key_five[c1]+face_key_five[c1-1]+face_key_five[c1-2]+face_key_five[c1-3]+face_key_five[c1-4]
		face_rank[hand_key] = hand_rank
		hand_faces[hand_rank] = [c1, c1-1, c1-2, c1-3, c1-4]
		hand_type[hand_rank] = 'Straight'
		hand_rank += 1

	# Flush
	print 'start Flush'
	for c1 in range(4, nb_face):
		for c2 in range(0, c1):
			for c3 in range(0, c2):
				for c4 in range(0, c3):
					for c5 in range(0, c4):
						# No straights, including A2345
						if not ((c1 - c5 ==4) or (c1 == 12 and c2 == 3)):
							hand_key = flush_key_five[c1]+flush_key_five[c2]+flush_key_five[c3]+flush_key_five[c4]+flush_key_five[c5]
							flush_rank[hand_key] = hand_rank
							hand_faces[hand_rank] = [c1, c2, c3, c4, c5]
							hand_type[hand_rank] = 'Flush'
							hand_rank += 1

	# Full House
	print 'start Full House'
	for c1 in range(0, nb_face):
		for c2 in range(0, nb_face):
			# No Four of a Kind
			if not (c1 == c2):
				hand_key = 3*face_key_five[c1]+2*face_key_five[c2]
				face_rank[hand_key] = hand_rank
				hand_faces[hand_rank] = [c1, c1, c1, c2, c2]
				hand_type[hand_rank] = 'Full House'
				hand_rank += 1

	# Four of a Kind
	print 'start Four of a Kind'
	for c1 in range(0, nb_face):
		for c2 in range(0, nb_face):
			# No 'Five of a Kind'
			if not (c1 == c2):
				hand_key = 4*face_key_five[c1]+1*face_key_five[c2]
				face_rank[hand_key] = hand_rank
				hand_faces[hand_rank] = [c1, c1, c1, c1, c2]
				hand_type[hand_rank] = 'Four of a Kind'
				hand_rank += 1

	# Low Straight Flush
	print 'start Low Straight Flush'
	c1 = 3
	c5 = 12
	hand_key = flush_key_five[c1]+flush_key_five[c1-1]+flush_key_five[c1-2]+flush_key_five[c1-3]+flush_key_five[c5]
	flush_rank[hand_key] = hand_rank
	hand_faces[hand_rank] = [c1, c1-1, c1-2, c1-3, c5]
	hand_type[hand_rank] = 'Straight Flush'
	hand_rank += 1

	# Usual Straights Flush
	print 'start Usual Straight Flush'
	for c1 in range(4, nb_face):
		hand_key = flush_key_five[c1]+flush_key_five[c1-1]+flush_key_five[c1-2]+flush_key_five[c1-3]+flush_key_five[c1-4]
		flush_rank[hand_key] = hand_rank
		hand_faces[hand_rank] = [c1, c1-1, c1-2, c1-3, c1-4]
		hand_type[hand_rank] = 'Straight Flush'
		hand_rank += 1

	t1 = timer()
	print 'compute_tables time = {:8.4f} s'.format(t1-t0)
	print '--------------- end EvalFive.compute_tables'



def save_vector_to_csv_as_sparse(vect, directory, filename):
	"""save numpy array to csv as sparse"""
	sparse_vector = sparse.csc_matrix(vect)
	row, col = sparse_vector.nonzero()
	data = sparse_vector.data
	np.savetxt(os.path.join(directory, filename+'.csv'), np.array([col, data]).T, delimiter=',', fmt='%d')



def load_vector_from_sparse_csv(directory, filename):
	"""load csv containing sparse array and return dense numpy array"""
	arr = np.loadtxt(os.path.join(directory, filename+'.csv'), delimiter=',', dtype=np.int32)
	data = arr[:, 1]
	col = arr[:, 0]
	row = np.zeros(data.size)
	# print 'file {} loaded from disk'.format(os.path.join(directory, filename+'.csv'))
	return np.array(sparse.csc_matrix((data, (row,col))).todense())[0]



def save_tables():
	"""save all EvalFive tables on disk: flush_rank, face_rank, hand_faces, hand_type"""
	print '\n--------------- start EvalFive.save_tables'
	table_dir = 'Tables'
	if not os.path.exists(table_dir):
		os.makedirs(table_dir)
		print 'directory {} created'.format(table_dir)
	save_vector_to_csv_as_sparse(flush_rank, table_dir, 'sparse_flush_rank_five')
	save_vector_to_csv_as_sparse(face_rank, table_dir, 'sparse_face_rank_five')
	np.savetxt(os.path.join(table_dir, 'hand_faces.txt'), hand_faces, delimiter=',', fmt='%d')
	np.savetxt(os.path.join(table_dir, 'hand_type.txt'), hand_type, delimiter=',', fmt='%s')
	for f in ['sparse_flush_rank_five.csv', 'sparse_face_rank_five.csv', 'hand_faces.txt', 'hand_type.txt']:
		print '{} saved to disk as {}'.format(f[:-4], os.path.join(table_dir, f))



def load_tables():
	"""load all EvalFive tables from disk: flush_rank, face_rank, hand_faces, hand_type"""
	global flush_rank, face_rank, hand_faces, hand_type
	print '\n---------------EvalFive Tables loaded from disk'
	table_dir = 'Tables'
	if os.path.exists(table_dir):
		flush_rank = load_vector_from_sparse_csv(table_dir, 'sparse_flush_rank_five')
		face_rank = load_vector_from_sparse_csv(table_dir, 'sparse_face_rank_five')
		hand_faces = np.loadtxt(os.path.join(table_dir, 'hand_faces.txt'), delimiter=',', dtype=np.int32)
		hand_type = np.loadtxt(os.path.join(table_dir, 'hand_type.txt'), delimiter=',', dtype=np.str)
		for f in ['sparse_flush_rank_five.csv', 'sparse_face_rank_five.csv', 'hand_faces.txt', 'hand_type.txt']:
			print '{} loaded from file {}'.format(f[:-4], os.path.join(table_dir, f))
	else:
		print 'No tables on disk'



def get_five_rank_simple(five_cards):
	"""five_card is np.array of 5 distincts integers from 0 to 51, each one card of the deck"""
	c1, c2, c3, c4, c5 = five_cards
	hand_rank = -1
	if (keys.CARD_SUIT[c1] == keys.CARD_SUIT[c2] and
				keys.CARD_SUIT[c1] == keys.CARD_SUIT[c3] and
				keys.CARD_SUIT[c1] == keys.CARD_SUIT[c4] and
				keys.CARD_SUIT[c1] == keys.CARD_SUIT[c5]):
		hand_key = keys.FLUSH_KEY_FIVE[keys.CARD_FACE[c1]]+ \
				keys.FLUSH_KEY_FIVE[keys.CARD_FACE[c2]]+ \
				keys.FLUSH_KEY_FIVE[keys.CARD_FACE[c3]]+ \
				keys.FLUSH_KEY_FIVE[keys.CARD_FACE[c4]]+ \
				keys.FLUSH_KEY_FIVE[keys.CARD_FACE[c5]]
		hand_rank = flush_rank[hand_key]
	else:
		hand_key = keys.FACE_KEY_FIVE[keys.CARD_FACE[c1]]+ \
				keys.FACE_KEY_FIVE[keys.CARD_FACE[c2]]+ \
				keys.FACE_KEY_FIVE[keys.CARD_FACE[c3]]+ \
				keys.FACE_KEY_FIVE[keys.CARD_FACE[c4]]+ \
				keys.FACE_KEY_FIVE[keys.CARD_FACE[c5]]
		hand_rank = face_rank[hand_key]
	return hand_rank



def get_five_rank_full(array_five_cards, flush_key_five, face_key_five, card_suit, card_face, flush_rank, face_rank):
	"""array_five_cards is an array of Nx5 distincts integers from 0 to 51, each one card of the deck"""
	N = array_five_cards.shape[0]
	hand_rank = np.zeros(N, dtype=np.int32)
	for i in xrange(N):
		hand_rank[i] = -1
		c1 = array_five_cards[i, 0]
		c2 = array_five_cards[i, 1]
		c3 = array_five_cards[i, 2]
		c4 = array_five_cards[i, 3]
		c5 = array_five_cards[i, 4]
		if ((card_suit[c1] == card_suit[c2]) and
					(card_suit[c1] == card_suit[c3]) and
					(card_suit[c1] == card_suit[c4]) and
					(card_suit[c1] == card_suit[c5])):
			hand_key = flush_key_five[card_face[c1]]+ \
					flush_key_five[card_face[c2]]+ \
					flush_key_five[card_face[c3]]+ \
					flush_key_five[card_face[c4]]+ \
					flush_key_five[card_face[c5]]
			hand_rank[i]= flush_rank[hand_key]
		else:
			hand_key = face_key_five[card_face[c1]]+ \
					face_key_five[card_face[c2]]+ \
					face_key_five[card_face[c3]]+ \
					face_key_five[card_face[c4]]+ \
					face_key_five[card_face[c5]]
			hand_rank[i]= face_rank[hand_key]
	return hand_rank

get_five_rank_fast = jit(int32[:](int32[:, :], int32[:], int32[:], int32[:], int32[:], int32[:], int32[:]))(get_five_rank_full)



def get_seven_rank_simple(seven_cards):
	"""seven_cards is an array of 7 distincts integers from 0 to 51, each one card of the deck"""
	five_cards = np.zeros(5)
	bestHandRank = -1
	for c1 in range(0, 7):
		for c2 in range(0, c1):
			k = 0
			for i in range(0, 7):
				# exclude cards c1 and c2
				if (not (i == c1) and not (i == c2)):
					five_cards[k] = seven_cards[i]
					k += 1
			hand_rank = get_five_rank_simple(five_cards)
			if hand_rank > bestHandRank:
				bestHandRank = hand_rank
	return bestHandRank



def get_seven_rank_full_inline(array_seven_cards, flush_key_five, face_key_five, card_suit, card_face, flush_rank, face_rank):
	"""
	array_seven_cards is an array of Nx7 distincts integers from 0 to 51, each one card of the deck
	"""
	N = array_seven_cards.shape[0]
	bestHandRank = np.zeros(N, dtype=np.int32)
	five_cards = np.zeros([1, 5], dtype=np.int32)
	for q in xrange(N):
		bestHandRank[q] = -1
		for c1 in range(0, 7):
			for c2 in range(0, c1):
				k = 0
				for i in range(0, 7):
					# exclude cards c1 and c2
					if (not(i == c1) and not(i == c2)):
						five_cards[0, k] = array_seven_cards[q, i]
						k += 1

				# hand_rank calculation inlined - start
				sc1 = five_cards[0, 0]
				sc2 = five_cards[0, 1]
				sc3 = five_cards[0, 2]
				sc4 = five_cards[0, 3]
				sc5 = five_cards[0, 4]
				if ((card_suit[sc1] == card_suit[sc2]) and
							(card_suit[sc1] == card_suit[sc3]) and
							(card_suit[sc1] == card_suit[sc4]) and
							(card_suit[sc1] == card_suit[sc5])):
					hand_key = flush_key_five[card_face[sc1]]+ \
							flush_key_five[card_face[sc2]]+ \
							flush_key_five[card_face[sc3]]+ \
							flush_key_five[card_face[sc4]]+ \
							flush_key_five[card_face[sc5]]
					hand_rank= flush_rank[hand_key]
				else:
					hand_key = face_key_five[card_face[sc1]]+ \
							face_key_five[card_face[sc2]]+ \
							face_key_five[card_face[sc3]]+ \
							face_key_five[card_face[sc4]]+ \
							face_key_five[card_face[sc5]]
					hand_rank= face_rank[hand_key]
				# hand_rank calculation inlined - end

				if hand_rank > bestHandRank[q]:
					bestHandRank[q] = hand_rank
	return bestHandRank

get_seven_rank_fast = jit(int32[:](int32[:, :], int32[:], int32[:], int32[:], int32[:], int32[:], int32[:]))(get_seven_rank_full_inline)



def test():
	"""display all EvalFive tables, run getFiveRank_ getSevenRank_ evaluators on sample hands """
	global five_cards, array_five_cards, seven_cards, array_seven_cards, hr1, hr2, hr3, hr4, hr5, h6, sparse_flush_rank, sparse_face_rank
	print "\n--------------- start EvalFive.test"

	print '-------- EvalFive tables'
	sparse_flush_rank = sparse.csc_matrix(flush_rank)
	print 'flush_rank = \n{}\n{}\nnb of nonzero elements = {}'.format(sparse_flush_rank.nonzero()[1], sparse_flush_rank.data, sparse_flush_rank.nonzero()[1].size)
	sparse_face_rank = sparse.csc_matrix(face_rank)
	print 'face_rank = \n{}\n{}\nnb of nonzero elements = {}'.format(sparse_face_rank.nonzero()[1], sparse_face_rank.data, sparse_flush_rank.nonzero()[1].size)

	print '-------- EvalFive getFiveRank_ getSevenRank_ evaluators sample runs'
	np.random.seed(99)
	array_five_cards = np.array([np.random.choice(keys.DECK_SIZE, 5, replace=False) for k in xrange(10)])
	print 'array_five_cards=\n{}'.format(array_five_cards)
	five_cards = array_five_cards[0]
	print 'five_cards={}'.format(five_cards)
	array_seven_cards = np.array([np.random.choice(keys.DECK_SIZE, 7, replace=False) for k in xrange(10)])
	print 'array_seven_cards={}\n'.format(array_seven_cards)
	seven_cards = array_seven_cards[0]
	print 'seven_cards={}'.format(seven_cards)

	hr1 = get_five_rank_simple(five_cards)
	print '\nget_five_rank_simple(five_cards)={}'.format(hr1)

	hr2 = get_five_rank_full(array_five_cards, keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, flush_rank, face_rank)
	print 'get_five_rank_full(array_five_cards)={}'.format(hr2)

	hr3 = get_five_rank_fast(array_five_cards, keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, flush_rank, face_rank)
	print 'get_five_rank_fast(array_five_cards)={}'.format(hr3)

	hr4 = get_seven_rank_simple(seven_cards)
	print '\nget_seven_rank_simple(seven_cards)={}'.format(hr4)

	hr5 = get_seven_rank_full_inline(array_seven_cards, keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, flush_rank, face_rank)
	print 'get_seven_rank_full_inline(array_seven_cards)={}'.format(hr5)

	hr6 = get_seven_rank_fast(array_seven_cards, keys.FLUSH_KEY_FIVE, keys.FACE_KEY_FIVE, keys.CARD_SUIT, keys.CARD_FACE, flush_rank, face_rank)
	print 'get_seven_rank_fast(array_seven_cards)={}'.format(hr6)

	print "--------------- end EvalFive.test"




# ------------------------ main
if __name__ == '__main__':
	compute_tables()
	save_tables()
	test()

else:
	load_tables()
	# test()







