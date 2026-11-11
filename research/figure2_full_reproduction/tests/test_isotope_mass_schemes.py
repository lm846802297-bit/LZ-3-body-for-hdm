import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from isotope_mass_schemes import electron_binding_energy_eV, isotope_mass_GeV
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

    def test_ame2020_electron_binding_energy_for_xenon(self):
        self.assertAlmostEqual(
            electron_binding_energy_eV(54),
            202378.2777170466,
            places=6,
        )

    def test_cod2022_electron_mass_ratio_in_u(self):
        from isotope_mass_schemes import ELECTRON_MASS_U_CODATA2022
        self.assertAlmostEqual(
            ELECTRON_MASS_U_CODATA2022,
            5.485799090441e-4,
            places=16,
        )

    def test_ame2020_cod2022_xe131_nuclear_mass(self):
        self.assertAlmostEqual(
            isotope_mass_GeV(131, "ame2020_nuclear"),
            121.9099223838014,
            places=10,
        )

    def test_ame2020_scheme_includes_positive_electron_binding_correction(self):
        from isotope_mass_schemes import (
            ELECTRON_MASS_U_CODATA2022,
            NIST_XE_ATOMIC_MASS_U,
            U_GEV_CODATA2022,
            Z_XE,
        )
        A = 131
        mass_without_binding = (
            NIST_XE_ATOMIC_MASS_U[A] - Z_XE * ELECTRON_MASS_U_CODATA2022
        ) * U_GEV_CODATA2022
        mass_with_binding = isotope_mass_GeV(A, "ame2020_nuclear")
        self.assertAlmostEqual(
            mass_with_binding - mass_without_binding,
            electron_binding_energy_eV(54) * 1.0e-9,
            places=14,
        )

    def test_ame2020_xe136_threshold_is_just_below_shm_endpoint(self):
        vmin = vmin_three_body_km_s(
            1000.0,
            0.0003,
            isotope_mass_GeV(136, "ame2020_nuclear"),
            101.0e-6,
        )
        self.assertAlmostEqual(vmin, 775.805285248, delta=2e-6)
        self.assertLess(vmin, 776.0)

    def test_ame2020_xe131_threshold_is_above_shm_endpoint_at_101kev(self):
        vmin = vmin_three_body_km_s(
            1000.0,
            0.0003,
            isotope_mass_GeV(131, "ame2020_nuclear"),
            101.0e-6,
        )
        self.assertAlmostEqual(vmin, 789.592969144, delta=2e-6)
        self.assertGreater(vmin, 776.0)


if __name__ == "__main__":
    unittest.main()
