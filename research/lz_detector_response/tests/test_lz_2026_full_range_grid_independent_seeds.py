import importlib.util
import math
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_full_range_grid_independent_seeds.py"
)
SPEC = importlib.util.spec_from_file_location("full_range_grid_independent", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class FullRangeIndependentSeedTests(unittest.TestCase):
    def test_full_range_grid_edges_have_expected_bin_counts(self):
        one = MOD.grid.make_edges(MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, 1.0)
        five = MOD.grid.make_edges(MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, 5.0)
        self.assertEqual(len(one) - 1, 265)
        self.assertEqual(len(five) - 1, 53)
        self.assertAlmostEqual(one[-1], 269.9)
        self.assertAlmostEqual(five[-1], 269.9)

    def test_response_validation_accepts_both_independent_grid_widths(self):
        for width, events_per_bin in ((1.0, 4000), (5.0, 20000)):
            edges = MOD.grid.make_edges(
                MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, width
            )
            stats = {}
            for ibin, (lo, hi) in enumerate(zip(edges, edges[1:])):
                for replica in (0, 1):
                    stats[(ibin, replica)] = {
                        "lo": lo,
                        "hi": hi,
                        "n": events_per_bin // 2,
                    }
            MOD.validate_response_sample(
                stats, width, events_per_bin, f"test-{width:g}keV"
            )

    def test_response_validation_rejects_missing_replica(self):
        edges = MOD.grid.make_edges(
            MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, 1.0
        )
        stats = {}
        for ibin, (lo, hi) in enumerate(zip(edges, edges[1:])):
            stats[(ibin, 0)] = {"lo": lo, "hi": hi, "n": 2000}
        with self.assertRaisesRegex(ValueError, "missing bin"):
            MOD.validate_response_sample(stats, 1.0, 4000, "incomplete")

    def test_response_validation_rejects_wrong_per_replica_count(self):
        edges = MOD.grid.make_edges(
            MOD.ROI_MIN_KEV, MOD.ROI_MAX_KEV, 1.0
        )
        stats = {}
        for ibin, (lo, hi) in enumerate(zip(edges, edges[1:])):
            for replica in (0, 1):
                stats[(ibin, replica)] = {
                    "lo": lo,
                    "hi": hi,
                    "n": 1999,
                }
        with self.assertRaisesRegex(ValueError, "expected 2000"):
            MOD.validate_response_sample(stats, 1.0, 4000, "bad-count")

    def test_pairwise_seed_spread_is_symmetric(self):
        forward = MOD.symmetric_relative_difference(1.0, 1.1)
        reverse = MOD.symmetric_relative_difference(1.1, 1.0)
        self.assertAlmostEqual(forward, reverse)
        self.assertAlmostEqual(forward, 1.0 / 11.0)

    def test_equal_events_per_kev_is_the_required_sampling_design(self):
        self.assertEqual(4000 / 1.0, 20000 / 5.0)
        self.assertNotEqual(4000, 20000)

    def test_mean_and_standard_error_require_independent_seeds(self):
        mean, sd, se = MOD.mean_sd_se([1.0, 1.1, 0.9])
        self.assertAlmostEqual(mean, 1.0)
        self.assertGreater(sd, 0.0)
        self.assertAlmostEqual(se, sd / math.sqrt(3))
        with self.assertRaises(ValueError):
            MOD.mean_sd_se([1.0])

    def test_comparison_uses_independent_mean_maps(self):
        def sample(seed, rate, fraction):
            return {
                "seed": seed,
                "folds": {
                    ("red_ms200_dm1", "GCN"): {
                        "pooled": {
                            "ws_roi": {
                                "accepted_rate_events_kg_day": rate,
                                "intensity": {
                                    (0, 0): fraction,
                                    (1, 0): 1.0 - fraction,
                                },
                            }
                        },
                        "split_rate_difference": {"ws_roi": 0.001},
                        "split_tv_distance": {"ws_roi": 0.002},
                    }
                },
            }

        one = [
            sample(1, 1.000, 0.600),
            sample(2, 1.001, 0.601),
            sample(3, 0.999, 0.599),
        ]
        five = [
            sample(4, 1.005, 0.595),
            sample(5, 1.006, 0.596),
            sample(6, 1.004, 0.594),
        ]
        row = MOD.summarize_comparison(
            one, five, "red_ms200_dm1", "GCN", "ws_roi", "eft2024"
        )
        self.assertEqual(row["reference_grid_keV"], 1.0)
        self.assertEqual(row["candidate_grid_keV"], 5.0)
        self.assertEqual(row["n_independent_seeds_per_grid"], 3)
        self.assertAlmostEqual(row["relative_rate_difference_5_vs_1keV"], 0.005)
        self.assertAlmostEqual(row["tv_distance_between_mean_2d_maps"], 0.005)

    def test_full_range_gate_checks_both_rate_and_2d_tv(self):
        passing = MOD.evaluate_full_range_grid_gate([
            {
                "relative_rate_difference_5_vs_1keV": 0.004,
                "tv_distance_between_mean_2d_maps": 0.008,
            },
            {
                "relative_rate_difference_5_vs_1keV": 0.009,
                "tv_distance_between_mean_2d_maps": 0.006,
            },
        ])
        self.assertTrue(passing["point_estimate_pass"])
        self.assertEqual(passing["n_comparisons"], 2)

        failing = MOD.evaluate_full_range_grid_gate([
            {
                "relative_rate_difference_5_vs_1keV": 0.004,
                "tv_distance_between_mean_2d_maps": 0.0101,
            }
        ])
        self.assertFalse(failing["point_estimate_pass"])

    def test_gate_rejects_nonfinite_comparison(self):
        with self.assertRaisesRegex(ValueError, "non-finite"):
            MOD.evaluate_full_range_grid_gate([
                {
                    "relative_rate_difference_5_vs_1keV": math.inf,
                    "tv_distance_between_mean_2d_maps": 0.0,
                }
            ])


if __name__ == "__main__":
    unittest.main()
