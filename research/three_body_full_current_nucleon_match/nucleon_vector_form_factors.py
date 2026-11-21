#!/usr/bin/env python3
"""Low-momentum flavor-resolved nucleon vector form factors for the B baseline.

The quark current is J_q^mu = ubar gamma^mu u + dbar gamma^mu d
+ sbar gamma^mu s. Bishara et al., JHEP 11 (2017) 059,
arXiv:1707.06998, Appendix A.1, provide the first-order flavor-separated
Dirac slopes and the zero-transfer Pauli inputs:
  F1^{uds}(t_N) = 3 + 8.392 t_N + O(t_N^2),
  F2^{uds}(t_N) = -0.552 + O(t_N).
The leading B-baseline prescription therefore keeps the F1 slope and the
available leading F2 value; it does not invent an F2 slope.

The AFH W_M(y_A) response describes the finite spatial distribution of
nucleons in the whole nucleus. These nucleon form factors describe the
quark-current matrix element inside an individual nucleon. Both enter B,
and neither may replace or duplicate the other.

The physical rate prefactor is written with g_VN=3*g_Vq outside the
nucleon-current coefficients. Thus every absolute-rate caller must use
Fhat_i=F_i^{uds}/3, with Fhat_1(0)=1 and Fhat_2(0)=-0.184.
The raw quark-summed form factors remain available for provenance and
flavor-level checks.

The isoscalar_zexp option is retained as an alternative form-factor
sensitivity model, not as the default B prescription.
"""
from __future__ import annotations

import math

M_N_GEV = 0.938918
F1V0 = 3.0
F2V0 = -0.552
F1N0 = 1.0
F2N0 = F2V0 / 3.0
DEFAULT_FORM_FACTOR_PRESCRIPTION = "bishara_linear"


def effective_nucleon_form_factors(F1_quark: float, F2_quark: float) -> tuple[float, float]:
    """Normalize the universal u+d+s current to the external effective g_VN.

    The paper/Mathematica rate prefactor contains g_VN=3*g_Vq. Therefore the
    full quark-current form factors (F1(0)=3, F2(0)=-0.552) must be divided
    by three before they enter Dirac-Pauli coefficients multiplying that
    g_VN-normalized prefactor. This gives Fhat1(0)=1 and Fhat2(0)=-0.184.
    """
    if not math.isfinite(F1_quark) or not math.isfinite(F2_quark):
        raise ValueError("quark-current form factors must be finite")
    if F1V0 != 3.0:
        raise ArithmeticError("universal u+d+s normalization changed; revisit g_VN=3*g_Vq")
    return F1_quark / F1V0, F2_quark / F1V0

# Bishara et al., Appendix A.1, Eqs. (A6)-(A8):
# flavor-separated proton Dirac slopes in GeV^{-2}.
BISHARA_F1_SLOPES = {"u": 5.57, "d": 2.84, "s": -0.018}
BISHARA_F1_SLOPE_ERRORS = {"u": 0.09, "d": 0.05, "s": 0.009}
F1_SLOPE_BISHARA = sum(BISHARA_F1_SLOPES.values())
F1_SLOPE_BISHARA_ERR = math.sqrt(sum(x * x for x in BISHARA_F1_SLOPE_ERRORS.values()))

# Bishara et al., Appendix A.1, Eqs. (A3)-(A5): F2^{s/p}(0), F2^{u/p}(0), F2^{d/p}(0).
BISHARA_F2_ZERO = {"u": 1.609, "d": -2.097, "s": -0.064}
F2S0 = BISHARA_F2_ZERO["s"]

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

def bishara_flavor_components(Q2: float) -> dict:
    """Flavor-resolved low-Q_N^2 Dirac-Pauli inputs from Bishara et al.

    With t_N=-Q_N^2, use F1^{q/p}(t_N)=F1^{q/p}(0)+t_N F1'^{q/p}(0)
    and the quoted F2^{q/p}(0). Neutron values follow p->n, u<->d.
    """
    if Q2 < 0.0:
        raise ValueError("Q2 must be non-negative")
    F1_zero = {"u": 2.0, "d": 1.0, "s": 0.0}
    F1 = {
        flavor: F1_zero[flavor] - Q2 * slope
        for flavor, slope in BISHARA_F1_SLOPES.items()
    }
    F2 = dict(BISHARA_F2_ZERO)
    return {
        "F1_by_flavor": F1,
        "F2_by_flavor": F2,
        "F1V": sum(F1.values()),
        "F2V": sum(F2.values()),
    }


def bishara_linear(Q2: float) -> tuple[float, float]:
    components = bishara_flavor_components(Q2)
    return components["F1V"], components["F2V"]

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

def charge_coefficients(
    qA_GeV: float,
    *,
    F1: float,
    F2: float,
    mN_GeV: float = M_N_GEV,
    tN_GeV2: float | None = None,
) -> tuple[float, float]:
    """Return charge-sector coefficients with separate spatial Q_A^2 and t_N.

    If tN_GeV2 is omitted, retain the legacy static-nucleon diagnostic
    q_N^0=0, t_N=-|q_A|^2.  The strict one-body impulse prescription passes
    tN_GeV2=t_A=-2 m_A E_R, while the spatial Q_A^2 remains exact.
    """
    if qA_GeV < 0.0 or mN_GeV <= 0.0:
        raise ValueError("invalid qA or nucleon mass")
    Q_A2 = qA_GeV * qA_GeV
    tN = -Q_A2 if tN_GeV2 is None else float(tN_GeV2)
    if not math.isfinite(tN):
        raise ValueError("tN_GeV2 must be finite")
    cM = F1 + tN * (F1 + 2.0 * F2) / (8.0 * mN_GeV**2)
    cPhiPP = Q_A2 * (F1 + 2.0 * F2) / (4.0 * mN_GeV**2)
    return cM, cPhiPP

def q0_anchor_baseline_correction(
    qA_GeV: float,
    W_phi_over_WM: float,
    W_Mphi_over_WM: float,
    *,
    prescription: str = DEFAULT_FORM_FACTOR_PRESCRIPTION,
    tN_GeV2: float | None = None,
) -> dict:
    """Compare the finite-t_N M+Phi'' kernel with the A (q=0-current) M baseline.

    The AFH W_M(Q_A) factor is present in both numerator and denominator.
    The returned coefficients use Fhat_i=F_i^{uds}/3 because the public
    prefactor is expressed with g_VN=3*g_Vq.
    """
    Q2 = qA_GeV * qA_GeV if tN_GeV2 is None else -float(tN_GeV2)
    if Q2 < 0.0 or not math.isfinite(Q2):
        raise ValueError("nucleon form-factor Q_N^2 must be finite and non-negative")
    if prescription == "bishara_linear":
        F1_quark, F2_quark = bishara_linear(Q2)
    elif prescription == "isoscalar_zexp":
        F1_quark, F2_quark = isoscalar_zexp(Q2)
    else:
        raise ValueError("unknown form-factor prescription")
    F1, F2 = effective_nucleon_form_factors(F1_quark, F2_quark)
    cM, cPhi = charge_coefficients(
        qA_GeV, F1=F1, F2=F2, tN_GeV2=tN_GeV2
    )
    eta = cPhi / cM
    Qphi = 1.0 + 2.0 * eta * W_Mphi_over_WM + eta * eta * W_phi_over_WM
    return {
        "qA_GeV": qA_GeV,
        "Q_N2_GeV2": Q2,
        "tN_GeV2": -Q2,
        "F1V_quark_sum": F1_quark,
        "F2V_quark_sum": F2_quark,
        "F1N_effective": F1,
        "F2N_effective": F2,
        "cM": cM,
        "cPhiPP": cPhi,
        "eta": eta,
        "Q_phiPP": Qphi,
        "relative_to_A_AFH_finite_size_M": cM * cM * Qphi - 1.0,
        "relative_to_B_finite_tN_M": Qphi - 1.0,
        "prescription": prescription,
    }
