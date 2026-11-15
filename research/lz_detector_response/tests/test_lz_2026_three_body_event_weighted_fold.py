import array
import importlib.util
import math
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "fold_lz_2026_three_body_event_weighted_response.py"
SPEC = importlib.util.spec_from_file_location("event_weighted_fold", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EventWeightedFoldTests(unittest.TestCase):
    def test_piecewise_linear_interpolation(self):
        xs = [0.0, 1.0, 2.0]
        ys = [1.0, 3.0, 5.0]
        self.assertAlmostEqual(MOD.interpolate_linear(xs, ys, 0.0), 1.0)
        self.assertAlmostEqual(MOD.interpolate_linear(xs, ys, 0.5), 2.0)
        self.assertAlmostEqual(MOD.interpolate_linear(xs, ys, 1.5), 4.0)
        self.assertAlmostEqual(MOD.interpolate_linear(xs, ys, 2.0), 5.0)

    def test_weighted_fold_normalizes_each_bin_to_exact_rate(self):
        events = {}
        for replica in (0, 1):
            events[(0, replica)] = {
                "lo": 0.0,
                "hi": 1.0,
                "energy": array.array("d", [0.25, 0.75]),
                "s1_bin": array.array("i", [0, 1]),
                "log_s2_bin": array.array("i", [0, 0]),
                "nest_pass": bytearray([1, 1]),
                "roi_pass": bytearray([1, 0]),
            }

        folded = MOD.weighted_fold_all_replicas(
            events, [0.0, 1.0], [1.0, 3.0]
        )
        for replica in (0, 1, None):
            self.assertAlmostEqual(folded[replica]["raw_rate"], 2.0)
            self.assertAlmostEqual(
                folded[replica]["accepted_rate"]["nest"], 2.0
            )
            self.assertAlmostEqual(
                folded[replica]["accepted_rate"]["ws_roi"], 0.75
            )
            self.assertAlmostEqual(
                math.fsum(folded[replica]["intensity"]["nest"].values()), 2.0
            )
            self.assertAlmostEqual(
                math.fsum(folded[replica]["intensity"]["ws_roi"].values()), 0.75
            )
            self.assertAlmostEqual(
                folded[replica]["intensity"]["nest"][(0, 0)], 0.75
            )
            self.assertAlmostEqual(
                folded[replica]["intensity"]["nest"][(1, 0)], 1.25
            )

    def test_weighted_fold_rejects_missing_replica(self):
        events = {
            (0, 0): {
                "lo": 0.0, "hi": 1.0,
                "energy": array.array("d", [0.5]),
                "s1_bin": array.array("i", [0]),
                "log_s2_bin": array.array("i", [0]),
                "nest_pass": bytearray([1]),
                "roi_pass": bytearray([1]),
            }
        }
        with self.assertRaises(KeyError):
            MOD.weighted_fold_all_replicas(events, [0.0, 1.0], [1.0, 1.0])


if __name__ == "__main__":
    unittest.main()
