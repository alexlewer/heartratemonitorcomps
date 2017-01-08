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
    for obs_ind in xrange(k):
        f_row_vec = np.matrix(fw[:,obs_ind])
        fw[:, obs_ind+1] = f_row_vec * \
                           np.matrix(trans) * \
                           np.matrix(np.diag(emit[:,observ[obs_ind]]))
        fw[:,obs_ind+1] = fw[:,obs_ind+1]/np.sum(fw[:,obs_ind+1])
    # backward part
    bw[:,-1] = 1.0
    for obs_ind in xrange(k, 0, -1):
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


def baum_welch( trans, emit, num_states, num_obs, observ ):
    # allocate
    #trans = np.ones( (num_states, num_states) )
    #trans = trans / np.sum(trans,1)
    #emit = np.ones( (num_states, num_obs) )
    #emit = emit / np.sum(emit,1)
    theta = np.zeros( (num_states, num_states, observ.size) )

    while True:
        old_trans = trans
        old_emit = emit
        trans = np.ones( (num_states, num_states) )
        emit = np.ones( (num_states, num_obs) )
        # expectation step, forward and backward probs
        P,F,B = fb_alg( old_trans, old_emit, observ)
        # need to get transitional probabilities at each time step too
        for a_ind in xrange(num_states):
            for b_ind in xrange(num_states):
                for t_ind in xrange(observ.size):
                    theta[a_ind,b_ind,t_ind] = \
                    F[a_ind,t_ind] * \
                    B[b_ind,t_ind+1] * \
                    old_trans[a_ind,b_ind] * \
                    old_emit[b_ind, observ[t_ind]]
        # form trans and emit
        for a_ind in xrange(num_states):
            for b_ind in xrange(num_states):
                trans[a_ind, b_ind] = np.sum( theta[a_ind, b_ind, :] )/ \
                                      np.sum(P[a_ind,:])
        trans = trans / np.sum(trans,1)
        for a_ind in xrange(num_states):
            for o_ind in xrange(num_obs):
                right_obs_ind = np.array(np.where(observ == o_ind))+1
                emit[a_ind, o_ind] = np.sum(P[a_ind,right_obs_ind])/ \
                                      np.sum( P[a_ind,1:])
        emit = emit / np.sum(emit,1)
        # compare
        if np.linalg.norm(old_trans-trans) < .00001 and np.linalg.norm(old_emit-emit) < .00001:
            break
    # get out
    return trans, emit
