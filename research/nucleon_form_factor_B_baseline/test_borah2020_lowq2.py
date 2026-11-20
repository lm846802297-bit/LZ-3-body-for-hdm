import math
import unittest
import numpy as np

import borah2020_lowq2 as ff


class Borah2020LowQ2Tests(unittest.TestCase):
    def test_sachs_normalizations(self):
        s = ff.sachs_form_factors(0.0)
        self.assertAlmostEqual(float(s["GEp"]), 1.0, places=12)
        self.assertAlmostEqual(float(s["GMp"]), 2.7928473508, places=10)
        self.assertAlmostEqual(float(s["GEn"]), 0.0, places=12)
        self.assertAlmostEqual(float(s["GMn"]), -1.9156796943025016, places=10)

    def test_dirac_pauli_zero_momentum(self):
        f = ff.dirac_pauli_form_factors(0.0)
        self.assertAlmostEqual(float(f["F1p"]), 1.0, places=12)
        self.assertAlmostEqual(float(f["F2p"]), 1.7928473508, places=10)
        self.assertAlmostEqual(float(f["F1n"]), 0.0, places=12)
        self.assertAlmostEqual(float(f["F2n"]), -1.9156796943025016, places=10)

    def test_q4_sum_rules(self):
        for c in (ff.COEFF_GEP, ff.COEFF_GMP, ff.COEFF_GEN, ff.COEFF_GMN):
            for n in range(4):
                value = sum(
                    math.factorial(k)/math.factorial(k-n)*c[k]
                    for k in range(n, 9)
                )
                self.assertAlmostEqual(float(value), 0.0, delta=2e-10)

    def test_published_radii(self):
        h = 1e-6
        s0 = ff.sachs_form_factors(0.0)
        sh = ff.sachs_form_factors(h)
        r2_ep = -6.0*(float(sh["GEp"])-float(s0["GEp"]))/h*ff.HBARC_GEV_FM**2
        r2_mp = -6.0*(float(sh["GMp"])-float(s0["GMp"]))/h/float(s0["GMp"])*ff.HBARC_GEV_FM**2
        r2_en = -6.0*(float(sh["GEn"])-float(s0["GEn"]))/h*ff.HBARC_GEV_FM**2
        r2_mn = -6.0*(float(sh["GMn"])-float(s0["GMn"]))/h/float(s0["GMn"])*ff.HBARC_GEV_FM**2
        self.assertAlmostEqual(math.sqrt(r2_ep), 0.8409, delta=0.002)
        self.assertAlmostEqual(math.sqrt(r2_mp), 0.739, delta=0.003)
        self.assertAlmostEqual(r2_en, -0.1161, delta=0.001)
        self.assertAlmostEqual(math.sqrt(r2_mn), 0.881, delta=0.01)

    def test_strange_current_conventions_are_explicit(self):
        q2 = np.asarray([0.0, 0.1])
        suf = ff.flavor_sum_form_factors(q2, "sufian2017_unit_current")
        alt = ff.flavor_sum_form_factors(q2, "alexandrou2020_charge_weighted_converted")
        latest = ff.flavor_sum_form_factors(q2, "alexandrou2026_continuum_unit_current")
        self.assertAlmostEqual(float(suf["GM_s_unit"][0]), -0.064, places=12)
        self.assertAlmostEqual(float(alt["GM_s_unit"][0]), 0.051, places=12)
        self.assertAlmostEqual(float(latest["GM_s_unit"][0]), -0.01792, places=12)
        self.assertAlmostEqual(float(suf["GE_s_unit"][0]), 0.0, places=12)
        self.assertAlmostEqual(float(alt["GE_s_unit"][0]), 0.0, places=12)
        self.assertAlmostEqual(float(latest["GE_s_unit"][0]), 0.0, places=12)

    def test_magnetic_radius_uses_normalized_GM_expansion(self):
        q2 = np.asarray([0.0, 1e-5])
        for model, rM2 in (
            ("alexandrou2020_charge_weighted_converted", -0.015),
            ("alexandrou2026_continuum_unit_current", -0.01212),
        ):
            gm = ff._strange_sachs(q2, model)[1]
            measured = (float(gm[1]/gm[0])-1.0)/q2[1]
            expected = -rM2*ff.FM2_TO_GEVM2/6.0
            self.assertAlmostEqual(measured, expected, delta=2e-8)

    def test_charge_normalized_B_factor_at_zero(self):
        for model in (
            "sufian2017_unit_current",
            "alexandrou2020_charge_weighted_converted",
            "alexandrou2026_continuum_unit_current",
        ):
            result = ff.cM_and_factor(0.0, model)
            self.assertAlmostEqual(float(result["F1uds"]), 3.0, places=10)
            self.assertAlmostEqual(float(result["F_M"]), 1.0, places=10)
            self.assertAlmostEqual(float(result["rate_multiplier"]), 1.0, places=10)

    def test_covariance_matrices_are_positive(self):
        d = ff.covariance_diagnostics()
        self.assertTrue(d["proton_covariance_symmetric"])
        self.assertTrue(d["neutron_GE_covariance_symmetric"])
        self.assertTrue(d["neutron_GM_covariance_symmetric"])
        self.assertGreater(d["proton_min_eigenvalue"], 0.0)
        self.assertGreater(d["neutron_GE_min_eigenvalue"], 0.0)
        self.assertGreater(d["neutron_GM_min_eigenvalue"], 0.0)

    def test_uncertainty_sampling(self):
        q2 = np.asarray([0.0, 0.06, 0.2])
        d = ff.sample_cM_factors(q2, n_draws=128, seed=42)
        self.assertEqual(len(d["F_M_median"]), 3)
        self.assertTrue(np.all(d["rate_multiplier_p84"] >= d["rate_multiplier_p16"]))
        self.assertAlmostEqual(float(d["F_M_median"][0]), 1.0, delta=0.03)


if __name__ == "__main__":
    unittest.main()
