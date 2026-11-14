import importlib.util
import math
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "converge_lz_2026_three_body_energy_grid.py"
SPEC = importlib.util.spec_from_file_location("energy_grid_convergence", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EnergyGridConvergenceTests(unittest.TestCase):
    def test_grid_edges_cover_exact_roi(self):
        for width, expected_bins in ((1.0, 265), (5.0, 53), (10.0, 27)):
            edges = MOD.make_edges(MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, width)
            self.assertEqual(len(edges) - 1, expected_bins)
            self.assertAlmostEqual(edges[0], 5.4)
            self.assertAlmostEqual(edges[-1], 269.9)
            self.assertTrue(all(b > a for a, b in zip(edges, edges[1:])))

    def test_partial_terminal_bins_preserve_exact_roi_width(self):
        for width in (1.0, 5.0, 10.0):
            edges = MOD.make_edges(MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, width)
            self.assertAlmostEqual(sum(b - a for a, b in zip(edges, edges[1:])), 264.5)
            self.assertAlmostEqual(edges[-1] - edges[-2], 0.5 if width == 1.0 else (4.5 if width == 5.0 else 4.5))

    def test_roi_mask_uses_published_boundaries(self):
        self.assertTrue(MOD.ws_roi_pass(3.0, 646.0, 10**2.75))
        self.assertTrue(MOD.ws_roi_pass(600.0, 646.0, 10**4.15))
        self.assertFalse(MOD.ws_roi_pass(2.999, 646.0, 1000.0))
        self.assertFalse(MOD.ws_roi_pass(600.001, 646.0, 1000.0))
        self.assertFalse(MOD.ws_roi_pass(100.0, 645.0, 1000.0))
        self.assertFalse(MOD.ws_roi_pass(100.0, 646.0, 10**2.749))
        self.assertFalse(MOD.ws_roi_pass(100.0, 646.0, 10**4.151))

    def test_piecewise_linear_integral(self):
        self.assertAlmostEqual(
            MOD.integrate_linear([0.0, 10.0], [2.0, 2.0], 2.0, 8.0), 12.0
        )
        self.assertAlmostEqual(
            MOD.integrate_linear([0.0, 10.0], [0.0, 10.0], 2.0, 8.0), 30.0
        )

    def test_total_variation(self):
        self.assertAlmostEqual(MOD.total_variation({(0, 0): 1.0}, {(0, 0): 2.0}), 0.0)
        self.assertAlmostEqual(
            MOD.total_variation({(0, 0): 1.0}, {(1, 0): 1.0}), 1.0
        )


if __name__ == "__main__":
    unittest.main()
