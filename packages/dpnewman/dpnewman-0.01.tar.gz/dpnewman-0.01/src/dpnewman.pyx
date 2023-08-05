# -*- coding: utf-8 -*-
import numpy as np
cimport numpy as np
from libc.math cimport log
from scipy.misc import logsumexp

cdef double digamma(double x):
    cdef double result = 0.0
    cdef double xx, xx2, xx4
    assert x>=0, "digamma error"
    while(x<7):
        result -= 1.0/x
        x+=1.0
    x -= 1.0/2.0
    xx = 1.0/x
    xx2 = xx*xx
    xx4 = xx2*xx2
    result += log(x)+(1./24.)*xx2-(7.0/960.0)*xx4+(31.0/8064.0)*xx4*xx2-(127.0/30720.0)*xx4*xx4
    return result;

cdef class DPNewman:
    cdef int _T, _niter
    cdef double _c1, _c2, _phi0, _thresh

    def __init__(self,int T=10, double c1=1.0, double c2=1.0, double phi = 0.001, double thresh=0.001, int niter = 500):
        self._T = T #クラスタ数
        self._c1 = c1
        self._c2 = c2
        self._phi0 = phi
        self._thresh = thresh
        self._niter = niter

    cdef int _N
    cdef double _lambda1, _lambda2
    cdef public np.ndarray _q,_s

    def fit(self,np.ndarray[np.float64_t, ndim=2] mat):
        cdef double ll,maxll,lastll
        lastll = -float('inf')
        maxll = -float('inf')
        self._N = mat.shape[0]
        cdef np.ndarray[np.float64_t, ndim=1] _tau1 = np.random.random(self._T)#クラス数用意
        cdef np.ndarray[np.float64_t, ndim=1] _tau2 = np.random.random(self._T)#同上
        cdef np.ndarray[np.float64_t, ndim=2] _psi = np.random.random((self._T,self._N))
        self._lambda1 = np.random.rand()
        self._lambda2 = np.random.rand()
        cdef np.ndarray[np.float64_t, ndim=2] _q = np.zeros((self._N,self._T))#頂点ごとの帰属確率
        cdef np.ndarray[np.float64_t, ndim=2] _s = np.zeros((self._N,self._T))#si
        cdef np.ndarray[np.float64_t, ndim=2] _phi = np.zeros((self._T,self._N))+self._phi0#phi
        cdef np.ndarray[np.float64_t, ndim=1] _digtau = np.zeros(self._T)
        cdef np.ndarray[np.float64_t, ndim=1] _digpsi = np.zeros(self._T)
        cdef np.ndarray[np.float64_t, ndim=2] _digpsi2 = np.random.random((self._T,self._N))
        cdef int i
        for i in xrange(self._niter):
            self._estep(mat,_q,_s,_tau1,_tau2,_psi,_digtau,_digpsi,_digpsi2)
            #update tau1
            _tau1 = _q.sum(axis=0)+1.0
            self._mstep(mat,_q,_s,_tau1,_tau2,_psi,_phi)
            ll = self.loglikelihood(_q,_s)
            print ll
            if maxll<ll:#現時点での尤度最大時の値を保持
               maxll=ll
               self._q = _q.copy()
               self._s = _s.copy()
            if np.abs(ll-lastll)<self._thresh:#殆ど変化しなくなったら修了
                break
            lastll=ll
        return maxll

    cdef double loglikelihood(self,np.ndarray[np.float64_t, ndim=2] _q,np.ndarray[np.float64_t, ndim=2] _s):
        return np.sum(_q*_s)

    cdef void _estep(self,np.ndarray[np.float64_t, ndim=2] mat, np.ndarray[np.float64_t, ndim=2] _q,
                np.ndarray[np.float64_t, ndim=2] _s, np.ndarray[np.float64_t, ndim=1] _tau1,
                np.ndarray[np.float64_t, ndim=1] _tau2, np.ndarray[np.float64_t, ndim=2] _psi,
                np.ndarray[np.float64_t, ndim=1] _digtau,np.ndarray[np.float64_t, ndim=1] _digpsi,
                np.ndarray[np.float64_t, ndim=2] _digpsi2):

        cdef int i,r,l,j

        for r in xrange(self._T):
            _digtau[r] = digamma(_tau2[r])-digamma(_tau1[r]+_tau2[r])
            _digpsi[r] = digamma(np.sum(_psi[r]))
            for j in xrange(self._N):
                _digpsi2[r,j] = digamma(_psi[r,j])
        for i in xrange(self._N):
            for r in xrange(self._T):
                _s[i,r]=0.0
                #stick-breakingでυ(Newmanのπに相当)を計算
                if r<(self._T-1):
                    _s[i,r]+= _digtau[r]#最後以外計算
                if r>0:#0オリジンのため
                   for l in xrange(r):#最初以外自分以下のインデックスの値を計算
                        _s[i,r]+= _digtau[l]
                for j in xrange(self._N):
                    _s[i,r]+=mat[j,i]*(_digpsi2[r,j]-_digpsi[r])
        #calculate q_i_r
        cdef double ibase
        for i in xrange(self._N):
            ibase = logsumexp(_s[i])
            for r in xrange(self._T):
                _q[i,r]=np.exp(_s[i,r] - ibase)

    cdef void _mstep(self,np.ndarray[np.float64_t, ndim=2] mat, np.ndarray[np.float64_t, ndim=2] _q,
                np.ndarray[np.float64_t, ndim=2] _s, np.ndarray[np.float64_t, ndim=1] _tau1,
                np.ndarray[np.float64_t, ndim=1] _tau2, np.ndarray[np.float64_t, ndim=2] _psi,
                np.ndarray[np.float64_t, ndim=2] _phi):
        cdef int i,r,j,k
        #update tau2
        for r in xrange(self._T):
            _tau2[r] = self._lambda1/self._lambda2
            for i in xrange(self._N):
                _tau2[r]+=np.sum(_q[i][r+1:])
        #update psi
        for r in xrange(self._T):
            for j in xrange(self._N):
                _psi[r,j] = _phi[r,j]
                for i in range(self._N):
                    _psi[r,j]+=mat[j,i]*_q[i,r]
        #update lambda
        self._lambda1 = self._c1+self._T-1
        self._lambda2 = self._c2
        for k in xrange(self._T-1):
            self._lambda2 -= (digamma(_tau2[k])-digamma(_tau1[k]+_tau2[k]))

    def get_cluster(self):
        return np.argsort(self._q,axis=1).T[-1]
