import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "aggregate_lz_2026_paired_s1_2d_independent_seeds.py"
)
SPEC = importlib.util.spec_from_file_location("paired_s1_2d_independent_seeds", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PairedS1IndependentSeedAggregationTests(unittest.TestCase):
    def test_total_variation_and_mean_map(self):
        self.assertAlmostEqual(
            MOD.total_variation({"a": 0.8, "b": 0.2}, {"a": 0.7, "b": 0.3}),
            0.1,
        )
        mean = MOD.ensemble_mean_map([
            {(0, 0): 1.0, (1, 0): 1.0},
            {(0, 0): 3.0, (1, 0): 1.0},
            {(0, 0): 2.0, (1, 0): 2.0},
        ])
        self.assertAlmostEqual(mean[(0, 0)], 2.0)
        self.assertAlmostEqual(mean[(1, 0)], 4.0/3.0)

    def test_three_seed_summary_separates_mode_and_seed_spread(self):
        maps = {
            "seed1": {
                "parametric": {(0, 0): 0.60, (1, 0): 0.40},
                "full": {(0, 0): 0.50, (1, 0): 0.50},
            },
            "seed2": {
                "parametric": {(0, 0): 0.55, (1, 0): 0.45},
                "full": {(0, 0): 0.45, (1, 0): 0.55},
            },
            "seed3": {
                "parametric": {(0, 0): 0.58, (1, 0): 0.42},
                "full": {(0, 0): 0.48, (1, 0): 0.52},
            },
        }
        result = MOD.summarize_seed_maps(maps)
        self.assertEqual(result["n_seeds"], 3)
        self.assertAlmostEqual(result["mean_map_parametric_vs_full_tv"], 0.1)
        self.assertAlmostEqual(result["mean_seed_parametric_vs_full_tv"], 0.1)
        self.assertAlmostEqual(result["mean_within_mode_seed_pairwise_tv"], 1.0/30.0)
        self.assertAlmostEqual(
            result["mean_map_tv_over_within_mode_seed_pairwise_tv"], 3.0
        )
        self.assertEqual(set(result["per_seed_parametric_vs_full_tv"]), set(maps))

    def test_requires_three_distinct_seed_labels(self):
        with self.assertRaisesRegex(ValueError, "at least two independent seeds"):
            MOD.summarize_seed_maps({
                "seed1": {
                    "parametric": {(0, 0): 1.0},
                    "full": {(0, 0): 1.0},
                }
            })


if __name__ == "__main__":
    unittest.main()
