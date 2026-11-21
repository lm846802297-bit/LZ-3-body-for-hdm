import math
import unittest

import nucleon_vector_form_factors as ff


class VectorFormFactorTests(unittest.TestCase):
    def test_zero_momentum_bishara_anchor(self):
        f1, f2 = ff.bishara_linear(0.0)
        self.assertAlmostEqual(f1, 3.0, places=12)
        self.assertAlmostEqual(f2, -0.552, places=12)

    def test_zero_momentum_zexp_anchor(self):
        f1, f2 = ff.isoscalar_zexp(0.0)
        self.assertAlmostEqual(f1, 3.0, places=10)
        self.assertAlmostEqual(f2, -0.552, places=10)

    def test_effective_nucleon_form_factors_remove_quark_charge_factor_once(self):
        f1, f2 = ff.effective_nucleon_form_factors(ff.F1V0, ff.F2V0)
        self.assertAlmostEqual(f1, 1.0, places=15)
        self.assertAlmostEqual(f2, -0.184, places=15)
        # g_Vq^2 * F_i^2 == g_VN^2 * Fhat_i^2 when g_VN=3*g_Vq.
        g_vn, g_vq = 0.7, 0.7 / 3.0
        self.assertAlmostEqual((g_vq * ff.F1V0)**2, (g_vn * f1)**2, places=15)
        self.assertAlmostEqual((g_vq * ff.F2V0)**2, (g_vn * f2)**2, places=15)

    def test_finite_momentum_coupling_basis_equivalence(self):
        q2 = 0.047
        f1_raw, f2_raw = ff.bishara_linear(q2)
        f1_hat, f2_hat = ff.effective_nucleon_form_factors(f1_raw, f2_raw)
        g_vq = 0.13
        g_vn = 3.0 * g_vq
        self.assertAlmostEqual(g_vq * f1_raw, g_vn * f1_hat, places=14)
        self.assertAlmostEqual(g_vq * f2_raw, g_vn * f2_hat, places=14)
        self.assertAlmostEqual((g_vq * f1_raw)**2, (g_vn * f1_hat)**2, places=14)
        self.assertAlmostEqual((g_vq * f2_raw)**2, (g_vn * f2_hat)**2, places=14)

    def test_bishara_flavor_components_sum_to_universal_current(self):
        q2 = 0.047
        components = ff.bishara_flavor_components(q2)
        self.assertAlmostEqual(
            sum(components["F1_by_flavor"].values()),
            components["F1V"],
            places=14,
        )
        self.assertAlmostEqual(
            sum(components["F2_by_flavor"].values()),
            components["F2V"],
            places=14,
        )
        self.assertAlmostEqual(components["F1_by_flavor"]["u"], 2.0 - 5.57 * q2)
        self.assertAlmostEqual(components["F1_by_flavor"]["d"], 1.0 - 2.84 * q2)
        self.assertAlmostEqual(components["F1_by_flavor"]["s"], 0.018 * q2)
        self.assertAlmostEqual(components["F2V"], -0.552, places=14)

    def test_bishara_slope(self):
        q2 = 1.0e-6
        f1, _ = ff.bishara_linear(q2)
        expected = 3.0 - ff.F1_SLOPE_BISHARA * q2
        self.assertAlmostEqual(f1, expected, places=14)
        self.assertAlmostEqual(
            ff.F1_SLOPE_BISHARA, 8.392, places=12
        )

    def test_charge_coefficients_use_independent_tN_and_spatial_QA(self):
        qA = 0.22
        tN = -0.04
        F1, F2 = 2.7, -0.5
        mN = ff.M_N_GEV
        cM, cPhi = ff.charge_coefficients(
            qA, F1=F1, F2=F2, mN_GeV=mN, tN_GeV2=tN
        )
        expected_cM = F1 + tN * (F1 + 2.0 * F2) / (8.0 * mN**2)
        expected_cPhi = qA**2 * (F1 + 2.0 * F2) / (4.0 * mN**2)
        self.assertAlmostEqual(cM, expected_cM, places=14)
        self.assertAlmostEqual(cPhi, expected_cPhi, places=14)

    def test_charge_coefficients_zero_q(self):
        c_m, c_phi = ff.charge_coefficients(0.0, F1=3.0, F2=-0.552)
        self.assertAlmostEqual(c_m, 3.0, places=12)
        self.assertAlmostEqual(c_phi, 0.0, places=12)

    def test_default_baseline_is_bishara_linear(self):
        self.assertEqual(ff.DEFAULT_FORM_FACTOR_PRESCRIPTION, "bishara_linear")
        q2 = 0.05
        f1q, f2q = ff.bishara_linear(q2)
        f1n, f2n = ff.effective_nucleon_form_factors(f1q, f2q)
        self.assertAlmostEqual(f1n, 1.0 - (8.392 / 3.0) * q2, places=14)
        self.assertAlmostEqual(f2n, -0.184, places=14)

    def test_selected_xe131_charge_benchmark_is_finite(self):
        row = ff.q0_anchor_baseline_correction(
            0.256271868,
            115.8894642,
            -1.46249,
            prescription="isoscalar_zexp",
            tN_GeV2=-0.065,
        )
        self.assertTrue(math.isfinite(row["F1V_quark_sum"]))
        self.assertTrue(math.isfinite(row["F2V_quark_sum"]))
        self.assertTrue(math.isfinite(row["relative_to_A_AFH_finite_size_M"]))
        self.assertLess(row["relative_to_A_AFH_finite_size_M"], -0.2)
        self.assertGreater(row["relative_to_A_AFH_finite_size_M"], -0.4)

    def test_phi_relative_correction_is_reported_separately_from_B(self):
        row = ff.q0_anchor_baseline_correction(
            0.256271868,
            115.8894642,
            -1.46249,
            prescription="isoscalar_zexp",
            tN_GeV2=-0.065,
        )
        self.assertAlmostEqual(row["relative_to_B_finite_tN_M"], -0.01843, delta=0.002)

if __name__ == "__main__":
    unittest.main()
