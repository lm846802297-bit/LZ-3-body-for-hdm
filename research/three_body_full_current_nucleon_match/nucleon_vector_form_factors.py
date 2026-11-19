#!/usr/bin/env python3
"""Universal light-quark vector nucleon form factors and charge matching.

The raw flavor-summed current is ubar*gamma^mu*u + dbar*gamma^mu*d
+ sbar*gamma^mu*s, with F1_uds(0)=3 and F2_uds(0)=-0.552.  When the
external rate prefactor is written with g_VN=3*g_Vq, the current-side
coefficients must use the effective form factors Fhat_i=F_i^uds/3.

The adopted B prescription is the first-order Bishara Dirac slope with
the available constant Pauli anchor.  The isoscalar z-expansion remains
an alternate sensitivity diagnostic, not the adopted B input.

The charge matching deliberately accepts both the exact spatial momentum
squared Q_A^2=|q_A|_spatial^2 and the Lorentz invariant nucleon transfer
t_N as separate inputs: c_M depends on t_N, while c_Phi'' depends on Q_A^2.
The first positional argument qA_GeV is the spatial magnitude Q_A, not the
four-vector q_A^mu.  Formal B production
uses t_N=t_A=-2*m_A*E_R; static q_N^0=0 diagnostics must be labelled
separately.
"""

from __future__ import annotations

import math

M_N_GEV = 0.938918
RAW_F1_UDS0 = 3.0
RAW_F2_UDS0 = -0.552

# Backward-compatible aliases. These are raw u+d+s sums, not effective
# nucleon form factors; new code should use the explicit RAW_F*_UDS0 names.
F1V0 = RAW_F1_UDS0
F2V0 = RAW_F2_UDS0

# Bishara et al. Appendix A.1:
# F1^{u/p}'(0)=5.57(9), F1^{d/p}'(0)=2.84(5),
# F1^{s/p}'(0)=-0.018(9), in GeV^{-2}.
F1_SLOPE_BISHARA = 5.57 + 2.84 - 0.018
F1_SLOPE_BISHARA_ERR = math.sqrt(0.09**2 + 0.05**2 + 0.009**2)

# F2^{s/p}(0)=-0.064(17), while the universal sum is -0.552.
F2S0 = -0.064

FORMAL_NUCLEON_TRANSFER_SCHEME = (
    "strict one-body impulse q_N^mu=q_A^mu; t_N=t_A=-2*m_A*E_R"
)
STATIC_NUCLEON_TRANSFER_SCHEME = (
    "static diagnostic q_N^0=0; t_N=-Q_A^2; not formal B"
)


def transfer_kinematics_from_q_omega(
    qA_GeV: float,
    omega_GeV: float,
    *,
    nucleon_transfer_scheme: str = FORMAL_NUCLEON_TRANSFER_SCHEME,
) -> dict:
    """Build the external nuclear transfer and one-body vertex transfer.

    In the q-aligned frame with metric (+---), q_A^mu=(omega,0,0,Q_A).
    Formal B assigns the same external four-transfer to the one-body
    nucleon-current vertex, q_N^mu=q_A^mu. For a free on-shell impulse
    benchmark this can be realized as k_N'^mu-k_N^mu=q_A^mu. In a bound
    nucleus this is the external transfer entering the one-body current;
    it does not reconstruct each bound nucleon's microscopic off-shell
    initial and final four-momenta. The q_N^0=0 static choice is diagnostic.
    """
    qA = float(qA_GeV)
    omega = float(omega_GeV)
    if not math.isfinite(qA) or not math.isfinite(omega):
        raise ValueError("q_A and omega must be finite")
    if qA < 0.0 or omega < 0.0:
        raise ValueError("q_A and omega must be non-negative")
    if nucleon_transfer_scheme == FORMAL_NUCLEON_TRANSFER_SCHEME:
        qN0 = omega
        scheme_id = "strict_one_body_impulse_qN_equals_qA"
        qN_definition = (
            "external four-momentum at the one-body nucleon-current vertex; "
            "set q_N=q_A by impulse matching, not a microscopic bound-nucleon "
            "off-shell momentum reconstruction"
        )
    elif nucleon_transfer_scheme == STATIC_NUCLEON_TRANSFER_SCHEME:
        qN0 = 0.0
        scheme_id = "static_qN0_zero_diagnostic"
        qN_definition = (
            "static diagnostic vertex assignment q_N^0=0 and "
            "boldsymbol q_N=boldsymbol q_A; not the physical nuclear energy transfer"
        )
    else:
        raise ValueError(f"unknown nucleon transfer scheme: {nucleon_transfer_scheme}")

    Q_A2 = qA * qA
    tA = omega * omega - Q_A2
    tN = qN0 * qN0 - Q_A2
    if tA > 1.0e-14 or tN > 1.0e-14:
        raise ValueError("nuclear and nucleon transfers must be spacelike or zero")

    qA4 = [omega, 0.0, 0.0, qA]
    qN4 = [qN0, 0.0, 0.0, qA]
    return {
        "qA_four_vector_GeV": qA4,
        "qN_four_vector_GeV": qN4,
        "qA_energy_GeV": omega,
        "qN_energy_GeV": qN0,
        "Q_A_GeV": qA,
        "Q_A2_GeV2": Q_A2,
        "tA_GeV2": tA,
        "tN_GeV2": tN,
        "metric_signature": "+---",
        "four_vector_frame": "q-aligned frame with boldsymbol q_A along +z",
        "qA_definition": "P_A' - P_A",
        "qN_definition": qN_definition,
        "nucleon_transfer_scheme": nucleon_transfer_scheme,
        "nucleon_transfer_scheme_id": scheme_id,
    }


def recoil_transfer_kinematics(
    mA_GeV: float,
    ER_keV: float,
    *,
    nucleon_transfer_scheme: str = FORMAL_NUCLEON_TRANSFER_SCHEME,
) -> dict:
    """Return exact recoil q_A^mu and the selected one-body q_N^mu prescription."""
    mA = float(mA_GeV)
    ER_keV = float(ER_keV)
    ER = ER_keV * 1.0e-6
    if not math.isfinite(mA) or not math.isfinite(ER_keV) or mA <= 0.0 or ER < 0.0:
        raise ValueError("invalid nuclear mass or recoil energy")
    Q_A = math.sqrt(2.0 * mA * ER + ER * ER)
    result = transfer_kinematics_from_q_omega(
        Q_A, ER, nucleon_transfer_scheme=nucleon_transfer_scheme
    )
    expected_tA = -2.0 * mA * ER
    if not math.isclose(
        result["tA_GeV2"], expected_tA, rel_tol=2.0e-12, abs_tol=2.0e-18
    ):
        raise ArithmeticError("q_A four-vector violates the exact nuclear mass-shell relation")
    result.update({
        "mA_GeV": mA,
        "ER_keV": ER_keV,
        "mass_shell_tA_GeV2": expected_tA,
    })
    return result

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
    F1 = RAW_F1_UDS0 - Q2 * F1_SLOPE_BISHARA
    return F1, RAW_F2_UDS0

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

def effective_nucleon_form_factors(
    F1_uds: float, F2_uds: float
) -> tuple[float, float]:
    """Convert raw universal u+d+s sums to the external-gVN nucleon basis.

    The public rate prefactor contains g_VN=3*g_Vq.  Therefore the raw
    flavor-summed form factors must be divided by three before they enter
    the current coefficients.  This conversion is independent of AFH's
    raw-to-physical nuclear-response factor of four.
    """
    if not math.isfinite(F1_uds) or not math.isfinite(F2_uds):
        raise ValueError("raw flavor-summed form factors must be finite")
    return F1_uds / 3.0, F2_uds / 3.0


def charge_coefficients(
    qA_GeV: float,
    *,
    F1: float,
    F2: float,
    tN_GeV2: float,
    mN_GeV: float = M_N_GEV,
) -> tuple[float, float]:
    """Return M and Phi'' charge coefficients with separate q_A and t_N.

    qA_GeV denotes the exact spatial magnitude Q_A=|q_A|_spatial;
    Q_A^2 enters c_Phi''. The nucleon invariant t_N enters c_M.  Formal B production
    uses t_N=t_A=-2*m_A*E_R; the static q_N^0=0 diagnostic instead uses
    t_N=-Q_A^2 and must pass that value explicitly.
    """
    if (
        not math.isfinite(qA_GeV)
        or not math.isfinite(F1)
        or not math.isfinite(F2)
        or not math.isfinite(tN_GeV2)
        or not math.isfinite(mN_GeV)
        or qA_GeV < 0.0
        or tN_GeV2 > 1.0e-14
        or mN_GeV <= 0.0
    ):
        raise ValueError("invalid q_A, t_N, form factor, or nucleon mass")
    Q_A2 = qA_GeV * qA_GeV
    cM = F1 + tN_GeV2 * (F1 + 2.0 * F2) / (8.0 * mN_GeV**2)
    cPhiPP = Q_A2 * (F1 + 2.0 * F2) / (4.0 * mN_GeV**2)
    return cM, cPhiPP


def static_A_reference_correction(
    qA_GeV: float,
    W_phi_over_WM: float,
    W_Mphi_over_WM: float,
    *,
    prescription: str = "bishara_linear",
) -> dict:
    """Legacy static-q_N^0=0 diagnostic, not the formal B production path."""
    Q_A2 = qA_GeV * qA_GeV
    if prescription == "bishara_linear":
        F1_raw, F2_raw = bishara_linear(Q_A2)
    elif prescription == "isoscalar_zexp":
        F1_raw, F2_raw = isoscalar_zexp(Q_A2)
    else:
        raise ValueError("unknown form-factor prescription")
    F1, F2 = effective_nucleon_form_factors(F1_raw, F2_raw)
    cM, cPhi = charge_coefficients(
        qA_GeV, F1=F1, F2=F2, tN_GeV2=-Q_A2
    )
    F1hat0, _ = effective_nucleon_form_factors(RAW_F1_UDS0, RAW_F2_UDS0)
    eta = cPhi / cM
    Qphi = 1.0 + 2.0 * eta * W_Mphi_over_WM + eta * eta * W_phi_over_WM
    return {
        "qA_GeV": qA_GeV,
        "Q_A2_GeV2": Q_A2,
        "tN_GeV2_static_diagnostic": -Q_A2,
        "F1V_quark_sum": F1_raw,
        "F2V_quark_sum": F2_raw,
        "F1N_effective": F1,
        "F2N_effective": F2,
        "cM": cM,
        "cPhiPP": cPhi,
        "eta": eta,
        "Q_phiPP": Qphi,
        "relative_to_A_reference": (cM * cM / F1hat0**2) * Qphi - 1.0,
        "relative_to_finite_t_M": Qphi - 1.0,
        "kinematics": "static diagnostic q_N^0=0; t_N=-Q_A^2; not formal B",
        "prescription": prescription,
    }
