#!/usr/bin/env python3
"""Exact one-nucleon Dirac-Pauli current contracted with spin-resolved T3^mu.

The nucleon is treated in a static elastic impulse-approximation point:
p_N=l-q/2, p_N'=l+q/2, with l perpendicular to q, so q_N^0=0.
This is a matching diagnostic, not a nuclear many-body calculation.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPIN_DIR = ROOT / "research" / "three_body_spin_resolved_current"
if str(SPIN_DIR) not in sys.path:
    sys.path.insert(0, str(SPIN_DIR))
import spin_resolved_three_body_current as dm  # noqa: E402

eq6 = dm.eq6
M_N_GEV = 0.938918
# F1 is normalized to one in this diagnostic.  F2/F1=-0.184 is the
# project's flavour-universal zero-momentum anchor; F2=0 is the control.
F2_SCENARIOS = (0.0, -0.184)
PAULI = (eq6.I2, eq6.s1, eq6.s2, eq6.s3)
METRIC = np.diag([1.0, -1.0, -1.0, -1.0])


def dirac_sigma(mu: int, nu: int) -> np.ndarray:
    return 0.5j * (
        eq6.GAMMA[mu] @ eq6.GAMMA[nu]
        - eq6.GAMMA[nu] @ eq6.GAMMA[mu]
    )


def nucleon_current_matrices(
    q_vec: np.ndarray,
    l_vec: np.ndarray,
    f1: float = 1.0,
    f2: float = 0.0,
    m_n: float = M_N_GEV,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return J_N^mu, q_N^mu, and the initial/final nucleon momenta.

    q_N^0 is fixed by the on-shell free-nucleon energies. For l perpendicular
    to q, q_N^0=0 up to floating-point roundoff.
    """
    q_vec = np.asarray(q_vec, dtype=float)
    l_vec = np.asarray(l_vec, dtype=float)
    if q_vec.shape != (3,) or l_vec.shape != (3,):
        raise ValueError("q_vec and l_vec must be three-vectors")
    if abs(float(np.dot(q_vec, l_vec))) > 1e-10 * max(np.linalg.norm(q_vec)*np.linalg.norm(l_vec), 1.0):
        raise ValueError("l_vec must be perpendicular to q_vec")

    p_i = l_vec - 0.5 * q_vec
    p_f = l_vec + 0.5 * q_vec
    e_i = math.sqrt(m_n * m_n + float(np.dot(p_i, p_i)))
    e_f = math.sqrt(m_n * m_n + float(np.dot(p_f, p_f)))
    q4 = np.asarray([e_f - e_i, *q_vec], dtype=float)

    u_i = dm.dirac_spinor_matrix(np.asarray([e_i, *p_i]), m_n)
    u_f = dm.dirac_spinor_matrix(np.asarray([e_f, *p_f]), m_n)
    ubar_f = u_f.conj().T @ eq6.GAMMA[0]
    q_lower = METRIC @ q4

    current = []
    for mu in range(4):
        vertex = f1 * eq6.GAMMA[mu].copy()
        pauli_term = sum(
            (dirac_sigma(mu, nu) * q_lower[nu] for nu in range(4)),
            start=np.zeros((4, 4), dtype=complex),
        )
        # q_N = p_N' - p_N. This sign is the translated project convention.
        vertex = vertex + 1j * f2 / (2.0 * m_n) * pauli_term
        current.append(ubar_f @ vertex @ u_i)
    return np.asarray(current), q4, (p_i, p_f)


def full_amplitude_operator(
    dm_current: np.ndarray, nucleon_current: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return full, charge-only, and spatial-only 4x4 spin operators."""
    if dm_current.shape != (4, 2, 2) or nucleon_current.shape != (4, 2, 2):
        raise ValueError("both currents must have shape (4,2,2)")
    charge = np.kron(dm_current[0], nucleon_current[0])
    spatial = -sum(
        (np.kron(dm_current[i], nucleon_current[i]) for i in range(1, 4)),
        start=np.zeros((4, 4), dtype=complex),
    )
    return charge + spatial, charge, spatial


def pauli_product_coefficients(amplitude: np.ndarray) -> np.ndarray:
    """Expand A=sum_ab c_ab sigma_chi^a tensor sigma_N^b."""
    if amplitude.shape != (4, 4):
        raise ValueError("amplitude must be a 4x4 matrix")
    return np.asarray([
        [
            0.25 * np.trace(np.kron(PAULI[a], PAULI[b]) @ amplitude)
            for b in range(4)
        ]
        for a in range(4)
    ], dtype=complex)


def reconstruct_from_pauli_coefficients(coeff: np.ndarray) -> np.ndarray:
    result = np.zeros((4, 4), dtype=complex)
    for a in range(4):
        for b in range(4):
            result += coeff[a, b] * np.kron(PAULI[a], PAULI[b])
    return result


def pauli_decomposition_residual(amplitude: np.ndarray) -> float:
    coeff = pauli_product_coefficients(amplitude)
    reconstructed = reconstruct_from_pauli_coefficients(coeff)
    return float(np.linalg.norm(amplitude - reconstructed) / max(np.linalg.norm(amplitude), 1.0))


def nucleon_ward_residual(q4: np.ndarray, current: np.ndarray) -> float:
    lhs = q4[0] * current[0] - np.einsum("i,ijk->jk", q4[1:], current[1:])
    scale = max(float(np.linalg.norm(q4) * np.linalg.norm(current)), 1.0)
    return float(np.linalg.norm(lhs) / scale)


def perpendicular_unit(q_vec: np.ndarray) -> np.ndarray:
    qhat = q_vec / np.linalg.norm(q_vec)
    reference = np.asarray([1.0, 0.0, 0.0])
    if abs(float(np.dot(qhat, reference))) > 0.9:
        reference = np.asarray([0.0, 1.0, 0.0])
    unit = np.cross(qhat, reference)
    return unit / np.linalg.norm(unit)


def nonrel_state_normalization(
    p_i: np.ndarray, p_f: np.ndarray, m_n: float = M_N_GEV
) -> float:
    """Return 1/(2 sqrt(E_i E_f)) for NR-normalized one-nucleon states."""
    e_i = math.sqrt(m_n * m_n + float(np.dot(p_i, p_i)))
    e_f = math.sqrt(m_n * m_n + float(np.dot(p_f, p_f)))
    return 1.0 / (2.0 * math.sqrt(e_i * e_f))


def spin_orbit_odd_coefficient(
    dm_current: np.ndarray,
    q_vec: np.ndarray,
    v_n: float,
    f1: float = 1.0,
    f2: float = 0.0,
    part: str = "full",
    nonrel_normalized: bool = False,
) -> complex:
    """Extract the DM-spin-independent nucleon-spin term odd in l.

    The projected direction is q x l.  By default the coefficient is in
    covariant spinor normalization.  Set nonrel_normalized=True to divide
    the one-nucleon current by 2 sqrt(E_i E_f), as required before matching
    to AFH one-body operators.  The returned coefficient multiplies
    sigma_N dot (q x l), before converting l=m_N*v_N.
    """
    q_vec = np.asarray(q_vec, dtype=float)
    qnorm = float(np.linalg.norm(q_vec))
    if v_n == 0:
        return 0.0j
    l_plus = M_N_GEV * v_n * perpendicular_unit(q_vec)
    outputs = []
    # Keep one fixed projection axis while reversing l; otherwise both the
    # odd coefficient and the projection direction flip and the odd part is lost.
    q_cross_l_reference = np.cross(q_vec, l_plus)
    direction = q_cross_l_reference / np.linalg.norm(q_cross_l_reference)
    for l_vec in (l_plus, -l_plus):
        jn, _, (p_i, p_f) = nucleon_current_matrices(q_vec, l_vec, f1, f2)
        if nonrel_normalized:
            jn = jn * nonrel_state_normalization(p_i, p_f)
        full, charge, spatial = full_amplitude_operator(dm_current, jn)
        chosen = {"full": full, "charge": charge, "spatial": spatial}[part]
        coeff = pauli_product_coefficients(chosen)
        outputs.append(np.dot(coeff[0, 1:], direction))
    odd = 0.5 * (outputs[0] - outputs[1])
    return complex(odd / (qnorm * M_N_GEV * v_n))


def pauli_coefficients_as_pairs(amplitude: np.ndarray) -> list[list[list[float]]]:
    """JSON-safe [real, imag] entries for all 16 Pauli-product coefficients."""
    coeff = pauli_product_coefficients(amplitude)
    return [
        [[float(value.real), float(value.imag)] for value in row]
        for row in coeff
    ]


def build_reference_inputs(denominator_imaginary_part: float = 0.0):
    point = dm.build_reference_point()
    mchi2 = dm.MCHI_GEV + 362.0e-6
    _, _, current = dm.spin_resolved_diagram_currents(
        point, dm.MCHI_GEV, mchi2, denominator_imaginary_part
    )
    return point, current


def run_finite_width_scenarios(point, q_vec: np.ndarray) -> list[dict]:
    """Repeat the full-current contraction with the project's finite-width T3.

    The width is inserted only in the after-emission chi2 propagator, exactly
    as in vector_current_response_audit.vector_current_vertices. We retain
    zero, pole, and running-width controls and both benchmark g2 values.
    """
    mchi = dm.MCHI_GEV
    delta_m = 362.0e-6
    mchi2 = mchi + delta_m
    ms = dm.MS_GEV
    v_n = 0.10
    f1, f2 = 1.0, -0.184
    l_vec = M_N_GEV * v_n * perpendicular_unit(q_vec)
    jn, _, (p_i, p_f) = nucleon_current_matrices(
        q_vec, l_vec, f1, f2
    )
    jn_nr = jn * nonrel_state_normalization(p_i, p_f)
    out = []
    for g2 in (0.1, 1.0):
        for scheme in ("zero", "pole", "running"):
            imag = dm.vca.width_imaginary_part(
                point, mchi, ms, delta_m, g2, scheme
            )
            before, after, current = dm.spin_resolved_diagram_currents(
                point, mchi, mchi2, imag
            )
            full, charge, spatial = full_amplitude_operator(current, jn_nr)
            coeff_spatial = pauli_product_coefficients(spatial)
            ward_lhs = dm.ward_lhs(point, current)
            ward_rhs = dm.ward_rhs_finite_width(
                point, mchi, mchi2, imag
            )
            tensor_from_spin = dm.tensor_from_spin_matrices(current)
            tensor_trace = dm.vca.dm_current_tensor(
                point, mchi, mchi2, imag
            )
            proj_full = spin_orbit_odd_coefficient(
                current, q_vec, v_n, f1, f2, "full",
                nonrel_normalized=True
            )
            proj_charge = spin_orbit_odd_coefficient(
                current, q_vec, v_n, f1, f2, "charge",
                nonrel_normalized=True
            )
            proj_spatial = spin_orbit_odd_coefficient(
                current, q_vec, v_n, f1, f2, "spatial",
                nonrel_normalized=True
            )
            out.append({
                "g2": g2,
                "width_scheme": scheme,
                "denominator_imaginary_part_GeV2": imag,
                "Gamma_pole_keV": (
                    dm.eq6.chi2_width_dirac_scalar(mchi, ms, delta_m, g2)
                    * 1.0e6
                ),
                "Gamma_running_at_reference_W_keV": (
                    dm.eq6.chi2_width_dirac_scalar_at_mass(
                        math.sqrt(point.W2), mchi, ms, g2
                    ) * 1.0e6
                    if scheme == "running" else None
                ),
                "pole_clearance_keV": (
                    mchi2 - math.sqrt(point.W2)
                ) * 1.0e6,
                "spin_trace_relative_residual": dm.relative_matrix_residual(
                    tensor_from_spin, tensor_trace
                ),
                "finite_width_Ward_identity_relative_residual": (
                    dm.scaled_ward_identity_residual(
                        point, current, ward_lhs, ward_rhs
                    )
                ),
                "DM_current_norm": float(np.linalg.norm(current)),
                "charge_amplitude_norm": float(np.linalg.norm(charge)),
                "spatial_amplitude_norm": float(np.linalg.norm(spatial)),
                "spatial_over_charge_operator_norm": float(
                    np.linalg.norm(spatial) / max(np.linalg.norm(charge), 1e-300)
                ),
                "selected_PhiPP_odd_projection_full_NR": [
                    proj_full.real, proj_full.imag
                ],
                "selected_PhiPP_odd_projection_charge_NR": [
                    proj_charge.real, proj_charge.imag
                ],
                "selected_PhiPP_odd_projection_spatial_NR": [
                    proj_spatial.real, proj_spatial.imag
                ],
                "spatial_transverse_spin_coefficient_c02": [
                    float(coeff_spatial[0, 2].real),
                    float(coeff_spatial[0, 2].imag),
                ],
                "full_pauli_reconstruction_residual": (
                    pauli_decomposition_residual(full)
                ),
                "charge_pauli_reconstruction_residual": (
                    pauli_decomposition_residual(charge)
                ),
                "spatial_pauli_reconstruction_residual": (
                    pauli_decomposition_residual(spatial)
                ),
                "coherent_two_diagram_interference_norm": float(np.linalg.norm(
                    tensor_from_spin
                    - dm.tensor_from_spin_matrices(before)
                    - dm.tensor_from_spin_matrices(after)
                )),
            })
    return out


def run_diagnostic() -> dict:
    point, t3 = build_reference_inputs()
    q_vec = np.asarray(point.q_A[1:], dtype=float)
    q_a4 = np.asarray(point.q_A, dtype=float)
    results = []
    pauli_decompositions = {}
    for f2 in F2_SCENARIOS:
        for v_n in (0.02, 0.05, 0.10, 0.20):
            projections = {}
            for part in ("full", "charge", "spatial"):
                cov = spin_orbit_odd_coefficient(
                    t3, q_vec, v_n, 1.0, f2, part,
                    nonrel_normalized=False,
                )
                nr = spin_orbit_odd_coefficient(
                    t3, q_vec, v_n, 1.0, f2, part,
                    nonrel_normalized=True,
                )
                projections[part] = {"covariant": cov, "nonrel": nr}
            full = projections["full"]["nonrel"]
            charge = projections["charge"]["nonrel"]
            spatial = projections["spatial"]["nonrel"]
            results.append({
                "F1_over_F1zero": 1.0,
                "F2_over_F1zero": f2,
                "vN": v_n,
                "C_full_per_qcrossl_covariant": [
                    projections["full"]["covariant"].real,
                    projections["full"]["covariant"].imag,
                ],
                "C_charge_per_qcrossl_covariant": [
                    projections["charge"]["covariant"].real,
                    projections["charge"]["covariant"].imag,
                ],
                "C_spatial_per_qcrossl_covariant": [
                    projections["spatial"]["covariant"].real,
                    projections["spatial"]["covariant"].imag,
                ],
                "C_full_per_qcrossl_NR": [full.real, full.imag],
                "C_charge_per_qcrossl_NR": [charge.real, charge.imag],
                "C_spatial_per_qcrossl_NR": [spatial.real, spatial.imag],
                "full_minus_charge_equals_spatial_NR_residual": [
                    (full - charge - spatial).real,
                    (full - charge - spatial).imag,
                ],
            })

        # Preserve the complete Pauli-product decomposition at v_N=0.10.
        v_n = 0.10
        l_vec = M_N_GEV * v_n * perpendicular_unit(q_vec)
        jn, qn, (p_i, p_f) = nucleon_current_matrices(q_vec, l_vec, 1.0, f2)
        norm = nonrel_state_normalization(p_i, p_f)
        jn_nr = norm * jn
        full_nr, charge_nr, spatial_nr = full_amplitude_operator(t3, jn_nr)
        pauli_decompositions[f"{f2:+.3f}"] = {
            "normalization_1_over_2sqrt_EiEf_GeV_inverse": norm,
            "full_4x4_Pauli_coefficients_a_chi_b_N": pauli_coefficients_as_pairs(full_nr),
            "charge_4x4_Pauli_coefficients_a_chi_b_N": pauli_coefficients_as_pairs(charge_nr),
            "spatial_4x4_Pauli_coefficients_a_chi_b_N": pauli_coefficients_as_pairs(spatial_nr),
            "full_reconstruction_residual": pauli_decomposition_residual(full_nr),
            "charge_reconstruction_residual": pauli_decomposition_residual(charge_nr),
            "spatial_reconstruction_residual": pauli_decomposition_residual(spatial_nr),
        }

    l_ref = 0.10 * M_N_GEV * perpendicular_unit(q_vec)
    jn, qn, _ = nucleon_current_matrices(q_vec, l_ref, 1.0, -0.184)
    q_a_ward_residual = nucleon_ward_residual(q_a4, jn)
    return {
        "status": "static_one_nucleon_full_current_matching_diagnostic",
        "form_factor_benchmark": {
            "F1_over_F1zero": 1.0,
            "F2_over_F1zero": -0.184,
            "interpretation": "zero-momentum flavour-universal anchor; finite-t form factors are not supplied",
        },
        "nucleon_mass_GeV": M_N_GEV,
        "qA_GeV": point.q_A.tolist(),
        "qN_static_GeV": qn.tolist(),
        "nucleon_static_q0_GeV": float(qn[0]),
        "nucleon_current_ward_scaled_residual_qN": nucleon_ward_residual(qn, jn),
        "nucleon_current_ward_scaled_residual_using_physical_qA": q_a_ward_residual,
        "qA0_over_qA_magnitude": float(q_a4[0] / np.linalg.norm(q_a4[1:])),
        "DM_current_spin_trace_residual": dm.relative_matrix_residual(
            dm.tensor_from_spin_matrices(t3),
            dm.vca.dm_current_tensor(point, dm.MCHI_GEV, dm.MCHI_GEV + 362.0e-6, 0.0),
        ),
        "results": results,
        "complete_Pauli_decompositions_at_vN_0p10": pauli_decompositions,
        "finite_width_scenarios": run_finite_width_scenarios(point, q_vec),
        "limitations": [
            "The nucleon is an on-shell static impulse-approximation point with q_N^0=0 and l perpendicular to q.",
            "The physical nuclear transfer has q_A^0=E_R != 0; the q_N^0=0 approximation is not exactly conserved with q_A and its residual is reported separately.",
            "AFH matching requires nonrelativistic one-nucleon state normalization 1/(2 sqrt(E_i E_f)); both covariant and normalized projections are reported.",
            "The finite-t F1 and F2 are not supplied; F2/F1=-0.184 is only the zero-momentum flavour-universal anchor.",
            "This is one phase-space point and one nucleon-momentum orientation, not a nuclear many-body response calculation.",
            "No AFH response coefficient is claimed until the full operator structures are projected and normalized.",
            "The Proca propagator longitudinal term and the full bound-nucleon continuity equation are not included in this static diagnostic.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    result = run_diagnostic()
    payload = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
