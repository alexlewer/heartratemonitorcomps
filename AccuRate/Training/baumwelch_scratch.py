# Aidan Holloway-Bidwell, Lucy Lu, Grant Terrien, Renzhi Wu
# Baum-Welch training
import numpy as np
import csv
from DiscreteHMM import DiscreteHMM
import sys
import fancy_bw as fancy

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
	pastProb = 0

	count = 1
	while True:
		alph = alpha(curA, curB, cur_pi, observations)
		bet = beta(curA, curB, observations)

		curProb = prob_obs(alph)
		#for r in alph.T:
			#print(r)
		x = xi(curA, curB, alph, bet, observations)
		gam = gamma(alph, bet, observations)

		oldA, oldB, old_pi = curA, curB, cur_pi

		curA = a_hat(x)
		curB = b_hat(oldB, gam, observations)
		cur_pi = gam[0]

		if (curProb == pastProb) or (np.linalg.norm(oldA - curA) < .00000001 and np.linalg.norm(oldB - curB) < .00000001):
			break

		pastProb = curProb

		count += 1
		print(".",end='')
		sys.stdout.flush()

	print(count," iterations.")

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
				newA1, newB1, newPi1 = baum_welch(ourA.copy(), ourB.copy(), ourPi.copy(), O1)
				print("Second half")
				newA2, newB2, newPi2 = baum_welch(ourA.copy(), ourB.copy(), ourPi.copy(), O2)

				sumA += newA1
				sumB += newB1
				sumPi += newPi1

				sumA += newA2
				sumB += newB2
				sumPi += newPi2

				count += 2
				
				#print("Running Guy's model...")
				#hmm2 = DiscreteHMM(4,4,guyA,guyB,guyPi,init_type='user',precision=np.longdouble,verbose=True)
				#hmm2.train(O, iterations=1000,epsilon=.00001)
				#guyA, guyB, guyPi = hmm2.A, hmm2.B, hmm2.pi

				#print("Running fancy model...")
				#fancyA, fancyB = fancy.baum_welch(fancyA, fancyB, fancyPi, np.array(O))

	with open("results_alldata_vanillamatrices.txt", 'w') as file:
		file.write("Our Results:\n")
		file.write("A: " + str(sumA / count) + "\n")
		file.write("B: " + str(sumB / count) + "\n")
		file.write("Pi: " + str(sumPi / count) +  "\n\n")
		#file.write("Guy's Results:\n")
		#file.write("A: " + str(guyA) + "\n")
		#file.write("B: " + str(guyB) + "\n")
		#file.write("Pi: " + str(guyPi) +  "\n\n")
		#file.write("Fancy Results:\n")
		#file.write("A: " + str(fancyA) + "\n")
		#file.write("B: " + str(fancyB) + "\n")












