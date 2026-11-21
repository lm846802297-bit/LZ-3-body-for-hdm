#!/usr/bin/env python3
"""Quadrature-order convergence audit for every component of the 3-body Gram tensor.

This is a numerical convergence diagnostic for the DM-side integrated tensor.
It does not project onto AFH nuclear multipoles.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from three_body_phase_space_tensor import (
    M_A,
    MCHI,
    integrate_spin_resolved_tensor,
)

WIDTH_SCHEMES = ("pole",)

# Formal-production stress points: near-pole and off-pole Xe-131 benchmarks.
# All convergence levels use the same constant pole-width prescription.
CASES = (
    {
        "name": "near_pole_g2_0p1",
        "ms": 300.0e-6,
        "delta_m": 362.0e-6,
        "ER": 267.0e-6,
        "speed_kms": 776.0,
        "g2": 0.1,
        "mapping": "sine2",
        "orders": ((32, 16, 8), (40, 24, 12), (48, 32, 16)),
    },
    {
        "name": "near_pole_g2_1",
        "ms": 300.0e-6,
        "delta_m": 362.0e-6,
        "ER": 267.0e-6,
        "speed_kms": 776.0,
        "g2": 1.0,
        "mapping": "sine2",
        "orders": ((32, 16, 8), (40, 24, 12), (48, 32, 16)),
    },
    {
        "name": "green_450keV_g2_1",
        "ms": 300.0e-6,
        "delta_m": 450.0e-6,
        "ER": 200.0e-6,
        "speed_kms": 776.0,
        "g2": 1.0,
        "mapping": "threshold_u2",
        "orders": ((24, 16, 8), (32, 24, 12), (40, 32, 16)),
    },
)

# These are reporting thresholds, not a substitute for checking the observed
# convergence pattern and the stability of the final physical rate.
DEFAULT_FROBENIUS_TOL = 1.0e-3
DEFAULT_ACTIVE_COMPONENT_TOL = 1.0e-2
DEFAULT_CONTRACTION_TOL = 1.0e-3
ACTIVE_COMPONENT_FLOOR = 1.0e-8


def complex_from_pairs(value) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.shape[-1] != 2:
        raise ValueError("complex-pair array must have a final [real, imag] axis")
    return array[..., 0] + 1j * array[..., 1]


def convergence_metrics(
    coarse: np.ndarray,
    fine: np.ndarray,
    *,
    frobenius_tolerance: float = DEFAULT_FROBENIUS_TOL,
    active_component_tolerance: float = DEFAULT_ACTIVE_COMPONENT_TOL,
    active_floor: float = ACTIVE_COMPONENT_FLOOR,
) -> dict:
    """Compare all complex tensor entries, including small but active terms."""
    coarse = np.asarray(coarse, dtype=complex)
    fine = np.asarray(fine, dtype=complex)
    if coarse.shape != fine.shape:
        raise ValueError(f"shape mismatch: {coarse.shape} != {fine.shape}")
    if not np.all(np.isfinite(coarse)) or not np.all(np.isfinite(fine)):
        raise ValueError("non-finite tensor component in convergence comparison")

    difference = fine - coarse
    fine_norm = float(np.linalg.norm(fine))
    diff_norm = float(np.linalg.norm(difference))
    frobenius_relative = diff_norm / max(fine_norm, 1.0e-300)
    fine_abs = np.abs(fine)
    diff_abs = np.abs(difference)
    max_fine = float(np.max(fine_abs)) if fine_abs.size else 0.0
    max_abs_difference = float(np.max(diff_abs)) if diff_abs.size else 0.0
    max_scaled_absolute = max_abs_difference / max(max_fine, 1.0e-300)

    active = fine_abs >= max_fine * active_floor if max_fine > 0 else np.zeros_like(fine_abs, dtype=bool)
    if np.any(active):
        component_relative = diff_abs[active] / np.maximum(fine_abs[active], 1.0e-300)
        active_flat_indices = np.flatnonzero(active)
        worst_local = int(np.argmax(component_relative))
        worst_flat = int(active_flat_indices[worst_local])
        worst_index = [int(index) for index in np.unravel_index(worst_flat, fine.shape)]
        max_active_component_relative = float(component_relative[worst_local])
    else:
        worst_index = None
        max_active_component_relative = 0.0

    passed = (
        frobenius_relative <= frobenius_tolerance
        and max_active_component_relative <= active_component_tolerance
    )
    return {
        "shape": list(fine.shape),
        "frobenius_relative_difference": frobenius_relative,
        "max_absolute_difference": max_abs_difference,
        "max_difference_over_max_fine_component": max_scaled_absolute,
        "active_component_floor_relative_to_max": active_floor,
        "active_component_count": int(np.count_nonzero(active)),
        "max_active_component_relative_difference": max_active_component_relative,
        "worst_active_component_index": worst_index,
        "frobenius_tolerance": frobenius_tolerance,
        "active_component_tolerance": active_component_tolerance,
        "pass": passed,
    }


def _tensor_eigen_summary(gram: np.ndarray, tensor: np.ndarray) -> dict:
    gram_matrix = gram.reshape(16, 16)
    gram_hermitian = 0.5 * (gram_matrix + gram_matrix.conj().T)
    tensor_hermitian = 0.5 * (tensor + tensor.conj().T)
    gram_eigs = np.linalg.eigvalsh(gram_hermitian)
    tensor_eigs = np.linalg.eigvalsh(tensor_hermitian)
    return {
        "gram_min_eigenvalue": float(np.min(gram_eigs)),
        "gram_max_eigenvalue": float(np.max(gram_eigs)),
        "tensor_min_eigenvalue": float(np.min(tensor_eigs)),
        "tensor_max_eigenvalue": float(np.max(tensor_eigs)),
        "gram_hermiticity_residual": float(
            np.linalg.norm(gram_matrix - gram_matrix.conj().T)
            / max(np.linalg.norm(gram_matrix), 1.0)
        ),
        "tensor_hermiticity_residual": float(
            np.linalg.norm(tensor - tensor.conj().T)
            / max(np.linalg.norm(tensor), 1.0)
        ),
    }


def run_convergence_scan(
    *,
    frobenius_tolerance: float = DEFAULT_FROBENIUS_TOL,
    active_component_tolerance: float = DEFAULT_ACTIVE_COMPONENT_TOL,
    contraction_tolerance: float = DEFAULT_CONTRACTION_TOL,
) -> dict:
    case_results = []
    for case in CASES:
        for width_scheme in WIDTH_SCHEMES:
            level_results = []
            for nw, nz, nphi in case["orders"]:
                result = integrate_spin_resolved_tensor(
                    mchi=MCHI,
                    ms=case["ms"],
                    delta_m=case["delta_m"],
                    mA=M_A,
                    ER=case["ER"],
                    speed_kms=case["speed_kms"],
                    g2=case["g2"],
                    width_scheme=width_scheme,
                    mapping=case["mapping"],
                    nw=nw,
                    nz=nz,
                    nphi=nphi,
                    crosscheck_dirac_trace=False,
                )
                if not result.get("phase_space_open"):
                    raise RuntimeError(
                        f"phase space unexpectedly closed: {case['name']} {width_scheme}"
                    )
                gram = complex_from_pairs(result["G_q_aligned_real_imag"])
                tensor = complex_from_pairs(result["L_q_aligned_real_imag"])
                level_results.append({
                    "orders": {"nw": nw, "nz": nz, "nphi": nphi},
                    "quadrature_points": result["quadrature_points"],
                    "gram": gram,
                    "tensor": tensor,
                    "contractions": result["point_nucleus_contractions"],
                    "eigen_summary": _tensor_eigen_summary(gram, tensor),
                    "pole_clearance_keV": result["pole_clearance_keV"],
                    "Gamma_pole_keV": result["Gamma_pole_keV"],
                })

            comparisons = []
            for index in range(len(level_results) - 1):
                coarse = level_results[index]
                fine = level_results[index + 1]
                comparisons.append({
                    "from_orders": coarse["orders"],
                    "to_orders": fine["orders"],
                    "gram": convergence_metrics(
                        coarse["gram"], fine["gram"],
                        frobenius_tolerance=frobenius_tolerance,
                        active_component_tolerance=active_component_tolerance,
                    ),
                    "L_munu": convergence_metrics(
                        coarse["tensor"], fine["tensor"],
                        frobenius_tolerance=frobenius_tolerance,
                        active_component_tolerance=active_component_tolerance,
                    ),
                    "point_nucleus_contractions": {
                        key: {
                            "coarse": float(coarse["contractions"][key]),
                            "fine": float(fine["contractions"][key]),
                            "relative_difference": abs(
                                float(fine["contractions"][key])
                                - float(coarse["contractions"][key])
                            ) / max(
                                abs(float(fine["contractions"][key])),
                                abs(float(coarse["contractions"][key])),
                                1.0,
                            ),
                            "pass": abs(
                                float(fine["contractions"][key])
                                - float(coarse["contractions"][key])
                            ) / max(
                                abs(float(fine["contractions"][key])),
                                abs(float(coarse["contractions"][key])),
                                1.0,
                            ) <= contraction_tolerance,
                        }
                        for key in coarse["contractions"]
                    },
                })

            high = level_results[-1]
            case_results.append({
                "case": case["name"],
                "width_scheme": width_scheme,
                "g2": case["g2"],
                "mapping": case["mapping"],
                "levels": [
                    {
                        "orders": item["orders"],
                        "quadrature_points": item["quadrature_points"],
                        "contractions": item["contractions"],
                        "eigen_summary": item["eigen_summary"],
                    }
                    for item in level_results
                ],
                "successive_comparisons": comparisons,
                "high_order_contractions": high["contractions"],
            })

    all_pairs = [
        pair
        for case in case_results
        for pair in case["successive_comparisons"]
    ]
    final_pairs = [
        case["successive_comparisons"][-1]
        for case in case_results
    ]
    all_final_pass = all(
        pair["gram"]["pass"]
        and pair["L_munu"]["pass"]
        and all(item["pass"] for item in pair["point_nucleus_contractions"].values())
        for pair in final_pairs
    )
    max_gram_fro = max(
        pair["gram"]["frobenius_relative_difference"] for pair in final_pairs
    )
    max_l_fro = max(
        pair["L_munu"]["frobenius_relative_difference"] for pair in final_pairs
    )
    max_gram_active = max(
        pair["gram"]["max_active_component_relative_difference"] for pair in final_pairs
    )
    max_l_active = max(
        pair["L_munu"]["max_active_component_relative_difference"] for pair in final_pairs
    )
    max_contraction_difference = max(
        item["relative_difference"]
        for pair in final_pairs
        for item in pair["point_nucleus_contractions"].values()
    )
    return {
        "status": "CONVERGED_AT_REPORTED_ORDERS" if all_final_pass else "CONVERGENCE_NOT_YET_ESTABLISHED",
        "scope": (
            "quadrature-order convergence of the phase-space-integrated DM-side "
            "G and L tensors at selected fixed-speed Xe-131 stress benchmarks; "
            "not AFH nuclear matching"
        ),
        "width_schemes": list(WIDTH_SCHEMES),
        "formal_width_prescription": "Eq. (19) asymmetric constant pole width in the second chi2 propagator only",
        "benchmarks": case_results,
        "acceptance": {
            "successive_high_order_pair_pass": all_final_pass,
            "frobenius_relative_tolerance": frobenius_tolerance,
            "active_component_relative_tolerance": active_component_tolerance,
            "point_nucleus_contraction_relative_tolerance": contraction_tolerance,
            "active_component_floor": ACTIVE_COMPONENT_FLOOR,
            "max_final_gram_frobenius_difference": max_gram_fro,
            "max_final_L_frobenius_difference": max_l_fro,
            "max_final_gram_active_component_difference": max_gram_active,
            "max_final_L_active_component_difference": max_l_active,
            "max_final_point_nucleus_contraction_difference": max_contraction_difference,
            "all_sixteen_by_sixteen_complex_Gram_components_compared": True,
            "all_four_by_four_complex_L_components_compared": True,
            "scope_note": (
                "The final comparison is medium-to-high order. A PASS is a "
                "numerical convergence statement only at the selected "
                "benchmarks and stated tolerances."
            ),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--frobenius-tol", type=float, default=DEFAULT_FROBENIUS_TOL)
    parser.add_argument("--active-component-tol", type=float, default=DEFAULT_ACTIVE_COMPONENT_TOL)
    parser.add_argument("--contraction-tol", type=float, default=DEFAULT_CONTRACTION_TOL)
    args = parser.parse_args()
    result = run_convergence_scan(
        frobenius_tolerance=args.frobenius_tol,
        active_component_tolerance=args.active_component_tol,
        contraction_tolerance=args.contraction_tol,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "acceptance": result["acceptance"],
        "benchmarks": len(result["benchmarks"]),
        "output": str(args.out),
    }, indent=2))


if __name__ == "__main__":
    main()
