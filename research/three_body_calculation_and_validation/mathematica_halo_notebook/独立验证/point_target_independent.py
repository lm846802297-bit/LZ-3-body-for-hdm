import numpy as np, math
from numpy.polynomial.legendre import leggauss
from pathlib import Path
import csv, json
# Independent pointlike scalar target: Feynman current (P+P')^mu/(2 mA).
I2=np.eye(2,dtype=complex); Z=np.zeros((2,2),complex)
sigmas=[np.array([[0,1],[1,0]],complex),np.array([[0,-1j],[1j,0]],complex),np.diag([1,-1]).astype(complex)]
gamma=[np.block([[I2,Z],[Z,-I2]])]+[np.block([[Z,s],[-s,Z]]) for s in sigmas]
ident=np.eye(4,dtype=complex)
def dot(a,b):return a[0]*b[0]-np.dot(a[1:],b[1:])
def slash(a):return gamma[0]*a[0]-sum(gamma[j]*a[j] for j in range(1,4))
def width(m,ms,dm,g=1.):
 m2=m+dm
 return g*g*math.sqrt(dm*dm-ms*ms)*(((2*m+dm)**2-ms*ms)**1.5)/(16*math.pi*m2**3) if dm>ms else 0.
def integrate(erkev,vkms,order,include_recoil):
 m=1000.; ma=131*.93149410242; ms=.0003; dm=.001; mv=10.; gamma2=width(m,ms,dm); er=erkev*1e-6
 beta=vkms/299792.458; E=m/math.sqrt(1-beta*beta); p=E*beta;q=math.sqrt(er*(2*ma+er));lo=(m+ms)**2;hi=m*m+2*p*q-2*(E+ma)*er
 if hi<=lo:return 0.,0.
 if hi >= (m+dm)**2:raise ValueError('on-shell region requires separate treatment')
 pin=np.array([E,0.,0.,p]);pinspin=slash(pin)+m*ident
 us,uw=leggauss(order[0]);zs,zw=leggauss(order[1]);ps,pw=leggauss(order[2]); us=(us+1)/2;uw=uw/2
 result=0.
 for u,wu in zip(us,uw):
  w2=lo+(hi-lo)*u*u;root=math.sqrt(w2);cq=np.clip((w2-m*m+2*(E+ma)*er)/(2*p*q),-1,1)
  qv=np.array([q*math.sqrt(max(0,1-cq*cq)),0.,q*cq]);Qv=np.array([0.,0.,p])-qv;Q0=E-er
  ez=Qv/np.linalg.norm(Qv);ref=np.array([0.,0.,1.]) if abs(ez[2])<.9 else np.array([0.,1.,0.]);ex=np.cross(ref,ez);ex/=np.linalg.norm(ex);ey=np.cross(ez,ex)
  lam=max(0.,(w2-(m+ms)**2)*(w2-(m-ms)**2));kabs=math.sqrt(lam)/(2*root);estar=(w2-m*m+ms*ms)/(2*root)
  weight=wu*2*(hi-lo)*u*math.sqrt(lam)/w2
  nuc=gamma[0] if not include_recoil else gamma[0]*(2*ma+er)/(2*ma)-sum(gamma[j]*qv[j-1]/(2*ma) for j in range(1,4))
  subtotal=0.
  for z,wz in zip(zs,zw):
   for x,wx in zip(ps,pw):
    phi=math.pi*(x+1);ks=kabs*(z*ez+math.sqrt(max(0,1-z*z))*(math.cos(phi)*ex+math.sin(phi)*ey));qdot=np.dot(Qv,ks)
    k=np.r_[(Q0*estar+qdot)/root,ks+Qv*(estar/root+qdot/(root*(Q0+root)))]; pout=np.r_[Q0,Qv]-k
    d1=dot(pin-k,pin-k)-(m+dm)**2;d2=w2-(m+dm)**2+1j*(m+dm)*gamma2
    c1=nuc@(slash(pin-k)+(m+dm)*ident)/d1
    c2=(slash(pout+k)+(m+dm)*ident)@nuc/d2
    chain=c1+c2;bar=gamma[0]@chain.conj().T@gamma[0]
    spin=(np.trace((slash(pout)+m*ident)@chain@pinspin@bar).real/2)
    subtotal+=wz*wx/2*spin
  result+=weight*subtotal
 pref=ma/(256*math.pi**3*p*p*(mv*mv+2*ma*er)**2)
 return result,pref*result
rows=[]
for er in [101.,109.16,110.,150.,200.,267.,300.,542.,654.94,700.]:
 for n in [8,12,16,24]:
  a,ds=integrate(er,776.,(n,n,max(8,n//2)),False)
  _,full=integrate(er,776.,(n,n,max(8,n//2)),True)
  rows.append(dict(ER_keV=er,n=n,nphi=max(8,n//2),I6=a,dsigma_static=ds,dsigma_scalar_current=full,full_over_static=(full/ds if ds else 'closed')))
  print('ER',er,'n',n,'I6',a,'static',ds,'full/static',full/ds if ds else 'closed',flush=True)
out=Path(__file__).parent/'point_target_convergence.csv'
with out.open('w',newline='',encoding='utf-8') as f:
 writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
