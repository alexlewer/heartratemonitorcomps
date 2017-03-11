# Aidan Holloway-Bidwell, Lucy Lu, Grant Terrien, Renzhi Wu
# Baum-Welch training
import numpy as np
import csv
from DiscreteHMM import DiscreteHMM
import sys
import fancy_bw as fancy
from decimal import *
import matplotlib.pyplot as plt

# calculate forward probability matrix
def alpha(A, B, pi, observations):

	T = len(observations)
	num_states, num_obs = B.shape

	fw = np.zeros((num_states, T), dtype=np.longdouble)

	for index, prob in enumerate(pi):
		fw[index, 0] = prob * B[index, observations[0]]	

	for t in range(1, T):
		for j in range(num_states):
			for i in range(num_states):
				fw[j,t] += fw[i,t-1] * A[i,j]
			fw[j,t] *= B[j,observations[t]]

	return fw

# calculate backward probability matrix
def beta(A, B, observations):

	T = len(observations)
	num_states, num_obs = B.shape

	bw = np.zeros((num_states, T), dtype=np.longdouble)

	# Assuming if a state is last, it has a 1.0 prob of being last.
	# If this is not true, line below may have to be changed.
	bw[:,-1] = 1.0

	for t in range(T-2, -1, -1):
		for i in range(num_states):
			for j in range(num_states):
				bw[i,t] += bw[j,t+1] * A[i,j] * B[j,observations[t + 1]]

	return bw

# Calculate probability of going from state i to j, given probability sequence,
# at any time t
def xi(A, B, alpha, beta, observations):
	prob = prob_obs(alpha)

	num_states = A.shape[0]
	T = len(observations)
	xi = np.zeros((T, num_states, num_states), dtype=np.longdouble)

	for i_ind in range(num_states):
		for j_ind in range(num_states):
			for t_ind in range(T - 1):
				not_quite_xi = \
					alpha[i_ind,t_ind] * \
					beta[j_ind,t_ind + 1] * \
					A[i_ind,j_ind] * \
					B[j_ind, observations[t_ind + 1]]

				xi[t_ind,i_ind,j_ind] = not_quite_xi / prob

	return xi

# Probability of entire observation sequence
def prob_obs(alpha):
	return sum(alpha.T[-1])

# New transition probabilities
def a_hat(xi):
	T, num_states = xi.shape[:2]
	a_hat = np.zeros((num_states, num_states), dtype=np.longdouble)

	for i in range(num_states):
		for j in range(num_states):
			a_hat[i, j] = np.sum(xi[0:T, i, j]) / np.sum(xi[0:T, i, :])

	return a_hat

# Calculate the probability of being in state j at time t
def gamma(alpha, beta, observations):
	prob = prob_obs(alpha)

	T = len(observations)
	num_states = alpha.shape[0]
	gamma = np.zeros((T, num_states), dtype=np.longdouble)

	for t_ind in range(T):
		for j_ind in range(num_states):
			gamma[t_ind, j_ind] = alpha[j_ind, t_ind] * beta[j_ind, t_ind] / prob

	return gamma

# New emission probabilities
def b_hat(B, gamma, observations):
	num_states, num_obs = B.shape
	T = len(observations)

	b_hat = np.zeros((num_states, num_obs), dtype=np.longdouble)

	for i_ind in range(num_states):
		for o_ind in range(num_obs):
			for t_ind in range(T):
				if observations[t_ind] == o_ind:
					b_hat[i_ind, o_ind] += gamma[t_ind, i_ind]
			b_hat[i_ind, o_ind] /= sum(gamma[:, i_ind])

	return b_hat

def baum_welch(A, B, pi, observations, display_graph=False):
	curA = A
	curB = B
	cur_pi = pi
	num_states, num_obs = B.shape
	T = len(observations)

	# variables for displaying graph of probabilities changing over iterations
	ind = []
	p = []
	A1, A2 ,A3 ,A4 ,A5 ,A6 ,A7 ,A8 = [], [], [], [], [], [], [], []
	B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16 = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

	count = 1
	while True:
		# calculate forward and backward probabilities based on current matrices
		alph = alpha(curA, curB, cur_pi, observations)
		bet = beta(curA, curB, observations)

		if display_graph:
			ind.append(count)
			p.append(prob_obs(alph))
			A1.append(curA[0][0])
			A2.append(curA[0][1])
			A3.append(curA[1][1])
			A4.append(curA[1][2])
			A5.append(curA[2][2])
			A6.append(curA[2][3])
			A7.append(curA[3][3])
			A8.append(curA[3][0])
			B1.append(curB[0][0])
			B2.append(curB[0][1])
			B3.append(curB[0][2])
			B4.append(curB[0][3])
			B5.append(curB[1][0])
			B6.append(curB[1][1])
			B7.append(curB[1][2])
			B8.append(curB[1][3])
			B9.append(curB[2][0])
			B10.append(curB[2][1])
			B11.append(curB[2][2])
			B12.append(curB[2][3])
			B13.append(curB[3][0])
			B14.append(curB[3][1])
			B15.append(curB[3][2])
			B16.append(curB[3][3])

		# calculate prob of making transition at time t and 
		# prob of being in state at time t
		x = xi(curA, curB, alph, bet, observations)
		gam = gamma(alph, bet, observations)

		oldA, oldB, old_pi = curA, curB, cur_pi

		# update matrices to new probabilities
		curA = a_hat(x)
		curB = b_hat(oldB, gam, observations)
		cur_pi = gam[0]

		# if we are close enough to maximizing the probability of our observation sequence, stop the algorithm
		if np.linalg.norm(oldA - curA) < .00001 and np.linalg.norm(oldB - curB) < .00001:
			break

		count += 1
		print(".",end='')
		sys.stdout.flush()

	print(count," iterations.")

	if display_graph:
		f, axarr = plt.subplots(2, sharex=True)
		axarr[0].set_axis_bgcolor('black')
		axarr[1].set_axis_bgcolor('black')
		axarr[0].plot(ind,B1,'c')
		axarr[0].plot(ind,B2,'c')
		axarr[0].plot(ind,B3,'c')
		axarr[0].plot(ind,B4,'c')
		axarr[0].plot(ind,B5,'c')
		axarr[0].plot(ind,B6,'c')
		axarr[0].plot(ind,B7,'c')
		axarr[0].plot(ind,B8,'c')
		axarr[0].plot(ind,B9,'c')
		axarr[0].plot(ind,B10,'c')
		axarr[0].plot(ind,B11,'c')
		axarr[0].plot(ind,B12,'c')
		axarr[0].plot(ind,B13,'c')
		axarr[0].plot(ind,B14,'c')
		axarr[0].plot(ind,B15,'c')
		axarr[0].plot(ind,B16,'c')
		axarr[0].plot(ind,A1,'y')
		axarr[0].plot(ind,A2,'y')
		axarr[0].plot(ind,A3,'y')
		axarr[0].plot(ind,A4,'y')
		axarr[0].plot(ind,A5,'y')
		axarr[0].plot(ind,A6,'y')
		axarr[0].plot(ind,A7,'y')
		axarr[0].plot(ind,A8,'y')
		axarr[1].plot(ind,p,'r')

		plt.show()
		plt.savefig('baum_welch.png')

	return curA, curB, cur_pi

def simple_test():
	A = np.array([.3, .7, .1, .9])

	B = np.array([.4, .6, .5, .5])

	A = A.reshape((-1,2))
	B = B.reshape((-1,2))

	pi = [.85, .15]

	O = [0, 1, 1, 0]

	alph = alpha(A, B, pi, O)
	print("Alpha: ", alph)
	bet = beta(A, B, O)
	print("Beta: ", bet)
	gam = gamma(alph, bet, O)
	print("Gamma: ", gam)
	x = xi(A, B, alph, bet, O)
	print("Xi: ", x)

def train(filepath,display_graph=False):

	#ourA = np.array([0.6794, 0.3206, 0.0, 0.0, \
	#			  0.0, 0.5366, 0.4634, 0.0, \
	#			  0.0, 0.0, 0.3485, 0.6516, \
	#			  0.1508, 0.0, 0.0, 0.8492])

	#ourB = np.array([0.6884, 0.0015, 0.3002, 0.0099, \
	#			  0.0, 0.7205, 0.0102, 0.2694, \
	#			  0.2894, 0.3731, 0.3362, 0.0023, \
	#			  0.0005, 0.8440, 0.0021, 0.1534])

	ourA = np.array([.5, .5, 0.0, 0.0, \
					0.0, .5, .5, 0.0, \
					0.0, 0.0, .5, .5, \
					.5, 0.0, 0.0, .5])

	ourB = np.array([.25, .25, .25, .25, \
				.25, .25, .25, .25, \
				.25, .25, .25, .25, \
				.25, .25, .25, .25])

	ourPi = [.25, .25, .25, .25]

	# ourPi = [0.25, 0.20, 0.10, 0.45]

	ourA = ourA.reshape((-1,4))
	ourB = ourB.reshape((-1,4))

	guyA, guyB, guyPi = np.zeros((4,4)), np.zeros((4,4)), []
	guyA[:], guyB[:], guyPi[:] = ourA, ourB, ourPi
	fancyA, fancyB, fancyPi = np.zeros((4,4)), np.zeros((4,4)), []
	fancyA[:], fancyB[:], fancyPi[:] = ourA, ourB, ourPi

	count = 0

	with open("data/" + filepath, 'r') as file:
		obs_files = file.readlines()
		for obs_filepath in obs_files:
			print("Training on ", obs_filepath.rstrip())
			with open("data/" + obs_filepath.rstrip(), 'r') as obs_file:
				O = []
				reader = csv.reader(obs_file)
				for row in reader:
					try:
						O.append(int(row[2]))
					except ValueError:
						pass

				print("Running our model...")
				ourA, ourB, ourPi = baum_welch(ourA, ourB, ourPi, O, display_graph=display_graph)

				count += 1
				
				#print("Running Guy's model...")
				#hmm2 = DiscreteHMM(4,4,guyA,guyB,guyPi,init_type='user',precision=np.longdouble,verbose=True)
				#hmm2.train(O, iterations=1000,epsilon=.00001)
				#guyA, guyB, guyPi = hmm2.A, hmm2.B, hmm2.pi

				#print("Running fancy model...")
				#fancyA, fancyB = fancy.baum_welch(fancyA, fancyB, fancyPi, np.array(O))

	with open("results_vanilla.txt", 'w') as file:
		file.write("Our Results:\n")
		file.write("A: " + str(ourA) + "\n")
		file.write("B: " + str(ourB) + "\n")
		file.write("Pi: " + str(ourPi) +  "\n\n")
		#file.write("Guy's Results:\n")
		#file.write("A: " + str(guyA) + "\n")
		#file.write("B: " + str(guyB) + "\n")
		#file.write("Pi: " + str(guyPi) +  "\n\n")
		#file.write("Fancy Results:\n")
		#file.write("A: " + str(fancyA) + "\n")
		#file.write("B: " + str(fancyB) + "\n")










