#!/usr/bin/env python3
"""Spin-resolved three-body DM current and finite-width Ward audit."""
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
    """4x2 positive-energy spinors, normalized by ubar_s u_s'=2m delta."""
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
    return np.vstack((root * eq6.I2, sigma_p / root))


def external_spinor_pair(point: eq6.Point, mchi: float):
    u_in = dirac_spinor_matrix(point.p, mchi)
    u_out = dirac_spinor_matrix(point.p_prime, mchi)
    return u_out.conj().T @ eq6.GAMMA[0], u_in


def spin_resolved_diagram_currents(
    point: eq6.Point,
    mchi: float,
    mchi2: float,
    denominator_imaginary_part: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Before, after, and coherent T3^mu as four 2x2 spin matrices."""
    before, after, total = vca.vector_current_vertices(
        point, mchi2, denominator_imaginary_part
    )
    ubar_out, u_in = external_spinor_pair(point, mchi)

    def sandwich(vertices):
        return np.asarray(
            [ubar_out @ vertex @ u_in for vertex in vertices], dtype=complex
        )

    return sandwich(before), sandwich(after), sandwich(total)


def tensor_from_spin_matrices(current: np.ndarray) -> np.ndarray:
    r"""L^{mu nu}=1/2 Tr_2[T^mu T^{nu dagger}]."""
    if current.shape != (4, 2, 2):
        raise ValueError(f"expected (4,2,2) current, got {current.shape}")
    return np.asarray(
        [
            [
                0.5 * np.trace(current[mu] @ current[nu].conj().T)
                for nu in range(4)
            ]
            for mu in range(4)
        ],
        dtype=complex,
    )


def ward_lhs(point: eq6.Point, current: np.ndarray) -> np.ndarray:
    """q_A_mu T3^mu with metric (+---), q_A=P'-P=p-p'-k_s."""
    q = np.asarray(point.q_A, dtype=float)
    return q[0] * current[0] - np.einsum("i,ijk->jk", q[1:], current[1:])


def ward_rhs_finite_width(
    point: eq6.Point,
    mchi: float,
    mchi2: float,
    denominator_imaginary_part: float = 0.0,
) -> np.ndarray:
    r"""Exact identity for the project's denominator-only width insertion.

    Only the after-emission propagator has D2+i*a; the before propagator
    remains D1. The extra i*a/(D2+i*a) ubar'u term is therefore mandatory.
    """
    r_before, r_after = eq6.chi2_internal_momenta(point)
    d1 = eq6.dot(r_before, r_before) - mchi2 * mchi2
    d2 = eq6.dot(r_after, r_after) - mchi2 * mchi2
    d2_complex = d2 + 1j * denominator_imaginary_part
    if abs(d1) < 1e-30 or abs(d2_complex) < 1e-30:
        raise ZeroDivisionError("chi2 propagator pole in Ward identity")

    ubar_out, u_in = external_spinor_pair(point, mchi)
    operator = (
        (eq6.slash(r_before) + mchi2 * eq6.ID4) / d1
        - (eq6.slash(r_after) + mchi2 * eq6.ID4) / d2_complex
    )
    scalar_bilinear = ubar_out @ u_in
    return (
        (mchi2 - mchi) * ubar_out @ operator @ u_in
        + (1j * denominator_imaginary_part / d2_complex) * scalar_bilinear
    )


def transverse_project_current(point: eq6.Point, current: np.ndarray) -> np.ndarray:
    """Project T^mu -> T^mu-q^mu(q.T)/q^2; valid for spacelike q_A^2 != 0."""
    q = np.asarray(point.q_A, dtype=float)
    q2 = eq6.dot(q, q)
    if abs(q2) < 1e-30:
        raise ZeroDivisionError("cannot project a null momentum transfer")
    divergence = ward_lhs(point, current)
    return current - q[:, None, None] * divergence[None, :, :] / q2


def conserved_point_nucleus_current(point: eq6.Point, mA: float) -> np.ndarray:
    """J_A^mu=(P+P')^mu with F_A(q_A^2) factored out."""
    return np.r_[2.0 * mA + point.E_R, point.q_A[1:]]


def contract_current_with_nucleus(current: np.ndarray, nucleus: np.ndarray) -> np.ndarray:
    """Return the 2x2 matrix J_{A,mu} T^mu for every external spin pair."""
    return nucleus[0] * current[0] - np.einsum(
        "i,ijk->jk", nucleus[1:], current[1:]
    )


def relative_matrix_residual(a: np.ndarray, b: np.ndarray) -> float:
    scale = max(float(np.linalg.norm(a)), float(np.linalg.norm(b)), 1.0)
    return float(np.linalg.norm(a - b) / scale)


def scaled_ward_residual(point: eq6.Point, current: np.ndarray) -> float:
    """Scale q.T by |q| ||T|| to avoid a misleading absolute cancellation test."""
    q_norm = float(np.linalg.norm(np.asarray(point.q_A, dtype=float)))
    current_norm = float(np.linalg.norm(current))
    scale = max(q_norm * current_norm, 1.0)
    return float(np.linalg.norm(ward_lhs(point, current)) / scale)


def scaled_ward_identity_residual(
    point: eq6.Point, current: np.ndarray, lhs: np.ndarray, rhs: np.ndarray
) -> float:
    """Scale the Ward-identity residual by |q| ||T||."""
    q_norm = float(np.linalg.norm(np.asarray(point.q_A, dtype=float)))
    current_norm = float(np.linalg.norm(current))
    scale = max(q_norm * current_norm, 1.0)
    return float(np.linalg.norm(lhs - rhs) / scale)


def build_reference_point() -> eq6.Point:
    w_min, w_max = eq6.limits(
        MCHI_GEV, MS_GEV, M_A_GEV, ER_GEV, SPEED_KMS
    )
    if w_max <= w_min:
        raise RuntimeError("reference three-body phase space is closed")
    # Cluster the reference point toward the upper W endpoint, near the
    # Delta-m=362-keV propagator pole, without sitting on the pole.
    delta_w2 = 0.37 * (w_max - w_min)
    return vca.stable_build_point(
        MCHI_GEV, MS_GEV, M_A_GEV, ER_GEV, SPEED_KMS,
        delta_w2, z=0.21, phi=0.73,
    )


def run_smoke_test() -> dict:
    point = build_reference_point()
    mchi2 = MCHI_GEV + 362.0e-6
    nucleus = conserved_point_nucleus_current(point, M_A_GEV)
    qdotj = point.q_A[0] * nucleus[0] - np.dot(point.q_A[1:], nucleus[1:])
    output = {
        "status": "finite_width_spin_resolved_current_diagnostic",
        "qA_GeV": point.q_A.tolist(),
        "qA2_GeV2": eq6.dot(point.q_A, point.q_A),
        "pole_clearance_at_reference_point_keV": (
            mchi2 - math.sqrt(point.W2)
        ) * 1.0e6,
        "nucleus_current_conservation_residual_GeV2": float(qdotj),
        "width_schemes": [],
    }
    for g2 in (0.1, 1.0):
        imag = vca.width_imaginary_part(
            point, MCHI_GEV, MS_GEV, 362.0e-6, g2, "pole"
        )
        before, after, total = spin_resolved_diagram_currents(
            point, MCHI_GEV, mchi2, imag
        )
        matrix_tensor = tensor_from_spin_matrices(total)
        trace_tensor = vca.dm_current_tensor(point, MCHI_GEV, mchi2, imag)
        lhs = ward_lhs(point, total)
        rhs = ward_rhs_finite_width(point, MCHI_GEV, mchi2, imag)
        transverse = transverse_project_current(point, total)
        amp = contract_current_with_nucleus(total, nucleus)
        amp_transverse = contract_current_with_nucleus(transverse, nucleus)
        output["width_schemes"].append({
            "g2": g2,
            "Gamma_pole_keV": imag / mchi2 * 1.0e6,
            "denominator_imaginary_part_GeV2": imag,
            "spin_trace_relative_residual": relative_matrix_residual(
                matrix_tensor, trace_tensor
            ),
            "finite_width_ward_identity_relative_residual": relative_matrix_residual(
                lhs, rhs
            ),
            "ward_divergence_norm": float(np.linalg.norm(lhs)),
            "transverse_projection_amplitude_residual": relative_matrix_residual(
                amp, amp_transverse
            ),
            "coherent_two_diagram_interference_norm": float(np.linalg.norm(
                tensor_from_spin_matrices(total)
                - tensor_from_spin_matrices(before)
                - tensor_from_spin_matrices(after)
            )),
        })
    return output


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
