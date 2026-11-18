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


def extract_leptonic_weights(L: np.ndarray, *, hermiticity_tolerance=1e-10) -> dict:
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

    return {
        "charge_L00": charge,
        "longitudinal_L33": longitudinal,
        "charge_longitudinal_raw_2ReL03": float(charge_longitudinal_raw),
        "transverse_sum_L11_plus_L22": transverse_sum,
        "transverse_even_half_sum": float(transverse_even),
        "generic_transverse_helicity_odd_minus_2i_L12_minus_L21": helicity_odd,
        "generic_transverse_helicity_odd_imaginary_residual": helicity_imaginary_residual,
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


def extract_afh_vector_coefficients(
    L: np.ndarray,
    qA_GeV: float,
    *,
    f1: float = DEFAULT_F1,
    f2: float = DEFAULT_F2,
    mN_GeV: float = DEFAULT_MN_GEV,
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

    # Charge coefficients already matched in the M + Phi'' study.
    cM = f1 + tN * (f1 + 2.0 * f2) / (8.0 * mN_GeV * mN_GeV)
    cPhiPP = Q2 * (f1 + 2.0 * f2) / (4.0 * mN_GeV * mN_GeV)
    C_M = cM * cM * L00
    C_PhiPP = cPhiPP * cPhiPP * L00
    C_MPhiPP = 2.0 * cM * cPhiPP * L00

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
        "tN_GeV2": float(tN),
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
        weights = extract_leptonic_weights(L)
        afh = extract_afh_vector_coefficients(
            L, qA, f1=f1, f2=f2, mN_GeV=mN_GeV
        )
        rows.append({
            "benchmark": benchmark.get("benchmark"),
            "width_scheme": benchmark.get("width_scheme"),
            "g2": benchmark.get("g2"),
            "ER_keV": benchmark.get("ER_keV"),
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
