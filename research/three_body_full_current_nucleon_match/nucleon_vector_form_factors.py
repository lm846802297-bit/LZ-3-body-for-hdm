#!/usr/bin/env python3
"""Finite-t diagnostic for the universal light-quark vector nucleon current.

The model current is J_q^mu = ubar gamma^mu u + dbar gamma^mu d
+ sbar gamma^mu s.  At Q^2=0 the proton and neutron form factors are
F1^V=3 and F2^V=-0.552.

Two diagnostic finite-Q^2 prescriptions are provided:

1. bishara_linear:
   use the slopes of the flavor-separated Dirac form factors quoted in
   Bishara et al. (JHEP 11 (2017) 059, arXiv:1707.06998), while holding F2
   at its q=0 value.  This is a first-order low-Q^2 diagnostic.

2. isoscalar_zexp:
   reconstruct the light-flavor sum from the isoscalar electromagnetic
   proton+neutron form factors of Borah et al. (PRD 102, 074012 (2020))
   plus the strange-current q=0/slope inputs from Bishara et al.  The
   strange Pauli form factor is kept at its q=0 value because the cited
   Bishara input does not provide a finite-Q^2 F2^s curve.

Neither prescription is established as the exact legacy/model-specific
finite-t form factor. They are controlled diagnostics for the size of the
form-factor effect relative to the q=0 nucleon-current anchor
F1(0)=3, F2(0)=-0.552.

The q=0 anchor is not a point-nucleus approximation: the AFH nuclear
response still carries finite nuclear structure. Only the nucleon
Dirac-Pauli form factors are frozen at zero transfer. For any AFH
correction, the primary denominator must be the M-only result evaluated
with the same finite-t F1,F2 prescription.
"""

from __future__ import annotations

import math

M_N_GEV = 0.938918
F1V0 = 3.0
F2V0 = -0.552

# Bishara et al. Appendix A.1:
# F1^{u/p}'(0)=5.57(9), F1^{d/p}'(0)=2.84(5),
# F1^{s/p}'(0)=-0.018(9), in GeV^{-2}.
F1_SLOPE_BISHARA = 5.57 + 2.84 - 0.018
F1_SLOPE_BISHARA_ERR = math.sqrt(0.09**2 + 0.05**2 + 0.009**2)

# F2^{s/p}(0)=-0.064(17), while the universal sum is -0.552.
F2S0 = -0.064

# Borah et al. isoscalar Sachs z expansion, Q^2 < 1 GeV^2 default fit.
M_PI_GEV = 0.13957
TCUT_ISOSCALAR_GEV2 = 9.0 * M_PI_GEV**2
T0_ISOSCALAR_GEV2 = -0.28
MU_ISOSCALAR = 2.793 - 1.913

# Published a_1..a_4 and b_1..b_4. a_0,b_0 are fixed by
# G_E^S(0)=1 and the normalized G_M^S(0)=1 at the chosen t0.
A_REST = (-1.809, 0.91, 1.92, -0.98)
B_REST = (-1.938, 0.78, 3.71, -4.0)

def _z(Q2: float) -> float:
    if Q2 < 0.0:
        raise ValueError("Q2 must be non-negative")
    tcut = TCUT_ISOSCALAR_GEV2
    t0 = T0_ISOSCALAR_GEV2
    return (math.sqrt(tcut + Q2) - math.sqrt(tcut - t0)) / (
        math.sqrt(tcut + Q2) + math.sqrt(tcut - t0)
    )

def _normalized_coefficients(rest: tuple[float, ...], target_at_zero: float) -> tuple[float, ...]:
    z0 = _z(0.0)
    a0 = target_at_zero - sum(c * z0**k for k, c in enumerate(rest, 1))
    return (a0, *rest)

A_COEFF = _normalized_coefficients(A_REST, 1.0)
B_COEFF = _normalized_coefficients(B_REST, 1.0)

def _poly(coefficients: tuple[float, ...], Q2: float) -> float:
    z = _z(Q2)
    return sum(c * z**k for k, c in enumerate(coefficients))

def isoscalar_em_sachs(Q2: float) -> tuple[float, float]:
    if Q2 < 0.0:
        raise ValueError("Q2 must be non-negative")
    return _poly(A_COEFF, Q2), MU_ISOSCALAR * _poly(B_COEFF, Q2)

def isoscalar_em_dirac_pauli(Q2: float, *, mN_GeV: float = M_N_GEV) -> tuple[float, float]:
    if mN_GeV <= 0.0:
        raise ValueError("mN_GeV must be positive")
    GE, GM = isoscalar_em_sachs(Q2)
    tau = Q2 / (4.0 * mN_GeV**2)
    F1 = (GE + tau * GM) / (1.0 + tau)
    F2 = (GM - GE) / (1.0 + tau)
    return F1, F2

def bishara_linear(Q2: float) -> tuple[float, float]:
    if Q2 < 0.0:
        raise ValueError("Q2 must be non-negative")
    F1 = F1V0 - Q2 * F1_SLOPE_BISHARA
    return F1, F2V0

def isoscalar_zexp(Q2: float) -> tuple[float, float]:
    """Central finite-Q^2 benchmark for the universal light-quark current.

    Charge symmetry gives
      F_i^u+F_i^d+F_i^s = 3(F_i^p+F_i^n+F_i^s).
    The EM isoscalar piece is supplied by Borah et al. The strange F1 is
    included to first order using the Bishara slope; strange F2 is held at
    q=0 because no finite-Q^2 F2^s curve is supplied by that input set.
    """
    if Q2 < 0.0:
        raise ValueError("Q2 must be non-negative")
    F1S, F2S = isoscalar_em_dirac_pauli(Q2)
    F1s = -0.018 * (-Q2)
    F2s = F2S0
    return 3.0 * (F1S + F1s), 3.0 * (F2S + F2s)

def charge_coefficients(qA_GeV: float, *, F1: float, F2: float, mN_GeV: float = M_N_GEV) -> tuple[float, float]:
    if qA_GeV < 0.0 or mN_GeV <= 0.0:
        raise ValueError("invalid qA or nucleon mass")
    Q2 = qA_GeV * qA_GeV
    tN = -Q2
    cM = F1 + tN * (F1 + 2.0 * F2) / (8.0 * mN_GeV**2)
    cPhiPP = Q2 * (F1 + 2.0 * F2) / (4.0 * mN_GeV**2)
    return cM, cPhiPP

def pointlike_baseline_correction(qA_GeV: float, W_phi_over_WM: float, W_Mphi_over_WM: float, *, prescription: str = "isoscalar_zexp") -> dict:
    Q2 = qA_GeV * qA_GeV
    if prescription == "bishara_linear":
        F1, F2 = bishara_linear(Q2)
    elif prescription == "isoscalar_zexp":
        F1, F2 = isoscalar_zexp(Q2)
    else:
        raise ValueError("unknown form-factor prescription")
    cM, cPhi = charge_coefficients(qA_GeV, F1=F1, F2=F2)
    eta = cPhi / cM
    Qphi = 1.0 + 2.0 * eta * W_Mphi_over_WM + eta * eta * W_phi_over_WM
    return {
        "qA_GeV": qA_GeV,
        "Q2_GeV2": Q2,
        "F1V": F1,
        "F2V": F2,
        "cM": cM,
        "cPhiPP": cPhi,
        "eta": eta,
        "Q_phiPP": Qphi,
        "relative_to_pointlike_M": (cM * cM / F1V0**2) * Qphi - 1.0,
        "relative_to_finite_t_M": Qphi - 1.0,
        "prescription": prescription,
    }
