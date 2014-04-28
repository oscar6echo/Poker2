
import numpy as np
from numba import jit, int32			# numba 0.11.1
from timeit import default_timer as timer


# ---------------Key Gen Suit

def gen_suit_keys(bound):
	stored = np.zeros([1000, 4], dtype=np.int32)
	sum_arr = np.zeros(50000, dtype=np.int32)
	key = np.zeros(4, dtype=np.int32)
	idx = 0

	for k1 in xrange(bound+1):
		for k2 in xrange(k1, bound+1):
			for k3 in xrange(k2, bound+1):
				for k4 in xrange(k3, bound+1):
					key[0] = k1
					key[1] = k2
					key[2] = k3
					key[3] = k4

					valid = 1
					c = 0
					for c1 in xrange(0, 4) :
						for c2 in xrange(c1, 4) :
							for c3 in xrange(c2, 4) :
								for c4 in xrange(c3, 4) :
									for c5 in xrange(c4, 4) :
										for c6 in xrange(c5, 4) :
											for c7 in xrange(c6, 4) :
												sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]+key[c6]+key[c7]
												c += 1

					i = 0
					while (valid) & (i< c-1) :
						j = i+1
						while (valid) & (j<c):
							if (sum_arr[i] == sum_arr[j]) :
								valid = 0
							j += 1
						i += 1

					if (valid):
						stored[idx, 0] = key[0]
						stored[idx, 1] = key[1]
						stored[idx, 2] = key[2]
						stored[idx, 3] = key[3]
						idx += 1
	return stored[:idx]

gen_suit_keys_fast = jit(int32[:, :](int32))(gen_suit_keys)

def keygen_suit(nb_key):
	print '\nstart keygen suit'
	t0 = timer()
	keys = gen_suit_keys_fast(nb_key)
	t1 = timer()
	print 'keys=\n{}'.format(keys)
	print 'run time = {:.4f} s'.format(t1-t0)
	return keys



# ---------------Key Gen Flush Five

def gen_flush_five_keys(nb_key):
	key = np.zeros(nb_key, dtype=np.int32)
	key[0] = 0
	key[1] = 1
	key[2] = 2
	key[3] = 4
	key[4] = 8
	key[5] = 16
	key[6] = 32
	sum_arr = np.zeros(50000, dtype=np.int32)

	for i in xrange(7):
		print 'key[{}]={}'.format(i, key[i])

	k=7
	while (k<nb_key):
		t = key[k-1]+1
		valid = 0
		while (not valid) :
			key[k] = t
			valid = 1
			c = 0
			# 5 suited cards
			for c1 in xrange(0, k+1) :
				for c2 in xrange(c1+1, k+1) :
					for c3 in xrange(c2+1, k+1) :
						for c4 in xrange(c3+1, k+1) :
							for c5 in xrange(c4+1, k+1) :
								sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]
								c += 1
			i = 0
			while ((valid) & (i<c-1)):
				j = i+1
				while (valid) & (j<c):
					if (sum_arr[i] == sum_arr[j]):
						valid = 0
						t += 1
					j += 1
				i += 1
		print 'key[{}]={}'.format(k, key[k])
		k += 1
	return key

gen_flush_five_keys_fast = jit(int32[:](int32))(gen_flush_five_keys)

def keygen_flush_five(nb_key):
	print '\nstart keygen flush_five'
	t0 = timer()
	keys = gen_flush_five_keys_fast(nb_key)
	t1 = timer()
	print 'keys=\n{}'.format(keys)
	print 'run time = {:.4f} s'.format(t1-t0)



# ---------------Key Gen Face Five

def gen_face_five_keys(nb_key):
	key = np.zeros(nb_key, dtype=np.int32)
	key[0] = 0
	key[1] = 1
	key[2] = 5
	sum_arr = np.zeros(50000, dtype=np.int32)

	for i in xrange(3):
		print 'key[{}]={}'.format(i, key[i])

	k=3
	while (k<nb_key):
		t = key[k-1]+1
		valid = 0
		while (not valid) :
			key[k] = t
			valid = 1
			c = 0
			for c1 in xrange(0, k+1) :
				for c2 in xrange(c1, k+1) :
					for c3 in xrange(c2, k+1) :
						for c4 in xrange(c3, k+1) :
							for c5 in xrange(c4, k+1) :
								if (c1 != c5) :
									sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]
									c += 1
			i = 0
			while ((valid) & (i<c-1)):
				j = i+1
				while (valid) & (j<c):
					if (sum_arr[i] == sum_arr[j]):
						valid = 0
						t += 1
					j += 1
				i += 1
		print 'key[{}]={}'.format(k, key[k])
		k += 1
	return key

gen_face_five_keys_fast = jit(int32[:](int32))(gen_face_five_keys)

def keygen_face_five(nb_key):
	print '\nstart keygen face_five'
	t0 = timer()
	keys = gen_face_five_keys_fast(nb_key)
	t1 = timer()
	print 'keys=\n{}'.format(keys)
	print 'run time = {:.4f} s'.format(t1-t0)



# ---------------Key Gen Flush Seven

def gen_flush_seven_keys(nb_key):
	key = np.zeros(nb_key, dtype=np.int32)
	key[0] = 1
	key[1] = 2
	key[2] = 4
	key[3] = 8
	key[4] = 16
	key[5] = 32
	key[6] = 64
	key[7] = 128
	sum_arr = np.zeros(50000, dtype=np.int32)

	for i in xrange(8):
		print 'key[{}]={}'.format(i, key[i])

	k=8
	while (k<nb_key):
		t = key[k-1]+1
		valid = 0
		while (not valid) :
			key[k] = t
			valid = 1
			c = 0
			# 7 suited cards
			for c1 in xrange(0, k+1) :
				for c2 in xrange(c1+1, k+1) :
					for c3 in xrange(c2+1, k+1) :
						for c4 in xrange(c3+1, k+1) :
							for c5 in xrange(c4+1, k+1) :
								for c6 in xrange(c5+1, k+1) :
									for c7 in xrange(c6+1, k+1) :
										sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]+key[c6]+key[c7]
										c += 1
			# 6 suited cards
			for c1 in xrange(0, k+1) :
				for c2 in xrange(c1+1, k+1) :
					for c3 in xrange(c2+1, k+1) :
						for c4 in xrange(c3+1, k+1) :
							for c5 in xrange(c4+1, k+1) :
								for c6 in xrange(c5+1, k+1) :
									sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]+key[c6]
									c += 1
			# 5 suited cards
			for c1 in xrange(0, k+1) :
				for c2 in xrange(c1+1, k+1) :
					for c3 in xrange(c2+1, k+1) :
						for c4 in xrange(c3+1, k+1) :
							for c5 in xrange(c4+1, k+1) :
								sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]
								c += 1
			i = 0
			while ((valid) & (i<c-1)):
				j = i+1
				while (valid) & (j<c):
					if (sum_arr[i] == sum_arr[j]):
						valid = 0
						t += 1
					j += 1
				i += 1
		print 'key[{}]={}'.format(k, key[k])
		k += 1
	return key

gen_flush_seven_keys_fast = jit(int32[:](int32))(gen_flush_seven_keys)

def keygen_flush_seven(nb_key):
	print '\nstart keygen flush_seven'
	t0 = timer()
	keys = gen_flush_seven_keys_fast(nb_key)
	t1 = timer()
	print 'keys=\n{}'.format(keys)
	print 'run time = {:.4f} s'.format(t1-t0)


# ---------------Key Gen Face Seven

def gen_face_seven_keys(nb_key):
	key = np.zeros(nb_key, dtype=np.int32)
	key[0] = 0
	key[1] = 1
	key[2] = 5
	sum_arr = np.zeros(50000, dtype=np.int32)

	for i in xrange(3):
		print 'key[{}]={}'.format(i, key[i])

	k=3
	while (k<nb_key):
		t = key[k-1]+1
		valid = 0
		while (not valid) :
			key[k] = t
			valid = 1
			c = 0
			for c1 in xrange(0, k+1) :
				for c2 in xrange(c1, k+1) :
					for c3 in xrange(c2, k+1) :
						for c4 in xrange(c3, k+1) :
							for c5 in xrange(c4, k+1) :
								for c6 in xrange(c5, k+1) :
									for c7 in xrange(c6, k+1) :
										if ((c1 != c5) & (c2 != c6) & (c3 != c7)) :
											sum_arr[c] = key[c1]+key[c2]+key[c3]+key[c4]+key[c5]+key[c6]+key[c7]
											c += 1
			i = 0
			while ((valid) & (i<c-1)):
				j = i+1
				while (valid) & (j<c):
					if (sum_arr[i] == sum_arr[j]):
						valid = 0
						t += 1
					j += 1
				i += 1
		print 'key[{}]={}'.format(k, key[k])
		k += 1
	return key

gen_face_seven_keys_fast = jit(int32[:](int32))(gen_face_seven_keys)

def keygen_face_seven(nb_key):
	print '\nstart keygen face_seven'
	t0 = timer()
	keys = gen_face_seven_keys_fast(nb_key)
	t1 = timer()
	print 'keys=\n{}'.format(keys)
	print 'run time = {:.4f} s'.format(t1-t0)




if __name__ == '__main__':
	keys = keygen_suit(37)
	# keygen_flush_five(5)
	# keygen_face_five(5)
	# keygen_flush_seven(8)
	# keygen_face_seven(8)


