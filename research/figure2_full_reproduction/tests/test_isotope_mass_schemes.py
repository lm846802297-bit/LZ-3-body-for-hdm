import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from isotope_mass_schemes import isotope_mass_GeV
from rate_kinematics import vmin_three_body_km_s


class IsotopeMassSchemeTests(unittest.TestCase):
    def test_default_mass_scheme_preserves_previous_Au_baseline(self):
        self.assertAlmostEqual(
            isotope_mass_GeV(131, "A_u"),
            131 * 0.93149410242,
            places=13,
        )

    def test_nist_nuclear_mass_is_below_Au_approximation(self):
        for A in (128, 131, 136):
            m_au = isotope_mass_GeV(A, "A_u")
            m_nist = isotope_mass_GeV(A, "nist_nuclear")
            self.assertLess(m_nist, m_au)
            self.assertGreater((m_nist / m_au - 1.0), -1.2e-3)
            self.assertLess((m_nist / m_au - 1.0), -7.0e-4)

    def test_xe136_101kev_threshold_shift_is_about_point_three_km_s(self):
        mchi, ms, ER = 1000.0, 0.0003, 101.0e-6
        v_au = vmin_three_body_km_s(
            mchi, ms, isotope_mass_GeV(136, "A_u"), ER
        )
        v_nist = vmin_three_body_km_s(
            mchi, ms, isotope_mass_GeV(136, "nist_nuclear"), ER
        )
        self.assertAlmostEqual(v_au, 775.4782, delta=0.002)
        self.assertAlmostEqual(v_nist, 775.8059, delta=0.002)
        self.assertAlmostEqual(v_nist - v_au, 0.3276, delta=0.002)

    def test_only_xe136_is_open_at_101kev_with_both_mass_schemes(self):
        mchi, ms, ER, vmax = 1000.0, 0.0003, 101.0e-6, 776.0
        for scheme in ("A_u", "nist_nuclear"):
            open_isotopes = [
                A for A in (128, 129, 130, 131, 132, 134, 136)
                if vmin_three_body_km_s(
                    mchi, ms, isotope_mass_GeV(A, scheme), ER
                ) < vmax
            ]
            self.assertEqual(open_isotopes, [136])

    def test_nist_mass_response_momentum_is_smaller(self):
        ER = 101.0e-6
        q_au = math.sqrt(2.0 * isotope_mass_GeV(136, "A_u") * ER)
        q_nist = math.sqrt(2.0 * isotope_mass_GeV(136, "nist_nuclear") * ER)
        self.assertLess(q_nist, q_au)


if __name__ == "__main__":
    unittest.main()
