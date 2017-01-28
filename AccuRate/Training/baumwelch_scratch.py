# Aidan Holloway-Bidwell, Lucy Lu, Grant Terrien, Renzhi Wu
# Baum-Welch training
import numpy as np

# calculate forward probability matrix
def alpha(A, B, observations):

	T = len(observations)
	num_states, num_obs = B.shape

	fw = np.zeros((num_states, T))

	initial = [0.25, 0.20, 0.10, 0.45]
	for index, prob in enumerate(initial):
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

	bw = np.zeros((num_states, T))

	# Assuming if a state is last, it has a 1.0 prob of being last.
	# If this is not true, line below may have to be changed.
	bw[:,-1] = 1.0
	for t in range(T-2, -1, -1):
		for j in range(num_states):
			for i in range(num_states):
				bw[j,t] += bw[i,t+1] * A[i,j]
			bw[j,t] *= B[j,observations[t]]

	return bw

def xi(A, B, alpha, beta, prob_obs, observations):
	num_states = A.shape[0]
	T = len(observations)
	xi = np.zeros((T, num_states, num_states))

	for i_ind in range(num_states):
		for j_ind in range(num_states):
			for t_ind in range(T):
				not_quite_xi = \
				alpha[i_ind,t_ind] * \
				beta[j_ind,t_ind] * \
				A[i_ind,j_ind] * \
				B[j_ind, observations[t_ind]]

				xi[t_ind,i_ind,j_ind] = not_quite_xi / prob_obs

	return xi

def a_hat(xi):
	T, num_states = xi.shape[:2]
	a_hat = np.zeros((num_states, num_states))

	for i in range(num_states):
		for j in range(num_states):
			a_hat[i, j] = np.sum(xi[:, i, j]) / np.sum(xi[:, i, :])

	return a_hat

def gamma(alpha, beta, prob_obs, observations):
	T = len(observations)
	num_states = alpha.shape[0]
	gamma = np.zeros((T, num_states))

	for t_ind in range(T):
		for j_ind in range(num_states):
			gamma[t_ind, j_ind] = alpha[j_ind, t_ind] * beta[j_ind, t_ind] / prob_obs

	return gamma

def b_hat(B, gamma, observations):
	num_states, num_obs = B.shape
	b_hat = np.zeros((num_states, num_obs))

	for i_ind in range(num_states):
		for o_ind in range(num_obs):
			#print("i_ind: ", i_ind, " o_ind: ", o_ind)
			cur_obs_ind = np.array(np.where(observations == o_ind)) + 1
			b_hat[i_ind, o_ind] = np.sum(gamma[cur_obs_ind, i_ind]) / np.sum(gamma[:, i_ind])

	return b_hat


def baum_welch(A, B, observations):
	curA = A
	curB = B
	num_states, num_obs = B.shape
	T = len(observations)

	count = 1
	while True:
		alph = alpha(curA, curB, observations)
		bet = beta(curA, curB, observations)

		print("Ours, iteration ", count, ": alpha = ", alph, ", beta = ", bet)

		prob_obs = 0
		for t_ind in range(T):
			for k in range(num_states):
				prob_obs += alph[k, t_ind] * bet[k, t_ind]

		x = xi(curA, curB, alph, bet, prob_obs, observations)

		gam = gamma(alph, bet, prob_obs, observations)

		oldA, oldB = curA, curB

		curA = a_hat(x)
		curB = b_hat(oldB, gam, observations)


		if np.linalg.norm(oldA - curA) < .00001 and np.linalg.norm(oldB - curB) < .00001:
			break

		count += 1

	return curA, curB

def test():
	A = np.array([0.6794, 0.3206, 0.0, 0.0, \
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

	O = np.array([0,3,1,2,1,0,2,3,0,1,0,2,0,1,2,2,0,3,0,0,2,0,0,1,2,0,1,2,0])

	print(baum_welch(A,B,O))










