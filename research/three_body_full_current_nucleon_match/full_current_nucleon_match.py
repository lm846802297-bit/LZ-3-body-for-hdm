#!/usr/bin/env python3
"""Exact one-nucleon Dirac-Pauli current contracted with spin-resolved T3^mu.

The diagnostic retains the static impulse-approximation point
p_N=l-q/2, p_N'=l+q/2, l perpendicular to q, so q_N^0=0, and adds a
separate free on-shell kinematic slice with q_N^0=q_A^0=E_R. The latter is
not a bound-nucleon model. This is a matching diagnostic, not a nuclear
many-body calculation.
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

    q_N^0 is fixed by the on-shell free-nucleon energies. It vanishes only
    when l is perpendicular to q; arbitrary internal-momentum directions
    are supported.
    """
    q_vec = np.asarray(q_vec, dtype=float)
    l_vec = np.asarray(l_vec, dtype=float)
    if q_vec.shape != (3,) or l_vec.shape != (3,):
        raise ValueError("q_vec and l_vec must be three-vectors")
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


def q_aligned_rotation(q_vec: np.ndarray) -> np.ndarray:
    """Return a right-handed rotation whose rows are (e1,e2,qhat)."""
    q_vec = np.asarray(q_vec, dtype=float)
    if q_vec.shape != (3,) or not np.all(np.isfinite(q_vec)):
        raise ValueError("q_vec must be a finite three-vector")
    q_norm = float(np.linalg.norm(q_vec))
    if q_norm <= 0.0:
        raise ValueError("q_vec must be nonzero")
    qhat = q_vec / q_norm
    e1 = perpendicular_unit(q_vec)
    e2 = np.cross(qhat, e1)
    rotation = np.stack((e1, e2, qhat), axis=0)
    return rotation


def rotate_current_to_q_frame(current: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    """Rotate only spatial components of a four-current into the q frame."""
    current = np.asarray(current, dtype=complex)
    rotation = np.asarray(rotation, dtype=float)
    if current.shape != (4, 2, 2):
        raise ValueError("current must have shape (4,2,2)")
    if rotation.shape != (3, 3):
        raise ValueError("rotation must have shape (3,3)")
    rotated = current.copy()
    rotated[1:] = np.einsum("ij,jab->iab", rotation, current[1:])
    return rotated


def run_q_frame_full_current_validation() -> dict:
    """Compare direct and q-frame full DM x nucleon spin-amplitude contractions."""
    point, t3 = build_reference_inputs()
    qA4 = np.asarray(point.q_A, dtype=float)
    q_vec = qA4[1:]
    Q = float(np.linalg.norm(q_vec))
    rotation = q_aligned_rotation(q_vec)
    t3_q = rotate_current_to_q_frame(t3, rotation)

    p_perp = 0.10
    l_vec, l_parallel = energy_transfer_matched_internal_momentum(
        q_vec, float(qA4[0]), p_perp
    )
    jn_covariant, qN4, (p_i, p_f) = nucleon_current_matrices(
        q_vec, l_vec, 1.0, -0.184
    )
    normalization = nonrel_state_normalization(p_i, p_f)
    jn = normalization * jn_covariant
    jn_q = rotate_current_to_q_frame(jn, rotation)

    full_lab, charge_lab, spatial_lab = full_amplitude_operator(t3, jn)
    full_q, charge_q, spatial_q = full_amplitude_operator(t3_q, jn_q)
    rotation4 = np.eye(4)
    rotation4[1:, 1:] = rotation
    L_lab = dm.tensor_from_spin_matrices(t3)
    L_q = dm.tensor_from_spin_matrices(t3_q)
    L_q_expected = rotation4 @ L_lab @ rotation4.T

    return {
        "status": "PASS_DIRECT_VS_Q_FRAME_FULL_CURRENT_CONTRACTION",
        "qA_lab_GeV": qA4.tolist(),
        "qA_q_frame_GeV": [float(qA4[0]), 0.0, 0.0, Q],
        "rotation_matrix": rotation.tolist(),
        "rotation_orthogonality_residual": float(
            np.linalg.norm(rotation @ rotation.T - np.eye(3))
        ),
        "rotation_determinant": float(np.linalg.det(rotation)),
        "DM_tensor_rotation_residual": dm.relative_matrix_residual(
            L_q, L_q_expected
        ),
        "nucleon_current_rotation_residual": dm.relative_matrix_residual(
            jn_q, rotate_current_to_q_frame(jn, rotation)
        ),
        "full_amplitude_rotation_residual": dm.relative_matrix_residual(
            full_q, full_lab
        ),
        "charge_amplitude_rotation_residual": dm.relative_matrix_residual(
            charge_q, charge_lab
        ),
        "spatial_amplitude_rotation_residual": dm.relative_matrix_residual(
            spatial_q, spatial_lab
        ),
        "spin_summed_norm_relative_residual": abs(
            float(np.linalg.norm(full_q) ** 2)
            - float(np.linalg.norm(full_lab) ** 2)
        ) / max(float(np.linalg.norm(full_lab) ** 2), 1.0e-300),
        "nucleon_qN0_GeV": float(qN4[0]),
        "nucleon_qN0_minus_qA0_GeV": float(qN4[0] - qA4[0]),
        "nucleon_Ward_residual_qN": nucleon_ward_residual(qN4, jn_covariant),
        "K_N_perp_GeV": p_perp,
        "K_N_parallel_GeV": l_parallel,
        "scope": (
            "exact free on-shell one-nucleon Dirac-Pauli current and exact "
            "spin-resolved three-body DM current; lab-vs-q-frame covariance "
            "only, not yet the AFH nuclear OBDME contraction"
        ),
    }


def energy_transfer_matched_internal_momentum(
    q_vec: np.ndarray,
    omega_GeV: float,
    p_perp_GeV: float,
    m_n: float = M_N_GEV,
) -> tuple[np.ndarray, float]:
    """Construct a free on-shell l with E_f-E_i=omega for q_N=q_A.

    With p_i=l-q/2 and p_f=l+q/2, the exact longitudinal component is
        l_parallel = omega * sqrt(m_N^2 + p_perp^2 + (Q^2-omega^2)/4)
                    / sqrt(Q^2-omega^2).
    This is a kinematic free-nucleon construction, not a bound-nucleon
    momentum distribution or a many-body continuity prescription.
    """
    q_vec = np.asarray(q_vec, dtype=float)
    if q_vec.shape != (3,) or not np.all(np.isfinite(q_vec)):
        raise ValueError("q_vec must be a finite three-vector")
    if not math.isfinite(omega_GeV) or not math.isfinite(p_perp_GeV):
        raise ValueError("energy transfer and transverse momentum must be finite")
    if omega_GeV < 0.0 or p_perp_GeV < 0.0 or m_n <= 0.0:
        raise ValueError("invalid energy transfer, transverse momentum, or mass")
    Q = float(np.linalg.norm(q_vec))
    if Q <= 0.0 or omega_GeV >= Q:
        raise ValueError("the transfer must be spacelike with Q > omega")
    qhat = q_vec / Q
    e1 = perpendicular_unit(q_vec)
    l_perp = p_perp_GeV * e1
    l_parallel = (
        omega_GeV
        * math.sqrt(
            m_n * m_n + p_perp_GeV * p_perp_GeV
            + 0.25 * (Q * Q - omega_GeV * omega_GeV)
        )
        / math.sqrt(Q * Q - omega_GeV * omega_GeV)
    )
    return l_perp + l_parallel * qhat, float(l_parallel)


def run_energy_transfer_matched_on_shell_scan(
    q_vec: np.ndarray,
    omega_GeV: float,
    *,
    f1: float = 1.0,
    f2: float = -0.184,
    p_perp_values_GeV: tuple[float, ...] = (0.0, 0.05, 0.10, 0.20),
) -> list[dict]:
    """Test the exact free on-shell slice q_N^0=omega=q_A^0."""
    q_vec = np.asarray(q_vec, dtype=float)
    q_A4 = np.asarray([omega_GeV, *q_vec], dtype=float)
    rows = []
    for p_perp in p_perp_values_GeV:
        l_vec, l_parallel = energy_transfer_matched_internal_momentum(
            q_vec, omega_GeV, p_perp
        )
        current, q_N4, (p_i, p_f) = nucleon_current_matrices(
            q_vec, l_vec, f1, f2
        )
        rows.append({
            "p_perp_GeV": float(p_perp),
            "l_parallel_GeV": l_parallel,
            "qN0_GeV": float(q_N4[0]),
            "qA0_GeV": float(omega_GeV),
            "qN0_minus_qA0_GeV": float(q_N4[0] - omega_GeV),
            "initial_nucleon_energy_GeV": math.sqrt(
                M_N_GEV * M_N_GEV + float(np.dot(p_i, p_i))
            ),
            "final_nucleon_energy_GeV": math.sqrt(
                M_N_GEV * M_N_GEV + float(np.dot(p_f, p_f))
            ),
            "nucleon_Ward_residual_qN": nucleon_ward_residual(q_N4, current),
            "nucleon_Ward_residual_qA": nucleon_ward_residual(q_A4, current),
        })
    return rows


def nonrel_state_normalization(
    p_i: np.ndarray, p_f: np.ndarray, m_n: float = M_N_GEV
) -> float:
    """Return 1/(2 sqrt(E_i E_f)) for NR-normalized one-nucleon states."""
    e_i = math.sqrt(m_n * m_n + float(np.dot(p_i, p_i)))
    e_f = math.sqrt(m_n * m_n + float(np.dot(p_f, p_f)))
    return 1.0 / (2.0 * math.sqrt(e_i * e_f))


def leading_nr_nucleon_current_matrices(
    q_vec: np.ndarray,
    l_vec: np.ndarray,
    f1: float = 1.0,
    f2: float = 0.0,
    m_n: float = M_N_GEV,
) -> np.ndarray:
    """Leading Pauli-reduced Dirac--Pauli current in NR state normalization.

    With q_N = p_N' - p_N and K_N = (p_N' + p_N)/2 = l_vec,
    the retained terms are
      J^0 = F1 + (F1+2F2) t_N/(8 m_N^2)
            + i (F1+2F2) sigma.(q_N x K_N)/(4 m_N^2),
      J  = F1 K_N/m_N + i (F1+F2) (sigma x q_N)/(2 m_N).
    The charge is kept through O(p^2/m^2); the spatial current is kept
    through O(p/m). The omitted terms are O(p^4/m^4) in J^0 and
    O(p^3/m^3) in J. F1,F2 are held constant over this diagnostic point.
    """
    q_vec = np.asarray(q_vec, dtype=float)
    l_vec = np.asarray(l_vec, dtype=float)
    if q_vec.shape != (3,) or l_vec.shape != (3,):
        raise ValueError("q_vec and l_vec must be three-vectors")
    if not np.all(np.isfinite(q_vec)) or not np.all(np.isfinite(l_vec)):
        raise ValueError("q_vec and l_vec must be finite")
    if not all(math.isfinite(x) for x in (f1, f2, m_n)) or m_n <= 0.0:
        raise ValueError("form factors must be finite and m_n positive")

    p_i = l_vec - 0.5 * q_vec
    p_f = l_vec + 0.5 * q_vec
    e_i = math.sqrt(m_n * m_n + float(np.dot(p_i, p_i)))
    e_f = math.sqrt(m_n * m_n + float(np.dot(p_f, p_f)))
    q0 = e_f - e_i
    t_n = q0 * q0 - float(np.dot(q_vec, q_vec))

    result = np.zeros((4, 2, 2), dtype=complex)
    spin_orbit = sum(
        (np.cross(q_vec, l_vec)[j] * PAULI[j + 1] for j in range(3)),
        start=np.zeros((2, 2), dtype=complex),
    )
    result[0] = (
        f1 + (f1 + 2.0 * f2) * t_n / (8.0 * m_n * m_n)
    ) * eq6.I2 + (
        1j * (f1 + 2.0 * f2) / (4.0 * m_n * m_n)
    ) * spin_orbit

    for i in range(3):
        # (sigma x q)_i = sum_j (q x e_i)_j sigma_j.
        basis_i = np.eye(3)[i]
        sigma_cross_q = sum(
            (
                np.cross(q_vec, basis_i)[j] * PAULI[j + 1]
                for j in range(3)
            ),
            start=np.zeros((2, 2), dtype=complex),
        )
        result[i + 1] = (
            f1 * l_vec[i] / m_n * eq6.I2
            + 1j * (f1 + f2) / (2.0 * m_n) * sigma_cross_q
        )
    return result


def _relative_matrix_residual(reference: np.ndarray, candidate: np.ndarray) -> float:
    return float(
        np.linalg.norm(reference - candidate)
        / max(float(np.linalg.norm(reference)), 1.0e-300)
    )


def analyze_one_body_nr_matching_point(
    q_vec: np.ndarray,
    l_vec: np.ndarray,
    *,
    f1: float = 1.0,
    f2: float = -0.184,
    m_n: float = M_N_GEV,
) -> dict:
    """Compare exact free on-shell Dirac--Pauli current with its NR expansion."""
    exact_covariant, q_n4, (p_i, p_f) = nucleon_current_matrices(
        q_vec, l_vec, f1, f2, m_n
    )
    normalization = nonrel_state_normalization(p_i, p_f, m_n)
    exact = normalization * exact_covariant
    leading = leading_nr_nucleon_current_matrices(
        q_vec, l_vec, f1, f2, m_n
    )

    q_magnitude = float(np.linalg.norm(q_vec))
    if q_magnitude <= 0.0:
        raise ValueError("q_vec must be nonzero for longitudinal/transverse split")
    qhat = np.asarray(q_vec, dtype=float) / q_magnitude
    exact_longitudinal = sum(
        (qhat[i] * exact[i + 1] for i in range(3)),
        start=np.zeros((2, 2), dtype=complex),
    )
    leading_longitudinal = sum(
        (qhat[i] * leading[i + 1] for i in range(3)),
        start=np.zeros((2, 2), dtype=complex),
    )
    exact_transverse = np.asarray([
        exact[i + 1] - qhat[i] * exact_longitudinal for i in range(3)
    ])
    leading_transverse = np.asarray([
        leading[i + 1] - qhat[i] * leading_longitudinal for i in range(3)
    ])
    continuity_longitudinal = (q_n4[0] / q_magnitude) * exact[0]

    return {
        "qN0_GeV": float(q_n4[0]),
        "qN_magnitude_GeV": q_magnitude,
        "tN_GeV2": float(q_n4[0] ** 2 - q_magnitude ** 2),
        "K_N_GeV": np.asarray(l_vec, dtype=float).tolist(),
        "normalization_1_over_2sqrt_EiEf_GeV_inverse": normalization,
        "charge_relative_residual": _relative_matrix_residual(
            exact[0], leading[0]
        ),
        "spatial_relative_residual": _relative_matrix_residual(
            exact[1:], leading[1:]
        ),
        "transverse_spatial_relative_residual": _relative_matrix_residual(
            exact_transverse, leading_transverse
        ),
        "longitudinal_spatial_relative_residual": _relative_matrix_residual(
            exact_longitudinal, leading_longitudinal
        ),
        "full_four_current_relative_residual": _relative_matrix_residual(
            exact, leading
        ),
        "exact_nucleon_ward_residual": nucleon_ward_residual(q_n4, exact_covariant),
        "exact_longitudinal_continuity_residual": _relative_matrix_residual(
            exact_longitudinal, continuity_longitudinal
        ),
        "leading_longitudinal_ward_residual": _relative_matrix_residual(
            q_n4[0] * leading[0], q_magnitude * leading_longitudinal
        ),
    }


def run_one_body_nr_matching_scan() -> list[dict]:
    """Benchmark the leading NR expansion at the two Xe-131 recoil points.

    The scan uses a free on-shell nucleon with q_N^0 = E_R = q_A^0.
    Transverse internal momenta are 0, 50, 100 and 200 MeV. This is a
    truncation diagnostic, not a bound-nucleon momentum distribution.
    """
    benchmarks = (
        ("Xe131_200keV", 0.2209306022, 0.000200),
        ("Xe131_267keV", 0.2552681134, 0.000267),
    )
    rows = []
    for name, q_magnitude, omega in benchmarks:
        q_vec = np.asarray([q_magnitude, 0.0, 0.0])
        for p_perp in (0.0, 0.05, 0.10, 0.20):
            l_vec, l_parallel = energy_transfer_matched_internal_momentum(
                q_vec, omega, p_perp
            )
            row = analyze_one_body_nr_matching_point(q_vec, l_vec)
            row.update({
                "benchmark": name,
                "E_R_GeV": omega,
                "p_perp_GeV": p_perp,
                "l_parallel_GeV": l_parallel,
                "qN0_minus_qA0_GeV": row["qN0_GeV"] - omega,
            })
            rows.append(row)
    return rows


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


def finite_width_ward_rhs(point, mchi: float, mchi2: float, imag: float) -> np.ndarray:
    """Finite-width Ward RHS for the denominator-only insertion used by PR #57.

    The width is inserted only in the after-emission propagator D2+i*imag.
    The additional i*imag/(D2+i*imag) external scalar bilinear is required.
    """
    r_before, r_after = eq6.chi2_internal_momenta(point)
    d1 = eq6.dot(r_before, r_before) - mchi2 * mchi2
    d2 = eq6.dot(r_after, r_after) - mchi2 * mchi2
    d2_complex = d2 + 1j * imag
    if abs(d1) < 1e-30 or abs(d2_complex) < 1e-30:
        raise ZeroDivisionError("chi2 propagator pole in finite-width Ward RHS")
    u_in = dm.dirac_spinor_matrix(point.p, mchi)
    u_out = dm.dirac_spinor_matrix(point.p_prime, mchi)
    ubar_out = u_out.conj().T @ eq6.GAMMA[0]
    operator = (
        (eq6.slash(r_before) + mchi2 * eq6.ID4) / d1
        - (eq6.slash(r_after) + mchi2 * eq6.ID4) / d2_complex
    )
    return (
        (mchi2 - mchi) * ubar_out @ operator @ u_in
        + (1j * imag / d2_complex) * (ubar_out @ u_in)
    )


def scaled_ward_identity_residual(point, current, lhs, rhs) -> float:
    q_norm = float(np.linalg.norm(np.asarray(point.q_A, dtype=float)))
    current_norm = float(np.linalg.norm(current))
    scale = max(q_norm * current_norm, 1.0)
    return float(np.linalg.norm(lhs - rhs) / scale)


def run_nucleon_orientation_scan(
    point, q_vec: np.ndarray, dm_current: np.ndarray, g2: float, scheme: str
) -> list[dict]:
    """Probe internal nucleon momentum directions at one fixed DM phase point.

    This is not a nuclear momentum-distribution average. It checks whether
    the one-point spatial-current diagnostic is an artifact of choosing
    l perpendicular to q_A.
    """
    qhat = q_vec / np.linalg.norm(q_vec)
    e1 = perpendicular_unit(q_vec)
    e2 = np.cross(qhat, e1)
    directions = {
        "parallel_q": qhat,
        "perpendicular_e1": e1,
        "perpendicular_e2": e2,
        "mixed_45deg": (qhat + e1) / math.sqrt(2.0),
    }
    v_values = (0.10, 0.30)
    rows = []
    q_a4 = np.asarray(point.q_A, dtype=float)
    for v_n in v_values:
        for label, direction in directions.items():
            l_vec = M_N_GEV * v_n * direction
            jn, qn, (p_i, p_f) = nucleon_current_matrices(
                q_vec, l_vec, 1.0, -0.184
            )
            jn_nr = jn * nonrel_state_normalization(p_i, p_f)
            full, charge, spatial = full_amplitude_operator(
                dm_current, jn_nr
            )
            coeff_spatial = pauli_product_coefficients(spatial)
            rows.append({
                "g2": g2,
                "width_scheme": scheme,
                "vN": v_n,
                "internal_momentum_direction": label,
                "qN0_GeV": float(qn[0]),
                "qN0_over_QA": float(qn[0] / np.linalg.norm(q_vec)),
                "nucleon_Ward_residual_qN": nucleon_ward_residual(qn, jn),
                "static_qA_Ward_residual": nucleon_ward_residual(q_a4, jn),
                "spatial_over_charge_operator_norm": float(
                    np.linalg.norm(spatial) / max(np.linalg.norm(charge), 1e-300)
                ),
                "spatial_nucleon_spin_block_norm": float(
                    np.linalg.norm(coeff_spatial[0, 1:])
                ),
                "spatial_DM_spin_dependent_block_norm": float(
                    np.linalg.norm(coeff_spatial[1:, :])
                ),
                "spatial_identity_identity_coefficient": [
                    float(coeff_spatial[0, 0].real),
                    float(coeff_spatial[0, 0].imag),
                ],
                "spatial_nucleon_spin_coefficients": [
                    [float(z.real), float(z.imag)]
                    for z in coeff_spatial[0, 1:]
                ],
                "full_amplitude_norm": float(np.linalg.norm(full)),
                "charge_amplitude_norm": float(np.linalg.norm(charge)),
                "spatial_amplitude_norm": float(np.linalg.norm(spatial)),
            })
    return rows


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
            ward_rhs = finite_width_ward_rhs(point, mchi, mchi2, imag)
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
                    scaled_ward_identity_residual(
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
                "internal_nucleon_orientation_scan": run_nucleon_orientation_scan(
                    point, q_vec, current, g2, scheme
                ),
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
        "calculation_role": "free on-shell one-nucleon P3-C matching diagnostic only; q=0 form-factor anchors; not B production",
        "primary_B_baseline_included": False,
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
        "energy_transfer_matched_on_shell_scan": (
            run_energy_transfer_matched_on_shell_scan(q_vec, float(q_a4[0]))
        ),
        "leading_NR_one_body_matching_scan": run_one_body_nr_matching_scan(),
        "q_frame_full_current_validation": run_q_frame_full_current_validation(),
        "limitations": [
            "The nucleon is an on-shell static impulse-approximation point with q_N^0=0 and l perpendicular to q.",
            "The physical nuclear transfer has q_A^0=E_R != 0; the q_N^0=0 approximation is not exactly conserved with q_A and its residual is reported separately.",
            "A separate free on-shell kinematic scan adjusts l_parallel so q_N^0=E_R; it is not a bound-nucleon momentum distribution or a many-body continuity calculation.",
            "AFH matching requires nonrelativistic one-nucleon state normalization 1/(2 sqrt(E_i E_f)); both covariant and normalized projections are reported.",
            "The finite-t F1 and F2 are not supplied; F2/F1=-0.184 is only the zero-momentum flavour-universal anchor.",
            "The leading NR expansion scan quantifies O(p^3/m_N^3) spatial-current truncation at two Xe-131 recoil points; it is not a bound-nucleon calculation.",
            "This is one phase-space point and one nucleon-momentum orientation, not a nuclear many-body response calculation.",
            "The particle-side AFH Eq. (107) coefficient phase is independently tested; the full nuclear OBDME multipole contraction remains pending.",
            "The q-frame full-current test checks spatial-rotation covariance, not the nuclear multipole reduction.",
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
