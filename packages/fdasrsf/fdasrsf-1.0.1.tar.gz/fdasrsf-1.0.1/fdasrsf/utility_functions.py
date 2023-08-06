"""
Utility functions for SRSF Manipulations

moduleauthor:: Derek Tucker <dtucker@stat.fsu.edu>

"""

from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.integrate import simps, cumtrapz
from scipy.linalg import norm
from scipy.stats.mstats import mquantiles
from numpy import zeros, interp, finfo, double, sqrt, diff, linspace, arccos, sin, cos, arange, ascontiguousarray, round
from numpy import ones, real, trapz, pi, cumsum
import numpy.random as rn
import optimum_reparamN as orN


def smooth_data(f, sparam):
    """
    This function smooths a collection of functions using a box filter

    :param f: numpy ndarray of shape (M,N) of M functions with N samples
    :param sparam: Number of times to run box filter (default = 25)

    :rtype: numpy ndarray
    :return f: smoothed functions functions

    """
    M = f.shape[0]
    N = f.shape[1]

    for k in xrange(1, sparam):
        for r in xrange(0, N):
            f[1:(M - 2), r] = (f[0:(M - 3), r] + 2 * f[1:(M - 2), r] + f[2:(M - 1), r]) / 4
    return f


def gradient_spline(time, f):
    """
    This function takes the gradient of f using b-spline smoothing

    :param time: vector of size N describing the sample points
    :param f: numpy ndarray of shape (M,N) of M functions with N samples

    :rtype: tuple of numpy ndarray
    :return f0: smoothed functions functions
    :return g: first derivative of each function
    :return g2: second derivative of each function

    """
    M = f.shape[0]
    if f.ndim > 1:
        N = f.shape[1]
        f0 = zeros((M, N))
        g = zeros((M, N))
        g2 = zeros((M, N))
        for k in xrange(0, N):
            tmp_spline = InterpolatedUnivariateSpline(time, f[:, k])
            f0[:, k] = tmp_spline(time)
            g[:, k] = tmp_spline(time, 1)
            g2[:, k] = tmp_spline(time, 2)
    else:
        tmp_spline = InterpolatedUnivariateSpline(time, f)
        f0 = tmp_spline(time)
        g = tmp_spline(time, 1)
        g2 = tmp_spline(time, 2)

    return f0, g, g2


def f_to_srvf(f, time):
    """
    converts f to a square-root slope function (SRSF)

    :param f: vector of size N samples
    :param time: vector of size N describing the sample points

    :rtype: vector
    :return q: srsf of f

    """
    eps = finfo(double).eps
    f0, g, g2 = gradient_spline(time, f)
    q = g / sqrt(abs(g) + eps)
    return q


def optimum_reparam(q1, time, q2, lam=0.0):
    """
    calculates the warping to align srsf q2 to q1

    :param q1: vector of size N or array of NxM samples of first SRSF
    :param time: vector of size N describing the sample points
    :param q2: vector of size N or array of NxM samples samples of second SRSF
    :param lam: controls the amount of elasticity (default = 0.0)

    :rtype: vector
    :return gam: describing the warping function used to align q2 with q1

    """
    if q1.ndim == 1 and q2.ndim == 1:
        gam = orN.coptimum_reparam(ascontiguousarray(q1), time, ascontiguousarray(q2), lam)

    if q1.ndim == 1 and q2.ndim == 2:
        gam = orN.coptimum_reparamN(ascontiguousarray(q1), time, ascontiguousarray(q2), lam)

    if q1.ndim == 2 and q2.ndim == 2:
        gam = orN.coptimum_reparamN2(ascontiguousarray(q1), time, ascontiguousarray(q2), lam)

    return gam


def elastic_distance(f1, f2, time, lam=0.0):
    """"
    calculates the distnaces between function, where f1 is aligned to f2. In other words
    caluclates the elastic distances

    :param f1: vector of size N
    :param f2: vector of size N
    :param time: vector of size N describing the sample points
    :param lam: controls the elasticity (default = 0.0)

    :rtype: scalar
    :return Dy: amplitude distance
    :return Dx: phase distance

    """
    q1 = f_to_srvf(f1, time)
    q2 = f_to_srvf(f2, time)

    gam = optimum_reparam(q1, time, q2, lam)
    fw = interp((time[-1] - time[0]) * gam + time[0], time, f2)
    qw = f_to_srvf(fw, time)

    Dy = sqrt(trapz((qw - q1) ** 2, time))
    M = time.shape[0]
    psi = sqrt(diff(gam) * (M - 1))
    mu = ones(M - 1)
    Dx = real(arccos(sum(mu * psi) / double(M - 1)))

    return Dy, Dx


def invertGamma(gam):
    """
    finds the inverse of the diffeomorphism gamma

    :param gam: vector describing the warping function

    :rtype: vector
    :return gamI: inverse of gam

    """
    N = gam.size
    x = arange(0, N) / float(N - 1)
    gamI = interp(x, gam, x)
    gamI[-1] = 1.0
    gamI = gamI / gamI[-1]
    return gamI


def SqrtMeanInverse(gam):
    """
    finds the inverse of the mean of the set of the diffeomorphisms gamma

    :param gam: numpy ndarray of shape (M,N) of M warping functions with N samples

    :rtype: vector
    :return gamI: inverse of gam

    """
    eps = finfo(double).eps
    n = gam.shape[1]
    T1 = gam.shape[0]
    dt = 1 / float(T1 - 1)
    psi = zeros((T1 - 1, n))
    for k in xrange(0, n):
        psi[:, k] = sqrt(diff(gam[:, k]) / dt + eps)

    # Find Direction
    mnpsi = psi.mean(axis=1)
    a = mnpsi.repeat(n)
    d1 = a.reshape(T1 - 1, n)
    d = (psi - d1) ** 2
    dqq = sqrt(d.sum(axis=0))
    min_ind = dqq.argmin()
    mu = psi[:, min_ind]
    maxiter = 20
    tt = 1
    lvm = zeros(maxiter)
    vec = zeros((T1 - 1, n))
    for itr in xrange(0, maxiter):
        for k in xrange(0, n):
            dot = simps(mu * psi[:, k], linspace(0, 1, T1 - 1))
            if dot > 1:
                dot = 1
            elif dot < (-1):
                dot = -1
            leng = arccos(dot)
            if leng > 0.0001:
                vec[:, k] = (leng / sin(leng)) * (psi[:, k] - cos(leng) * mu)
            else:
                vec[:, k] = zeros(T1 - 1)
        vm = vec.mean(axis=1)
        vm1 = vm * vm
        lvm[itr] = sqrt(vm1.sum() * dt)
        if lvm[itr] == 0:
            mu = mu
            break

        mu = cos(tt * lvm[itr]) * mu + (sin(tt * lvm[itr]) / lvm[itr]) * vm
        if lvm[itr] < 1e-6 or itr >= maxiter:
            break

    tmp = mu * mu
    gam_mu = zeros(T1)
    gam_mu[1:] = tmp.cumsum() / T1
    gam_mu = (gam_mu - gam_mu.min()) / (gam_mu.max() - gam_mu.min())
    gamI = invertGamma(gam_mu)
    return gamI


def SqrtMean(gam):
    """
    calculates the srsf of warping functions with corresponding shooting vectors

    :param gam: numpy ndarray of shape (M,N) of M warping functions with N samples

    :rtype: 2 numpy ndarray and vector
    :return mu: Karcher mean psi function
    :return gam_mu: vector of dim N which is the Karcher mean warping function
    :return psi: numpy ndarray of shape (M,N) of M SRSF of the warping functions
    :return vec: numpy ndarray of shape (M,N) of M shooting vectors

    """
    n = gam.shape[1]
    TT = double(gam.shape[0])
    psi = zeros((TT - 1, n))
    for k in xrange(0, n):
        psi[:, k] = sqrt(diff(gam[:, k]) * TT)

    # Find Direction
    mnpsi = psi.mean(axis=1)
    a = mnpsi.repeat(n)
    d1 = a.reshape(TT - 1, n)
    d = (psi - d1) ** 2
    dqq = sqrt(d.sum(axis=0))
    min_ind = dqq.argmin()
    mu = psi[:, min_ind]
    maxiter = 20
    tt = 1
    lvm = zeros(maxiter)
    vec = zeros((TT - 1, n))
    for itr in xrange(0, maxiter):
        for k in xrange(0, n):
            dot = simps(mu * psi[:, k], linspace(0, 1, TT - 1))
            if dot > 1:
                dot = 1
            elif dot < (-1):
                dot = -1
            leng = arccos(dot)
            if leng > 0.0001:
                vec[:, k] = (leng / sin(leng)) * (psi[:, k] - cos(leng) * mu)
            else:
                vec[:, k] = zeros(TT - 1)
        vm = vec.mean(axis=1)
        vm1 = vm * vm
        lvm[itr] = sqrt(vm1.sum() / TT)
        if lvm[itr] == 0:
            mu = mu
            break

        mu = cos(tt * lvm[itr]) * mu + (sin(tt * lvm[itr]) / lvm[itr]) * vm
        if lvm[itr] < 1e-6 or itr >= maxiter:
            break

    tmp = mu * mu
    gam_mu = zeros(TT)
    gam_mu[1:] = tmp.cumsum() / TT
    gam_mu = (gam_mu - gam_mu.min()) / (gam_mu.max() - gam_mu.min())

    return mu, gam_mu, psi, vec


def cumtrapzmid(x, y, c):
    """
    cummulative trapzodial numerical integration taken from midpoint

    :param x: vector of size N descibing the time samples
    :param y: vector of size N describing the function
    :param c: midpoint

    :rtype: vector
    :return fa: cummulative integration

    """
    a = x.shape[0]
    mid = int(round(a / 2.))

    # case < mid
    fa = zeros(a)
    tmpx = x[0:mid]
    tmpy = y[0:mid]
    tmp = c + cumtrapz(tmpy[::-1], tmpx[::-1], initial=0)
    fa[0:mid] = tmp[::-1]

    # case >= mid
    fa[mid:a] = c + cumtrapz(y[mid - 1:a - 1], x[mid - 1:a - 1], initial=0)

    return fa


def rgam(N, sigma, num):
    """
    Generates random warping functions

    :param N: length of warping function
    :param sigma: variance of warping functions
    :param num: number of warping functions
    :return: gam: numpy ndarray of warping functions

    """
    gam = zeros((N, num))

    TT = N - 1
    time = linspace(0, 1, TT)
    mu = sqrt(ones(N - 1) * TT / double(N - 1))
    omega = (2 * pi) / double(TT)
    for k in xrange(0, num):
        alpha_i = rn.normal(scale=sigma)
        v = alpha_i * ones(TT)
        cnt = 1
        for l in range(2, 11):
            alpha_i = rn.normal(scale=sigma)
            #odd
            if l % 2 != 0:
                v = v + alpha_i * sqrt(2) * cos(cnt * omega * time)
                cnt += 1

            #even
            if l % 2 == 0:
                v = v + alpha_i * sqrt(2) * cos(cnt * omega * time)
        v = v.reshape((TT, 1))
        mu = mu.reshape((TT, 1))
        tmp = mu.dot(v.transpose())
        v = v - tmp.dot(mu) / double(TT)
        vn = norm(v) / sqrt(TT)
        psi = cos(vn) * mu + sin(vn) * v / vn
        gam[1:, k] = cumsum(psi * psi) / double(TT)

    return gam


def outlier_detection(q, time, mq, k=1.5):
    """
    calculates outlier's using geodesci distnaces of the SRSFs from the median

    :param q: numpy ndarray of N x M of M SRS functions with N samples
    :param time: vector of size N describing the sample points
    :param mq: median calculated using :func:`time_warping.srsf_align`
    :param k: cutoff threshold (default = 1.5)

    :return: q_outlier: outlier functions

    """
    N = q.shape[1]
    ds = zeros(N)
    for kk in xrange(0, N):
        ds[kk] = sqrt(simps((mq - q[:, kk]) ** 2, time))

    quartile_range = mquantiles(ds)
    IQR = quartile_range[2] - quartile_range[0]

    thresh = quartile_range[2] + k * IQR

    ind = (ds > thresh).nonzero()

    q_outlier = q[:, ind]

    return q_outlier