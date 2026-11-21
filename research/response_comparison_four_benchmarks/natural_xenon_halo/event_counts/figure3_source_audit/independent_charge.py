"""Stand-alone Fig. 3 checks. Energies are in GeV except for explicitly labelled recoils."""
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq
from scipy.special import erf, roots_legendre

HERE = Path(__file__).resolve().parent
HALO = HERE.parents[1]
RESEARCH = HALO.parents[1]
MASS_INPUT = RESEARCH / "afh_default_density_xe131/output/ame2020_exact_spatial_xe131_partial/xenon_isotope_ame2020_masses.csv"
MCHI, MS, GAP, MV = 1000., 300.e-6, .010, 5.
G1, G2, GN = .1, 1.725, .04857
C_KMS, V0, VLAB, VESC = 299792.458, 220., 232., 544.
VMAX = VLAB + VESC
RHO, EXPOSURE = .3, 2.84 * 1000 * 365.25
GEV2_CM2 = (0.1973269804e-13)**2


@lru_cache(None)
def nodes(order):
    return roots_legendre(order)


def integrate_interval(low, high, order):
    x, w = nodes(order)
    return low + (high-low)*(1+x)/2, (high-low)*w/2


def threshold_excess(mass, er, speed):
    beta = speed / C_KMS
    echi = MCHI / np.sqrt(1 - beta*beta)
    q = np.sqrt(er * (2*mass+er))
    return 2*(echi*beta*q-(echi+mass)*er) - MS*(2*MCHI+MS)


def exact_min_speed(mass, er):
    return brentq(lambda v: threshold_excess(mass, er, v), 0., 5000., xtol=1e-11)


def support(mass):
    mu = MCHI*mass/(MCHI+mass)
    center = MS*mu/mass
    def f(er):
        return threshold_excess(mass, er, VMAX)
    return np.array([brentq(f, 0., center, xtol=1e-17),
                     brentq(f, center, .003, xtol=1e-17)]) * 1e6


def speed_pdf(speed):
    """Integrate the shifted, cut Galactic Maxwellian over incident directions."""
    speed = np.asarray(speed)
    ceiling = np.clip((VESC**2-speed**2-VLAB**2) / (2*speed*VLAB), -1., 1.)
    angle, weight = integrate_interval(-1., ceiling[..., None], 16)
    u2 = speed[..., None]**2+VLAB**2+2*speed[..., None]*VLAB*angle
    z = VESC/V0
    norm = np.pi**1.5*V0**3*(erf(z)-2*z*np.exp(-z*z)/np.sqrt(np.pi))
    return 2*np.pi*speed**2 * np.sum(weight*np.exp(-u2/V0**2), axis=-1)/norm


@lru_cache(None)
def isotope_inputs():
    table = pd.read_csv(MASS_INPUT).set_index("A")
    molar_mass = table.atomic_mass_u_AME2020 @ table.natural_atom_fraction
    assert abs(table.natural_atom_fraction.sum()-1) < 1e-12
    return table, 1000.*6.02214076e23/molar_mass


@lru_cache(None)
def charge_response(a):
    path = HALO / "inputs/afh_v6/native" / f"afh_v6_xe{a}_eight_response_native.csv"
    data = pd.read_csv(path)
    return CubicSpline(data.q_GeV, a*a*data.W_M00_AFH/data.W_M00_AFH.iloc[0],
                       extrapolate=False)


def common_rate_factor(a, er):
    tab, nuclei = isotope_inputs()
    mass = tab.at[a, "mA_AME2020_CODATA2022_GeV"]
    response = charge_response(a)(np.sqrt(2*mass*er))
    per_kg = nuclei * tab.at[a, "natural_atom_fraction"]
    # cm per km, seconds per day, and GeV of recoil per keV.
    return (EXPOSURE * per_kg * (RHO/MCHI) * 1e5 * 86400 * GEV2_CM2 * 1e-6
            * (G1*G2*GN)**2 * response / (MV**2+2*mass*er)**2)


def constant_amplitude_rate(a, recoil, order):
    """The absolute two-body vector cross section times the paper's radiative ratio."""
    mass = isotope_inputs()[0].at[a, "mA_AME2020_CODATA2022_GeV"]
    er = np.asarray(recoil)*1e-6
    q = np.sqrt(2*mass*er)
    mu = mass*MCHI/(mass+MCHI)
    vmin = C_KMS*(MS/q+q/(2*mu))
    v, dv = integrate_interval(vmin[:, None], np.maximum(vmin, VMAX)[:, None], order)
    d = q[:, None]*np.maximum(v-vmin[:, None], 0.)/C_KMS
    u, du = integrate_interval(0., 1., 12)
    # epsilon = D u^2 regularizes the threshold in the scalar-energy integral.
    phase = 2*d**1.5 * ((u*u*np.sqrt(2*MS+d[..., None]*u*u)) @ du)
    folded = (dv*speed_pdf(v)*v*phase/(v/C_KMS)**2).sum(axis=1)
    return common_rate_factor(a, er)*mass/(2*np.pi**3*GAP**2)*folded


def approximate_window(low, high, order):
    table = isotope_inputs()[0]
    panels = np.linspace(low, high, 1+int(np.ceil((high-low)/8.)))
    result = 0.
    for a, target in table[table.AFH_default_density_matrix_available_in_v6].iterrows():
        mass = target.mA_AME2020_CODATA2022_GeV
        mu = mass*MCHI/(mass+MCHI)
        v = VMAX/C_KMS
        ends = mu**2/(2*mass)*(v+np.array([-1,1])*np.sqrt(v*v-2*MS/mu))**2*1e6
        edges = np.unique(np.r_[panels, ends[(ends>low)&(ends<high)]])
        energy, weight = integrate_interval(edges[:-1,None], edges[1:,None], order)
        result += weight.ravel() @ constant_amplitude_rate(a, energy.ravel(), order)
    return float(result)


# Independent absolute check with original 4x4 vertices and a lab-energy Jacobian.
ID4 = np.eye(4)
G0 = np.diag([1., 1., -1., -1.])
ZERO2 = np.zeros((2,2))
PAULI = (np.array([[0,1],[1,0]]), np.array([[0,-1j],[1j,0]]), np.diag([1.,-1.]))
GAMMA = np.array([G0]+[np.block([[ZERO2,s],[-s,ZERO2]]) for s in PAULI])


def slash(p):
    return p[...,0,None,None]*G0-np.einsum("...a,aij->...ij",p[...,1:],GAMMA[1:])


def pole_width():
    m2 = MCHI+GAP
    p = np.sqrt((GAP*GAP-MS*MS)*((2*MCHI+GAP)**2-MS*MS))/(2*m2)
    return G2**2 * p*((m2+MCHI)**2-MS**2)/(8*np.pi*m2*m2)


def lab_integral(speed, mass, er, order, angular_order=(4,4)):
    """Integral per unit recoil: recoil polar cosine, lab scalar energy, free azimuth."""
    beta = speed/C_KMS
    ein = MCHI/np.sqrt(1-beta**2)
    p = ein*beta
    q = np.sqrt(er*(2*mass+er))
    cmin = (MS*(2*MCHI+MS)+2*(ein+mass)*er)/(2*p*q)
    # c=cmin+(1-cmin)u^2 cancels the square-root endpoint.
    u, wu = integrate_interval(0., 1., order)
    cosine = cmin+(1-cmin)*u*u
    dc = 2*(1-cmin)*u*wu
    recoil = q*np.stack([np.sqrt(1-cosine*cosine),np.zeros_like(u),cosine],axis=-1)
    pair = np.array([0.,0.,p])-recoil
    magnitude = np.linalg.norm(pair,axis=1)
    axis = pair/magnitude[:,None]
    side = np.stack([axis[:,2],np.zeros_like(u),-axis[:,0]],axis=-1)
    normal = np.array([0.,1.,0.])
    excess = 2*p*q*(1-cmin)*u*u
    W = np.sqrt((MCHI+MS)**2+excess)
    ks = np.sqrt(excess*(4*MCHI*MS+excess))/(2*W)
    es = (2*MS*(MCHI+MS)+excess)/(2*W)
    # Use the midpoint/half-span map for omega=(K0*es+|K|*ks*z)/W.
    # The boosted parallel momentum avoids subtraction of nearly equal energies.
    nz,nphi = angular_order
    z, wz = nodes(nz)
    phi = (np.arange(nphi)+.5)*2*np.pi/nphi
    transverse = np.sqrt(1-z*z)[None,:,None,None]*(
        np.cos(phi)[None,None,:,None]*side[:,None,None,:]
        +np.sin(phi)[None,None,:,None]*normal)
    k_parallel = (magnitude[:,None]*es[:,None]+(ein-er)*ks[:,None]*z)/W[:,None]
    kvec = k_parallel[:,:,None,None]*axis[:,None,None,:]+ks[:,None,None,None]*transverse
    omega = ((ein-er)*es[:,None]+magnitude[:,None]*ks[:,None]*z)/W[:,None]
    omega = np.broadcast_to(omega[:,:,None],kvec.shape[:-1])
    k = np.concatenate((omega[...,None],kvec),axis=-1)
    p_in = np.array([ein,0.,0.,p])
    pair4 = np.column_stack((np.full_like(u,ein-er),pair))[:,None,None,:]
    p_out = pair4-k
    assert np.max(np.abs(p_out[...,0]-np.sqrt(MCHI*MCHI+(p_out[...,1:]**2).sum(-1)))) < 2e-12
    assert np.max(np.abs(omega**2-(kvec*kvec).sum(-1)-MS**2)) < 2e-20
    m2 = MCHI+GAP
    before = MS*MS-GAP*(2*MCHI+GAP)-2*(ein*omega-p*kvec[...,2])
    after = excess + (MS-GAP)*(2*MCHI+MS+GAP)+1j*m2*pole_width()
    vertex = (G0@(slash(p_in-k)+m2*ID4))/before[...,None,None] + (
        (slash(pair4)+m2*ID4)@G0)/after[:,None,None,None,None]
    bar = G0@vertex.conj().swapaxes(-1,-2)@G0
    trace = .5*np.trace((slash(p_out)+MCHI*ID4)@vertex@(slash(p_in)+MCHI*ID4)@bar,axis1=-2,axis2=-1)
    assert np.max(np.abs(trace.imag)/trace.real) < 1e-12 and np.all(trace.real>0)
    domega = magnitude*ks/W
    integrated = (dc*domega/magnitude) @ (trace.real.mean(axis=2) @ wz)
    return mass*q*integrated/(64*np.pi**3*p)


def lab_isotope_rate(a, mass, recoil, order, angular_order=(4,4)):
    er = recoil*1e-6
    vmin = exact_min_speed(mass, er)
    if vmin >= VMAX:
        return 0.
    u, wu = integrate_interval(0., 1., order)
    v = vmin+(VMAX-vmin)*u*u
    dv = 2*(VMAX-vmin)*u*wu
    dsigma = np.array([lab_integral(speed, mass, er, order, angular_order) for speed in v])
    return float(common_rate_factor(a, er) * ((dv*speed_pdf(v)*v) @ dsigma))


def exact_charge_at(recoil, order, angular_order=(4,4)):
    table = isotope_inputs()[0]
    return sum(lab_isotope_rate(a,row.mA_AME2020_CODATA2022_GeV,recoil,order,angular_order)
               for a,row in table[table.AFH_default_density_matrix_available_in_v6].iterrows())


def lab_window(low, high, spatial_order, energy_order):
    table = isotope_inputs()[0]
    result = 0.
    for a,row in table[table.AFH_default_density_matrix_available_in_v6].iterrows():
        mass = row.mA_AME2020_CODATA2022_GeV
        start,stop = support(mass)
        start,stop = max(start,low), min(stop,high)
        if stop<=start:
            continue
        edges = np.linspace(start,stop,1+int(np.ceil((stop-start)/16.)))
        e,w = integrate_interval(edges[:-1,None],edges[1:,None],energy_order)
        rates = [lab_isotope_rate(a,mass,float(x),spatial_order) for x in e.ravel()]
        result += w.ravel() @ rates
    return float(result)
