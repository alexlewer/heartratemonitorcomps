
from DiscreteHMM import DiscreteHMM
import baumwelch_scratch as bw
import numpy
    
def test_discrete():

    ob5 = (0,3,1,2,1,0,2,3,0,1,0,2,0,1,2,2,0,3,0,0,2,0,0,1,2,0,1,2,0)
    T = len(ob5)
    #print "Doing Baum-welch"
    
    #atmp = numpy.random.random_sample((4, 4))
    #row_sums = atmp.sum(axis=1)
    #a = atmp / row_sums[:, numpy.newaxis]    

    #btmp = numpy.random.random_sample((4, 4))
    #row_sums = btmp.sum(axis=1)
    #b = btmp / row_sums[:, numpy.newaxis]
    
    a = numpy.array([0.6794, 0.3206, 0.0, 0.0, \
        0.0, 0.5366, 0.4634, 0.0, \
        0.0, 0.0, 0.3485, 0.6516, \
        0.1508, 0.0, 0.0, 0.8492])

    b = numpy.array([0.6884, 0.0015, 0.3002, 0.0099, \
        0.0, 0.7205, 0.0102, 0.2694, \
        0.2894, 0.3731, 0.3362, 0.0023, \
        0.0005, 0.8440, 0.0021, 0.1534])

    a = a.reshape((-1,4))
    b = b.reshape((-1,4))

    pi = numpy.array([0.25, 0.20, 0.10, 0.45])
    
    hmm2 = DiscreteHMM(4,4,a,b,pi,init_type='user',precision=numpy.longdouble,verbose=True)

    alpha1 = bw.alpha(a, b, ob5)
    beta1 = bw.beta(a, b, ob5)

    alpha2 = hmm2.alpha(ob5)
    beta2 = hmm2.beta(ob5)

    # Test if probabilities of obs sequences add up to 1
    total = 0
    for i in [0,1,2,3]:
        for j in [0,1,2,3]:
            for k in [0,1,2,3]:
                for l in [0,1,2,3]:
                    inp = (i,j,k,l)
                    alph = bw.alpha(a, b, inp)
                    prob = bw.prob_obs(alph)
                    total += prob

    print(total)

    xi1 = bw.xi(a, b, alpha1, beta1, ob5)
    xi2 = hmm2.xi(ob5)

    gamma1 = bw.gamma(alpha1, beta1, ob5)
    gamma2 = hmm2._calcgamma(xi2, T)

    new_alpha1 = bw.a_hat(xi1)
    new_alpha2 = hmm2._reestimateA(ob5, xi2, gamma2)

    new_beta1 = bw.b_hat(b, gamma1, ob5)
    new_beta2 = hmm2._reestimateB(ob5, gamma1)

    print(xi1 - xi2)

    #hmm2.train(numpy.array(ob5),iterations=10000,epsilon=.00001)
    #print "Pi",hmm2.pi
    #print "A",hmm2.A
    #print "B", hmm2.B
    
test_discrete()