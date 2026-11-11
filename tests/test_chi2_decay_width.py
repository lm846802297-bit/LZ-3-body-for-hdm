import math
import unittest

from calculations.chi2_decay_width import (
    chi2_to_chi1s_width_GeV,
    chi2_to_chi1s_width_heavy_limit_GeV,
)


class Chi2DecayWidthTests(unittest.TestCase):
    def test_reference_benchmark(self):
        # m_chi1 = 1 TeV, Delta m = 1 MeV, m_s = 300 keV, |g2| = 1.
        width_keV = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 3.0e-4, 1.0) * 1.0e6
        self.assertAlmostEqual(width_keV, 151.82391157876958, places=10)

    def test_coupling_squared_scaling(self):
        base = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 3.0e-4, 1.0)
        doubled = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 3.0e-4, 2.0)
        self.assertAlmostEqual(doubled / base, 4.0, places=13)

    def test_complex_coupling_uses_modulus_squared(self):
        real = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 3.0e-4, 2.0)
        complex_value = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 3.0e-4, 2.0j)
        self.assertAlmostEqual(complex_value / real, 1.0, places=13)

    def test_threshold_and_closed_channel(self):
        self.assertEqual(chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 1.0e-3, 1.0), 0.0)
        self.assertEqual(chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 1.1e-3, 1.0), 0.0)

    def test_360_kev_is_open_but_360_mev_is_closed_for_delta_1_mev(self):
        open_width_keV = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 360.0e-6, 1.0) * 1.0e6
        closed_width = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 360.0e-3, 1.0)
        self.assertAlmostEqual(open_width_keV, 148.48374799368014, places=10)
        self.assertEqual(closed_width, 0.0)

    def test_heavy_limit_is_accurate_for_1_tev_benchmark(self):
        exact = chi2_to_chi1s_width_GeV(1000.0, 1.0e-3, 3.0e-4, 1.0)
        approx = chi2_to_chi1s_width_heavy_limit_GeV(1000.0, 1.0e-3, 3.0e-4, 1.0)
        self.assertLess(abs(approx / exact - 1.0), 2.0e-6)

    def test_factorized_formula_matches_direct_kallen_formula(self):
        m1, delta, ms, g2 = 3.0, 1.0, 0.2, 0.7
        M = m1 + delta
        lam = (M**2 - (m1 + ms) ** 2) * (M**2 - (m1 - ms) ** 2)
        direct = (
            abs(g2) ** 2
            * math.sqrt(lam)
            * ((M + m1) ** 2 - ms**2)
            / (16.0 * math.pi * M**3)
        )
        factorized = chi2_to_chi1s_width_GeV(m1, delta, ms, g2)
        self.assertAlmostEqual(factorized / direct, 1.0, places=14)

    def test_invalid_masses_raise(self):
        with self.assertRaises(ValueError):
            chi2_to_chi1s_width_GeV(-1.0, 1.0e-3, 3.0e-4, 1.0)
        with self.assertRaises(ValueError):
            chi2_to_chi1s_width_GeV(1000.0, -1.0e-3, 3.0e-4, 1.0)


if __name__ == "__main__":
    unittest.main()
