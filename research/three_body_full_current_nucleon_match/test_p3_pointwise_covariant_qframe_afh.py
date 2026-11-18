import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import full_current_nucleon_match as full
import three_body_multipole_leptonic_weights as multipoles


def rotation_to_positive_z(vector):
    """Return a proper SO(3) rotation that maps vector to +z."""
    vector = np.asarray(vector, dtype=float)
    norm = float(np.linalg.norm(vector))
    if norm <= 0.0:
        raise ValueError("rotation axis vector must be nonzero")
    a = vector / norm
    b = np.asarray([0.0, 0.0, 1.0])
    cosine = float(np.dot(a, b))
    if cosine > 1.0 - 1.0e-14:
        return np.eye(3)
    if cosine < -1.0 + 1.0e-14:
        # A pi rotation about x maps -z to +z and remains proper.
        return np.diag([1.0, -1.0, -1.0])
    v = np.cross(a, b)
    vx = np.asarray([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0],
    ])
    return np.eye(3) + vx + (vx @ vx) / (1.0 + cosine)


def rotate_current_spatial_components(current, rotation):
    current = np.asarray(current, dtype=complex)
    if current.shape != (4, 2, 2):
        raise ValueError("current must have shape (4,2,2)")
    result = current.copy()
    result[1:] = np.einsum("ij,jab->iab", rotation, current[1:])
    return result


def spin_averaged_spatial_tensor(dm_current):
    """L_ij = (1/2) Tr[T_i T_j^dagger], with initial DM spin averaged."""
    dm_current = np.asarray(dm_current, dtype=complex)
    return np.asarray([
        [
            0.5 * np.trace(dm_current[i + 1] @ dm_current[j + 1].conj().T)
            for j in range(3)
        ]
        for i in range(3)
    ], dtype=complex)


def dm_spin_channels_as_amplitudes(dm_current):
    """Flatten the 2x2 DM spin matrix into channels with the 1/2 average."""
    dm_current = np.asarray(dm_current, dtype=complex)
    # The helper averages over rows. sqrt(2) makes its 1/4 row average
    # equal to the physical 1/2 initial-DM-spin average.
    return np.sqrt(2.0) * np.asarray([
        [dm_current[i + 1, a, b] for i in range(3)]
        for a in range(2)
        for b in range(2)
    ], dtype=complex)


class P3PointwiseCovariantQFrameAFHTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.point, cls.dm_current = full.build_reference_inputs()
        cls.qA = np.asarray(cls.point.q_A, dtype=float)
        cls.qmag = float(np.linalg.norm(cls.qA))
        cls.f1 = 1.0
        cls.f2 = -0.184
        cls.mN = full.M_N_GEV
        cls.lN = (
            0.10 * cls.mN * full.perpendicular_unit(cls.qA)
        )
        j_cov, cls.qN4, (p_i, p_f) = full.nucleon_current_matrices(
            cls.qA, cls.lN, cls.f1, cls.f2, cls.mN
        )
        cls.j_cov = np.asarray(j_cov, dtype=complex)
        cls.j_nr_norm = cls.j_cov * full.nonrel_state_normalization(
            p_i, p_f, cls.mN
        )

    def test_exact_covariant_full_amplitude_reconstructs_pauli_basis(self):
        amplitude, charge, spatial = full.full_amplitude_operator(
            self.dm_current, self.j_nr_norm
        )
        self.assertEqual(amplitude.shape, (4, 4))
        self.assertLess(full.pauli_decomposition_residual(amplitude), 2.0e-14)
        self.assertLess(full.pauli_decomposition_residual(charge), 2.0e-14)
        self.assertLess(full.pauli_decomposition_residual(spatial), 2.0e-14)
        self.assertLess(full.nucleon_ward_residual(self.qN4, self.j_cov), 2.0e-12)

    def test_direct_covariant_contraction_is_invariant_in_q_aligned_frame(self):
        rotation = rotation_to_positive_z(self.qA)
        self.assertAlmostEqual(float(np.linalg.det(rotation)), 1.0, places=13)
        self.assertLess(
            float(np.linalg.norm(rotation @ self.qA - np.asarray([0.0, 0.0, self.qmag]))),
            2.0e-13,
        )
        dm_rot = rotate_current_spatial_components(self.dm_current, rotation)
        j_rot = rotate_current_spatial_components(self.j_nr_norm, rotation)
        direct, _, _ = full.full_amplitude_operator(
            self.dm_current, self.j_nr_norm
        )
        qframe, _, _ = full.full_amplitude_operator(dm_rot, j_rot)
        residual = float(
            np.linalg.norm(direct - qframe)
            / max(float(np.linalg.norm(direct)), 1.0e-300)
        )
        self.assertLess(residual, 2.0e-13)

    def test_actual_three_body_dm_current_matches_afh_eq107_in_lab_and_q_frames(self):
        L_lab = spin_averaged_spatial_tensor(self.dm_current)
        channels_lab = dm_spin_channels_as_amplitudes(self.dm_current)
        direct_lab = multipoles.afh_eq107_spatial_coefficients_from_amplitudes(
            channels_lab, self.qA, f1=self.f1, f2=self.f2, mN_GeV=self.mN
        )
        tensor_lab = multipoles.extract_afh_vector_coefficients(
            np.pad(L_lab, ((1, 0), (1, 0))),
            self.qmag,
            f1=self.f1,
            f2=self.f2,
            mN_GeV=self.mN,
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            scale = max(abs(direct_lab[key]), abs(tensor_lab[key]), 1.0e-300)
            self.assertLess(abs(direct_lab[key] - tensor_lab[key]) / scale, 2.0e-13)

        rotation = rotation_to_positive_z(self.qA)
        dm_rot = rotate_current_spatial_components(self.dm_current, rotation)
        q_rot = rotation @ self.qA
        L_rot = spin_averaged_spatial_tensor(dm_rot)
        channels_rot = dm_spin_channels_as_amplitudes(dm_rot)
        direct_rot = multipoles.afh_eq107_spatial_coefficients_from_amplitudes(
            channels_rot, q_rot, f1=self.f1, f2=self.f2, mN_GeV=self.mN
        )
        tensor_rot = multipoles.extract_afh_vector_coefficients(
            np.pad(L_rot, ((1, 0), (1, 0))),
            self.qmag,
            f1=self.f1,
            f2=self.f2,
            mN_GeV=self.mN,
        )
        for key in ("C_Delta", "C_SigmaPrime", "C_SigmaPrimeDelta"):
            scale = max(abs(direct_rot[key]), abs(tensor_rot[key]), 1.0e-300)
            self.assertLess(abs(direct_rot[key] - tensor_rot[key]) / scale, 2.0e-13)
            scale_frame = max(abs(direct_lab[key]), abs(direct_rot[key]), 1.0e-300)
            self.assertLess(abs(direct_lab[key] - direct_rot[key]) / scale_frame, 2.0e-13)

    def test_two_scalar_emission_orderings_remain_coherent_in_full_amplitude(self):
        before, after, total = __import__(
            "spin_resolved_three_body_current"
        ).spin_resolved_diagram_currents(
            self.point,
            __import__("spin_resolved_three_body_current").MCHI_GEV,
            __import__("spin_resolved_three_body_current").MCHI_GEV + 362.0e-6,
            0.0,
        )
        coherent, _, _ = full.full_amplitude_operator(total, self.j_nr_norm)
        before_amp, _, _ = full.full_amplitude_operator(before, self.j_nr_norm)
        after_amp, _, _ = full.full_amplitude_operator(after, self.j_nr_norm)
        interference = coherent - before_amp - after_amp
        self.assertGreater(float(np.linalg.norm(interference)), 0.0)
        self.assertLess(
            float(np.linalg.norm(
                coherent - (before_amp + after_amp + interference)
            )),
            1.0e-13 * max(float(np.linalg.norm(coherent)), 1.0),
        )


if __name__ == "__main__":
    unittest.main()
