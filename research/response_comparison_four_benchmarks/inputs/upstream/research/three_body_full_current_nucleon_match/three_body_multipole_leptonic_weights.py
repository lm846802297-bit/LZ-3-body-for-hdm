#!/usr/bin/env python3
"""Extract q-aligned leptonic weights and leading AFH vector-current coefficients.

The AFH spatial coefficients follow the elastic response formula in
Anand--Fitzpatrick--Haxton, arXiv:1308.6288, Eq. (107). The output contains
particle-side coefficients only; nuclear responses and OBDMEs are not
contracted here.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np


DEFAULT_F1 = 3.0
DEFAULT_F2 = -0.552
DEFAULT_MN_GEV = 0.938918


def complex_from_pairs(value) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape[-1] != 2:
        raise ValueError("complex-pair array must have a final [real, imag] axis")
    result = array[..., 0] + 1j * array[..., 1]
    if not np.all(np.isfinite(result)):
        raise ValueError("non-finite component in complex-pair tensor")
    return result


def continuity_adjusted_coulomb_weight(
    L: np.ndarray, qA_GeV: float, omega_GeV: float
) -> tuple[float, float]:
    """Conditionally reduce the nuclear longitudinal current using continuity.

    This relation is valid only if the complete nuclear vector current obeys
    q_A_mu J_A^mu = 0. The algebraic reduction does not establish that a
    truncated many-body one-body current satisfies this dynamical identity.

    In the q-aligned frame q_A^mu=(omega,0,0,Q), nuclear-current
    conservation gives J_A^3=(omega/Q)J_A^0. Since the DM tensor is stored
    with contravariant current components and the metric is (+---), the
    effective Coulomb weight is
        L_C = L00 - (omega/Q)(L03+L30) + (omega/Q)^2 L33.
    This uses conservation of the nuclear vector current; it does not impose
    a Ward identity on the inelastic DM transition current.
    """
    if not np.isfinite(qA_GeV) or qA_GeV < 0.0:
        raise ValueError("qA_GeV must be finite and non-negative")
    if not np.isfinite(omega_GeV) or omega_GeV < 0.0:
        raise ValueError("omega_GeV must be finite and non-negative")
    if qA_GeV == 0.0:
        if omega_GeV != 0.0:
            raise ValueError("nonzero energy transfer with zero spatial transfer")
        omega_over_q = 0.0
    else:
        omega_over_q = omega_GeV / qA_GeV
    if omega_over_q > 1.0 + 1.0e-12:
        raise ValueError("nuclear transfer is not spacelike in the q-aligned frame")

    L = np.asarray(L, dtype=complex)
    if L.shape != (4, 4) or not np.all(np.isfinite(L)):
        raise ValueError("L must be a finite 4x4 complex Lorentz tensor")
    L00 = float(np.real(L[0, 0]))
    L03_plus_L30 = float(np.real(L[0, 3] + L[3, 0]))
    L33 = float(np.real(L[3, 3]))
    weight = L00 - omega_over_q * L03_plus_L30 + omega_over_q**2 * L33
    scale = max(abs(L00), abs(omega_over_q * L03_plus_L30), 1.0)
    if weight < -1.0e-10 * scale:
        raise ValueError(f"negative continuity-adjusted Coulomb weight: {weight:.6g}")
    return max(0.0, float(weight)), float(omega_over_q)


def extract_leptonic_weights(
    L: np.ndarray,
    *,
    qA_GeV: float | None = None,
    omega_GeV: float = 0.0,
    hermiticity_tolerance=1e-10,
) -> dict:
    """Return q-aligned charge, longitudinal, transverse-even and helicity-odd factors."""
    L = np.asarray(L, dtype=complex)
    if L.shape != (4, 4):
        raise ValueError(f"expected a 4x4 Lorentz tensor, got {L.shape}")
    if not np.all(np.isfinite(L)):
        raise ValueError("Lorentz tensor contains non-finite values")

    scale = max(float(np.linalg.norm(L)), 1.0e-300)
    hermiticity = float(np.linalg.norm(L - L.conj().T) / scale)
    if hermiticity > hermiticity_tolerance:
        raise ValueError(
            f"Lorentz tensor is not Hermitian: residual={hermiticity:.6g}"
        )

    charge = float(np.real(L[0, 0]))
    longitudinal = float(np.real(L[3, 3]))
    transverse_sum = float(np.real(L[1, 1] + L[2, 2]))
    transverse_even = 0.5 * transverse_sum
    charge_longitudinal_raw = 2.0 * np.real(L[0, 3])
    helicity_complex = -2j * (L[1, 2] - L[2, 1])
    helicity_odd = float(np.real(helicity_complex))
    helicity_imaginary_residual = float(abs(np.imag(helicity_complex)))
    helicity_odd_over_sum = abs(helicity_odd) / max(abs(transverse_sum), 1.0e-300)

    result = {
        "charge_L00": charge,
        "longitudinal_L33": longitudinal,
        "charge_longitudinal_raw_2ReL03": float(charge_longitudinal_raw),
        "transverse_sum_L11_plus_L22": transverse_sum,
        "transverse_even_half_sum": float(transverse_even),
        "generic_transverse_helicity_odd_minus_2i_L12_minus_L21": helicity_odd,
        # Backward-compatible explicit name retained by the regression suite.
        "transverse_helicity_odd_minus_2i_L12_minus_L21": helicity_odd,
        "generic_transverse_helicity_odd_imaginary_residual": helicity_imaginary_residual,
        "transverse_helicity_odd_over_transverse_sum": helicity_odd_over_sum,
        "generic_transverse_helicity_odd_over_transverse_sum": (
            abs(helicity_odd) / max(abs(transverse_sum), 1.0e-300)
        ),
        "transverse_even_over_charge": (
            transverse_even / max(abs(charge), 1.0e-300)
        ),
        "longitudinal_over_charge": (
            longitudinal / max(abs(charge), 1.0e-300)
        ),
        "hermiticity_relative_residual": hermiticity,
    }
    if qA_GeV is not None:
        effective_charge, omega_over_q = continuity_adjusted_coulomb_weight(
            L, qA_GeV, omega_GeV
        )
        result.update({
            "nuclear_omega_over_Q": omega_over_q,
            "continuity_adjusted_coulomb_weight": effective_charge,
            "continuity_charge_relative_correction": (
                effective_charge / max(abs(charge), 1.0e-300) - 1.0
            ),
        })
    return result


def afh_eq107_spatial_coefficients_from_amplitudes(
    T_amplitudes: np.ndarray,
    qA_vec_GeV: np.ndarray,
    *,
    f1: float = DEFAULT_F1,
    f2: float = DEFAULT_F2,
    mN_GeV: float = DEFAULT_MN_GEV,
    spin_average_denominator: float | None = None,
) -> dict:
    """Evaluate AFH Eq. (107) directly on complex spin-resolved amplitudes.

    Each row of T_amplitudes is one spin channel of the three-body DM
    transition current T_3^i in the q-aligned spatial basis. The function
    constructs l_M=-F1*T_3 and
    l_5=+i(F1+F2)/(2m_N) (q_AFH x T_3), with q_AFH=-q_A, then evaluates
    the three vector expressions in AFH Eq. (107) before spin averaging.

    This is an independent amplitude-level check of the scalar L_T formulas
    used by extract_afh_vector_coefficients. It validates the particle-side
    relative phase and normalization, not nuclear OBDME phases or the
    full AFH nuclear multipole contraction.
    """
    amplitudes = np.asarray(T_amplitudes, dtype=complex)
    qA = np.asarray(qA_vec_GeV, dtype=float)
    if amplitudes.ndim != 2 or amplitudes.shape[1] != 3 or amplitudes.shape[0] == 0:
        raise ValueError("T_amplitudes must have shape (n_spin_channels, 3)")
    if not np.all(np.isfinite(amplitudes)):
        raise ValueError("T_amplitudes contains non-finite values")
    if qA.shape != (3,) or not np.all(np.isfinite(qA)):
        raise ValueError("qA_vec_GeV must be a finite three-vector")
    if not all(np.isfinite(x) for x in (f1, f2, mN_GeV)) or mN_GeV <= 0.0:
        raise ValueError("form factors must be finite and mN_GeV positive")

    Q = float(np.linalg.norm(qA))
    if Q <= 0.0:
        raise ValueError("qA_vec_GeV must be nonzero")
    if spin_average_denominator is None:
        spin_average_denominator = float(amplitudes.shape[0])
    if not np.isfinite(spin_average_denominator) or spin_average_denominator <= 0.0:
        raise ValueError("spin_average_denominator must be positive and finite")
    qAFH = -qA
    qhat = qAFH / Q
    q_over_m = qAFH / mN_GeV
    lM = -f1 * amplitudes
    l5 = 1j * (f1 + f2) / (2.0 * mN_GeV) * np.cross(
        np.broadcast_to(qAFH, amplitudes.shape), amplitudes
    )

    c_delta = []
    c_sigma = []
    c_sigma_delta = []
    for lm, l5_channel in zip(lM, l5):
        q_lm = np.dot(q_over_m, lm)
        q_l5 = np.dot(qhat, l5_channel)
        c_delta.append(0.5 * (
            (Q * Q / (mN_GeV * mN_GeV)) * np.vdot(lm, lm).real
            - abs(q_lm) ** 2
        ))
        c_sigma.append(0.5 * (
            np.vdot(l5_channel, l5_channel).real - abs(q_l5) ** 2
        ))
        c_sigma_delta.append(float(np.dot(
            q_over_m,
            np.real(1j * np.cross(lm, np.conjugate(l5_channel))),
        )))

    return {
        "C_Delta": float(np.sum(c_delta) / spin_average_denominator),
        "C_SigmaPrime": float(np.sum(c_sigma) / spin_average_denominator),
        "C_SigmaPrimeDelta": float(np.sum(c_sigma_delta) / spin_average_denominator),
        "qA_GeV": qA.tolist(),
        "q_AFH_GeV": qAFH.tolist(),
        "spin_channel_count": int(amplitudes.shape[0]),
        "spin_average": True,
        "spin_average_denominator": float(spin_average_denominator),
        "F1V": float(f1),
        "F2V": float(f2),
        "mN_GeV": float(mN_GeV),
        "transverse_DM_norm_L_T": float(np.sum(
            np.sum(np.abs(amplitudes) ** 2, axis=1)
            - np.abs(amplitudes @ qhat) ** 2
        ) / spin_average_denominator),
        "AFH_q_convention": "q_AFH=-q_A; q_N=+q_A",
        "source_formula": "AFH Appendix A Eq. (107), evaluated before spin averaging",
    }


def extract_afh_spatial_coefficients_from_tensor(
    L_spatial: np.ndarray,
    qA_vec_GeV: np.ndarray,
    *,
    f1: float = DEFAULT_F1,
    f2: float = DEFAULT_F2,
    mN_GeV: float = DEFAULT_MN_GEV,
) -> dict:
    """AFH Eq. (107) spatial coefficients for a tensor in any spatial frame.

    The q-aligned extractor uses L_11+L_22. This routine instead evaluates
    the transverse projector P_ij=delta_ij-qhat_i*qhat_j, so it is valid in
    the lab frame as well as in the q-aligned frame.
    """
    Ls = np.asarray(L_spatial, dtype=complex)
    qA = np.asarray(qA_vec_GeV, dtype=float)
    if Ls.shape != (3, 3) or not np.all(np.isfinite(Ls)):
        raise ValueError("L_spatial must be a finite 3x3 tensor")
    if qA.shape != (3,) or not np.all(np.isfinite(qA)):
        raise ValueError("qA_vec_GeV must be a finite three-vector")
    if not all(np.isfinite(x) for x in (f1, f2, mN_GeV)) or mN_GeV <= 0.0:
        raise ValueError("form factors must be finite and mN_GeV positive")
    hermiticity = float(
        np.linalg.norm(Ls - Ls.conj().T)
        / max(float(np.linalg.norm(Ls)), 1.0e-300)
    )
    if hermiticity > 1.0e-10:
        raise ValueError(f"spatial tensor is not Hermitian: {hermiticity:.6g}")
    Q = float(np.linalg.norm(qA))
    if Q <= 0.0:
        raise ValueError("qA_vec_GeV must be nonzero")
    qhat = qA / Q
    projector = np.eye(3) - np.outer(qhat, qhat)
    L_T = float(np.real(np.trace(projector @ Ls)))
    if L_T < -1.0e-10 * max(float(np.linalg.norm(Ls)), 1.0):
        raise ValueError(f"negative transverse tensor trace: {L_T:.6g}")
    L_T = max(0.0, L_T)
    Q2 = Q * Q
    return {
        "C_Delta": float(f1 * f1 * Q2 * L_T / (2.0 * mN_GeV * mN_GeV)),
        "C_SigmaPrime": float(
            (f1 + f2) ** 2 * Q2 * L_T / (8.0 * mN_GeV * mN_GeV)
        ),
        "C_SigmaPrimeDelta": float(
            -f1 * (f1 + f2) * Q2 * L_T / (2.0 * mN_GeV * mN_GeV)
        ),
        "L_T_transverse_projector_trace": L_T,
        "qA_GeV": qA.tolist(),
        "q_AFH_GeV": (-qA).tolist(),
        "hermiticity_relative_residual": hermiticity,
    }


def extract_afh_vector_coefficients(
    L: np.ndarray,
    qA_GeV: float,
    *,
    f1: float = DEFAULT_F1,
    f2: float = DEFAULT_F2,
    mN_GeV: float = DEFAULT_MN_GEV,
    omega_GeV: float = 0.0,
) -> dict:
    """AFH Eq. (107) coefficients for the leading static Dirac--Pauli current.

    Convention: q_AFH=-q_A, q_N=+q_A, metric (+---). The coefficients
    multiply the physical equal-p/n AFH response columns. The default F1/F2
    are provisional q=0 anchors, not finite-t form factors.
    """
    if not np.isfinite(qA_GeV) or qA_GeV < 0:
        raise ValueError("qA_GeV must be finite and non-negative")
    if not np.isfinite(f1) or not np.isfinite(f2):
        raise ValueError("F1 and F2 must be finite")
    if not np.isfinite(mN_GeV) or mN_GeV <= 0:
        raise ValueError("mN_GeV must be positive and finite")

    L = np.asarray(L, dtype=complex)
    if L.shape != (4, 4) or not np.all(np.isfinite(L)):
        raise ValueError("L must be a finite 4x4 complex Lorentz tensor")
    hermiticity = float(
        np.linalg.norm(L - L.conj().T) / max(float(np.linalg.norm(L)), 1e-300)
    )
    if hermiticity > 1e-10:
        raise ValueError(f"L is not Hermitian: relative residual {hermiticity:.6g}")

    Q2 = qA_GeV * qA_GeV
    tN = -Q2
    LT = float(np.real(L[1, 1] + L[2, 2]))
    L00 = float(np.real(L[0, 0]))
    if LT < -1e-10 or L00 < -1e-10:
        raise ValueError("negative diagonal spin-averaged leptonic weight")
    L_C, omega_over_Q = continuity_adjusted_coulomb_weight(
        L, qA_GeV, omega_GeV
    )

    # The Coulomb/longitudinal sector is reduced with nuclear-current
    # continuity. The DM transition current itself is not assumed conserved.
    # Charge coefficients already matched in the M + Phi'' study.
    cM = f1 + tN * (f1 + 2.0 * f2) / (8.0 * mN_GeV * mN_GeV)
    cPhiPP = Q2 * (f1 + 2.0 * f2) / (4.0 * mN_GeV * mN_GeV)
    C_M = cM * cM * L_C
    C_PhiPP = cPhiPP * cPhiPP * L_C
    C_MPhiPP = 2.0 * cM * cPhiPP * L_C

    # AFH Eq. (107), with l_M=-F1*T3 and
    # l_5=+i(F1+F2)/(2mN) (q_AFH x T3).
    C_Delta = f1 * f1 * Q2 * LT / (2.0 * mN_GeV * mN_GeV)
    C_SigmaPrime = (
        (f1 + f2) * (f1 + f2) * Q2 * LT
        / (8.0 * mN_GeV * mN_GeV)
    )
    C_SigmaPrimeDelta = (
        -f1 * (f1 + f2) * Q2 * LT
        / (2.0 * mN_GeV * mN_GeV)
    )

    cauchy_identity_residual = (
        C_SigmaPrimeDelta
        + 2.0 * np.sign(f1 * (f1 + f2))
        * np.sqrt(max(0.0, C_Delta * C_SigmaPrime))
    )
    identity_scale = max(
        abs(C_SigmaPrimeDelta),
        2.0 * np.sqrt(max(0.0, C_Delta * C_SigmaPrime)),
        1.0e-300,
    )

    return {
        "qA_GeV": float(qA_GeV),
        "omega_GeV": float(omega_GeV),
        "omega_over_Q": float(omega_over_Q),
        "tN_GeV2": float(tN),
        "L00_charge_weight": float(L00),
        "L_C_continuity_adjusted_charge_weight": float(L_C),
        "charge_continuity_relative_correction": float(
            L_C / max(abs(L00), 1.0e-300) - 1.0
        ),
        "F1V_input": float(f1),
        "F2V_input": float(f2),
        "mN_GeV": float(mN_GeV),
        "form_factor_status": "constant provisional q=0 anchors; finite-t dependence not included",
        "AFH_q_convention": "q_AFH=-q_A; q_N=+q_A",
        "response_column_convention": "physical equal-p/n AFH columns; factor four belongs to response columns exactly once",
        "C_M": float(C_M),
        "C_PhiPP": float(C_PhiPP),
        "C_MPhiPP": float(C_MPhiPP),
        "C_Delta": float(C_Delta),
        "C_SigmaPrime": float(C_SigmaPrime),
        "C_SigmaPrimeDelta": float(C_SigmaPrimeDelta),
        "C_SigmaDoublePrime": 0.0,
        "C_PhiTildePrime": 0.0,
        "C_Delta_over_C_M": float(C_Delta / max(abs(C_M), 1e-300)),
        "C_SigmaPrime_over_C_M": float(C_SigmaPrime / max(abs(C_M), 1e-300)),
        "C_SigmaPrimeDelta_over_C_M": float(C_SigmaPrimeDelta / max(abs(C_M), 1e-300)),
        "C_SigmaPrimeDelta_cauchy_identity_relative_residual": float(
            abs(cauchy_identity_residual) / identity_scale
        ),
        "scope": (
            "leading static one-body vector-current AFH particle coefficients; "
            "no AFH nuclear responses, OBDME, mediator propagator, or halo fold"
        ),
    }


def validate_nuclear_continuity_archive_entry(
    benchmark: dict, L: np.ndarray, *, tolerance: float = 5.0e-12
) -> dict:
    """Check recoil kinematics and the stored direct-vs-continuity contraction.

    The direct-vs-reduced identity is algebraic for a point nucleus whose
    elastic current obeys q_A.mu J_A^mu=0. It checks tensor/index conventions
    and archive consistency; it does not prove that a truncated many-body
    one-body nuclear current is dynamically conserved.
    """
    try:
        qA = float(benchmark["qA_magnitude_GeV"])
        omega = float(
            benchmark.get(
                "ER_GeV",
                float(benchmark.get("ER_keV", 0.0)) * 1.0e-6,
            )
        )
        mA = float(benchmark["mA_GeV"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "integrated tensor benchmark must contain qA_magnitude_GeV, "
            "mA_GeV and ER_GeV (or ER_keV)"
        ) from exc
    if not all(np.isfinite(value) for value in (qA, omega, mA)):
        raise ValueError("non-finite nuclear transfer kinematics")
    if qA <= 0.0 or omega < 0.0 or mA <= 0.0:
        raise ValueError("invalid nuclear transfer kinematics")

    q2_mass_shell = 2.0 * mA * omega + omega * omega
    q2_residual = abs(qA * qA - q2_mass_shell) / max(
        abs(qA * qA), abs(q2_mass_shell), 1.0e-300
    )
    if q2_residual > tolerance:
        raise ValueError(
            "qA, ER and mA do not satisfy the elastic nuclear mass-shell "
            f"relation: relative residual={q2_residual:.6g}"
        )

    contractions = benchmark.get("point_nucleus_contractions")
    if not isinstance(contractions, dict):
        raise ValueError("integrated tensor benchmark lacks point_nucleus_contractions")

    eta = omega / qA
    L00 = float(np.real(L[0, 0]))
    L03sum = float(np.real(L[0, 3] + L[3, 0]))
    L33 = float(np.real(L[3, 3]))
    J0 = 2.0 * mA + omega
    L_C = L00 - eta * L03sum + eta * eta * L33
    direct = J0 * J0 * L00 + qA * qA * L33 - J0 * qA * L03sum
    reduced = J0 * J0 * L_C
    identity_residual = abs(reduced - direct) / max(
        abs(reduced), abs(direct), 1.0
    )
    if identity_residual > tolerance:
        raise ValueError(
            "direct point-nucleus contraction disagrees with continuity "
            f"reduction: relative residual={identity_residual:.6g}"
        )

    stored_residual = float(
        contractions.get("continuity_reduced_relative_residual", math.inf)
    )
    if not np.isfinite(stored_residual) or stored_residual > tolerance:
        raise ValueError(
            "stored point-nucleus continuity identity residual exceeds "
            f"{tolerance}: {stored_residual}"
        )
    stored_L00 = float(contractions.get("I00", math.nan))
    stored_LC = float(
        contractions.get("L_C_continuity_adjusted", math.nan)
    )
    stored_direct = float(contractions.get("Ifull", math.nan))
    for name, stored, calculated in (
        ("I00", stored_L00, L00),
        ("L_C_continuity_adjusted", stored_LC, L_C),
        ("Ifull", stored_direct, direct),
    ):
        if not np.isfinite(stored) or not math.isclose(
            stored, calculated, rel_tol=2.0e-11, abs_tol=2.0e-12
        ):
            raise ValueError(
                f"stored {name} disagrees with recomputed tensor contraction"
            )
    return {
        "mA_GeV": mA,
        "ER_GeV": omega,
        "qA_GeV": qA,
        "qA_mass_shell_relative_residual": q2_residual,
        "nuclear_omega_over_Q": eta,
        "direct_vs_continuity_relative_residual": identity_residual,
        "continuity_reduction_assumption": (
            "conditional on conservation of the complete nuclear vector current"
        ),
    }


def analyze_tensor_archive(
    archive: dict,
    *,
    f1: float = DEFAULT_F1,
    f2: float = DEFAULT_F2,
    mN_GeV: float = DEFAULT_MN_GEV,
) -> dict:
    if "benchmarks" not in archive or not isinstance(archive["benchmarks"], list):
        raise ValueError("input archive has no benchmarks list")
    rows = []
    for benchmark in archive["benchmarks"]:
        L = complex_from_pairs(benchmark["L_q_aligned_real_imag"])
        if L.shape != (4, 4):
            raise ValueError(
                f"{benchmark.get('benchmark', 'unknown')}: L tensor shape {L.shape}"
            )
        qA = float(benchmark["qA_magnitude_GeV"])
        continuity_validation = validate_nuclear_continuity_archive_entry(
            benchmark, L
        )
        omega = continuity_validation["ER_GeV"]
        weights = extract_leptonic_weights(
            L, qA_GeV=qA, omega_GeV=omega
        )
        afh = extract_afh_vector_coefficients(
            L, qA, f1=f1, f2=f2, mN_GeV=mN_GeV, omega_GeV=omega
        )
        rows.append({
            "benchmark": benchmark.get("benchmark"),
            "width_scheme": benchmark.get("width_scheme"),
            "g2": benchmark.get("g2"),
            "ER_keV": benchmark.get("ER_keV"),
            "ER_GeV": omega,
            "nuclear_continuity_validation": continuity_validation,
            "speed_kms": benchmark.get("speed_kms"),
            "quadrature": {
                "nw": benchmark.get("nw"),
                "nz": benchmark.get("nz"),
                "nphi": benchmark.get("nphi"),
            },
            "leptonic_weights": weights,
            "afh_vector_coefficients": afh,
        })

    max_helicity_ratio = max(
        row["leptonic_weights"]["generic_transverse_helicity_odd_over_transverse_sum"]
        for row in rows
    )
    max_cauchy_residual = max(
        row["afh_vector_coefficients"]["C_SigmaPrimeDelta_cauchy_identity_relative_residual"]
        for row in rows
    )
    return {
        "status": "PASS_AFH_LEPTONIC_COEFFICIENT_EXTRACTION",
        "source_status": archive.get("status"),
        "scope": (
            "leading static vector-current particle coefficients from AFH Eq. (107); "
            "not yet contracted with AFH nuclear response values"
        ),
        "form_factor_input": {
            "F1V": f1,
            "F2V": f2,
            "mN_GeV": mN_GeV,
            "status": "constant provisional q=0 anchors; finite-t dependence not included",
        },
        "benchmarks": rows,
        "summary": {
            "benchmark_count": len(rows),
            "max_generic_transverse_helicity_odd_over_transverse_sum": max_helicity_ratio,
            "max_AFH_spatial_Cauchy_identity_relative_residual": max_cauchy_residual,
            "max_abs_continuity_charge_relative_correction": max(
                abs(row["afh_vector_coefficients"]["charge_continuity_relative_correction"])
                for row in rows
            ),
            "max_qA_mass_shell_relative_residual": max(
                row["nuclear_continuity_validation"]["qA_mass_shell_relative_residual"]
                for row in rows
            ),
            "max_direct_vs_continuity_relative_residual": max(
                row["nuclear_continuity_validation"]["direct_vs_continuity_relative_residual"]
                for row in rows
            ),
            "continuity_reduction_scope": (
                "conditional on conservation of the complete nuclear vector current; "
                "the point-nucleus identity validates kinematics and tensor conventions only"
            ),
            "min_C_Delta_over_C_M": min(
                row["afh_vector_coefficients"]["C_Delta_over_C_M"] for row in rows
            ),
            "max_C_Delta_over_C_M": max(
                row["afh_vector_coefficients"]["C_Delta_over_C_M"] for row in rows
            ),
            "min_C_SigmaPrime_over_C_M": min(
                row["afh_vector_coefficients"]["C_SigmaPrime_over_C_M"] for row in rows
            ),
            "max_C_SigmaPrime_over_C_M": max(
                row["afh_vector_coefficients"]["C_SigmaPrime_over_C_M"] for row in rows
            ),
            "min_C_SigmaPrimeDelta_over_C_M": min(
                row["afh_vector_coefficients"]["C_SigmaPrimeDelta_over_C_M"] for row in rows
            ),
            "max_C_SigmaPrimeDelta_over_C_M": max(
                row["afh_vector_coefficients"]["C_SigmaPrimeDelta_over_C_M"] for row in rows
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--f1", type=float, default=DEFAULT_F1)
    parser.add_argument("--f2", type=float, default=DEFAULT_F2)
    parser.add_argument("--mN", type=float, default=DEFAULT_MN_GEV)
    args = parser.parse_args()

    archive = json.loads(args.input.read_text(encoding="utf-8"))
    result = analyze_tensor_archive(
        archive, f1=args.f1, f2=args.f2, mN_GeV=args.mN
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
