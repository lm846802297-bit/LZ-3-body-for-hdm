import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spin_resolved_three_body_current as src


class SpinResolvedCurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.point = src.build_reference_point()
        cls.mchi = src.MCHI_GEV
        cls.mchi2 = cls.mchi + 362.0e-6

    def test_current_is_four_two_by_two_matrices(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, 0.0
        )
        self.assertEqual(total.shape, (4, 2, 2))

    def test_spin_trace_reproduces_existing_Lmunu(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, 0.0
        )
        reconstructed = src.tensor_from_spin_matrices(total)
        reference = src.vca.dm_current_tensor(
            self.point, self.mchi, self.mchi2, 0.0
        )
        self.assertLess(src.relative_matrix_residual(reconstructed, reference), 2e-12)

    def test_spin_trace_reproduces_existing_Lmunu_with_width(self):
        gamma = src.eq6.chi2_width_dirac_scalar(
            self.mchi, src.MS_GEV, 362.0e-6, 1.0
        )
        imag = self.mchi2 * gamma
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, imag
        )
        reconstructed = src.tensor_from_spin_matrices(total)
        reference = src.vca.dm_current_tensor(
            self.point, self.mchi, self.mchi2, imag
        )
        self.assertLess(src.relative_matrix_residual(reconstructed, reference), 2e-12)

    def test_two_emission_orderings_interfere_coherently(self):
        before, after, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, 0.0
        )
        coherent = src.tensor_from_spin_matrices(total)
        incoherent = (
            src.tensor_from_spin_matrices(before)
            + src.tensor_from_spin_matrices(after)
        )
        self.assertGreater(np.linalg.norm(coherent - incoherent), 1e-8)

    def test_exact_ward_identity_for_non_degenerate_masses(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, 0.0
        )
        lhs = src.ward_lhs(self.point, total)
        rhs = src.ward_rhs(self.point, self.mchi, self.mchi2)
        self.assertLess(src.relative_matrix_residual(lhs, rhs), 2e-9)
        self.assertGreater(np.linalg.norm(lhs), 1e-8)

    def test_current_is_conserved_in_degenerate_mass_limit(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi, 0.0
        )
        divergence = src.ward_lhs(self.point, total)
        self.assertLess(src.scaled_ward_residual(self.point, total), 1e-7)

    def test_momentum_routing_identity(self):
        r_before, r_after = src.eq6.chi2_internal_momenta(self.point)
        q = self.point.q_A
        self.assertLess(np.max(np.abs(q - (r_before - self.point.p_prime))), 2e-12)
        self.assertLess(np.max(np.abs(q - (self.point.p - r_after))), 2e-12)

    def test_reference_point_is_physically_open(self):
        w_min, w_max = src.eq6.limits(
            src.MCHI_GEV, src.MS_GEV, src.M_A_GEV,
            src.ER_GEV, src.SPEED_KMS
        )
        self.assertGreater(w_max, w_min)
        self.assertAlmostEqual(src.eq6.dot(self.point.K, self.point.K), self.point.W2, places=6)


if __name__ == "__main__":
    unittest.main()
