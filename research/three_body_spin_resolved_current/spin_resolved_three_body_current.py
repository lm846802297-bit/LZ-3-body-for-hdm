#!/usr/bin/env python3
"""Spin-resolved 2x2 matrices for the coherent three-body dark-matter current."""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KERNEL_DIR = ROOT / "research" / "three_body_calculation_and_validation"
AUDIT_DIR = ROOT / "research" / "vector_current_response_audit"
for path in (KERNEL_DIR, AUDIT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import eq6_kernel as eq6  # noqa: E402
import vector_current_response_audit as vca  # noqa: E402

MASS_U_GEV = 0.93149410242
MCHI_GEV = 1000.0
MS_GEV = 300.0e-6
M_A_GEV = 131.0 * MASS_U_GEV
ER_GEV = 200.0e-6
SPEED_KMS = 776.0


def dirac_spinor_matrix(p4: np.ndarray, mass: float) -> np.ndarray:
    """Return the 4x2 positive-energy Dirac spinors, normalized ubar u=2m."""
    energy = float(p4[0])
    momentum = np.asarray(p4[1:], dtype=float)
    if energy + mass <= 0:
        raise ValueError("invalid positive-energy spinor")
    sigma_p = (
        eq6.s1 * momentum[0]
        + eq6.s2 * momentum[1]
        + eq6.s3 * momentum[2]
    )
    root = math.sqrt(energy + mass)
    upper = root * eq6.I2
    lower = sigma_p / root
    return np.vstack((upper, lower))


def spin_resolved_diagram_currents(
    point: eq6.Point,
    mchi: float,
    mchi2: float,
    denominator_imaginary_part: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return before, after, and coherent total T_3^mu as 4 arrays of 2x2 matrices.

    Matrix row/column indices are outgoing/incoming external chi1 spin.
    """
    before, after, total = vca.vector_current_vertices(
        point, mchi2, denominator_imaginary_part
    )
    u_in = dirac_spinor_matrix(point.p, mchi)
    u_out = dirac_spinor_matrix(point.p_prime, mchi)
    ubar_out = u_out.conj().T @ eq6.GAMMA[0]

    def sandwich(vertices):
        return np.asarray([
            ubar_out @ vertex @ u_in for vertex in vertices
        ], dtype=complex)

    return sandwich(before), sandwich(after), sandwich(total)


def tensor_from_spin_matrices(current: np.ndarray) -> np.ndarray:
    r"""Compute L^{mu nu}=1/2 Tr_2[T^mu T^{nu dagger}]."""
    if current.shape != (4, 2, 2):
        raise ValueError(f"expected (4,2,2) current, got {current.shape}")
    return np.asarray([
        [
            0.5 * np.trace(current[mu] @ current[nu].conj().T)
            for nu in range(4)
        ]
        for mu in range(4)
    ], dtype=complex)


def ward_lhs(point: eq6.Point, current: np.ndarray) -> np.ndarray:
    """q_A_mu T_3^mu using metric (+---) and q_A=P'-P=p-p'-k_s."""
    q = np.asarray(point.q_A, dtype=float)
    return q[0] * current[0] - np.einsum("i,ijk->jk", q[1:], current[1:])


def ward_rhs(
    point: eq6.Point, mchi: float, mchi2: float
) -> np.ndarray:
    r"""Exact zero-width identity:
    q_A_mu T_3^mu = (mchi2-mchi) ubar'[
      (slash(r_before)+mchi2)/D_before
      -(slash(r_after)+mchi2)/D_after]u.
    """
    r_before, r_after = eq6.chi2_internal_momenta(point)
    d_before = eq6.dot(r_before, r_before) - mchi2 * mchi2
    d_after = eq6.dot(r_after, r_after) - mchi2 * mchi2
    if abs(d_before) < 1e-30 or abs(d_after) < 1e-30:
        raise ZeroDivisionError("chi2 propagator pole in Ward identity")
    u_in = dirac_spinor_matrix(point.p, mchi)
    u_out = dirac_spinor_matrix(point.p_prime, mchi)
    ubar_out = u_out.conj().T @ eq6.GAMMA[0]
    operator = (
        (eq6.slash(r_before) + mchi2 * eq6.ID4) / d_before
        - (eq6.slash(r_after) + mchi2 * eq6.ID4) / d_after
    )
    return (mchi2 - mchi) * ubar_out @ operator @ u_in


def relative_matrix_residual(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / max(np.linalg.norm(a), np.linalg.norm(b), 1.0))


def scaled_ward_residual(point: eq6.Point, current: np.ndarray) -> float:
    """Scale q.T by |q| ||T|| to avoid a misleading absolute cancellation test."""
    q_norm = float(np.linalg.norm(np.asarray(point.q_A, dtype=float)))
    current_norm = float(np.linalg.norm(current))
    scale = max(q_norm * current_norm, 1.0)
    return float(np.linalg.norm(ward_lhs(point, current)) / scale)


def build_reference_point() -> eq6.Point:
    w_min, w_max = eq6.limits(
        MCHI_GEV, MS_GEV, M_A_GEV, ER_GEV, SPEED_KMS
    )
    if w_max <= w_min:
        raise RuntimeError("reference three-body phase space is closed")
    delta_w2 = 0.37 * (w_max - w_min)
    return vca.stable_build_point(
        MCHI_GEV, MS_GEV, M_A_GEV, ER_GEV, SPEED_KMS,
        delta_w2, z=0.21, phi=0.73,
    )


def run_smoke_test() -> dict:
    point = build_reference_point()
    mchi2 = MCHI_GEV + 362.0e-6
    before, after, total = spin_resolved_diagram_currents(
        point, MCHI_GEV, mchi2, 0.0
    )
    matrix_tensor = tensor_from_spin_matrices(total)
    trace_tensor = vca.dm_current_tensor(point, MCHI_GEV, mchi2, 0.0)
    lhs = ward_lhs(point, total)
    rhs = ward_rhs(point, MCHI_GEV, mchi2)
    degenerate = spin_resolved_diagram_currents(
        point, MCHI_GEV, MCHI_GEV, 0.0
    )[2]
    degenerate_divergence = ward_lhs(point, degenerate)
    separate_tensor = (
        tensor_from_spin_matrices(before) + tensor_from_spin_matrices(after)
    )
    return {
        "status": "spin_resolved_three_body_current_diagnostic",
        "current_shape": list(total.shape),
        "spin_trace_relative_residual": relative_matrix_residual(
            matrix_tensor, trace_tensor
        ),
        "ward_identity_relative_residual": relative_matrix_residual(lhs, rhs),
        "mass_split_GeV": mchi2 - MCHI_GEV,
        "nonconservation_norm_mass_split": float(np.linalg.norm(lhs)),
        "degenerate_mass_divergence_norm": float(np.linalg.norm(degenerate_divergence)),
        "degenerate_mass_divergence_scaled_residual": scaled_ward_residual(point, degenerate),
        "coherent_interference_tensor_norm": float(
            np.linalg.norm(matrix_tensor - separate_tensor)
        ),
        "qA_GeV": point.q_A.tolist(),
        "r_before_GeV": eq6.chi2_internal_momenta(point)[0].tolist(),
        "r_after_GeV": eq6.chi2_internal_momenta(point)[1].tolist(),
        "interpretation": [
            "The 2x2 spin matrices reproduce the existing spin-averaged L^{mu nu}.",
            "The off-diagonal current is not conserved for mchi2 != mchi1.",
            "The coherent two-diagram interference is retained before spin summation.",
            "This is a current-level validation, not yet a nucleon or AFH response matching.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    result = run_smoke_test()
    payload = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
