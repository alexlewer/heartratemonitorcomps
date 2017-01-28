# Baum Welch comparison

import baum_welch as bw
import baumwelch_scratch as bws
import numpy as np

def test():
	"""A = np.array([0.6794, 0.3206, 0.0, 0.0, \
					0.0, 0.5366, 0.4634, 0.0, \
					0.0, 0.0, 0.3485, 0.6516, \
					0.1508, 0.0, 0.0, 0.8492])
			
				B = np.array([0.6884, 0.0015, 0.3002, 0.0099, \
					0.0, 0.7205, 0.0102, 0.2694, \
					0.2894, 0.3731, 0.3362, 0.0023, \
					0.0005, 0.8440, 0.0021, 0.1534])
			
				A = A.reshape((-1,4))
				B = B.reshape((-1,4))
			
				#print(A, B)
			
				O = np.array([0,3,1,2,1,0,2,3,0,1,0,2,0,1,2,2,0,3,0,0,2,0,0,1,2,0,1,2,0])"""
			

	num_obs = 25
	num_states, num_ob_types = 2, 2
	A_mat = np.ones( (num_states, num_states) )
	A_mat = A_mat / np.sum(A_mat,1)
	O_mat = np.ones( (num_states, num_ob_types) )
	O_mat = O_mat / np.sum(O_mat,1)
	observations1 = np.random.randn( num_obs )
	observations1[observations1>0] = 1
	observations1[observations1<=0] = 0

	ourA, ourB = bws.baum_welch(A_mat, O_mat, observations1)
	theirA, theirB = bw.baum_welch(A_mat, O_mat, observations1)

	if not np.array_equal(ourA, theirA):
		print("transition arrays not equal: ", ourA, theirA)
	else:
		print("transition arrays equal")

	if not np.array_equal(ourB, theirB):
		print("emission arrays not equal: ", ourB, theirB)
	else:
		print("emission arrays equal")