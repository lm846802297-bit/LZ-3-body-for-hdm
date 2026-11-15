import importlib.util
import math
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "audit_lz_2026_black_tail_independent_seeds.py"
SPEC = importlib.util.spec_from_file_location("black_tail_independent_seeds", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class BlackTailIndependentSeedTests(unittest.TestCase):
    def test_mean_standard_deviation_and_standard_error(self):
        mean, sd, se = MOD.mean_sd_se([1.0, 2.0, 3.0])
        self.assertAlmostEqual(mean, 2.0)
        self.assertAlmostEqual(sd, 1.0)
        self.assertAlmostEqual(se, 1.0 / math.sqrt(3.0))

    def test_mean_intensity_and_pairwise_tv(self):
        maps = [
            {(0, 0): 2.0, (1, 0): 0.0},
            {(0, 0): 0.0, (1, 0): 4.0},
            {(0, 0): 1.0, (1, 0): 3.0},
        ]
        mean_map = MOD.mean_intensity(maps)
        self.assertAlmostEqual(mean_map[(0, 0)], 1.0)
        self.assertAlmostEqual(mean_map[(1, 0)], 7.0 / 3.0)
        tv = MOD.pairwise_tv_distances(maps)
        self.assertEqual(len(tv), 3)
        self.assertTrue(all(0.0 <= value <= 1.0 for value in tv))

    def test_independent_seed_comparison_reports_rate_and_shape(self):
        def item(seed, rate, cell, split_rate=0.001, split_tv=0.01):
            return {
                "seed": seed,
                "pooled": {
                    "ws_roi": {"accepted_rate_events_kg_day": rate},
                    "intensity": {"ws_roi": {cell: rate}},
                },
                "split_rate_difference": {"ws_roi": split_rate},
                "split_tv_distance": {"ws_roi": split_tv},
            }

        coarse = [
            item(11, 10.0, (0, 0)),
            item(12, 10.2, (0, 0)),
            item(13, 9.8, (0, 0)),
        ]
        fine = [
            item(21, 10.1, (1, 0)),
            item(22, 9.9, (1, 0)),
            item(23, 10.0, (1, 0)),
        ]
        row = MOD.summarize_comparison(coarse, fine, "GCN", "ws_roi")
        self.assertAlmostEqual(row["coarse_mean_accepted_rate_events_kg_day"], 10.0)
        self.assertAlmostEqual(row["fine_mean_accepted_rate_events_kg_day"], 10.0)
        self.assertAlmostEqual(row["relative_rate_difference_fine_vs_coarse"], 0.0)
        self.assertAlmostEqual(row["tv_distance_between_mean_2d_maps"], 1.0)
        self.assertEqual(row["n_independent_seeds_per_grid"], 3)
        self.assertEqual(row["independent_coarse_seeds"], [11, 12, 13])
        self.assertEqual(row["independent_fine_seeds"], [21, 22, 23])

    def test_one_seed_is_not_enough_for_variance(self):
        with self.assertRaises(ValueError):
            MOD.mean_sd_se([1.0])


if __name__ == "__main__":
    unittest.main()
