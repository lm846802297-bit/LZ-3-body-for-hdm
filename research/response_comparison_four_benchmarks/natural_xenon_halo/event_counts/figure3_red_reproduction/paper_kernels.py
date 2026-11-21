"""Static-charge spectra under explicit halo assumptions. GeV and km/s internally."""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.interpolate import RectBivariateSpline
from scipy.special import erf, exprel, roots_legendre, spherical_jn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/"figure3_source_audit"))
import independent_charge as phys

TABLE, NUCLEI_KG = phys.isotope_inputs()
ISOTOPES = tuple(int(a) for a in TABLE.index)
AFH = tuple(int(a) for a in TABLE.index[TABLE.AFH_default_density_matrix_available_in_v6])
TO_CM2_KEV = phys.GEV2_CM2*1e-6
EXPOSURE_FLUX = phys.EXPOSURE * NUCLEI_KG * (phys.RHO/phys.MCHI) * 1e5 * 86400
OUT = HERE/"output"


@dataclass(frozen=True)
class Halo:
    cut: str
    v0: float
    lab: float
    endpoint: float
    annual: float = 0.

    def __post_init__(self):
        if self.cut not in ("galactic","laboratory") or self.lab<=0 or self.v0<=0 or self.endpoint<=self.lab:
            raise ValueError("invalid halo")

    @property
    def maximum(self):
        return self.endpoint + self.annual

    def pdf(self, v):
        if not self.annual:
            return self._one(v,self.lab)
        # Uniform full-year average at midpoints. This is an astrophysical diagnostic.
        return sum(self._one(v,self.lab+self.annual*f) for f in annual_phases())/len(annual_phases())

    def _one(self, speed, lab):
        v = np.asarray(speed)
        esc = self.endpoint-self.lab
        cap = esc+lab if self.cut=="galactic" else self.endpoint
        v0 = self.v0
        z = esc/v0
        if self.cut=="galactic":
            norm = erf(z)-2*z*np.exp(-z*z)/np.sqrt(np.pi)
            upper = np.minimum(v+lab,esc)
        else:
            # CDF of the untruncated, shifted 3D Gaussian at a lab-frame speed cap.
            minus,plus = (cap-lab)/v0,(cap+lab)/v0
            norm = (erf(minus)+erf(plus))/2-v0*(np.exp(-minus**2)-np.exp(-plus**2))/(2*np.sqrt(np.pi)*lab)
            upper = v+lab
        first = (v-lab)/v0
        power = np.maximum((upper**2-(v-lab)**2)/v0**2,0.)
        difference = np.exp(-first**2)*(-np.expm1(-power))
        pdf = v*difference/(np.sqrt(np.pi)*v0*lab*norm)
        return np.where((v>=0)&(v<cap),pdf,0.)


@lru_cache(None)
def annual_phases():
    return np.cos(2*np.pi*(np.arange(64)+.5)/64)


@lru_cache(None)
def unit_quadrature(order):
    x,w=roots_legendre(order)
    return (1+x)/2,w/2


def speed_nodes(threshold,halo,order):
    u,w=unit_quadrature(order)
    span=np.maximum(halo.maximum-threshold,0.)[...,None]
    return threshold[...,None]+span*u*u,2*span*u*w


def masses(prescription):
    if prescription=="AME":
        return TABLE.mA_AME2020_CODATA2022_GeV.to_numpy()
    if prescription=="A_u":
        return TABLE.mA_Au_GeV_legacy.to_numpy()
    if prescription=="A_mp":
        return TABLE.index.to_numpy(dtype=float)*.938272
    raise ValueError(prescription)


def minimum_speed(mass,er):
    """Positive root of pq - Eχ ER = mA ER + mχ ms + ms²/2."""
    q=np.sqrt(er*(2*mass+er))
    t=2*mass*er
    b=mass*er+phys.MCHI*phys.MS+phys.MS**2/2
    p=(b*q+er*np.sqrt(b*b+t*phys.MCHI**2))/t
    return phys.C_KMS*p/np.sqrt(phys.MCHI**2+p*p)


def helm(a,q):
    # Same 1.0 fm skin convention as the project's Hybrid-9 reference.
    skin, diffuseness = 1.,.52
    core=1.23*a**(1/3)-.60
    radius=np.sqrt(core**2+7*np.pi**2*diffuseness**2/3-5*skin**2)
    qfm=q/.1973269804
    x=qfm*radius
    return (a*3*spherical_jn(1,x)/x)**2*np.exp(-(qfm*skin)**2)


def response_grid(energy,nuclear,mass):
    er=np.asarray(energy)*1e-6
    out=[]
    for a,m in zip(ISOTOPES,mass):
        q=np.sqrt(2*m*er)
        if nuclear=="Helm9" or (nuclear=="hybrid9" and a not in AFH):
            out.append(helm(a,q))
        elif a in AFH:
            out.append(phys.charge_response(a)(q))
        elif nuclear=="AFH7":
            out.append(np.zeros_like(q))
        else:
            raise ValueError(nuclear)
    return np.array(out)


class Blue:
    """Manuscript Eq. (12), I=1, before the unspecified blue normalization."""
    def __init__(self,energy,nuclear="AFH7",mass_label="AME",q_mass_label=None):
        self.energy = np.asarray(energy)
        m=masses(mass_label)
        er=self.energy[None,:]*1e-6
        q=np.sqrt(2*m[:,None]*er)
        mu=(m*phys.MCHI/(m+phys.MCHI))[:,None]
        self.vmin=phys.C_KMS*(phys.MS/q+q/(2*mu))
        q_mass=m if q_mass_label is None else masses(q_mass_label)
        self.weight=(m*TABLE.natural_atom_fraction.to_numpy())[:,None]*response_grid(self.energy,nuclear,q_mass)

    def evaluate(self,halo,order=24):
        speed,dv=speed_nodes(self.vmin,halo,order)
        eta=np.sum(dv*halo.pdf(speed)/speed,axis=-1)
        return (self.weight*eta).sum(axis=0)


def build_kernel_grid(mass_label="AME"):
    # The response and the full threshold power are divided out before interpolation.
    energy=np.arange(80.,831.,15.)
    excess_speed=np.array([.025,3.,12.,25.,44.,66.,90.,118.,150.,185.,225.])
    rows=[]
    for a,m in zip(ISOTOPES,masses(mass_label)):
        for e in energy:
            er=e*1e-6
            threshold=minimum_speed(m,er)
            for delta in excess_speed:
                v=threshold+delta
                h=phys.threshold_excess(m,er,v)
                beta=v/phys.C_KMS
                p2=phys.MCHI**2*beta**2/(1-beta**2)
                scaled=phys.lab_integral(v,m,er,10)*p2/h**1.5
                rows.append((mass_label,a,e,delta,scaled))
    return pd.DataFrame(rows,columns=["mass_set","A","ER_keV","above_threshold_km_s","scaled_lab_kernel"])


class Red:
    """Interpolate only the smooth exact Dirac integral, leaving support and W_M explicit."""
    def __init__(self,grid,mass_label="AME"):
        self.mass=masses(mass_label)
        self.models={}
        for a,g in grid[grid.mass_set==mass_label].groupby("A"):
            block=g.pivot(index="ER_keV",columns="above_threshold_km_s",values="scaled_lab_kernel")
            x,y=block.index.to_numpy(),block.columns.to_numpy()
            self.models[a]=RectBivariateSpline(x,y,block.to_numpy())
            self.range=(x[0],x[-1],y[-1])
        if set(self.models)!=set(ISOTOPES):
            raise ValueError("incomplete kernel grid")

    def dsigma(self,a,energy,speed,response):
        er=np.asarray(energy)*1e-6
        mass=self.mass[ISOTOPES.index(a)]
        delta=speed-minimum_speed(mass,er)
        if np.any(delta>self.range[-1]) or np.any(energy<self.range[0]) or np.any(energy>self.range[1]):
            raise ValueError("kernel interpolation outside its checked domain")
        # Splines clamp only the first 0.025 km/s to its first smooth coefficient.
        vbeta=speed/phys.C_KMS
        p2=phys.MCHI**2*vbeta**2/(1-vbeta*vbeta)
        h=np.maximum(phys.threshold_excess(mass,er,speed),0.)
        e,dv=np.broadcast_arrays(energy,delta)
        s=self.models[a].ev(e.ravel(),dv.ravel()).reshape(e.shape)
        pref=(phys.G1*phys.G2*phys.GN)**2*TO_CM2_KEV*response/(phys.MV**2+2*mass*er)**2
        return np.where(delta>0,s*h**1.5/p2*pref,0.)

    def fold(self,energy,halo,nuclear="AFH7",order=40,q_mass_label=None):
        energy=np.asarray(energy)
        q_mass=self.mass if q_mass_label is None else masses(q_mass_label)
        response=response_grid(energy,nuclear,q_mass)
        by_isotope=[]
        for i,(a,m) in enumerate(zip(ISOTOPES,self.mass)):
            threshold=minimum_speed(m,energy*1e-6)
            speed,dv=speed_nodes(threshold,halo,order)
            dsigma=self.dsigma(a,energy[:,None],speed,response[i,:,None])
            flux=dv*speed*halo.pdf(speed)
            by_isotope.append(EXPOSURE_FLUX*TABLE.at[a,"natural_atom_fraction"]*np.sum(flux*dsigma,axis=-1))
        return np.array(by_isotope)


def reference():
    path=HERE.parent/"figure3_source_audit/output/figure_vertices.csv"
    data=pd.read_csv(path).query("version=='supplied'")
    return {k:g[["ER_keV","value"]].to_numpy().T for k,g in data.groupby("curve")}


def read_curve(curve,e):
    return np.exp(np.interp(e,curve[0],np.log(curve[1]),left=np.nan,right=np.nan))


def reference_cumulative(curve,lower,upper):
    """Integrate the actual straight PDF segments in log ordinate between two energies."""
    x,y=curve
    if lower<x[0] or upper>x[-1] or upper<=lower:
        raise ValueError("window outside the digitized stroke")
    nodes=np.r_[lower,x[(x>lower)&(x<upper)],upper]
    ordinate=read_curve(curve,nodes)
    area=ordinate[:-1]*np.diff(nodes)*exprel(np.diff(np.log(ordinate)))
    return nodes,np.r_[0.,np.cumsum(area)]


def leading_rate(energy,halo,mass_label,q_mass_label,contact):
    """Absolute I(D) rate from the spin-averaged two-body cross section times Eq. (8)."""
    energy=np.asarray(energy)
    er=energy*1e-6
    mass=masses(mass_label)
    response=response_grid(energy,"AFH7",masses(q_mass_label))
    u,wu=unit_quadrature(10)
    rows=[]
    for i,(a,m) in enumerate(zip(ISOTOPES,mass)):
        q=np.sqrt(2*m*er)
        mu=m*phys.MCHI/(m+phys.MCHI)
        threshold=phys.C_KMS*(phys.MS/q+q/(2*mu))
        v,dv=speed_nodes(threshold,halo,48)
        budget=q[:,None]*(v-threshold[:,None])/phys.C_KMS
        phase=2*budget**1.5*np.sum(wu*u*u*np.sqrt(2*phys.MS+budget[...,None]*u*u),axis=-1)
        denominator=phys.MV**4 if contact else (phys.MV**2+2*m*er)**2
        pref=(TO_CM2_KEV*(phys.G1*phys.G2*phys.GN)**2*m
              *response[i]/(2*np.pi**3*phys.GAP**2*denominator))
        velocity_integral=np.sum(dv*halo.pdf(v)*v*phase/(v/phys.C_KMS)**2,axis=1)
        rows.append(EXPOSURE_FLUX*TABLE.at[a,"natural_atom_fraction"]*pref*velocity_integral)
    return np.array(rows)
