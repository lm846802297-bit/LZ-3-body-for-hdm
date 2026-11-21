import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import three_body_phase_space_tensor as tensor
import spin_resolved_three_body_current as dm


class ThreeBodyPhaseSpaceTensorTests(unittest.TestCase):
    def test_formal_production_width_policy_is_pole_only(self):
        self.assertEqual(tensor.FORMAL_WIDTH_SCHEME, "pole")
    def test_q_frame_rotation_is_orthonormal_and_right_handed(self):
        for q in (
            np.asarray([0.0, 0.0, 1.0, 0.0]),
            np.asarray([0.0, 0.3, 0.4, 0.866025403784]),
            np.asarray([0.0, 1.0, 0.0, 0.0]),
        ):
            rotation = tensor.q_aligned_rotation(q)
            self.assertLess(np.linalg.norm(rotation @ rotation.T - np.eye(3)), 2e-14)
            self.assertAlmostEqual(float(np.linalg.det(rotation)), 1.0, places=13)
            self.assertLess(np.linalg.norm(rotation[2] - q[1:] / np.linalg.norm(q[1:])), 2e-14)

    def test_pauli_gram_reconstructs_spin_trace(self):
        point = dm.build_reference_point()
        mchi2 = dm.MCHI_GEV + 362.0e-6
        before, after, total = dm.spin_resolved_diagram_currents(
            point, dm.MCHI_GEV, mchi2, 0.0
        )
        total_q, _ = tensor.rotate_current_to_q_frame(total, point.q_A)
        coefficients = tensor.pauli_components(total_q)
        gram = tensor.gram_from_pauli_coefficients(coefficients)
        reconstructed = tensor.tensor_from_gram(gram)
        direct = dm.tensor_from_spin_matrices(total_q)
        self.assertLess(
            np.linalg.norm(reconstructed - direct) / max(np.linalg.norm(direct), 1.0),
            3e-14,
        )

    def test_integrated_tensor_matches_independent_dirac_trace_kernel(self):
        result = tensor.integrate_spin_resolved_tensor(
            mchi=1000.0,
            ms=300.0e-6,
            delta_m=450.0e-6,
            mA=131.0 * 0.93149410242,
            ER=200.0e-6,
            speed_kms=776.0,
            g2=1.0,
            width_scheme="pole",
            mapping="threshold_u2",
            nw=6,
            nz=4,
            nphi=4,
            crosscheck_dirac_trace=True,
        )
        self.assertTrue(result["phase_space_open"])
        cross = result["dirac_trace_crosscheck"]
        self.assertLess(cross["max_relative_residual"], 5e-10, cross)
        self.assertLess(result["gram_hermiticity_relative_residual"], 2e-13)
        self.assertLess(result["tensor_hermiticity_relative_residual"], 2e-13)
        self.assertGreater(result["gram_min_eigenvalue"], -1e-8)
        self.assertGreater(result["tensor_min_eigenvalue"], -1e-8)
        self.assertLess(result["q_frame_rotation_max_orthogonality_residual"], 2e-14)
        self.assertLess(result["q_frame_rotation_max_determinant_residual"], 2e-14)

    def test_before_after_and_interference_tensors_are_preserved(self):
        result = tensor.integrate_spin_resolved_tensor(
            mchi=1000.0,
            ms=300.0e-6,
            delta_m=450.0e-6,
            mA=131.0 * 0.93149410242,
            ER=200.0e-6,
            speed_kms=776.0,
            g2=1.0,
            width_scheme="pole",
            mapping="threshold_u2",
            nw=6,
            nz=4,
            nphi=4,
            crosscheck_dirac_trace=False,
        )
        total = np.asarray(result["G_q_aligned_real_imag"])
        before = np.asarray(result["G_before_real_imag"])
        after = np.asarray(result["G_after_real_imag"])
        interference = np.asarray(result["G_interference_real_imag"])
        total_complex = total[..., 0] + 1j * total[..., 1]
        before_complex = before[..., 0] + 1j * before[..., 1]
        after_complex = after[..., 0] + 1j * after[..., 1]
        interference_complex = interference[..., 0] + 1j * interference[..., 1]
        self.assertLess(
            np.linalg.norm(total_complex - before_complex - after_complex - interference_complex),
            2e-12 * max(np.linalg.norm(total_complex), 1.0),
        )
        self.assertGreater(np.linalg.norm(interference_complex), 0.0)

    def test_q_aligned_point_nucleus_decomposition_sums_to_full(self):
        point = dm.build_reference_point()
        Q = float(np.linalg.norm(point.q_A[1:]))
        mA = 131.0 * 0.93149410242
        J0 = 2.0 * mA + point.E_R
        fake = np.zeros((4, 4), dtype=complex)
        fake[0, 0] = 3.0
        fake[1, 1] = 2.0
        fake[2, 2] = 1.0
        fake[3, 3] = 4.0
        fake[0, 3] = 0.25 + 0.1j
        fake[3, 0] = 0.25 - 0.1j
        result = tensor.scalar_contractions_from_q_frame(fake, mA=mA, ER=point.E_R)
        self.assertAlmostEqual(
            result["Ifull"],
            result["Icharge"] + result["Ispatial_nuclear"] + result["Iinterference"],
            places=12,
        )
        self.assertAlmostEqual(result["Ilongitudinal"], 4.0, places=12)
        self.assertAlmostEqual(result["Itransverse"], 3.0, places=12)
        self.assertLess(result["continuity_reduced_relative_residual"], 2e-15)
        self.assertAlmostEqual(
            result["Icontinuity_reduced"], result["Ifull"], places=10
        )
        self.assertGreater(Q, 0.0)
        self.assertGreater(J0, 0.0)


if __name__ == "__main__":
    unittest.main()
