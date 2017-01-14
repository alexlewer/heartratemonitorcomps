# Aidan Holloway-Bidwell, Lucy Lu, Grant Terrien, Renzhi Wu
# Baum-Welch training
import numpy as np

# calculate forward probability matrix
def alpha(A, B, observations):

	T = len(observations)
	num_states, num_obs = B.shape

	fw = np.zeros((num_states, T + 1))

	# Assuming all states have equal probability of being start state.
	# If this is not true, line below may have to be changed.
	# EDIT: changed to 1.0 for all states
	fw[:, 0] = 1.0

	for time in xrange(T):
		for state in xrange(num_states):

			# Still not sure about this part
			fw_prob = np.sum(np.matrix(fw[:, time]) * \
							 np.matrix(A[:, state]) * \
							 # other implementations put a np.diag here but not sure why
							 np.matrix((O[:, observations[time]])))

			fw[state + 1][time + 1] = fw_prob

	return fw

# calculate backward probability matrix
def beta(A, B, observations):

	T = len(observations)
	num_states, num_obs = B.shape

	bw = np.zeros((num_states, T + 1))

	# Assuming if a state is last, it has a 1.0 prob of being last.
	# If this is not true, line below may have to be changed.
	bw[:, -1] = 1.0

	for time in xrange(T, 0, -1):
		for state in xrange(num_states):

			# Still not sure about this part
			bw_prob = np.sum(np.matrix(bw[:, time]) * \
							 np.matrix(A[:, state]) * \
							 np.matrix(np.diag(O[:, observations[time]])))

			bw[state - 1][time - 1] = bw_prob

	return bw

def xi(A, B, alpha, beta, prob_obs, observations):
	num_states = A.shape[0]
	T = len(observations)
	xi = np.zeros((T, num_states, num_states))

	for i_ind in xrange(num_states):
        for j_ind in xrange(num_states):
            for t_ind in xrange(T):
                not_quite_xi = \
                alpha[i_ind,t_ind] * \
                beta[j_ind,t_ind+1] * \
                A[i_ind,j_ind] * \
                B[j_ind, observ[t_ind]]

                xi[t_ind,i_ind,j_ind] = not_quite_xi / prob_obs

    return xi

def a_hat(xi):
	T, num_states = xi.shape[:2]
	a_hat = np.zeros((num_states, num_states))

	for i in xrange(num_states):
		for j in xrange(num_states):
			a_hat[i, j] = np.sum(xi[:, i, j]) / np.sum(xi[:, i, :])

	return a_hat

def gamma(alpha, beta, prob_obs, observations):
	T = len(observations)
	num_states = alpha.shape[0]
	gamma = np.zeros((T, num_states))

	for t_ind in xrange(T):
		for j_ind in xrange(num_states):
			gamma[t_ind, j_ind] = alpha[j_ind, t_ind] * beta[j_ind, t_ind] / prob_obs

	return gamma

def b_hat(B, gamma):
	num_states, num_obs = B.shape
	b_hat = np.zeros((num_states, num_obs))

	for i_ind in xrange(num_states):
		for o_ind in xrange(num_obs):
			cur_obs_ind = np.array(np.where(observations == o_ind)) + 1
			b_hat[i_ind, o_ind] = np.sum(gamma[cur_obs_ind, i_ind]) / np.sum(gamma[:, i_ind])

	return b_hat


def baum_welch(A, B, observations):
	curA = A
	curB = B

	while True:
		alpha = alpha(curA, curB, observations)
		beta = beta(curA, curB, observations)

		prob_obs = 0
        for k in xrange(num_states):
        	prob_obs += alpha[k_ind, t_ind] * beta[k_ind, t_ind]

        xi = xi(curA, curB, alpha, beta, prob_obs, observations)

        gamma = gamma(alpha, beta, prob_obs, observations)

        oldA, oldB = curA, curB

        curA = a_hat(xi)
        curB = b_hat(B, gamma)


        if np.linalg.norm(oldA - curA) < .00001 and np.linalg.norm(oldB - curB) < .00001:
        	break

    return curA, curB










