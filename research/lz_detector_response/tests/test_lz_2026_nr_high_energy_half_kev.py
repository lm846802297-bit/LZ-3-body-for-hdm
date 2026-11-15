import importlib.util
import math
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "compare_lz_2026_nr_high_energy_half_kev.py"
SPEC = importlib.util.spec_from_file_location("high_energy_half_kev", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class HighEnergyHalfKeVTests(unittest.TestCase):
    def test_half_kev_edges_cover_exact_tail_interval(self):
        edges = MOD.interval_edges(225.4, 269.9, 0.5)
        self.assertEqual(len(edges) - 1, 89)
        self.assertAlmostEqual(edges[0], 225.4)
        self.assertAlmostEqual(edges[-1], 269.9)
        self.assertAlmostEqual(sum(b - a for a, b in zip(edges, edges[1:])), 44.5)
        self.assertAlmostEqual(edges[-1] - edges[-2], 0.5)

    def test_interval_fold_preserves_rate_and_cell_normalization(self):
        stats = {}
        for ibin, lo, hi, cell, roi_count in (
            (0, 0.0, 1.0, (0, 0), 5),
            (1, 1.0, 2.0, (1, 0), 10),
        ):
            for replica in (0, 1):
                stats[(ibin, replica)] = {
                    "lo": lo,
                    "hi": hi,
                    "n": 10,
                    "n_s1_coin": 10,
                    "n_s2_threshold": 10,
                    "n_nest": 10,
                    "n_ws_roi": roi_count,
                    "nest_cells": {cell: 10},
                    "roi_cells": {cell: roi_count} if roi_count else {},
                }

        xs, ys = [0.0, 2.0], [1.0, 1.0]
        fine = MOD.fold_interval(stats, xs, ys, 0.0, 2.0, 1.0, None)
        coarse = MOD.fold_interval(stats, xs, ys, 0.0, 2.0, 2.0, None)

        self.assertAlmostEqual(fine["raw_rate"], 2.0)
        self.assertAlmostEqual(fine["nest"]["accepted_rate_events_kg_day"], 2.0)
        self.assertAlmostEqual(fine["ws_roi"]["accepted_rate_events_kg_day"], 1.5)
        self.assertAlmostEqual(
            MOD.grid.total_variation(
                fine["intensity"]["nest"], coarse["intensity"]["nest"]
            ),
            0.0,
        )
        self.assertAlmostEqual(
            MOD.grid.total_variation(
                fine["intensity"]["ws_roi"], coarse["intensity"]["ws_roi"]
            ),
            0.0,
        )

    def test_interval_fold_requires_complete_response_coverage(self):
        stats = {
            (0, 0): {
                "lo": 0.0, "hi": 1.0, "n": 10,
                "n_s1_coin": 10, "n_s2_threshold": 10,
                "n_nest": 10, "n_ws_roi": 10,
                "nest_cells": {(0, 0): 10}, "roi_cells": {(0, 0): 10},
            },
            (0, 1): {
                "lo": 0.0, "hi": 1.0, "n": 10,
                "n_s1_coin": 10, "n_s2_threshold": 10,
                "n_nest": 10, "n_ws_roi": 10,
                "nest_cells": {(0, 0): 10}, "roi_cells": {(0, 0): 10},
            },
        }
        with self.assertRaises(ValueError):
            MOD.fold_interval(stats, [0.0, 2.0], [1.0, 1.0], 0.0, 2.0, 1.0, None)


if __name__ == "__main__":
    unittest.main()
