'''
Created on Nov 13, 2012

@author: GuyZ
'''

#from GMHMM import GMHMM
from DiscreteHMM import DiscreteHMM
import numpy

"""def test_simple():
    n = 2
    m = 2
    d = 2
    pi = numpy.array([0.5, 0.5])
    A = numpy.ones((n,n),dtype=numpy.double)/float(n)
    
    w = numpy.ones((n,m),dtype=numpy.double)
    means = numpy.ones((n,m,d),dtype=numpy.double)
    covars = [[ numpy.matrix(numpy.eye(d,d)) for j in xrange(m)] for i in xrange(n)]
    
    w[0][0] = 0.5
    w[0][1] = 0.5
    w[1][0] = 0.5
    w[1][1] = 0.5    
    means[0][0][0] = 0.5
    means[0][0][1] = 0.5
    means[0][1][0] = 0.5    
    means[0][1][1] = 0.5
    means[1][0][0] = 0.5
    means[1][0][1] = 0.5
    means[1][1][0] = 0.5    
    means[1][1][1] = 0.5    

    gmmhmm = GMHMM(n,m,d,A,means,covars,w,pi,init_type='user',verbose=True)
    
    obs = numpy.array([ [0.3,0.3], [0.1,0.1], [0.2,0.2]])
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,10)
    print
    print "Pi",gmmhmm.pi
    print "A",gmmhmm.A
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_rand():
    n = 5
    m = 4
    d = 2
    atmp = numpy.random.random_sample((n, n))
    row_sums = atmp.sum(axis=1)
    a = numpy.array(atmp / row_sums[:, numpy.newaxis], dtype=numpy.double)    

    wtmp = numpy.random.random_sample((n, m))
    row_sums = wtmp.sum(axis=1)
    w = numpy.array(wtmp / row_sums[:, numpy.newaxis], dtype=numpy.double)
    
    means = numpy.array((0.6 * numpy.random.random_sample((n, m, d)) - 0.3), dtype=numpy.double)
    covars = numpy.zeros( (n,m,d,d) )
    
    for i in xrange(n):
        for j in xrange(m):
            for k in xrange(d):
                covars[i][j][k][k] = 1    
    
    pitmp = numpy.random.random_sample((n))
    pi = numpy.array(pitmp / sum(pitmp), dtype=numpy.double)

    gmmhmm = GMHMM(n,m,d,a,means,covars,w,pi,init_type='user',verbose=True)
    
    obs = numpy.array((0.6 * numpy.random.random_sample((40,d)) - 0.3), dtype=numpy.double)
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,1000)
    print
    print "Pi",gmmhmm.pi
    print "A",gmmhmm.A
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars"""
    
def test_discrete():

    ob5 = (0,3,1,2,1,0,2,3,0,1,0,2,0,1,2,2,0,3,0,0,2,0,0,1,2,0,1,2,0)
    print "Doing Baum-welch"
    
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
    hmm2.train(numpy.array(ob5),iterations=10000,epsilon=.00001)
    print "Pi",hmm2.pi
    print "A",hmm2.A
    print "B", hmm2.B
    
    
#test_simple()
#test_rand()
test_discrete()