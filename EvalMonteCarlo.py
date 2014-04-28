
from __future__ import division

import os
import numpy as np
import pandas as pd
import random
import cPickle, gzip
from numba import jit, int32, uint32
from timeit import default_timer as timer

import EvalKeys as keys
import EvalSeven
from EvalAnalysis import all_preflop_hands, hand_str_to_no


def pickle(fname, obj):
	# compresslevel from 0 to 9, 9 is default, slowest, most compressed
	cPickle.dump(obj=obj, file=gzip.open(fname, "wb", compresslevel=0), protocol=cPickle.HIGHEST_PROTOCOL)


def unpickle(fname):
	return cPickle.load(gzip.open(fname, "rb"))


def rnd_games_slow(G, P, C, seed):
	np.random.seed(seed)
	return np.array([random.sample(xrange(C), P) for _ in xrange(G)], dtype=np.int32)


def rnd_games_from_rnd(G, P, rnd):
	"returns G random games of P cards (without replacement) from rnd=np.random.randint() array"
	# N = rnd.size
	games = np.zeros([G, P], dtype=np.int32)

	co = 0
	s = 0
	for g in xrange(G):
		# print 'g={}'.format(g)
		games[g, 0] = rnd[s]
		s += 1
		for p in xrange(1, P):
			overlap = 1
			while overlap:
				games[g, p] = rnd[s]
				s += 1
				# print '\tgames[{}, {}]={}'.format(g, p, games[g, p])
				overlap = 0
				i = 0
				while ((i<p) and (not overlap)):
					# print '\t\tgames[{}, {}]={}'.format(g, i, games[g, i])
					if (games[g, p]==games[g, i]):
						# print '\t\t\toverlap !'
						overlap=1
						co += 1
					i += 1
		# print 'games[{}, :]={}'.format(g, games[g, :])
	# print 'G*P={}'.format(G*P)
	# print 'co={}'.format(co)
	# print 'co/(G*P)={:.4f}'.format(1.0*co/(G*P))
	return games

rnd_games_from_rnd_fast = jit(int32[:, :](int32, int32, int32[:]), target='cpu')(rnd_games_from_rnd)


def rnd_games(G, P, C, N, seed):
	np.random.seed(seed)
	rnd = np.random.randint(C, size=N)
	return rnd_games_from_rnd_fast(G, P, rnd)



def mc_block(hand, p, rnd, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit):
	"""returns array [equity win, equity tie] for hand and p opponents"""

	G = rnd.shape[0]
	deck = np.zeros([50], dtype=np.int32)
	player = np.zeros([2*(p+1)], dtype=np.int32)
	hand_rank = np.zeros([p+1], dtype=np.int32)
	eq_w = 0.0
	eq_t = 0.0
	eq_agg = np.zeros([2], dtype=np.float32)

	pc1 = hand[0]
	pc2 = hand[1]

	# build deck of other cards
	k = 0
	for c in xrange(52):
		if ((c!=pc1) and (c!=pc2)):
			deck[k] = c
			k += 1

	# go through all random games
	for g in xrange(G):

	# set up table card for hand evaluator
		c3 = deck[rnd[g, 2*p]]
		c4 = deck[rnd[g, 2*p+1]]
		c5 = deck[rnd[g, 2*p+2]]
		c6 = deck[rnd[g, 2*p+3]]
		c7 = deck[rnd[g, 2*p+4]]

		# build player cards for 1 player+p opponents
		player[0] = pc1
		player[1] = pc2
		k = 0
		for k in xrange(p):
			player[2+2*k] = deck[rnd[g, 2*k]]
			player[2+2*k+1] = deck[rnd[g, 2*k+1]]

		# set up player card for hand evaluator
		for u in xrange(p+1):
			c1 = player[2*u]
			c2 = player[2*u+1]

			# hand evaluator inlined - start
			hand_key = card_face_key[c1]+card_face_key[c2]+card_face_key[c3]+card_face_key[c4]+card_face_key[c5]+card_face_key[c6]+card_face_key[c7]
			hand_suit_key = hand_key & suit_mask
			hand_suit = flush_suit[hand_suit_key]
			if (hand_suit == -1):
				hand_face_key = hand_key >> suit_bit_shift
				hand_rank[u] = face_rank[hand_face_key]
			else:
				hand_flush_key = (card_flush_key[c1]*(card_suit[c1]==hand_suit)+
					card_flush_key[c2]*(card_suit[c2]==hand_suit)+
					card_flush_key[c3]*(card_suit[c3]==hand_suit)+
					card_flush_key[c4]*(card_suit[c4]==hand_suit)+
					card_flush_key[c5]*(card_suit[c5]==hand_suit)+
					card_flush_key[c6]*(card_suit[c6]==hand_suit)+
					card_flush_key[c7]*(card_suit[c7]==hand_suit))
				hand_rank[u] = flush_rank[hand_flush_key]
			# hand evaluator inlined - end

		# compute equity_win and equity_tie
		i = 1
		nb_best_hand = 1
		while ((i<p+1) and (nb_best_hand>0)):
			if (hand_rank[0]<hand_rank[i]):
				nb_best_hand = 0
			elif (hand_rank[0]==hand_rank[i]):
				nb_best_hand += 1
			i += 1
		if ((i==p+1) and (nb_best_hand>0)):
			if (nb_best_hand==1):
				eq_w += 1
			else:
				eq_t += 1.0/nb_best_hand

	# normalize eq_w_agg and eq_t_agg
	eq_agg[0] = eq_w/G
	eq_agg[1] = eq_t/G

	return eq_agg

mc_block_fast = jit(int32[:](int32[:], int32, int32[:, :], int32[:], uint32[:], int32[:], int32, int32, int32[:], int32[:], int32[:]))(mc_block)



def mc_block_all(hands, P, rnd, card_flush_key, card_face_key, card_suit, suit_mask, suit_bit_shift, flush_rank, face_rank, flush_suit):
	"""returns array [nb_hands x nb_opponents (from 1 to P) x 2] containing for each hand/nb_opponents [equity win, equity tie]"""

	H = hands.shape[0]
	G = rnd.shape[0]
	deck = np.zeros([50], dtype=np.int32)
	player = np.zeros([2*(P+1)], dtype=np.int32)
	hand_rank = np.zeros([P+1], dtype=np.int32)
	max_rank = np.zeros([P], dtype=np.int32)
	max_reached = np.zeros([P, P+1], dtype=np.int32)
	eq_w = np.zeros([G, P], dtype=np.float32)
	eq_t = np.zeros([G, P], dtype=np.float32)
	eq_agg = np.zeros([H, P, 2], dtype=np.float32)


	# go through all different hands
	for h in xrange(H):
		pc1 = hands[h, 0]
		pc2 = hands[h ,1]

		# build deck of other cards
		k = 0
		for c in xrange(52):
			if ((c!=pc1) and (c!=pc2)):
				deck[k] = c
				k += 1

		# go through all random games
		for g in xrange(G):

		# set up table card for hand evaluator
			c3 = deck[rnd[g, 2*P]]
			c4 = deck[rnd[g, 2*P+1]]
			c5 = deck[rnd[g, 2*P+2]]
			c6 = deck[rnd[g, 2*P+3]]
			c7 = deck[rnd[g, 2*P+4]]

			# build player cards for 1 player+P opponents
			player[0] = pc1
			player[1] = pc2
			k = 0
			for k in xrange(P):
				player[2+2*k] = deck[rnd[g, 2*k]]
				player[2+2*k+1] = deck[rnd[g, 2*k+1]]

			# set up player card for hand evaluator
			for u in xrange(P+1):
				c1 = player[2*u]
				c2 = player[2*u+1]

				# hand evaluator inlined - start
				hand_key = card_face_key[c1]+card_face_key[c2]+card_face_key[c3]+card_face_key[c4]+card_face_key[c5]+card_face_key[c6]+card_face_key[c7]
				hand_suit_key = hand_key & suit_mask
				hand_suit = flush_suit[hand_suit_key]
				if (hand_suit == -1):
					hand_face_key = hand_key >> suit_bit_shift
					hand_rank[u] = face_rank[hand_face_key]
				else:
					hand_flush_key = (card_flush_key[c1]*(card_suit[c1]==hand_suit)+
						card_flush_key[c2]*(card_suit[c2]==hand_suit)+
						card_flush_key[c3]*(card_suit[c3]==hand_suit)+
						card_flush_key[c4]*(card_suit[c4]==hand_suit)+
						card_flush_key[c5]*(card_suit[c5]==hand_suit)+
						card_flush_key[c6]*(card_suit[c6]==hand_suit)+
						card_flush_key[c7]*(card_suit[c7]==hand_suit))
					hand_rank[u] = flush_rank[hand_flush_key]
				# hand evaluator inlined - end

			# build max_rank table
			for p in xrange(P):
				max_rank[p] = max(hand_rank[0], hand_rank[1])
				for u in xrange(2, p+2):
					max_rank[p] = max(max_rank[p], hand_rank[u])

			# compute boolean array of hands with max_rank
			for p in xrange(P):
				for u in xrange(p+2):
					max_reached[p, u] = 0
					if (hand_rank[u]==max_rank[p]):
						max_reached[p, u] = 1

			# compute equity_win and equity_tie for each number of opponents from 1 to P
			for p in xrange(P):
				if (max_reached[p, 0]==0):
					eq_w[g, p] = 0
					eq_t[g, p] = 0
				else:
					s = 1
					for u in xrange(1, p+2):
						s += max_reached[p, u]
					if (s==1):
							eq_w[g, p] = 1
							eq_t[g, p] = 0
					else:
						eq_w[g, p] = 0
						eq_t[g, p] = 1.0/s

			# accumulate equity wins and ties in _agg
			for p in xrange(P):
				eq_agg[h, p, 0] += eq_w[g, p]
				eq_agg[h, p, 1] += eq_t[g, p]


		# normalize eq_w_agg and eq_t_agg
		for p in xrange(P):
			eq_agg[h, p, 0] /= G
			eq_agg[h, p, 1] /= G

	return eq_agg

mc_block_all_fast = jit(int32[:, :, :](int32[:, :], int32, int32[:, :], int32[:], uint32[:], int32[:], int32, int32, int32[:], int32[:], int32[:]))(mc_block_all)



def mc_simul_one_hand(hand_str, nb_opp):
	"""compute G games MC simulations for one hand (as a string eg 'AJo') given a nb_opp number of oppenents (from 1 to 9)"""
	# global hands, H, G, B, P, rnd, equity_arr, equity_all, equity_win, equity_tie, df, equity_mc_cvg

	hand = hand_str_to_no(hand_str)
	G = int(5e5)
	equity_arr = np.zeros([2], dtype=np.float32)

	print '\n---------------- Monte Carlo simulation start'
	print 'hand_str={}'.format(hand_str)
	print 'hand={}'.format(hand)
	print 'G={}'.format(G)

	t0 = timer()

	# random games generation
	C = 50-2
	P = 2*nb_opp+5
	N = int(1.5*P*G)
	seed = 0	# None
	rnd = rnd_games(G, P, C, N, seed)
	# rnd = rnd_games_slow(G, P, C, seed)

	t1 = timer()
	print 'RNG time = \t{:.6f} s'.format(t1-t0)

	# hand ranking
	equity_arr = mc_block_fast(hand, nb_opp, rnd, keys.CARD_FLUSH_KEY,
												keys.CARD_FACE_KEY,
												keys.CARD_SUIT,
												keys.SUIT_MASK,
												keys.SUIT_BIT_SHIFT,
												EvalSeven.flush_rank,
												EvalSeven.face_rank,
												EvalSeven.flush_suit)

	t2 = timer()
	print 'equity time = \t{:.6f} s'.format(t2-t1)
	print 'total time = \t{:.6f} s'.format(t2-t0)
	print equity_arr
	print '\n---------------- Monte Carlo simulation end'

	return equity_arr



def mc_simul_all_hands():
	"""compute and store MC simulations for B blocks of G games for all 169 preflop hands"""
	global hands, H, G, B, P, rnd, equity_arr, equity_all, equity_win, equity_tie, df, equity_mc_cvg

	hands = np.array(map(hand_str_to_no, all_preflop_hands), dtype=np.int32)
	H = hands.shape[0]
	G = int(2e5)			# 1e6		2e5
	B = int(500)			# 300		500
	nb_opp = 9
	equity_arr = np.zeros([B, H, nb_opp, 2], dtype=np.float32)

	print '\n---------------- Monte Carlo simulation start'
	print 'nb of hands = {}'.format(H)
	print 'nb of random games per block = {}'.format(G)
	print 'nb of blocks = {}\n'.format(B)


	t_init = timer()
	for b in xrange(B):
		print 'block #{}'.format(b)
		t0 = timer()

		# random games generation
		C = 50-2
		P = 2*nb_opp+5
		N = int(2*P*G)
		seed = 0	# None
		rnd = rnd_games(G, P, C, N, seed)
		# rnd = rnd_games_slow(G, P, C)

		t1 = timer()
		print '\tRNG time = \t{:.6f} s'.format(t1-t0)

		# hand ranking
		equity_arr[b, :, :, :] = mc_block_all_fast(hands, nb_opp, rnd, keys.CARD_FLUSH_KEY,
													keys.CARD_FACE_KEY,
													keys.CARD_SUIT,
													keys.SUIT_MASK,
													keys.SUIT_BIT_SHIFT,
													EvalSeven.flush_rank,
													EvalSeven.face_rank,
													EvalSeven.flush_suit)

		t2 = timer()
		print '\tequity time = \t{:.6f} s'.format(t2-t1)
		print '\tblock time = \t{:.6f} s'.format(t2-t0)

	print '\n---------------- Monte Carlo simulation end'
	print 'full run time = {:.6f} s'.format(t2-t_init)
	pickle(os.path.join('Tables', 'equity_array.pk'), equity_arr)


	equity_all = np.mean(equity_arr, axis=0)
	equity_win = equity_all[:, :, 0]
	equity_tie = equity_all[:, :, 1]
	df = pd.DataFrame(data=np.concatenate((equity_win, equity_tie), axis=1),
						index=all_preflop_hands,
						columns=[str(i)+'_win' for i in range(1, nb_opp+1)]+[str(i)+'_tie' for i in range(1, nb_opp+1)])
	df.to_pickle(os.path.join('Tables', 'df_equity_montecarlo.pd'))
	df.to_csv(os.path.join('Tables', 'df_equity_montecarlo.csv'))

	equity_mc_cvg = np.zeros_like(equity_arr)
	for k in xrange(B):
		equity_mc_cvg[k, :, :, :] = np.mean(equity_arr[:k+1, :, :, :], axis=0)
	pickle(os.path.join('Tables', 'equity_mc_cvg.pk'), equity_mc_cvg)

	# df_equity_montecarlo = pd.read_pickle(os.path.join('Tables', 'df_equity_montecarlo.pd'))
	# equity_arr_1 = unpickle(os.path.join('Tables', 'test.pk'))
	# equity_mc_cvg_1 = unpickle(os.path.join('Tables', 'equity_mc_cvg.pk'))



def test_rnd(nb_opp):
	global G, P, C, seed, rnd, games, games_slow

	G = int(1e6)
	P = 5+2*nb_opp
	C = 50
	N = int(2*P*G)
	seed = 0

	t0 = timer()

	games = rnd_games(G, P, C, N, seed)

	t1 = timer()

	# games_slow = rnd_games_slow(G, P, C, seed)

	t2 = timer()
	print 'run time = {:.6f} s'.format(t1-t0)
	print 'run time = {:.6f} s'.format(t2-t1)

	print '\ngames.shape={}'.format(games.shape)
	analyze(games, C)
	# print '\ngames_slow.shape={}'.format(games_slow.shape)
	# analyze(games_slow, C)


def analyze(games, C):
	print 'card frequency'
	freq = np.zeros([C], np.float32)
	for k in xrange(C):
		freq[k] = 1.0*np.sum(games==k)/games.size
		print '\tfreq[{}]={:.6f}'.format(k, freq[k])
	print '\tsum={:.6f}'.format(freq.sum())






if __name__ == '__main__':
	print '\n----------------EvalMonteCarlo start'
	# eqty = mc_simul_one_hand('AJs', 9)
	mc_simul_all_hands()
	# test_rnd(9)



