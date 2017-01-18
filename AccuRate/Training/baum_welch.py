# Baum-Welch algorithm

import numpy as np
# functions and classes go here
def fb_alg(trans, emit, observ):
    # set up
    k = observ.size
    (n,m) = emit.shape
    prob_mat = np.zeros( (n,k) )
    fw = np.zeros( (n,k+1) )
    bw = np.zeros( (n,k+1) )
    # forward part
    fw[:, 0] = 1.0/n
    for obs_ind in range(k):
        f_row_vec = np.matrix(fw[:,obs_ind])
        print("vector", emit[:,observ[obs_ind]].flatten())
        print("diagonal", np.diag(emit[:,observ[obs_ind]].flatten()))

        d = np.reshape(emit[:,observ[obs_ind]].flatten(), n)
        print("d", d)

        fw[:, obs_ind+1] = f_row_vec * \
                           np.matrix(trans) * \
                           np.matrix(np.diag(emit[:,observ[obs_ind]].flatten()))
        fw[:,obs_ind+1] = fw[:,obs_ind+1]/np.sum(fw[:,obs_ind+1])
    # backward part
    bw[:,-1] = 1.0
    for obs_ind in range(k, 0, -1):
        b_col_vec = np.matrix(bw[:,obs_ind]).transpose()
        bw[:, obs_ind-1] = (np.matrix(trans) * \
                            np.matrix(np.diag(emit[:,observ[obs_ind-1]])) * \
                            b_col_vec).transpose()
        bw[:,obs_ind-1] = bw[:,obs_ind-1]/np.sum(bw[:,obs_ind-1])
    # combine it
    prob_mat = np.array(fw)*np.array(bw)
    prob_mat = prob_mat/np.sum(prob_mat, 0)
    # get out
    return prob_mat, fw, bw


def baum_welch( trans, emit, observ ):
    num_states, num_obs = emit.shape
    # allocate
    
    A_mat = np.ones( (num_states, num_states) )
    A_mat = A_mat / np.sum(A_mat,1)
    O_mat = np.ones( (num_states, num_obs) )
    O_mat = O_mat / np.sum(O_mat,1)

    print(trans.shape, emit.shape)
    print(A_mat.shape, O_mat.shape)
    theta = np.zeros( (num_states, num_states, observ.size) )

    count = 1
    while True:
        print("Iteration: ", count)

        old_trans = trans
        old_emit = emit
        trans = np.ones( (num_states, num_states) )
        emit = np.ones( (num_states, num_obs) )
        # expectation step, forward and backward probs
        P,F,B = fb_alg( old_trans, old_emit, observ)
        # need to get transitional probabilities at each time step too
        for a_ind in range(num_states):
            for b_ind in range(num_states):
                for t_ind in range(observ.size):
                    theta[a_ind,b_ind,t_ind] = \
                    F[a_ind,t_ind] * \
                    B[b_ind,t_ind+1] * \
                    old_trans[a_ind,b_ind] * \
                    old_emit[b_ind, observ[t_ind]]
        # form trans and emit
        for a_ind in range(num_states):
            for b_ind in range(num_states):
                trans[a_ind, b_ind] = np.sum( theta[a_ind, b_ind, :] )/ \
                                      np.sum(P[a_ind,:])
        trans = trans / np.sum(trans,1)
        for a_ind in range(num_states):
            for o_ind in range(num_obs):
                right_obs_ind = np.array(np.where(observ == o_ind))+1
                emit[a_ind, o_ind] = np.sum(P[a_ind,right_obs_ind])/ \
                                      np.sum( P[a_ind,1:])
        emit = emit / np.sum(emit,1)
        # compare
        if np.linalg.norm(old_trans-trans) < .00001 and np.linalg.norm(old_emit-emit) < .00001:
            break

        count += 1
    # get out
    return trans, emit
    """while True:
                    old_A = A_mat
                    old_O = O_mat
                    A_mat = np.ones( (num_states, num_states) )
                    O_mat = np.ones( (num_states, num_obs) )
                    # expectation step, forward and backward probs
                    P,F,B = fb_alg( old_A, old_O, observ)
                    # need to get transitional probabilities at each time step too
                    for a_ind in range(num_states):
                        for b_ind in range(num_states):
                            for t_ind in range(observ.size):
                                theta[a_ind,b_ind,t_ind] = \
                                F[a_ind,t_ind] * \
                                B[b_ind,t_ind+1] * \
                                old_A[a_ind,b_ind] * \
                                old_O[b_ind, observ[t_ind]]
                    # form A_mat and O_mat
                    for a_ind in range(num_states):
                        for b_ind in range(num_states):
                            A_mat[a_ind, b_ind] = np.sum( theta[a_ind, b_ind, :] )/ \
                                                  np.sum(P[a_ind,:])
                    A_mat = A_mat / np.sum(A_mat,1)
                    for a_ind in range(num_states):
                        for o_ind in range(num_obs):
                            right_obs_ind = np.array(np.where(observ == o_ind))+1
                            O_mat[a_ind, o_ind] = np.sum(P[a_ind,right_obs_ind])/ \
                                                  np.sum( P[a_ind,1:])
                    O_mat = O_mat / np.sum(O_mat,1)
                    # compare
                    if np.linalg.norm(old_A-A_mat) < .00001 and np.linalg.norm(old_O-O_mat) < .00001:
                        break
                # get out
                return A_mat, O_mat"""

def test():
    A = np.matrix([[0.6794, 0.3206, 0.0, 0.0], \
        [0.0, 0.5366, 0.4634, 0.0], \
        [0.0, 0.0, 0.3485, 0.6516], \
        [0.1508, 0.0, 0.0, 0.8492]])

    B = np.matrix([[0.6884, 0.0015, 0.3002, 0.0099], \
        [0.0, 0.7205, 0.0102, 0.2694], \
        [0.2894, 0.3731, 0.3362, 0.0023], \
        [0.0005, 0.8440, 0.0021, 0.1534]])

    O = np.array([0,3,1,2,1,0,2,3,0,1,0,2,0,1,2,2,0,3,0,0,2,0,0,1,2,0,1,2,0])

    print(baum_welch(A,B,O))
