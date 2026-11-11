import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from isotope_mass_schemes import isotope_mass_GeV  # noqa: E402
from rate_kinematics import vmin_three_body_km_s  # noqa: E402


class NaturalXenonEarthSpeedScanTests(unittest.TestCase):
    def open_isotopes(self, ve_km_s):
        vmax = 544.0 + ve_km_s
        opened = []
        for A in (128, 129, 130, 131, 132, 134, 136):
            vmin = vmin_three_body_km_s(
                1000.0,
                0.0003,
                isotope_mass_GeV(A, "nist_nuclear"),
                101.0e-6,
            )
            if vmin < vmax:
                opened.append(A)
        return opened

    def test_annual_speed_bracket_changes_open_isotopes(self):
        self.assertEqual(self.open_isotopes(217.0), [])
        self.assertEqual(self.open_isotopes(232.0), [136])
        self.assertEqual(self.open_isotopes(247.0), [131, 132, 134, 136])

    def test_xe136_critical_earth_speed(self):
        vmin = vmin_three_body_km_s(
            1000.0, 0.0003, isotope_mass_GeV(136, "nist_nuclear"), 101.0e-6
        )
        ve_critical = vmin - 544.0
        self.assertAlmostEqual(ve_critical, 231.8059, delta=0.002)
        self.assertGreater(232.0, ve_critical)
        self.assertLess(217.0, ve_critical)

    def test_xe131_opens_only_near_high_earth_speed_endpoint(self):
        vmin = vmin_three_body_km_s(
            1000.0, 0.0003, isotope_mass_GeV(131, "nist_nuclear"), 101.0e-6
        )
        self.assertGreater(vmin, 544.0 + 245.0)
        self.assertLess(vmin, 544.0 + 247.0)


if __name__ == "__main__":
    unittest.main()
