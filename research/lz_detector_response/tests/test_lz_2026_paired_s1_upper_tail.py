import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "audit_lz_2026_paired_s1_upper_tail.py"
SPEC = importlib.util.spec_from_file_location("paired_s1_upper_tail", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class PairedS1UpperTailTests(unittest.TestCase):
    def test_csv_nested_values_are_valid_json(self):
        row = MOD.csv_safe_row({
            "nested": {"mean": 0.25, "ci": [0.1, 0.4]},
            "plain": "black",
        })
        self.assertEqual(json.loads(row["nested"]), {"mean": 0.25, "ci": [0.1, 0.4]})
        self.assertEqual(row["plain"], "black")

    def test_exact_stratum_normalization_closes_to_integrated_rate(self):
        differential = [1.0, 2.0, 3.0, 4.0]
        denominator = sum(differential)
        weights = [
            MOD.normalized_stratum_event_weight(12.0, value, denominator)
            for value in differential
        ]
        self.assertAlmostEqual(sum(weights), 12.0, places=14)
        self.assertEqual(MOD.normalized_stratum_event_weight(0.0, 4.0, 0.0), 0.0)
        with self.assertRaises(ValueError):
            MOD.normalized_stratum_event_weight(1.0, 0.0, 0.0)

    def test_s1_roi_boundaries_are_inclusive(self):
        self.assertTrue(MOD.s1_roi_pass(True, 3.0))
        self.assertTrue(MOD.s1_roi_pass(True, 600.0))
        self.assertFalse(MOD.s1_roi_pass(True, 600.000001))
        self.assertFalse(MOD.s1_roi_pass(False, 100.0))

    def test_ws_roi_uses_s1_and_common_s2_bounds(self):
        self.assertTrue(MOD.ws_roi_pass(True, 100.0, 646.0, 1000.0, True))
        self.assertFalse(MOD.ws_roi_pass(True, 100.0, 645.0, 1000.0, True))
        self.assertFalse(MOD.ws_roi_pass(True, 600.1, 646.0, 1000.0, True))
        self.assertFalse(MOD.ws_roi_pass(True, 100.0, 646.0, 1000.0, False))

    def test_total_variation_normalizes_input_maps(self):
        self.assertAlmostEqual(MOD.total_variation({0: 2.0, 1: 2.0}, {0: 1.0, 1: 1.0}), 0.0)
        self.assertAlmostEqual(MOD.total_variation({0: 1.0}, {1: 1.0}), 1.0)

    def test_weighted_quantile_uses_one_phd_histogram(self):
        hist = {10: 1.0, 20: 3.0}
        self.assertEqual(MOD.weighted_quantile_from_hist(hist, 0.5), 20.0)
        self.assertEqual(MOD.weighted_quantile_from_hist(hist, 0.0), 10.0)

    def test_seed_level_t_interval(self):
        stats = MOD.scalar_stats([-0.003, -0.004, -0.005, -0.006])
        self.assertAlmostEqual(stats["mean"], -0.0045)
        self.assertLess(stats["t95_ci"][0], stats["mean"])
        self.assertGreater(stats["t95_ci"][1], stats["mean"])

    def test_bootstrap_is_seed_clustered_and_reproducible(self):
        a = [{0: 9.0, 1: 1.0}, {0: 8.0, 1: 2.0}, {0: 7.0, 1: 3.0}]
        b = [{0: 8.0, 1: 2.0}, {0: 7.0, 1: 3.0}, {0: 6.0, 1: 4.0}]
        ci1 = MOD.bootstrap_tv_interval(a, b, replicates=300, seed=1234)
        ci2 = MOD.bootstrap_tv_interval(a, b, replicates=300, seed=1234)
        self.assertEqual(ci1, ci2)
        self.assertLessEqual(ci1[0], ci1[1])

    def test_band_edges_do_not_double_count_adjacent_intervals(self):
        self.assertFalse(MOD.in_band(225.0, 205.0, 225.0))
        self.assertTrue(MOD.in_band(224.999, 205.0, 225.0))
        self.assertTrue(MOD.in_band(225.0, 225.0, 240.0))
        self.assertTrue(MOD.in_band(269.9, 255.0, 269.9))


if __name__ == "__main__":
    unittest.main()
