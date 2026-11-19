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
        cls.nucleus = src.conserved_point_nucleus_current(
            cls.point, src.M_A_GEV
        )

    def _current(self, g2):
        imag = src.vca.width_imaginary_part(
            self.point, self.mchi, src.MS_GEV, 362.0e-6, g2, "pole"
        )
        before, after, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, imag
        )
        return imag, before, after, total

    def test_current_is_four_two_by_two_matrices(self):
        _, _, _, total = self._current(0.1)
        self.assertEqual(total.shape, (4, 2, 2))

    def test_spin_trace_reproduces_existing_Lmunu_zero_width(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, 0.0
        )
        reconstructed = src.tensor_from_spin_matrices(total)
        reference = src.vca.dm_current_tensor(
            self.point, self.mchi, self.mchi2, 0.0
        )
        self.assertLess(src.relative_matrix_residual(reconstructed, reference), 2e-12)

    def test_spin_trace_reproduces_existing_Lmunu_finite_width(self):
        for g2 in (0.1, 1.0):
            imag, _, _, total = self._current(g2)
            reconstructed = src.tensor_from_spin_matrices(total)
            reference = src.vca.dm_current_tensor(
                self.point, self.mchi, self.mchi2, imag
            )
            self.assertLess(
                src.relative_matrix_residual(reconstructed, reference), 2e-12
            )

    def test_finite_width_ward_identity_includes_extra_term(self):
        for g2 in (0.1, 1.0):
            imag, _, _, total = self._current(g2)
            lhs = src.ward_lhs(self.point, total)
            rhs = src.ward_rhs_finite_width(
                self.point, self.mchi, self.mchi2, imag
            )
            self.assertLess(
                src.scaled_ward_identity_residual(self.point, total, lhs, rhs),
                1e-7,
            )
            self.assertGreater(np.linalg.norm(lhs), 1e-8)

    def test_zero_width_ward_identity_is_recovered(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi2, 0.0
        )
        lhs = src.ward_lhs(self.point, total)
        rhs = src.ward_rhs_finite_width(
            self.point, self.mchi, self.mchi2, 0.0
        )
        self.assertLess(
                src.scaled_ward_identity_residual(self.point, total, lhs, rhs),
                1e-7,
            )

    def test_degenerate_mass_zero_width_current_is_conserved(self):
        _, _, total = src.spin_resolved_diagram_currents(
            self.point, self.mchi, self.mchi, 0.0
        )
        divergence = src.ward_lhs(self.point, total)
        self.assertLess(src.scaled_ward_residual(self.point, total), 1e-7)

    def test_conserved_nuclear_current_annihilates_longitudinal_projection(self):
        q = self.point.q_A
        qdotj = q[0] * self.nucleus[0] - np.dot(q[1:], self.nucleus[1:])
        self.assertLess(abs(float(qdotj)), 2e-12)
        for g2 in (0.1, 1.0):
            _, _, _, total = self._current(g2)
            transverse = src.transverse_project_current(self.point, total)
            amp = src.contract_current_with_nucleus(total, self.nucleus)
            amp_t = src.contract_current_with_nucleus(transverse, self.nucleus)
            self.assertLess(src.relative_matrix_residual(amp, amp_t), 2e-11)

    def test_two_emission_orderings_interfere_coherently(self):
        _, before, after, total = self._current(0.1)
        coherent = src.tensor_from_spin_matrices(total)
        incoherent = (
            src.tensor_from_spin_matrices(before)
            + src.tensor_from_spin_matrices(after)
        )
        self.assertGreater(np.linalg.norm(coherent - incoherent), 1e-8)

    def test_momentum_routing_identity(self):
        r_before, r_after = src.eq6.chi2_internal_momenta(self.point)
        q = self.point.q_A
        self.assertLess(np.max(np.abs(q - (r_before - self.point.p_prime))), 2e-12)
        self.assertLess(np.max(np.abs(q - (self.point.p - r_after))), 2e-12)


if __name__ == "__main__":
    unittest.main()
