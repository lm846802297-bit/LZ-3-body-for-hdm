import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run_user_dsigma_curve import (
    dsigma_GeVminus3_to_cm2_per_keV,
    recoil_interval,
)


class FixedSpeedXe131CurveTests(unittest.TestCase):
    def test_open_recoil_point(self):
        mA = 131 * 0.93149410242
        wmin2, wmax2 = recoil_interval(1000.0, 300e-6, mA, 130e-6, 776.0)
        self.assertGreater(wmax2, wmin2)

    def test_recoil_above_open_interval_is_closed(self):
        mA = 131 * 0.93149410242
        wmin2, wmax2 = recoil_interval(1000.0, 300e-6, mA, 655e-6, 776.0)
        self.assertLessEqual(wmax2, wmin2)

    def test_kinematic_endpoint_brackets(self):
        # Open interval: approximately [109.150286, 654.955583] keV.
        mA = 131 * 0.93149410242

        # Lower boundary: 109.149 keV is closed; 109.151 keV is open.
        wmin2, wmax2 = recoil_interval(
            1000.0, 300e-6, mA, 109.149e-6, 776.0
        )
        self.assertLessEqual(wmax2, wmin2)
        wmin2, wmax2 = recoil_interval(
            1000.0, 300e-6, mA, 109.151e-6, 776.0
        )
        self.assertGreater(wmax2, wmin2)

        # Upper boundary: 654.955 keV is open; 654.956 keV is closed.
        wmin2, wmax2 = recoil_interval(
            1000.0, 300e-6, mA, 654.955e-6, 776.0
        )
        self.assertGreater(wmax2, wmin2)
        wmin2, wmax2 = recoil_interval(
            1000.0, 300e-6, mA, 654.956e-6, 776.0
        )
        self.assertLessEqual(wmax2, wmin2)
    def test_differential_cross_section_unit_conversion(self):
        expected = 0.3893793721e-33
        self.assertTrue(math.isclose(
            dsigma_GeVminus3_to_cm2_per_keV(1.0),
            expected,
            rel_tol=1e-15,
        ))


if __name__ == "__main__":
    unittest.main()
