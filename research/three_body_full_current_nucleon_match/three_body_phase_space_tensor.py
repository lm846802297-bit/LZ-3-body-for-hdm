#!/usr/bin/env python3
"""Phase-space-integrated, spin-resolved three-body DM-current tensor.

The tensor is stored in a local frame whose z axis is q_A at each phase-space
point.  It preserves the complete four-vector current, external DM spin
structure, both scalar-emission orderings, and their coherent interference.
It is a prerequisite for AFH operator matching, not yet an AFH response
coefficient or a nuclear event rate.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPIN_DIR = ROOT / "research" / "three_body_spin_resolved_current"
AUDIT_DIR = ROOT / "research" / "vector_current_response_audit"
for path in (SPIN_DIR, AUDIT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import spin_resolved_three_body_current as dm  # noqa: E402
import vector_current_response_audit as vca  # noqa: E402

eq6 = dm.eq6
PAULI = (eq6.I2, eq6.s1, eq6.s2, eq6.s3)
MCHI = 1000.0
MASS_U_GEV = 0.93149410242
M_A = 131.0 * MASS_U_GEV
FORMAL_WIDTH_SCHEME = "pole"


def pauli_components(current: np.ndarray) -> np.ndarray:
    """Return c[mu,a] in T^mu=sum_a c[mu,a] sigma_chi^a."""
    if current.shape != (4, 2, 2):
        raise ValueError(f"expected (4,2,2) current, got {current.shape}")
    return np.asarray([
        [0.5 * np.trace(P @ current[mu]) for P in PAULI]
        for mu in range(4)
    ], dtype=complex)


def q_aligned_rotation(q_A: np.ndarray) -> np.ndarray:
    """Rows of R are a right-handed orthonormal basis (e1,e2,qhat)."""
    q_vec = np.asarray(q_A[1:], dtype=float)
    q_norm = float(np.linalg.norm(q_vec))
    if q_norm <= 0.0:
        raise ValueError("q_A spatial momentum must be nonzero")
    qhat = q_vec / q_norm
    reference = np.asarray([1.0, 0.0, 0.0])
    if abs(float(np.dot(reference, qhat))) > 0.9:
        reference = np.asarray([0.0, 1.0, 0.0])
    e1 = np.cross(reference, qhat)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(qhat, e1)
    return np.stack((e1, e2, qhat), axis=0)


def rotate_current_to_q_frame(current: np.ndarray, q_A: np.ndarray):
    """Rotate only the spatial Lorentz index; DM spin basis is retained."""
    rotation = q_aligned_rotation(q_A)
    rotated = np.asarray(current, dtype=complex).copy()
    rotated[1:] = np.einsum("ij,jab->iab", rotation, current[1:])
    return rotated, rotation


def gram_from_pauli_coefficients(coefficients: np.ndarray) -> np.ndarray:
    """G[mu,a,nu,b]=c[mu,a] c[nu,b]^*."""
    if coefficients.shape != (4, 4):
        raise ValueError("Pauli coefficient array must have shape (4,4)")
    return np.einsum("ma,nb->manb", coefficients, coefficients.conj())


def tensor_from_gram(gram: np.ndarray) -> np.ndarray:
    """Trace over the unpolarized initial/final DM spin: L^{mu nu}=sum_a G_mana."""
    if gram.shape != (4, 4, 4, 4):
        raise ValueError("Gram tensor must have shape (4,4,4,4)")
    return np.einsum("mana->mn", gram)


def complex_pairs(array: np.ndarray):
    array = np.asarray(array, dtype=complex)
    return np.stack((array.real, array.imag), axis=-1).tolist()


def _phase_space_nodes(nw: int, nz: int, nphi: int):
    xw, ww = leggauss(nw)
    xz, wz = leggauss(nz)
    xp, wp = leggauss(nphi)
    u = 0.5 * (xw + 1.0)
    wu = 0.5 * ww
    z_values = xz
    z_weights = wz
    phi_values = math.pi * (xp + 1.0)
    phi_weights = 0.5 * wp
    return u, wu, z_values, z_weights, phi_values, phi_weights


def scalar_contractions_from_q_frame(
    tensor: np.ndarray, *, mA: float, ER: float
) -> dict[str, float]:
    """Point-nucleus contractions in the q-aligned frame."""
    Q_A = math.sqrt(2.0 * mA * ER + ER * ER)
    J0 = 2.0 * mA + ER
    spatial_trace = np.trace(tensor[1:, 1:])
    longitudinal = tensor[3, 3]
    transverse = tensor[1, 1] + tensor[2, 2]
    charge = J0 * J0 * tensor[0, 0]
    spatial = Q_A * Q_A * tensor[3, 3]
    interference = -J0 * Q_A * (tensor[0, 3] + tensor[3, 0])
    full = charge + spatial + interference
    omega_over_Q = ER / Q_A if Q_A > 0.0 else 0.0
    L_coulomb = (
        tensor[0, 0]
        - omega_over_Q * (tensor[0, 3] + tensor[3, 0])
        + omega_over_Q * omega_over_Q * tensor[3, 3]
    )
    continuity_reduced = J0 * J0 * L_coulomb
    continuity_residual = float(
        abs(continuity_reduced - full)
        / max(abs(continuity_reduced), abs(full), 1.0)
    )
    return {
        "I00": float(np.real(tensor[0, 0])),
        "Ispatial_trace": float(np.real(spatial_trace)),
        "Ilongitudinal": float(np.real(longitudinal)),
        "Itransverse": float(np.real(transverse)),
        "Icharge": float(np.real(charge)),
        "Ispatial_nuclear": float(np.real(spatial)),
        "Iinterference": float(np.real(interference)),
        "Ifull": float(np.real(full)),
        "omega_over_Q": float(omega_over_Q),
        "L_C_continuity_adjusted": float(np.real(L_coulomb)),
        "Icontinuity_reduced": float(np.real(continuity_reduced)),
        "continuity_reduced_relative_residual": continuity_residual,
    }


def integrate_spin_resolved_tensor(
    *,
    mchi: float,
    ms: float,
    delta_m: float,
    mA: float,
    ER: float,
    speed_kms: float,
    g2: float,
    width_scheme: str = "pole",
    mapping: str = "threshold_u2",
    nw: int = 24,
    nz: int = 16,
    nphi: int = 8,
    crosscheck_dirac_trace: bool = True,
) -> dict:
    """Integrate the complete q-frame spin-resolved three-body current Gram tensor."""
    if width_scheme not in {"zero", "pole", "running"}:
        raise ValueError("width_scheme must be zero, pole, or running")
    if mapping not in {"threshold_u2", "sine2"}:
        raise ValueError("mapping must be threshold_u2 or sine2")
    if min(nw, nz, nphi) < 2:
        raise ValueError("quadrature orders must be at least two")

    wmin, wmax = eq6.limits(mchi, ms, mA, ER, speed_kms)
    if wmax <= wmin:
        return {"phase_space_open": False}

    u, wu, z_values, z_weights, phi_values, phi_weights = (
        _phase_space_nodes(nw, nz, nphi)
    )
    delta_W2_max = wmax - wmin
    if mapping == "threshold_u2":
        delta_W2_values = delta_W2_max * u * u
        jacobians = 2.0 * delta_W2_max * u
    else:
        angle = 0.5 * math.pi * u
        delta_W2_values = delta_W2_max * np.sin(angle) ** 2
        jacobians = 0.5 * math.pi * delta_W2_max * np.sin(math.pi * u)

    mchi2 = mchi + delta_m
    G_total = np.zeros((4, 4, 4, 4), dtype=complex)
    G_before = np.zeros_like(G_total)
    G_after = np.zeros_like(G_total)
    Q_A = math.sqrt(2.0 * mA * ER + ER * ER)
    max_rotation_orthogonality = 0.0
    max_rotation_determinant_error = 0.0
    n_points = 0

    for delta_W2, jac, w_weight in zip(delta_W2_values, jacobians, wu):
        delta_W2 = float(delta_W2)
        W2 = wmin + delta_W2
        lambda_dimensionless = (
            delta_W2 * (4.0 * mchi * ms + delta_W2) / (W2 * W2)
        )
        phase_weight = float(jac * w_weight) * math.sqrt(
            max(0.0, lambda_dimensionless)
        )
        for z, z_weight in zip(z_values, z_weights):
            for phi, phi_weight in zip(phi_values, phi_weights):
                point = vca.stable_build_point(
                    mchi, ms, mA, ER, speed_kms,
                    delta_W2, float(z), float(phi),
                )
                imag = vca.width_imaginary_part(
                    point, mchi, ms, delta_m, g2, width_scheme
                )
                before, after, total = dm.spin_resolved_diagram_currents(
                    point, mchi, mchi2, imag
                )
                before_q, rotation = rotate_current_to_q_frame(before, point.q_A)
                after_q, _ = rotate_current_to_q_frame(after, point.q_A)
                total_q, _ = rotate_current_to_q_frame(total, point.q_A)

                orthogonality = float(np.linalg.norm(rotation @ rotation.T - np.eye(3)))
                determinant_error = abs(float(np.linalg.det(rotation)) - 1.0)
                max_rotation_orthogonality = max(max_rotation_orthogonality, orthogonality)
                max_rotation_determinant_error = max(max_rotation_determinant_error, determinant_error)

                c_before = pauli_components(before_q)
                c_after = pauli_components(after_q)
                c_total = pauli_components(total_q)
                common = phase_weight * float(z_weight) * float(phi_weight)

                G_before += common * gram_from_pauli_coefficients(c_before)
                G_after += common * gram_from_pauli_coefficients(c_after)
                G_total += common * gram_from_pauli_coefficients(c_total)
                n_points += 1

    G_interference = G_total - G_before - G_after
    L_total = tensor_from_gram(G_total)
    L_before = tensor_from_gram(G_before)
    L_after = tensor_from_gram(G_after)
    L_interference = tensor_from_gram(G_interference)

    gram_matrix = G_total.reshape(16, 16)
    gram_hermiticity = float(
        np.linalg.norm(gram_matrix - gram_matrix.conj().T)
        / max(np.linalg.norm(gram_matrix), 1.0)
    )
    tensor_hermiticity = float(
        np.linalg.norm(L_total - L_total.conj().T)
        / max(np.linalg.norm(L_total), 1.0)
    )
    gram_eigenvalues = np.linalg.eigvalsh(
        0.5 * (gram_matrix + gram_matrix.conj().T)
    )
    tensor_eigenvalues = np.linalg.eigvalsh(
        0.5 * (L_total + L_total.conj().T)
    )
    contractions = scalar_contractions_from_q_frame(
        L_total, mA=mA, ER=ER
    )

    crosscheck = None
    if crosscheck_dirac_trace:
        reference = vca.integrate_current_components(
            mchi=mchi,
            ms=ms,
            delta_m=delta_m,
            mA=mA,
            ER=ER,
            speed_kms=speed_kms,
            g2=g2,
            width_scheme=width_scheme,
            mapping=mapping,
            nw=nw,
            nz=nz,
            nphi=nphi,
        )
        keys = (
            "I00", "Ispatial_trace", "Ilongitudinal", "Itransverse",
            "Icharge", "Ispatial_nuclear", "Iinterference", "Ifull",
        )
        residuals = {
            key: abs(contractions[key] - float(reference[key]))
            / max(abs(float(reference[key])), abs(contractions[key]), 1.0)
            for key in keys
        }
        crosscheck = {
            "reference": {key: float(reference[key]) for key in keys},
            "spin_resolved": contractions,
            "relative_residuals": residuals,
            "max_relative_residual": max(residuals.values()),
        }

    return {
        "phase_space_open": True,
        "mchi_GeV": mchi,
        "ms_GeV": ms,
        "delta_m_GeV": delta_m,
        "mchi2_GeV": mchi2,
        "mA_GeV": mA,
        "ER_GeV": ER,
        "ER_keV": ER * 1.0e6,
        "speed_kms": speed_kms,
        "g2": g2,
        "width_scheme": width_scheme,
        "mapping": mapping,
        "nw": nw,
        "nz": nz,
        "nphi": nphi,
        "quadrature_points": n_points,
        "qA_magnitude_GeV": Q_A,
        "pole_clearance_keV": (mchi2 - math.sqrt(wmax)) * 1.0e6,
        "Gamma_pole_keV": (
            eq6.chi2_width_dirac_scalar(mchi, ms, delta_m, g2) * 1.0e6
        ),
        "q_frame_rotation_max_orthogonality_residual": max_rotation_orthogonality,
        "q_frame_rotation_max_determinant_residual": max_rotation_determinant_error,
        "gram_hermiticity_relative_residual": gram_hermiticity,
        "tensor_hermiticity_relative_residual": tensor_hermiticity,
        "gram_min_eigenvalue": float(np.min(gram_eigenvalues)),
        "tensor_min_eigenvalue": float(np.min(tensor_eigenvalues)),
        "point_nucleus_contractions": contractions,
        "dirac_trace_crosscheck": crosscheck,
        "L_q_aligned_real_imag": complex_pairs(L_total),
        "L_before_real_imag": complex_pairs(L_before),
        "L_after_real_imag": complex_pairs(L_after),
        "L_interference_real_imag": complex_pairs(L_interference),
        "G_q_aligned_real_imag": complex_pairs(G_total),
        "G_before_real_imag": complex_pairs(G_before),
        "G_after_real_imag": complex_pairs(G_after),
        "G_interference_real_imag": complex_pairs(G_interference),
    }


def run_default_audit():
    results = []
    for case in vca.DEFAULT_CASES:
        for scheme in (FORMAL_WIDTH_SCHEME,):
            result = integrate_spin_resolved_tensor(
                mchi=MCHI,
                ms=case["ms"],
                delta_m=case["delta_m"],
                mA=M_A,
                ER=case["ER"],
                speed_kms=case["speed_kms"],
                g2=case["g2"],
                width_scheme=scheme,
                mapping=case["mapping"],
                nw=case["nw"],
                nz=case["nz"],
                nphi=case["nphi"],
                crosscheck_dirac_trace=True,
            )
            result["benchmark"] = case["benchmark"]
            results.append(result)
    max_crosscheck = max(
        item["dirac_trace_crosscheck"]["max_relative_residual"]
        for item in results
    )
    min_gram_eigenvalue = min(item["gram_min_eigenvalue"] for item in results)
    min_tensor_eigenvalue = min(item["tensor_min_eigenvalue"] for item in results)
    max_hermiticity = max(
        max(
            item["gram_hermiticity_relative_residual"],
            item["tensor_hermiticity_relative_residual"],
        )
        for item in results
    )
    max_rotation_residual = max(
        max(
            item["q_frame_rotation_max_orthogonality_residual"],
            item["q_frame_rotation_max_determinant_residual"],
        )
        for item in results
    )
    acceptance = {
        "dirac_trace_max_relative_residual": max_crosscheck,
        "dirac_trace_tolerance": 2e-9,
        "gram_min_eigenvalue": min_gram_eigenvalue,
        "tensor_min_eigenvalue": min_tensor_eigenvalue,
        "minimum_eigenvalue_tolerance": -1e-10,
        "max_hermiticity_relative_residual": max_hermiticity,
        "hermiticity_tolerance": 1e-12,
        "max_q_frame_rotation_residual": max_rotation_residual,
        "rotation_tolerance": 1e-12,
    }
    acceptance["pass"] = (
        max_crosscheck < acceptance["dirac_trace_tolerance"]
        and min_gram_eigenvalue > acceptance["minimum_eigenvalue_tolerance"]
        and min_tensor_eigenvalue > acceptance["minimum_eigenvalue_tolerance"]
        and max_hermiticity < acceptance["hermiticity_tolerance"]
        and max_rotation_residual < acceptance["rotation_tolerance"]
    )
    return {
        "status": (
            "PASS_SPIN_RESOLVED_DM_TENSOR"
            if acceptance["pass"] else "FAIL_SPIN_RESOLVED_DM_TENSOR"
        ),
        "scope": (
            "exact DM-side four-vector tensor integrated over three-body phase space; "
            "not yet AFH multipole coefficients or a nuclear event rate"
        ),
        "source": "PR #53 spin-resolved T3 and independent Dirac-trace current audit",
        "natural_units": "GeV, metric (+---)",
        "pauli_basis": ["I", "sigma_x", "sigma_y", "sigma_z"],
        "lorentz_frame": "q-aligned at each phase-space point: (0,e1,e2,qhat)",
        "phase_space_measure": "same threshold-stable Eq.(6) W2,z,phi quadrature and sqrt(lambda_K)/W^2 weight",
        "width_schemes": [FORMAL_WIDTH_SCHEME],
        "formal_width_prescription": (
            "Eq. (19) asymmetric prescription: the first p-k chi2 propagator "
            "retains +i0+, while the second p'+k propagator uses the constant "
            "pole width Gamma_chi2(m_chi2). Zero-width and running-width "
            "results are diagnostics only."
        ),
        "acceptance": acceptance,
        "benchmarks": results,
        "limitations": [
            "The q-aligned spin-resolved DM tensor is an intermediate dynamical object; AFH one-body operator coefficients are not yet projected.",
            "The nucleon convection and magnetization operators and their AFH multipole contractions are not included in this tensor archive.",
            "The formal pole-only component-wise convergence scan covers three selected benchmarks and stated tolerances; it does not establish global convergence over all kinematics.",
            "No AFH isotope response, halo fold, detector response, or likelihood is included.",
            "Formal production is pole-width only; zero-width and running-width controls are excluded from the production tensor archive.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_default_audit()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "benchmarks": len(result["benchmarks"]),
        "acceptance": result["acceptance"],
        "output": str(args.out),
    }, indent=2))
    if not result["acceptance"]["pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
