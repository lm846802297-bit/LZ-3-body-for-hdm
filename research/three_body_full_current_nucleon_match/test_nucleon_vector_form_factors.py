import math
import unittest

import nucleon_vector_form_factors as ff


class VectorFormFactorTests(unittest.TestCase):
    def test_zero_momentum_raw_bishara_anchor(self):
        f1, f2 = ff.bishara_linear(0.0)
        self.assertAlmostEqual(f1, 3.0, places=12)
        self.assertAlmostEqual(f2, -0.552, places=12)

    def test_zero_momentum_raw_zexp_anchor(self):
        f1, f2 = ff.isoscalar_zexp(0.0)
        self.assertAlmostEqual(f1, 3.0, places=10)
        self.assertAlmostEqual(f2, -0.552, places=10)

    def test_raw_to_effective_gVN_normalization_is_exactly_one_third(self):
        f1hat, f2hat = ff.effective_nucleon_form_factors(3.0, -0.552)
        self.assertAlmostEqual(f1hat, 1.0, places=14)
        self.assertAlmostEqual(f2hat, -0.184, places=14)

    def test_bishara_raw_dirac_slope(self):
        q2 = 1.0e-6
        f1, _ = ff.bishara_linear(q2)
        expected = 3.0 - ff.F1_SLOPE_BISHARA * q2
        self.assertAlmostEqual(f1, expected, places=14)
        self.assertAlmostEqual(ff.F1_SLOPE_BISHARA, 8.392, places=12)

    def test_charge_coefficients_zero_transfer(self):
        c_m, c_phi = ff.charge_coefficients(
            0.0, F1=1.0, F2=-0.184, tN_GeV2=0.0
        )
        self.assertAlmostEqual(c_m, 1.0, places=14)
        self.assertAlmostEqual(c_phi, 0.0, places=14)

    def test_charge_coefficients_keep_tN_separate_from_spatial_qA2(self):
        qA = 0.25
        tN = -0.060
        f1, f2 = 1.0, -0.184
        mN = ff.M_N_GEV
        c_m, c_phi = ff.charge_coefficients(
            qA, F1=f1, F2=f2, tN_GeV2=tN, mN_GeV=mN
        )
        expected_cm = f1 + tN * (f1 + 2.0 * f2) / (8.0 * mN**2)
        expected_cphi = qA**2 * (f1 + 2.0 * f2) / (4.0 * mN**2)
        static_cm = f1 - qA**2 * (f1 + 2.0 * f2) / (8.0 * mN**2)
        self.assertAlmostEqual(c_m, expected_cm, places=14)
        self.assertAlmostEqual(c_phi, expected_cphi, places=14)
        self.assertNotAlmostEqual(c_m, static_cm, places=10)

    def test_static_A_reference_is_explicitly_a_diagnostic(self):
        row = ff.static_A_reference_correction(
            0.256271868,
            115.8894642,
            -1.46249,
            prescription="isoscalar_zexp",
        )
        self.assertTrue(math.isfinite(row["F1N_effective"]))
        self.assertTrue(math.isfinite(row["F2N_effective"]))
        self.assertTrue(math.isfinite(row["relative_to_A_reference"]))
        self.assertEqual(
            row["kinematics"],
            "static diagnostic q_N^0=0; t_N=-Q_A^2; not formal B",
        )
        self.assertLess(row["relative_to_A_reference"], -0.2)
        self.assertGreater(row["relative_to_A_reference"], -0.4)

    def test_phi_relative_correction_remains_small_in_static_diagnostic(self):
        row = ff.static_A_reference_correction(
            0.256271868,
            115.8894642,
            -1.46249,
            prescription="isoscalar_zexp",
        )
        self.assertAlmostEqual(
            row["relative_to_finite_t_M"], -0.01843, delta=0.002
        )


if __name__ == "__main__":
    unittest.main()
