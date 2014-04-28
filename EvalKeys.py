
"""
Precomputed keys used by EvalFive and EvalSeven
"""
import numpy as np
np.set_printoptions(linewidth=250)

NB_FACE = 13
NB_SUIT = 4
DECK_SIZE = NB_SUIT*NB_FACE
SUIT_MASK = 511
SUIT_BIT_SHIFT = 9

# spades, hearts, diamonds, clubs
SUIT_KEY = np.array([0, 1, 29, 37], dtype=np.int32)

# faces 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A
FLUSH_KEY_FIVE = np.array([0, 1, 2, 4, 8, 16, 32, 56, 104, 192, 352, 672, 1288], dtype=np.int32)
FACE_KEY_FIVE = np.array([0, 1, 5, 22, 94, 312, 992, 2422, 5624, 12522, 19998, 43258, 79415], dtype=np.int32)
FLUSH_KEY_SEVEN = np.array([1, 2, 4, 8, 16, 32, 64, 128, 240, 464, 896, 1728, 3328], dtype=np.int32)
FACE_KEY_SEVEN = np.array([0, 1, 5, 22, 98, 453, 2031, 8698, 22854, 83661, 262349, 636345, 1479181], dtype=np.int32)

MAX_FLUSH_KEY_FIVE = sum(FLUSH_KEY_FIVE[-5:])
MAX_FACE_KEY_FIVE = FACE_KEY_FIVE[-1]*4 + FACE_KEY_FIVE[-2]*1
MAX_FLUSH_KEY_SEVEN = sum(FLUSH_KEY_SEVEN[-7:])
MAX_FACE_KEY_SEVEN = FACE_KEY_SEVEN[-1]*4 + FACE_KEY_SEVEN[-2]*3
MAX_SUIT_KEY = SUIT_KEY[-1]*7

CARD_FACE = np.zeros(DECK_SIZE, dtype=np.int32)
CARD_SUIT = np.zeros(DECK_SIZE, dtype=np.int32)
for f in range(NB_FACE):
	for s in range(NB_SUIT):
		CARD_FACE[NB_SUIT*f+s] = f
		CARD_SUIT[NB_SUIT*f+s] = s

CARD_FLUSH_KEY = np.zeros(DECK_SIZE, dtype=np.int32)
CARD_FACE_KEY = np.zeros(DECK_SIZE, dtype=np.uint32)	# uint32 to avoid overflow in EvalSeven.getSevenRank_ first sum
for f in range(NB_FACE):
	for s in range(NB_SUIT):
		CARD_FACE_KEY[NB_SUIT*f+s] = (FACE_KEY_SEVEN[f]<<SUIT_BIT_SHIFT) + SUIT_KEY[s]
		CARD_FLUSH_KEY[NB_SUIT*f+s] = FLUSH_KEY_SEVEN[f]


def show_keys():
	print '\n--------------- EvalKeys'
	print 'NB_FACE = {}'.format(NB_FACE)
	print 'NB_SUIT = {}'.format(NB_SUIT)
	print 'DECK_SIZE = {}'.format(DECK_SIZE)
	print 'SUIT_MASK = {}'.format(SUIT_MASK)
	print 'SUIT_BIT_SHIFT = {}'.format(SUIT_BIT_SHIFT)
	print 'SUIT_KEY = \n{}'.format(SUIT_KEY)
	print 'FLUSH_KEY_FIVE = \n{}'.format(FLUSH_KEY_FIVE)
	print 'FACE_KEY_FIVE = \n{}'.format(FACE_KEY_FIVE)
	print 'FLUSH_KEY_SEVEN = \n{}'.format(FLUSH_KEY_SEVEN)
	print 'FACE_KEY_SEVEN = \n{}'.format(FACE_KEY_SEVEN)
	print 'CARD_SUIT = \n{}'.format(CARD_SUIT)
	print 'CARD_FACE = \n{}'.format(CARD_FACE)
	print 'CARD_FLUSH_KEY = \n{}'.format(CARD_FLUSH_KEY)
	print 'CARD_FACE_KEY = \n{}'.format(CARD_FACE_KEY)

	print '\nFor any of the 52 cards'
	print 'suit key <= {0}'.format(MAX_SUIT_KEY)
	print 'flush key five <= {0}'.format(MAX_FLUSH_KEY_FIVE)
	print 'face key five <= {0}'.format(MAX_FACE_KEY_FIVE)
	print 'flush key seven <= {0}'.format(MAX_FLUSH_KEY_SEVEN)
	print 'face key seven <= {0}'.format(MAX_FACE_KEY_SEVEN)
	print 'hand key <= {0}'.format(np.sum(CARD_FACE_KEY[-7:]))
	print 'hand flush key <= {0}'.format(np.sum(CARD_FLUSH_KEY[-7:]))
	print '2^31-1 = {0}'.format(2**31-1)


if __name__ == '__main__':
	show_keys()

