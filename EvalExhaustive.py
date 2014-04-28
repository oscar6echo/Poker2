
from __future__ import division

import os
import numpy as np
import random
from numba import jit, int32, uint32
from timeit import default_timer as timer

import EvalKeys as keys
import EvalSeven

np.set_printoptions(linewidth=300)
np.set_printoptions(suppress=True)


def rank(card, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit):
	"""return hand rank for 7 card hand"""
	c1 = card[0]
	c2 = card[1]
	c3 = card[2]
	c4 = card[3]
	c5 = card[4]
	c6 = card[5]
	c7 = card[6]
	hand_key = card_face_key[c1]+card_face_key[c2]+card_face_key[c3]+card_face_key[c4]+card_face_key[c5]+card_face_key[c6]+card_face_key[c7]
	hand_suit_key = hand_key & suit_mask
	hand_suit = flush_suit[hand_suit_key]
	if (hand_suit == -1):
		hand_face_key = hand_key >> suit_bit_shift
		hand_rank = face_rank[hand_face_key]
	else:
		hand_flush_key = (card_flush_key[c1]*(card_suit[c1]==hand_suit)+
			card_flush_key[c2]*(card_suit[c2]==hand_suit)+
			card_flush_key[c3]*(card_suit[c3]==hand_suit)+
			card_flush_key[c4]*(card_suit[c4]==hand_suit)+
			card_flush_key[c5]*(card_suit[c5]==hand_suit)+
			card_flush_key[c6]*(card_suit[c6]==hand_suit)+
			card_flush_key[c7]*(card_suit[c7]==hand_suit))
		hand_rank = flush_rank[hand_flush_key]
	return hand_rank


def exhaustive_block(player_card, table_card, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit):
	"""returns array nb_player x [equity win, equity tie] for all players"""

	p = player_card.shape[0]
	t = table_card.size
	known_cards = np.ones([2*p+t], dtype=np.int32)
	deck = np.zeros([52-(2*p+t)], dtype=np.int32)
	card = np.zeros([7], dtype=np.int32)
	hand_rank = np.zeros([p], dtype=np.int32)
	eq_w = np.zeros([p], dtype=np.float32)
	eq_t = np.zeros([p], dtype=np.float32)
	eq_agg = np.zeros([p, 2], dtype=np.float32)
	n = 0

	# build known cards
	for k in xrange(p):
		known_cards[2*k] = player_card[k, 0]
		known_cards[2*k+1] = player_card[k, 1]
	for k in xrange(t):
		known_cards[2*p+k] = table_card[k]

	# build deck of cards in stack
	k = 0
	for c in xrange(52):
		cand = 1
		idx = 0
		while ((idx<k) and (cand)):
			if (c==known_cards[idx]):
				cand = 0
			idx += 1
		if (cand==1):
			deck[k] = c
			k += 1

	# go through all games exhaustively
	# no table cards
	if (t==0):
		for idx1 in xrange(52-(2*p+t)):
			for idx2 in xrange(idx1):
				for idx3 in xrange(idx2):
					for idx4 in xrange(idx3):
						for idx5 in xrange(idx4):
							n += 1

							# hand ranking all players
							for h in xrange(p):
								card[0] = player_card[h, 0]
								card[1] = player_card[h, 1]
								card[2] = deck[idx1]
								card[3] = deck[idx2]
								card[4] = deck[idx3]
								card[5] = deck[idx4]
								card[6] = deck[idx5]
								hand_rank[h] = rank_fast(card, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit)

							# compute max_rank and nb_best_hand
							max_rank = hand_rank[0]
							nb_best_hand = 1
							for h in xrange(1, p+1):
								if (hand_rank[h]>max_rank):
									max_rank = hand_rank[h]
									nb_best_hand = 1
								elif (hand_rank[h]==max_rank):
									nb_best_hand += 1

							# compute equity_win and equity_tie
							for h in xrange(p):
								if (hand_rank[h]==max_rank):
									if (nb_best_hand==1):
										eq_w[h] += 1
									else:
										eq_t[h] += 1.0/nb_best_hand

	# 3 table cards
	elif (t==3):
		for idx4 in xrange(52-(2*p+t)):
			for idx5 in xrange(idx4):
				n += 1

				# hand ranking all players
				for h in xrange(p):
					card[0] = player_card[h, 0]
					card[1] = player_card[h, 1]
					card[2] = table_card[0]
					card[3] = table_card[1]
					card[4] = table_card[2]
					card[5] = deck[idx4]
					card[6] = deck[idx5]
					hand_rank[h] = rank_fast(card, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit)

				# compute max_rank and nb_best_hand
				max_rank = hand_rank[0]
				nb_best_hand = 1
				for h in xrange(1, p+1):
					if (hand_rank[h]>max_rank):
						max_rank = hand_rank[h]
						nb_best_hand = 1
					elif (hand_rank[h]==max_rank):
						nb_best_hand += 1

				# compute equity_win and equity_tie
				for h in xrange(p):
					if (hand_rank[h]==max_rank):
						if (nb_best_hand==1):
							eq_w[h] += 1
						else:
							eq_t[h] += 1.0/nb_best_hand

	# 4 table cards
	elif (t==4):
		for idx5 in xrange(52-(2*p+t)):
			n += 1

			# hand ranking all players
			for h in xrange(p):
				card[0] = player_card[h, 0]
				card[1] = player_card[h, 1]
				card[2] = table_card[0]
				card[3] = table_card[1]
				card[4] = table_card[2]
				card[5] = table_card[3]
				card[6] = deck[idx5]
				hand_rank[h] = rank_fast(card, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit)

			# compute max_rank and nb_best_hand
			max_rank = hand_rank[0]
			nb_best_hand = 1
			for h in xrange(1, p+1):
				if (hand_rank[h]>max_rank):
					max_rank = hand_rank[h]
					nb_best_hand = 1
				elif (hand_rank[h]==max_rank):
					nb_best_hand += 1

			# compute equity_win and equity_tie
			for h in xrange(p):
				if (hand_rank[h]==max_rank):
					if (nb_best_hand==1):
						eq_w[h] += 1
					else:
						eq_t[h] += 1.0/nb_best_hand

	# 5 table cards
	elif (t==5):
		n += 1

		# hand ranking all players
		for h in xrange(p):
			card[0] = player_card[h, 0]
			card[1] = player_card[h, 1]
			card[2] = table_card[0]
			card[3] = table_card[1]
			card[4] = table_card[2]
			card[5] = table_card[3]
			card[6] = table_card[4]
			hand_rank[h] = rank_fast(card, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit)

		# compute max_rank and nb_best_hand
		max_rank = hand_rank[0]
		nb_best_hand = 1
		for h in xrange(1, p+1):
			if (hand_rank[h]>max_rank):
				max_rank = hand_rank[h]
				nb_best_hand = 1
			elif (hand_rank[h]==max_rank):
				nb_best_hand += 1

		# compute equity_win and equity_tie
		for h in xrange(p):
			if (hand_rank[h]==max_rank):
				if (nb_best_hand==1):
					eq_w[h] += 1
				else:
					eq_t[h] += 1.0/nb_best_hand

	# impossible : error
	else:
		return -1

	# normalize eq_w_agg and eq_t_agg
	for h in xrange(p):
		eq_agg[h, 0] = eq_w[h]/n
		eq_agg[h, 1] = eq_t[h]/n

	return eq_agg



rank_fast = jit(int32(int32[:], int32[:], uint32[:], int32[:], int32, int32, int32[:], int32[:], int32[:]))(rank)
exhaustive_block_fast = jit(int32[:](int32[:, :], int32[:], int32[:], uint32[:], int32[:], int32, int32, int32[:], int32[:], int32[:]))(exhaustive_block)



def exhaustive_eval(player_card, table_card):
	"""compute all possible games given the player/table cards (as a numbers from 0 to 51) and return equity win/tie for each player"""

	p = player_card.shape[0]
	equity_arr = np.zeros([p, 2], dtype=np.float32)

	print '\n---------------- Exhaustive eval start'
	print 'player_card=\n{}'.format(player_card)
	print 'table_card=\n{}'.format(table_card)
	print 'p={}'.format(p)

	t0 = timer()

	equity_arr = exhaustive_block_fast(player_card, table_card,
												keys.CARD_FLUSH_KEY,
												keys.CARD_FACE_KEY,
												keys.CARD_SUIT,
												keys.SUIT_MASK,
												keys.SUIT_BIT_SHIFT,
												EvalSeven.flush_rank,
												EvalSeven.face_rank,
												EvalSeven.flush_suit)

	t1 = timer()
	print 'run time = \t{:.6f} s'.format(t1-t0)
	print equity_arr
	print '\n---------------- Exhaustive eval end'

	return equity_arr




if __name__ == '__main__':
	p = 8		# 2 to 10
	t = 3		# 0, 3, 4, 5
	rr = np.array(random.sample(xrange(52), 2*p+t), dtype=np.int32)
	print rr
	player_card = rr[:(2*p)].reshape(p, 2)
	table_card = rr[(2*p):]

	eqty = exhaustive_eval(player_card, table_card)
	print eqty.sum()


