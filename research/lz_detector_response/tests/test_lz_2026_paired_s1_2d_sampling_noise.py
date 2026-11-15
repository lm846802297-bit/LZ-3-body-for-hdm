import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_paired_s1_2d_sampling_noise.py"
)
SPEC = importlib.util.spec_from_file_location("paired_s1_2d_sampling_noise", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PairedS1TwoDSamplingNoiseTests(unittest.TestCase):
    def test_total_variation_normalizes_maps(self):
        self.assertAlmostEqual(
            MOD.total_variation({"a": 8.0, "b": 2.0}, {"a": 7.0, "b": 3.0}),
            0.1,
        )
        self.assertIsNone(MOD.total_variation({}, {"a": 1.0}))

    def test_split_half_stability_is_reported_separately_from_mode_tv(self):
        metrics = MOD.compare_mode_maps(
            {(0, 0): 15.0, (1, 0): 5.0},
            {(0, 0): 13.0, (1, 0): 7.0},
            {(0, 0): 8.0, (1, 0): 2.0},
            {(0, 0): 7.0, (1, 0): 3.0},
            {(0, 0): 7.0, (1, 0): 3.0},
            {(0, 0): 6.0, (1, 0): 4.0},
        )
        self.assertAlmostEqual(metrics["parametric_vs_full_pooled_tv"], 0.1)
        self.assertAlmostEqual(metrics["parametric_replica0_vs_replica1_tv"], 0.1)
        self.assertAlmostEqual(metrics["full_replica0_vs_replica1_tv"], 0.1)
        self.assertAlmostEqual(metrics["mean_within_mode_split_half_tv"], 0.1)
        self.assertAlmostEqual(metrics["mode_tv_over_mean_split_half_tv"], 1.0)

    def test_joint_tv_can_exceed_both_marginal_tvs(self):
        parametric = {(0, 0): 0.5, (1, 1): 0.5}
        full = {(0, 1): 0.5, (1, 0): 0.5}
        metrics = MOD.compare_mode_maps(
            parametric, full, parametric, parametric, full, full
        )
        self.assertAlmostEqual(metrics["parametric_vs_full_pooled_tv"], 1.0)
        self.assertAlmostEqual(metrics["parametric_vs_full_s1_marginal_tv"], 0.0)
        self.assertAlmostEqual(metrics["parametric_vs_full_log10s2_marginal_tv"], 0.0)

    def test_mode_difference_can_be_smaller_than_split_half_variation(self):
        metrics = MOD.compare_mode_maps(
            {(0, 0): 0.51, (1, 0): 0.49},
            {(0, 0): 0.52, (1, 0): 0.48},
            {(0, 0): 0.60, (1, 0): 0.40},
            {(0, 0): 0.40, (1, 0): 0.60},
            {(0, 0): 0.62, (1, 0): 0.38},
            {(0, 0): 0.42, (1, 0): 0.58},
        )
        self.assertLess(
            metrics["parametric_vs_full_pooled_tv"],
            metrics["mean_within_mode_split_half_tv"],
        )


if __name__ == "__main__":
    unittest.main()
