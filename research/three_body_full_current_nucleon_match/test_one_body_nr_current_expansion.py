import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import full_current_nucleon_match as fm


class OneBodyNRCurrentExpansionTests(unittest.TestCase):
    def test_small_momentum_expansion_reproduces_exact_dirac_pauli_current(self):
        q = np.asarray([0.002, 0.0, 0.0])
        ell = np.asarray([0.0, 0.001, 0.0])
        exact_cov, _, (p_i, p_f) = fm.nucleon_current_matrices(
            q, ell, 1.0, -0.184
        )
        exact = exact_cov * fm.nonrel_state_normalization(p_i, p_f)
        leading = fm.leading_nr_nucleon_current_matrices(
            q, ell, 1.0, -0.184
        )
        self.assertLess(fm._relative_matrix_residual(exact[0], leading[0]), 1e-8)
        self.assertLess(fm._relative_matrix_residual(exact[1:], leading[1:]), 1e-5)

    def test_charge_darwin_foldy_and_spin_orbit_terms_have_the_declared_sign(self):
        q = np.asarray([0.08, 0.0, 0.0])
        ell = np.asarray([0.0, 0.07, 0.0])
        f1, f2, m = 1.0, -0.184, fm.M_N_GEV
        got = fm.leading_nr_nucleon_current_matrices(q, ell, f1, f2, m)
        p_i, p_f = ell - 0.5 * q, ell + 0.5 * q
        ei = np.sqrt(m * m + p_i @ p_i)
        ef = np.sqrt(m * m + p_f @ p_f)
        t_n = (ef - ei) ** 2 - q @ q
        expected_identity = f1 + (f1 + 2.0 * f2) * t_n / (8.0 * m * m)
        self.assertAlmostEqual(0.5 * np.trace(got[0]).real, expected_identity, places=14)
        spin_coefficients = np.asarray([
            0.5 * np.trace(fm.PAULI[j + 1] @ got[0])
            for j in range(3)
        ])
        expected_spin = (
            1j * (f1 + 2.0 * f2) / (4.0 * m * m) * np.cross(q, ell)
        )
        np.testing.assert_allclose(spin_coefficients, expected_spin, rtol=1e-13, atol=1e-15)

    def test_spatial_current_is_convection_plus_transverse_magnetization(self):
        q = np.asarray([0.12, 0.0, 0.0])
        ell = np.asarray([0.0, 0.09, 0.0])
        f1, f2, m = 1.0, -0.184, fm.M_N_GEV
        got = fm.leading_nr_nucleon_current_matrices(q, ell, f1, f2, m)
        identity_coefficients = np.asarray([
            0.5 * np.trace(got[i + 1]).real for i in range(3)
        ])
        np.testing.assert_allclose(identity_coefficients, f1 * ell / m, rtol=1e-13, atol=1e-15)
        spin_coefficients = np.asarray([
            [
                0.5 * np.trace(fm.PAULI[j + 1] @ got[i + 1])
                for j in range(3)
            ]
            for i in range(3)
        ])
        expected = np.asarray([
            [1j * (f1 + f2) / (2.0 * m) * np.cross(q, np.eye(3)[i])[j]
             for j in range(3)]
            for i in range(3)
        ])
        np.testing.assert_allclose(spin_coefficients, expected, rtol=1e-13, atol=1e-15)
        qhat = q / np.linalg.norm(q)
        longitudinal_spin = np.einsum("i,ij->j", qhat, spin_coefficients)
        np.testing.assert_allclose(longitudinal_spin, 0.0, atol=1e-15)

    def test_energy_transfer_matched_benchmarks_quantify_truncation_and_satisfy_exact_ward(self):
        rows = fm.run_one_body_nr_matching_scan()
        self.assertEqual(len(rows), 8)
        self.assertLess(max(abs(row["qN0_minus_qA0_GeV"]) for row in rows), 2e-13)
        self.assertLess(max(row["exact_nucleon_ward_residual"] for row in rows), 2e-12)
        self.assertLess(max(row["exact_longitudinal_continuity_residual"] for row in rows), 2e-12)
        self.assertLess(max(row["charge_relative_residual"] for row in rows), 6.0e-4)
        self.assertLess(max(row["transverse_spatial_relative_residual"] for row in rows), 3.2e-2)
        self.assertLess(max(row["full_four_current_relative_residual"] for row in rows), 8.0e-3)

    def test_spatial_expansion_error_decreases_in_the_small_momentum_limit(self):
        q = np.asarray([0.10, 0.0, 0.0])
        ell_large = np.asarray([0.0, 0.10, 0.0])
        ell_small = 0.5 * ell_large
        large = fm.analyze_one_body_nr_matching_point(q, ell_large)
        small = fm.analyze_one_body_nr_matching_point(0.5 * q, ell_small)
        self.assertLess(
            small["transverse_spatial_relative_residual"],
            large["transverse_spatial_relative_residual"],
        )


if __name__ == "__main__":
    unittest.main()
