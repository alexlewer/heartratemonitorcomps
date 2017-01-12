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

	fw = np.zeros((num_states, T + 1))

	# Assuming if a state is last, it has a 1.0 prob of being last.
	# If this is not true, line below may have to be changed.
	fw[:, -1] = 1.0

	for time in xrange(T, 0, -1):
		for state in xrange(num_states):

			# Still not sure about this part
			fw_prob = np.sum(np.matrix(fw[:, time]) * \
							 np.matrix(A[:, state]) * \
							 np.matrix(np.diag(O[:, observations[time]])))

			fw[state - 1][time - 1] = fw_prob

	return fw

def xi(A, B, alpha, beta, observations):
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

                prob_obs = 0
                for k in xrange(num_states):
                	prob_obs += alpha[k_ind, t_ind] * beta[k_ind, t_ind]

                xi[t_ind,i_ind,j_ind] = not_quite_xi / prob_obs

    return xi

def a_hat()





def baum_welch(A, B, observations):
	curA = A
	curB = B

	while True:












