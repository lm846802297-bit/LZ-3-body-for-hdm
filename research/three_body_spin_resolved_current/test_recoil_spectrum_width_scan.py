import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import recoil_spectrum_width_scan as scan


class RecoilSpectrumWidthScanTests(unittest.TestCase):
    def test_near_pole_scan_stays_below_pole(self):
        case = next(x for x in scan.CASES if x["name"] == "near_pole_dm362_g2_1")
        for er in case["energies_keV"]:
            wmin, wmax = scan.eq6.limits(
                scan.MCHI, scan.MS, scan.M_A, er * 1e-6, scan.SPEED
            )
            self.assertGreater(wmax, wmin)
            clearance = scan.MCHI + case["delta_m"] - wmax**0.5
            self.assertGreater(clearance, 0.0)

    def test_crossing_point_is_outside_offshell_scan(self):
        case = next(x for x in scan.CASES if x["name"] == "near_pole_dm362_g2_1")
        wmin, wmax = scan.eq6.limits(
            scan.MCHI, scan.MS, scan.M_A, 280.0e-6, scan.SPEED
        )
        self.assertGreater(wmax, wmin)
        clearance = scan.MCHI + case["delta_m"] - wmax**0.5
        self.assertLess(clearance, 0.0)

    def test_reference_cases_include_the_200keV_anchor(self):
        for case in scan.CASES:
            self.assertIn(200.0, case["energies_keV"])


if __name__ == "__main__":
    unittest.main()
