#!/usr/bin/env python3
"""
Compare the full three-body L^{00} integral with the I(D) approximation.

Benchmark: m_chi1=1 TeV, Delta=10 MeV, m_s=300 keV,
Xe-131 m_A=122 GeV, fixed v=776 km/s.
The common mediator/coupling/nuclear-response factors cancel in the ratio.
"""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy.polynomial.legendre import leggauss

# Dirac representation, metric (+---)
I2 = np.eye(2, dtype=complex)
Z2 = np.zeros((2, 2), dtype=complex)
s1 = np.array([[0, 1], [1, 0]], complex)
s2 = np.array([[0, -1j], [1j, 0]], complex)
s3 = np.array([[1, 0], [0, -1]], complex)
GAMMA = [np.block([[I2, Z2], [Z2, -I2]])]
for sig in (s1, s2, s3):
    GAMMA.append(np.block([[Z2, sig], [-sig, Z2]]))
GAMMA = np.asarray(GAMMA)
EYE4 = np.eye(4, dtype=complex)


def slash(p4):
    return GAMMA[0] * p4[0] - sum(GAMMA[i] * p4[i] for i in range(1, 4))


def mdot(a, b):
    return a[0] * b[0] - np.dot(a[1:], b[1:])


def boost_to_rest(p4, beta):
    b2 = np.dot(beta, beta)
    if b2 < 1e-30:
        return p4.copy()
    g = 1.0 / np.sqrt(1.0 - b2)
    bp = np.dot(beta, p4[1:])
    return np.r_[g * (p4[0] - bp),
                 p4[1:] + (((g - 1.0) * bp / b2) - g * p4[0]) * beta]


def boost_to_lab(p4, beta):
    b2 = np.dot(beta, beta)
    if b2 < 1e-30:
        return p4.copy()
    g = 1.0 / np.sqrt(1.0 - b2)
    bp = np.dot(beta, p4[1:])
    return np.r_[g * (p4[0] + bp),
                 p4[1:] + (((g - 1.0) * bp / b2) + g * p4[0]) * beta]


def L00_trace(p, pp, k, m, m2):
    # Coherent sum of the two scalar-radiation diagrams.
    r_after = pp + k
    r_before = p - k
    den_after = mdot(r_after, r_after) - m2 * m2
    den_before = mdot(r_before, r_before) - m2 * m2
    Gamma0 = ((slash(r_after) + m2 * EYE4) @ GAMMA[0] / den_after
              + GAMMA[0] @ (slash(r_before) + m2 * EYE4) / den_before)
    Gamma0_bar = GAMMA[0] @ Gamma0.conj().T @ GAMMA[0]
    tr = np.trace((slash(pp) + m * EYE4) @ Gamma0
                  @ (slash(p) + m * EYE4) @ Gamma0_bar)
    return float(np.real(tr / 2.0))


def kinematics(ER, v, m, ms, mA):
    E = m / np.sqrt(1.0 - v * v)
    pin = E * v
    q = np.sqrt(ER * (ER + 2.0 * mA))
    Wmin = m + ms
    Wmax2 = m*m - 2.0*(E + mA)*ER + 2.0*pin*q
    if Wmax2 <= Wmin*Wmin:
        return None
    return E, pin, q, Wmin, np.sqrt(Wmax2)


def L00_at(ER, v, eps, z, phi, m, ms, Delta, mA):
    kin = kinematics(ER, v, m, ms, mA)
    if kin is None:
        return np.nan
    E, pin, q, Wmin, Wmax = kin
    W = Wmin + eps
    W2 = W * W
    cos_lab = (W2 - m*m + 2.0*(E + mA)*ER) / (2.0*pin*q)
    if cos_lab < -1.0 - 1e-8 or cos_lab > 1.0 + 1e-8:
        return np.nan
    cos_lab = np.clip(cos_lab, -1.0, 1.0)
    qvec = q * np.array([np.sqrt(max(0.0, 1.0-cos_lab*cos_lab)), 0.0, cos_lab])
    p4 = np.array([E, 0.0, 0.0, pin])
    Q4 = np.r_[ER, qvec]
    K = p4 - Q4
    beta = K[1:] / K[0]
    pstar_in = boost_to_rest(p4, beta)
    axis = pstar_in[1:] / np.linalg.norm(pstar_in[1:])
    ref = np.array([0.0, 1.0, 0.0])
    if abs(np.dot(axis, ref)) > 0.95:
        ref = np.array([1.0, 0.0, 0.0])
    e2 = np.cross(ref, axis)
    e2 /= np.linalg.norm(e2)
    e3 = np.cross(axis, e2)

    lam_dimful = (W2-(m+ms)**2) * (W2-(m-ms)**2)
    pstar = np.sqrt(max(0.0, lam_dimful)) / (2.0*W)
    E_s = (W2 + ms*ms - m*m) / (2.0*W)
    E_chi = (W2 + m*m - ms*ms) / (2.0*W)
    direction = (z*axis + np.sqrt(max(0.0, 1.0-z*z))
                 * (np.cos(phi)*e2 + np.sin(phi)*e3))
    kstar = np.r_[E_s, pstar*direction]
    ppstar = np.r_[E_chi, -pstar*direction]
    k = boost_to_lab(kstar, beta)
    pp = boost_to_lab(ppstar, beta)
    return L00_trace(p4, pp, k, m, m+Delta)


def I_of_D(D, ms):
    if D <= 0:
        return 0.0
    root = np.sqrt(D*(D+2.0*ms))
    return 0.5*((D+ms)*root - ms*ms*np.log((D+ms+root)/ms))


def one_point(ER_keV, v_kms, m, ms, Delta, mA, nt, nz, nphi):
    ER = ER_keV * 1e-6
    v = v_kms * 3.33564095e-6
    kin = kinematics(ER, v, m, ms, mA)
    if kin is None:
        return None
    E, pin, q, Wmin, Wmax = kin
    Dex = Wmax - Wmin
    mu = m*mA/(m+mA)
    q_nr = np.sqrt(2.0*mA*ER)
    Dnr = v*q_nr - q_nr*q_nr/(2.0*mu) - ms
    if Dex <= 0 or Dnr <= 0:
        return None

    L0 = L00_at(ER, v, 0.0, 0.0, 0.0, m, ms, Delta, mA)
    xt, wt = leggauss(nt)
    tnodes, tw = 0.5*(xt+1.0), 0.5*wt
    znodes, zw = leggauss(nz)
    phis = 2.0*np.pi*(np.arange(nphi)+0.5)/nphi

    Jfull = 0.0
    Jphase_exact = 0.0
    for t, wt_i in zip(tnodes, tw):
        eps = Dex*t*t
        deps_weight = 2.0*Dex*t*wt_i
        W = Wmin + eps
        W2 = W*W
        lam_dimless = (1.0-(m+ms)**2/W2)*(1.0-(m-ms)**2/W2)
        measure = 2.0*W*np.sqrt(max(0.0, lam_dimless))*deps_weight
        z_integral = 0.0
        for z, wz_i in zip(znodes, zw):
            phi_average = 0.0
            for phi in phis:
                phi_average += L00_at(ER, v, eps, z, phi, m, ms, Delta, mA)
            phi_average /= nphi
            z_integral += wz_i*phi_average
        Jfull += measure*z_integral
        pstar = np.sqrt(max(0.0, (W2-(m+ms)**2)*(W2-(m-ms)**2))) / (2.0*W)
        Jphase_exact += 8.0*L0*pstar*deps_weight

    JI_Dexact = 8.0*L0*I_of_D(Dex, ms)
    JI_Dnr = 8.0*L0*I_of_D(Dnr, ms)
    return {
        "ER_keV": ER_keV, "Dexact_keV": Dex*1e6, "Dnr_keV": Dnr*1e6,
        "amp_corr": Jfull/Jphase_exact-1.0,
        "D_corr": JI_Dexact/JI_Dnr-1.0,
        "total_corr": Jfull/JI_Dnr-1.0,
        "shape_error_vs_248_pct": np.nan,
        "L0": L0, "Jfull": Jfull, "Jphase_exact": Jphase_exact,
        "JI_Dexact": JI_Dexact, "JI_Dnr": JI_Dnr
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--points", type=int, default=943)
    ap.add_argument("--v-kms", type=float, default=776.0)
    ap.add_argument("--er-min", type=float, default=109.64)
    ap.add_argument("--er-max", type=float, default=652.94)
    ap.add_argument("--nt", type=int, default=8)
    ap.add_argument("--nz", type=int, default=8)
    ap.add_argument("--nphi", type=int, default=8)
    ap.add_argument("--out-prefix", default="xe131_full_L00_vs_ID")
    args = ap.parse_args()

    m, ms, Delta, mA = 1000.0, 3e-4, 0.01, 122.0
    grid = np.linspace(args.er_min, args.er_max, args.points)
    rows = []
    for er in grid:
        r = one_point(er, args.v_kms, m, ms, Delta, mA,
                      args.nt, args.nz, args.nphi)
        if r is not None:
            rows.append(r)
    df = pd.DataFrame(rows)
    iref = (df.ER_keV-248.0).abs().idxmin()
    ref = df.loc[iref, "total_corr"]
    df["shape_error_vs_248_pct"] = ((1.0+df.total_corr)/(1.0+ref)-1.0)*100.0
    csv = args.out_prefix + ".csv"
    png = args.out_prefix + ".png"
    df.to_csv(csv, index=False, float_format="%.12e")
    plt.figure(figsize=(9, 5.6))
    plt.plot(df.ER_keV, df.amp_corr*100, label="Full-amplitude variation")
    plt.plot(df.ER_keV, df.D_corr*100, label="Exact D vs NR D")
    plt.plot(df.ER_keV, df.total_corr*100, label="Full integral vs I(D)")
    plt.axvline(248.0, color="black", linestyle=":", linewidth=1,
                label=r"$E_R=248$ keV")
    plt.xlabel(r"$E_R$ [keV]")
    plt.ylabel("Relative difference [%]")
    plt.title(r"Xe-131, fixed-speed full $L^{00}$ integral vs $I(D)$")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(png, dpi=200)
    print("Wrote", csv, "and", png)
    print("N =", len(df))
    print("max |full/I(D)-1| [%] =", np.max(np.abs(df.total_corr))*100)
    print("median |full/I(D)-1| [%] =", np.median(np.abs(df.total_corr))*100)


if __name__ == "__main__":
    main()
