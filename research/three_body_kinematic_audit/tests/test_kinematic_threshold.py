from __future__ import annotations

import sys
import unittest
from pathlib import Path

CALCULATIONS = Path(__file__).resolve().parents[1] / "calculations"
sys.path.insert(0, str(CALCULATIONS))

import kinematic_threshold as kt  # noqa: E402


class KinematicThresholdTests(unittest.TestCase):
    def test_776_kms_maximum(self) -> None:
        mass_kev, recoil_kev = kt.optimize_mass(776.0)
        self.assertAlmostEqual(mass_kev, 364.2680883331195, places=6)
        self.assertAlmostEqual(recoil_kev, 324.6594936959347, places=6)

    def test_360_kev_open_interval_at_776(self) -> None:
        roots = kt.allowed_recoil_roots(360.0, 776.0)
        self.assertEqual(len(roots), 2)
        self.assertAlmostEqual(roots[0], 258.1782515834949, places=5)
        self.assertAlmostEqual(roots[1], 398.74890768461205, places=5)

    def test_300_kev_global_threshold(self) -> None:
        speed_km_s, recoil_kev = kt.minimum_speed_for_mass(300.0)
        self.assertAlmostEqual(speed_km_s, 704.23, places=2)
        self.assertAlmostEqual(recoil_kev, 267.38, places=2)

    def test_mev_labels_are_kinematically_closed(self) -> None:
        for speed_km_s in kt.SPEEDS_KM_S:
            max_mass_kev, _ = kt.optimize_mass(speed_km_s)
            self.assertLess(max_mass_kev, 300_000.0)
            self.assertLess(max_mass_kev, 360_000.0)


if __name__ == "__main__":
    unittest.main()
