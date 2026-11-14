from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from compare_5kev_1kev_recoil_grid import (
    compare_group,
    expected_recoil_grid,
    TOLERANCES,
)


def make_rows(step_keV: int) -> list[dict[str, float]]:
    rows = []
    for energy in expected_recoil_grid(step_keV):
        rate = 1.0e-10 * (1.0 + 0.25 * __import__("math").exp(-((energy - 150.0) / 35.0) ** 2))
        rows.append({
            "ER_keV": energy,
            "rate": rate,
            "kernel": rate * 2.0,
        })
    return rows


class RecoilGridConvergenceTests(unittest.TestCase):
    def setUp(self):
        self.eff_x = [0.0, 5.4, 10.0, 50.0, 150.0, 225.0, 269.9, 300.0]
        self.eff_c = [0.0, 0.57, 0.92, 0.955, 0.955, 0.95, 0.50, 0.0]
        self.eff_lo = [0.0, 0.53, 0.87, 0.90, 0.90, 0.89, 0.46, 0.0]
        self.eff_hi = [0.0, 0.61, 0.97, 0.99, 0.99, 0.99, 0.52, 0.0]

    def test_declared_grid_sizes_and_common_nodes(self):
        coarse = expected_recoil_grid(5)
        fine = expected_recoil_grid(1)
        self.assertEqual(len(coarse), 84)
        self.assertEqual(len(fine), 294)
        self.assertEqual(len(set(coarse).intersection(fine)), 84)
        self.assertIn(101.0, coarse)
        self.assertIn(267.0, coarse)
        self.assertIn(542.0, coarse)

    def test_smooth_spectrum_passes(self):
        result = compare_group(
            make_rows(5), make_rows(1),
            self.eff_x, self.eff_c, self.eff_lo, self.eff_hi,
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["common_node_max_relative_rate_difference"], 0.0)
        self.assertLessEqual(
            result["roi_efficiency_weighted_relative_difference"],
            TOLERANCES["roi_efficiency_weighted_relative"],
        )

    def test_fine_grid_perturbation_is_detected(self):
        coarse = make_rows(5)
        fine = make_rows(1)
        for row in fine:
            if 5.4 <= row["ER_keV"] <= 269.9 and row["ER_keV"] % 5.0 != 0.0:
                row["rate"] *= 1.02
                row["kernel"] *= 1.02
        result = compare_group(
            coarse, fine,
            self.eff_x, self.eff_c, self.eff_lo, self.eff_hi,
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertGreater(
            result["roi_efficiency_weighted_relative_difference"],
            TOLERANCES["roi_efficiency_weighted_relative"],
        )


if __name__ == "__main__":
    unittest.main()
