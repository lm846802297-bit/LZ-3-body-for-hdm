"""Independent numerical kernel for Eq. (6) of the LZ 3-body manuscript.
Natural units (+---), all masses and energies in GeV.
This computes the spin trace and the W^2,z,phi* integral only; no halo,
nuclear response, mediator prefactor, or overall coupling prefactor.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss

C_KM_S = 299_792.458

@dataclass(frozen=True)
class Point:
    p: np.ndarray
    p_prime: np.ndarray
    k: np.ndarray
    K: np.ndarray
    q: np.ndarray
    W2: float

def dot(a, b):
    return float(a[0]*b[0] - np.dot(a[1:], b[1:]))

def boost(v, beta):
    b2=float(np.dot(beta,beta))
    if b2 < 1e-30: return v.copy()
    if b2 >= 1: raise ValueError("superluminal boost")
    b=math.sqrt(b2); gamma=1/math.sqrt(1-b2); bh=beta/b
    par=float(np.dot(v[1:],bh))
    return np.r_[gamma*(v[0]+b*par),
                 v[1:]+((gamma-1)*par+gamma*b*v[0])*bh]

def limits(mchi, ms, mA, ER, speed_kms):
    beta=speed_kms/C_KM_S; gamma=1/math.sqrt(1-beta*beta)
    E=mchi*gamma; p=mchi*gamma*beta
    q=math.sqrt(2*mA*ER+ER*ER)
    return (mchi+ms)**2, mchi*mchi+2*p*q-2*(E+mA)*ER

def build_point(mchi, ms, mA, ER, speed_kms, W2, z, phi):
    beta=speed_kms/C_KM_S; gamma=1/math.sqrt(1-beta*beta)
    E=mchi*gamma; pz=mchi*gamma*beta
    p=np.array([E,0.,0.,pz])
    qmag=math.sqrt(2*mA*ER+ER*ER)
    cq=(W2-mchi*mchi+2*(E+mA)*ER)/(2*pz*qmag)
    if abs(cq)>1+2e-8: raise ValueError(f"unphysical cos(theta_q)={cq}")
    cq=min(1.,max(-1.,cq)); sq=math.sqrt(max(0.,1-cq*cq))
    q=np.array([ER,qmag*sq,0.,qmag*cq]); K=p-q
    if abs(dot(K,K)-W2)>2e-7*max(1.,W2): raise ArithmeticError("K^2 != W^2")
    W=math.sqrt(W2); betaK=K[1:]/K[0]
    pstar=boost(p,-betaK); e3=pstar[1:]/np.linalg.norm(pstar[1:])
    ref=np.array([1.,0.,0.])
    if abs(np.dot(ref,e3))>.9: ref=np.array([0.,1.,0.])
    e1=np.cross(ref,e3); e1/=np.linalg.norm(e1); e2=np.cross(e3,e1)
    lam=(W2-(mchi+ms)**2)*(W2-(mchi-ms)**2)
    if lam < -1e-8: raise ValueError("closed chi1-s phase space")
    kabs=math.sqrt(max(0.,lam))/(2*W)
    Ek=(W2-mchi*mchi+ms*ms)/(2*W)
    Ep=(W2+mchi*mchi-ms*ms)/(2*W)
    n=z*e3+math.sqrt(max(0.,1-z*z))*(math.cos(phi)*e1+math.sin(phi)*e2)
    k=boost(np.r_[Ek,kabs*n],betaK)
    pp=boost(np.r_[Ep,-kabs*n],betaK)
    return Point(p,pp,k,K,q,W2)

I2=np.eye(2,dtype=complex); Z2=np.zeros((2,2),complex)
s1=np.array([[0,1],[1,0]],complex)
s2=np.array([[0,-1j],[1j,0]],complex)
s3=np.array([[1,0],[0,-1]],complex)
GAMMA=(np.block([[I2,Z2],[Z2,-I2]]),
       np.block([[Z2,s1],[-s1,Z2]]),
       np.block([[Z2,s2],[-s2,Z2]]),
       np.block([[Z2,s3],[-s3,Z2]]))
ID4=np.eye(4,dtype=complex)

def slash(p):
    return GAMMA[0]*p[0]-GAMMA[1]*p[1]-GAMMA[2]*p[2]-GAMMA[3]*p[3]

def vertices(point, mchi2, width=0.):
    p,pp,k=point.p,point.p_prime,point.k
    d1=dot(p-k,p-k)-mchi2*mchi2
    d2=point.W2-mchi2*mchi2+1j*mchi2*width
    if abs(d1)<1e-30 or abs(d2)<1e-30: raise ZeroDivisionError("propagator pole")
    before=GAMMA[0]@(slash(p-k)+mchi2*ID4)/d1
    after=(slash(pp+k)+mchi2*ID4)@GAMMA[0]/d2
    return before,after

def spin_trace(point,mchi,mchi2,width=0.):
    before,after=vertices(point,mchi2,width)
    pin=slash(point.p)+mchi*ID4; pout=slash(point.p_prime)+mchi*ID4
    def tr(G):
        Gbar=GAMMA[0]@G.conj().T@GAMMA[0]
        return np.trace(pout@G@pin@Gbar)/2.
    lb,la,lt=tr(before),tr(after),tr(before+after)
    return {"before":float(np.real_if_close(lb).real),
            "after":float(np.real_if_close(la).real),
            "interference":float(np.real_if_close(lt-lb-la).real),
            "total":float(np.real_if_close(lt).real),
            "imaginary_residual":float(abs(np.imag(lt)))}

def lambda_dimensionless(W2,mchi,ms):
    return ((W2-(mchi+ms)**2)*(W2-(mchi-ms)**2))/(W2*W2)

def chi2_width_dirac_scalar(mchi, ms, delta_m, g2):
    """Conditional pole width for Dirac chi2 -> Dirac chi1 + scalar s.

    Assumes a pure scalar off-diagonal Yukawa coupling, no other open decay
    channels, and the width convention written in the manuscript's Eq. (8).
    All masses and the returned width are in GeV.
    """
    mchi2 = mchi + delta_m
    lam = (mchi2**4 + mchi**4 + ms**4
           - 2*mchi2*mchi2*mchi*mchi
           - 2*mchi2*mchi2*ms*ms
           - 2*mchi*mchi*ms*ms)
    if lam <= 0:
        return 0.0
    return (abs(g2)**2/(16*math.pi*mchi2**3)
            * math.sqrt(lam) * ((mchi2+mchi)**2-ms*ms))


def reduced_kernel(mchi,ms,delta_m,mA,ER,speed_kms,width=0.,nw=16,nz=16,nphi=8):
    """Integral in Eq. (6), excluding its printed overall prefactor."""
    wmin,wmax=limits(mchi,ms,mA,ER,speed_kms)
    if wmax<=wmin: return 0.
    xw,ww=leggauss(nw); xz,wz=leggauss(nz); xp,wp=leggauss(nphi)
    wvals=.5*(wmax+wmin)+.5*(wmax-wmin)*xw
    wweights=.5*(wmax-wmin)*ww
    phis=math.pi*(xp+1.); phiweights=.5*wp
    total=0.; mchi2=mchi+delta_m
    for W2,wwi in zip(wvals,wweights):
        lam=lambda_dimensionless(float(W2),mchi,ms)
        if lam<0: continue
        angular=0.
        for z,wzi in zip(xz,wz):
            avg=0.
            for phi,wpi in zip(phis,phiweights):
                pt=build_point(mchi,ms,mA,ER,speed_kms,float(W2),float(z),float(phi))
                avg+=wpi*spin_trace(pt,mchi,mchi2,width)["total"]
            angular+=wzi*avg
        total+=wwi*math.sqrt(lam)*angular
    return float(total)

def residuals(pt,mchi,ms,mA):
    P=np.array([mA,0.,0.,0.]); Pf=P+pt.q
    closure=pt.p+P-pt.p_prime-pt.k-Pf
    return {"p2-mchi2":dot(pt.p,pt.p)-mchi*mchi,
            "pprime2-mchi2":dot(pt.p_prime,pt.p_prime)-mchi*mchi,
            "k2-ms2":dot(pt.k,pt.k)-ms*ms,
            "Pprime2-mA2":dot(Pf,Pf)-mA*mA,
            "four_momentum_max":float(np.max(np.abs(closure))),
            "K2-W2":dot(pt.K,pt.K)-pt.W2}
