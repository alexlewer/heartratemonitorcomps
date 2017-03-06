# Aidan Holloway-Bidwell, Lucy Lu, Grant Terrien, Renzhi Wu
# Baum-Welch training
import numpy as np
import csv
from DiscreteHMM import DiscreteHMM
import sys
import fancy_bw as fancy
from matplotlib import pyplot as plt
import math

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

def prob_obs(alpha):
	return sum(alpha.T[-1])

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

def baum_welch(A, B, pi, observations):
	curA = A
	curB = B
	cur_pi = pi
	num_states, num_obs = B.shape
	T = len(observations)

	ind = []
	p = []
	A1, A2 ,A3 ,A4 ,A5 ,A6 ,A7 ,A8 = [], [], [], [], [], [], [], []
	B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B12, B13, B14, B15, B16 = [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []

	count = 1
	while True:
		alph = alpha(curA, curB, cur_pi, observations)
		bet = beta(curA, curB, observations)

		ind.append(count)
		p.append(math.log(prob_obs(alph),10))
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

		#for r in alph.T:
			#print(r)
		x = xi(curA, curB, alph, bet, observations)
		gam = gamma(alph, bet, observations)

		oldA, oldB, old_pi = curA, curB, cur_pi

		curA = a_hat(x)
		curB = b_hat(oldB, gam, observations)
		cur_pi = gam[0]

		if np.linalg.norm(oldA - curA) < .00001 and np.linalg.norm(oldB - curB) < .00001:
			break

		count += 1
		print(".",end='')
		sys.stdout.flush()

	print(count," iterations.")
	f, axarr = plt.subplots(3, sharex=True)
	#axarr[0].set_axis_bgcolor('black')
	axarr[0].set_title('Transition Matrix Values')
	axarr[1].set_title('Emission Matrix Values')
	#axarr[1].set_axis_bgcolor('black')
	axarr[2].set_title('Probability of Observation Sequence (log)')
	axarr[1].plot(ind,B1,'b')
	axarr[1].plot(ind,B2,'b')
	axarr[1].plot(ind,B3,'b')
	axarr[1].plot(ind,B4,'b')
	axarr[1].plot(ind,B5,'b')
	axarr[1].plot(ind,B6,'b')
	axarr[1].plot(ind,B7,'b')
	axarr[1].plot(ind,B8,'b')
	axarr[1].plot(ind,B9,'b')
	axarr[1].plot(ind,B10,'b')
	axarr[1].plot(ind,B11,'b')
	axarr[1].plot(ind,B12,'b')
	axarr[1].plot(ind,B13,'b')
	axarr[1].plot(ind,B14,'b')
	axarr[1].plot(ind,B15,'b')
	axarr[1].plot(ind,B16,'b')
	axarr[0].plot(ind,A1,'brown')
	axarr[0].plot(ind,A2,'brown')
	axarr[0].plot(ind,A3,'brown')
	axarr[0].plot(ind,A4,'brown')
	axarr[0].plot(ind,A5,'brown')
	axarr[0].plot(ind,A6,'brown')
	axarr[0].plot(ind,A7,'brown')
	axarr[0].plot(ind,A8,'brown')
	axarr[2].plot(ind,p,'r')
	axarr[2].set_xlabel('Number of Iterations')

	plt.show()
	plt.savefig('baum_welch.png')

	return curA, curB, cur_pi

def train(A, B, initial, filepath):
	cur_pi = initial

	with open(filepath, 'r') as file:
		obs_files = file.readlines()
		for obs_filepath in obs_files:
			print("Training on ", obs_filepath.rstrip())
			with open(obs_filepath.rstrip(), 'r') as obs_file:
				O = []
				reader = csv.reader(obs_file)
				for row in reader:
					try:
						O.append(int(row[2]))
					except ValueError:
						pass

				A, B, cur_pi = baum_welch(A, B, cur_pi, O)

	with open("results.txt", 'w') as file:
		file.write(str(A))
		file.write(str(B))
		file.write(str(cur_pi))

	return A, B, cur_pi

def test(filepath):
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

	ourPi = [0.25, 0.20, 0.10, 0.45]

	ourA = ourA.reshape((-1,4))
	ourB = ourB.reshape((-1,4))

	sumA = np.zeros((4,4))
	sumB = np.zeros((4,4))
	sumPi = [0,0,0,0]
	count = 0

	guyA, guyB, guyPi = np.zeros((4,4)), np.zeros((4,4)), []
	guyA[:], guyB[:], guyPi[:] = ourA, ourB, ourPi
	fancyA, fancyB, fancyPi = np.zeros((4,4)), np.zeros((4,4)), []
	fancyA[:], fancyB[:], fancyPi[:] = ourA, ourB, ourPi

	with open(filepath, 'r') as file:
		obs_files = file.readlines()
		for obs_filepath in obs_files:
			print("Training on ", obs_filepath.rstrip())
			with open(obs_filepath.rstrip(), 'r') as obs_file:
				O = []
				reader = csv.reader(obs_file)
				for row in reader:
					try:
						O.append(int(row[2]))
					except ValueError:
						pass

				O1 = []
				O2 = []
				O1[:] = O[:int(len(O) / 2)]
				O2[:] = O[int(len(O) / 2):]

				print("Running our model...")
				print("First half")
				ourA, ourB, ourPi = baum_welch(ourA.copy(), ourB.copy(), ourPi.copy(), O1)
				print("Second half")
				#newA2, newB2, newPi2 = baum_welch(ourA.copy(), ourB.copy(), ourPi.copy(), O2)
				
				#print("Running Guy's model...")
				#hmm2 = DiscreteHMM(4,4,guyA,guyB,guyPi,init_type='user',precision=np.longdouble,verbose=True)
				#hmm2.train(O, iterations=1000,epsilon=.00001)
				#guyA, guyB, guyPi = hmm2.A, hmm2.B, hmm2.pi

				#print("Running fancy model...")
				#fancyA, fancyB = fancy.baum_welch(fancyA, fancyB, fancyPi, np.array(O))

	with open("results_alldata_vanillamatrices.txt", 'w') as file:
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












