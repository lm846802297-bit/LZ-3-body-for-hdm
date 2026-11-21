"""Phase-space integrated dark-current weights at arbitrary target mass, speed and recoil."""
from functools import lru_cache
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compare_responses as fixed

eq6 = fixed.eq6
MCHI = fixed.MCHI
PAULI = np.asarray((eq6.s1, eq6.s2, eq6.s3))


@lru_cache(None)
def angles(nw, nz, nphi):
    x, wx = eq6._cached_leggauss(nw)
    z, wz = eq6._cached_leggauss(nz)
    azimuth = (np.arange(nphi) + 0.5) * (2*np.pi / nphi)
    u, z, phi = np.meshgrid((1+x)/2, z, azimuth, indexing="ij")
    weight = wx[:, None, None] * wz[None, :, None] * np.ones(nphi)/nphi
    return u.ravel(), z.ravel(), phi.ravel(), weight.ravel()


def phase_space(mass, er, ms, speeds, order, w_map):
    """Work in the target frame with +z along q. z_star refers to p_in in the pair rest frame."""
    beta = np.asarray(speeds)/eq6.C_KM_S
    energy = MCHI / np.sqrt(1-beta**2)
    momentum = energy * beta
    q = np.sqrt(er*(2*mass+er))
    span = 2*(momentum*q - (energy+mass)*er) - ms*(2*MCHI+ms)
    if np.any(span <= 0):
        raise ValueError("phase_space requires open velocities")
    u, z, phi, weight = angles(*order)
    if w_map == "threshold_u2":
        fraction, jacobian = u*u, u
    elif w_map == "linear_w2":
        fraction, jacobian = u, .5
    else:
        raise ValueError("unknown invariant-mass quadrature map")
    delta = (span[:, None]*fraction).ravel()
    rootw = np.sqrt((MCHI+ms)**2+delta)
    pz = (ms*(2*MCHI+ms)+delta+2*(np.repeat(energy, u.size)+mass)*er)/(2*q)
    pin_norm = np.repeat(momentum, u.size)
    if np.any(pz > pin_norm*(1+1e-12)):
        raise ArithmeticError("recoil angle out of range")
    px = np.sqrt(np.maximum(0., (pin_norm-pz)*(pin_norm+pz)))
    pin = np.column_stack((np.repeat(energy, u.size), px, np.zeros_like(px), pz))
    pair = pin - np.array([er, 0., 0., q])
    boost = pair[:, 1:] / pair[:, :1]
    pstar = fixed.boost_batch(pin, -boost)[:, 1:]
    axis = pstar / np.linalg.norm(pstar, axis=1)[:, None]
    e1 = np.column_stack((axis[:, 2], np.zeros_like(px), -axis[:, 0]))
    z = np.tile(z, len(speeds))
    phi = np.tile(phi, len(speeds))
    direction = z[:, None]*axis + (np.sqrt(1-z*z)*np.cos(phi))[:, None]*e1
    direction[:, 1] += np.sqrt(1-z*z)*np.sin(phi)
    kallen_root = np.sqrt(delta*(4*MCHI*ms+delta))
    relative_momentum = (kallen_root/(2*rootw))[:, None]*direction
    ek = (2*ms*(MCHI+ms)+delta)/(2*rootw)
    ep = (2*MCHI*(MCHI+ms)+delta)/(2*rootw)
    k = fixed.boost_batch(np.column_stack((ek, relative_momentum)), boost)
    pout = fixed.boost_batch(np.column_stack((ep, -relative_momentum)), boost)
    weights = (span[:, None]*(jacobian*weight)).ravel() * kallen_root / rootw**2
    return pin, pout, k, delta, weights


def sigma_dot(vector):
    return np.einsum("ni,ijk->njk", vector, PAULI)


def integrated(mass, er_keV, ms, gap, speeds, order, *, check=False, w_map="threshold_u2"):
    """Return L00, coherent longitudinal-minus-time correction, LT and p_in^2 per speed."""
    er = er_keV*1e-6
    q = np.sqrt(er*(2*mass+er))
    pin, pout, k, delta, weights = phase_space(mass, er, ms, speeds, order, w_map)
    m2 = MCHI+gap
    width = eq6.chi2_width_dirac_scalar(MCHI, ms, gap, fixed.G2)
    pk = pin[:, 0]*k[:, 0] - np.sum(pin[:, 1:]*k[:, 1:], axis=1)
    before = 1/(ms*ms-gap*(2*MCHI+gap)-2*pk)
    after_real = (ms-gap)*(2*MCHI+ms+gap) + delta
    if np.any(after_real >= 0):
        raise ArithmeticError("on-shell intermediate state outside these benchmarks")
    after = 1/(after_real+1j*m2*width)

    # On-shell Dirac equations reduce the summed two-diagram vertex to
    # (before+after) gamma^mu (m1+m2-slash(k)) + 2 after k^mu I.
    a = sigma_dot(pin[:, 1:]/(pin[:, :1]+MCHI))
    b = sigma_dot(pout[:, 1:]/(pout[:, :1]+MCHI))
    ks = sigma_dot(k[:, 1:])
    hu = (MCHI+m2-k[:, 0])[:, None, None]*eq6.I2 + ks@a
    hl = (MCHI+m2+k[:, 0])[:, None, None]*a - ks
    norm = np.sqrt((pin[:, 0]+MCHI)*(pout[:, 0]+MCHI))
    vector = ((before+after)*norm)[:, None, None]
    scalar = (2*after*norm)[:, None, None]*(eq6.I2-b@a)
    j0 = vector*(hu+b@hl) + k[:, 0, None, None]*scalar
    space = [vector*(s@hl+(b@s)@hu)+k[:, j+1, None, None]*scalar
             for j, s in enumerate(PAULI)]
    def inner(x, y):
        return .5*np.sum((x*y.conj()).real, axis=(-1, -2))
    def average(x):
        return (weights*x).reshape(len(speeds), -1).sum(axis=1)
    l00 = average(inner(j0, j0))
    r = er/q
    dl = average(-2*r*inner(j0, space[2]) + r*r*inner(space[2], space[2]))
    lt = average(inner(space[0], space[0])+inner(space[1], space[1]))
    if np.any(l00 <= 0) or np.any(l00+dl <= 0) or np.any(lt < 0):
        raise ArithmeticError("invalid dark tensor contraction")
    beta = np.asarray(speeds)/eq6.C_KM_S
    p2 = MCHI**2*beta**2/(1-beta**2)
    if check:
        dev = pin - pout - k - np.array([er, 0., 0., q])
        if np.abs(dev).max() > 3e-12:
            raise ArithmeticError("four-momentum closure")
        for particle, m in ((pin, MCHI), (pout, MCHI), (k, ms)):
            shell = particle[:, 0]**2-np.sum(particle[:, 1:]**2, axis=1)-m*m
            if np.abs(shell).max() > 2e-14*m*m:
                raise ArithmeticError("mass shell")
    return l00, dl, lt, p2
