import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_paired_s1_2d_binning_stability.py"
)
SPEC = importlib.util.spec_from_file_location("paired_s1_2d_binning_stability", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PairedS1TwoDBinningStabilityTests(unittest.TestCase):
    def test_rebinning_preserves_integrated_rate(self):
        source = {
            (0, 0): 1.0,
            (1, 1): 2.0,
            (2, 2): 3.0,
            (3, 3): 4.0,
        }
        coarse = MOD.rebin_map(source, 2)
        self.assertEqual(coarse, {(0, 0): 3.0, (1, 1): 7.0})
        self.assertAlmostEqual(sum(source.values()), sum(coarse.values()))

    def test_total_variation_cannot_increase_under_exact_coarsening(self):
        parametric = {(0, 0): 0.5, (1, 1): 0.5}
        full = {(0, 1): 0.5, (1, 0): 0.5}
        fine_tv = MOD.total_variation(parametric, full)
        coarse_tv = MOD.total_variation(
            MOD.rebin_map(parametric, 2),
            MOD.rebin_map(full, 2),
        )
        self.assertAlmostEqual(fine_tv, 1.0)
        self.assertAlmostEqual(coarse_tv, 0.0)
        self.assertLessEqual(coarse_tv, fine_tv)

    def test_marginalization_projects_the_requested_axis(self):
        cells = {
            (0, 0): 1.0,
            (0, 1): 2.0,
            (1, 0): 3.0,
        }
        self.assertEqual(MOD.marginalize_map(cells, 0), {0: 3.0, 1: 3.0})
        self.assertEqual(MOD.marginalize_map(cells, 1), {0: 4.0, 1: 2.0})

    def test_invalid_rebin_factor_and_axis_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "factor must be one of"):
            MOD.rebin_map({(0, 0): 1.0}, 3)
        with self.assertRaisesRegex(ValueError, "axis must be"):
            MOD.marginalize_map({(0, 0): 1.0}, 2)


if __name__ == "__main__":
    unittest.main()
