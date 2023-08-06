cimport cDPQ
import numpy as np

cimport numpy as np
from cpython cimport array

def coptimum_reparamN(np.ndarray[double, ndim=1, mode="c"] mq, np.ndarray[double, ndim=1, mode="c"] time,
                      np.ndarray[double, ndim=2, mode="c"] q, lam1=0.0):
    """
    cython interface calculates the warping to align a set of srfs q to a single srsf mq

    :param mq: vector of size N samples of first SRSF
    :param time: vector of size N describing the sample points
    :param q: numpy ndarray of shape (M,N) of M srsfs with N samples
    :param lam1: controls the amount of elasticity (default = 0.0)

    :rtype numpy ndarray
    :return gam: describing the warping functions used to align columns of q with mq

    """
    cdef int M, N, n1
    cdef double lam
    M, N = q.shape[0], q.shape[1]
    n1 = 1
    lam = lam1
    cdef np.ndarray[double, ndim=1, mode="c"] G = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] T = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] qi = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] size = np.zeros(1)

    gam = np.zeros((M, N))
    sizes = np.zeros(N, dtype=np.int32)
    Go = np.zeros((M, N))
    To = np.zeros((M, N))
    for k in xrange(0, N):
        qi = np.ascontiguousarray(q[:, k])

        cDPQ.DynamicProgrammingQ2(&mq[0], &time[0], &qi[0], &time[0], n1, M, M, &time[0], &time[0], M, M, &G[0],
                                  &T[0], &size[0], lam)
        sizes[k] = np.int32(size)
        Go[:, k] = G
        To[:, k] = T

    for k in xrange(0, N):
        gam0 = np.interp(time, To[0:sizes[k], k], Go[0:sizes[k], k])
        gam[:, k] = (gam0 - gam0[0]) / (gam0[-1] - gam0[0])

    return gam

def coptimum_reparamN2(np.ndarray[double, ndim=2, mode="c"] q1, np.ndarray[double, ndim=1, mode="c"] time,
                       np.ndarray[double, ndim=2, mode="c"] q2, lam1=0.0):
    """
    cython interface calculates the warping to align a set of srsfs q1 to another set of srsfs q2

    :param q1: numpy ndarray of shape (M,N) of M srsfs with N samples
    :param time: vector of size N describing the sample points
    :param q2: numpy ndarray of shape (M,N) of M srsfs with N samples
    :param lam1: controls the amount of elasticity (default = 0.0)

    :rtype numpy ndarray
    :return gam: describing the warping functions used to align columns of q with mq

    """
    cdef int M, N, n1
    cdef double lam
    M, N = q1.shape[0], q1.shape[1]
    n1 = 1
    lam = lam1
    cdef np.ndarray[double, ndim=1, mode="c"] G = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] T = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] q1i = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] q2i = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] size = np.zeros(1)

    gam = np.zeros((M, N))
    sizes = np.zeros(N, dtype=np.int32)
    Go = np.zeros((M, N))
    To = np.zeros((M, N))
    for k in xrange(0, N):
        q1i = np.ascontiguousarray(q1[:, k])
        q2i = np.ascontiguousarray(q2[:, k])

        cDPQ.DynamicProgrammingQ2(&q1i[0], &time[0], &q2i[0], &time[0], n1, M, M, &time[0], &time[0], M, M, &G[0],
                                  &T[0], &size[0], lam)
        sizes[k] = np.int32(size)
        Go[:, k] = G
        To[:, k] = T

    for k in xrange(0, N):
        gam0 = np.interp(time, To[0:sizes[k], k], Go[0:sizes[k], k])
        gam[:, k] = (gam0 - gam0[0]) / (gam0[-1] - gam0[0])

    return gam

def coptimum_reparam(np.ndarray[double, ndim=1, mode="c"] q1, np.ndarray[double, ndim=1, mode="c"] time,
                     np.ndarray[double, ndim=1, mode="c"] q2, lam1=0.0):
    """
    cython interface for calculates the warping to align srsf q2 to q1

    :param q1: vector of size N samples of first SRSF
    :param time: vector of size N describing the sample points
    :param q2: vector of size N samples of second SRSF
    :param lam1: controls the amount of elasticity (default = 0.0)

    :rtype vector
    :return gam: describing the warping function used to align q2 with q1
    """
    cdef int M, n1
    cdef double lam
    M = q1.shape[0]
    n1 = 1
    lam = lam1
    cdef np.ndarray[double, ndim=1, mode="c"] G = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] T = np.zeros(M)
    cdef np.ndarray[double, ndim=1, mode="c"] size = np.zeros(1)

    sizes = np.zeros(1, dtype=np.int32)
    Go = np.zeros((M, 1))
    To = np.zeros((M, 1))
    cDPQ.DynamicProgrammingQ2(&q1[0], &time[0], &q2[0], &time[0], n1, M, M, &time[0], &time[0], M, M, &G[0],
                              &T[0], &size[0], lam)
    sizes = np.int32(size)
    Go[:, 0] = G
    To[:, 0] = T
    gam0 = np.interp(time, To[0:sizes[0], 0], Go[0:sizes[0], 0])
    gam = (gam0 - gam0[0]) / (gam0[-1] - gam0[0])

    return gam
