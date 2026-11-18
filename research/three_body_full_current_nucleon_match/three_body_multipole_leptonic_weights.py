#!/usr/bin/env python3
"""Extract q-aligned leptonic multipole weights from the integrated DM tensor.

The output is the DM-side kinematic tensor projection only. AFH nuclear
multipole normalizations and current coefficients are deliberately not
inserted here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def complex_from_pairs(value) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape[-1] != 2:
        raise ValueError("complex-pair array must have a final [real, imag] axis")
    result = array[..., 0] + 1j * array[..., 1]
    if not np.all(np.isfinite(result)):
        raise ValueError("non-finite component in complex-pair tensor")
    return result


def extract_leptonic_weights(L: np.ndarray, *, hermiticity_tolerance=1e-10) -> dict:
    """Return Coulomb, longitudinal, transverse-even and helicity-odd factors.

    The transverse weights follow the standard multipole decomposition:
      w_T   = (L_11 + L_22)/2
      w_hel = -2 i (L_12 - L_21)
    The latter multiplies the transverse electric--magnetic interference
    before the exact AFH spherical-projector phases are inserted.
    """
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
        "transverse_helicity_odd_minus_2i_L12_minus_L21": helicity_odd,
        "transverse_helicity_odd_imaginary_residual": helicity_imaginary_residual,
        "transverse_helicity_odd_over_transverse_sum": (
            abs(helicity_odd) / max(abs(transverse_sum), 1.0e-300)
        ),
        "transverse_even_over_charge": (
            transverse_even / max(abs(charge), 1.0e-300)
        ),
        "longitudinal_over_charge": (
            longitudinal / max(abs(charge), 1.0e-300)
        ),
        "hermiticity_relative_residual": hermiticity,
        "scope": (
            "DM-side leptonic multipole weights before AFH nuclear-current "
            "projector coefficients and OBDME contraction"
        ),
    }


def analyze_tensor_archive(archive: dict) -> dict:
    if "benchmarks" not in archive or not isinstance(archive["benchmarks"], list):
        raise ValueError("input archive has no benchmarks list")
    rows = []
    for benchmark in archive["benchmarks"]:
        L = complex_from_pairs(benchmark["L_q_aligned_real_imag"])
        if L.shape != (4, 4):
            raise ValueError(
                f"{benchmark.get('benchmark', 'unknown')}: L tensor shape {L.shape}"
            )
        weights = extract_leptonic_weights(L)
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
            "weights": weights,
        })

    max_helicity_ratio = max(
        row["weights"]["transverse_helicity_odd_over_transverse_sum"]
        for row in rows
    )
    return {
        "status": "PASS_LEPTONIC_MULTIPOLE_WEIGHTS",
        "source_status": archive.get("status"),
        "scope": (
            "q-aligned DM-side tensor weights only; no AFH multipole "
            "normalization, nuclear response, or event rate"
        ),
        "benchmarks": rows,
        "summary": {
            "benchmark_count": len(rows),
            "max_transverse_helicity_odd_over_transverse_sum": max_helicity_ratio,
            "min_transverse_even_over_charge": min(
                row["weights"]["transverse_even_over_charge"] for row in rows
            ),
            "max_transverse_even_over_charge": max(
                row["weights"]["transverse_even_over_charge"] for row in rows
            ),
            "min_longitudinal_over_charge": min(
                row["weights"]["longitudinal_over_charge"] for row in rows
            ),
            "max_longitudinal_over_charge": max(
                row["weights"]["longitudinal_over_charge"] for row in rows
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    archive = json.loads(args.input.read_text(encoding="utf-8"))
    result = analyze_tensor_archive(archive)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
