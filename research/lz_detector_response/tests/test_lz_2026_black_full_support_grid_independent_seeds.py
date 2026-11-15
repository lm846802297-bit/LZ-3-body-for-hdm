import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_black_full_support_grid_independent_seeds.py"
)
SPEC = importlib.util.spec_from_file_location("black_full_support_grid", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class BlackFullSupportGridTests(unittest.TestCase):
    def setUp(self):
        self.original = (
            MOD.base.ROI_MIN_KEV,
            MOD.base.ROI_MAX_KEV,
            MOD.base.BENCHMARKS,
        )

    def tearDown(self):
        (
            MOD.base.ROI_MIN_KEV,
            MOD.base.ROI_MAX_KEV,
            MOD.base.BENCHMARKS,
        ) = self.original

    def test_support_interval_has_60_one_kev_and_12_five_kev_bins(self):
        MOD.configure_base()
        one = MOD.base.grid.make_edges(
            MOD.base.ROI_MIN_KEV, MOD.base.ROI_MAX_KEV, 1.0
        )
        five = MOD.base.grid.make_edges(
            MOD.base.ROI_MIN_KEV, MOD.base.ROI_MAX_KEV, 5.0
        )
        self.assertEqual(len(one) - 1, 60)
        self.assertEqual(len(five) - 1, 12)
        self.assertAlmostEqual(one[-1], 269.9)
        self.assertAlmostEqual(five[-1], 269.9)

    def test_event_density_gives_equal_total_events_on_both_grids(self):
        MOD.configure_base()
        one_edges = MOD.base.grid.make_edges(210.0, 269.9, 1.0)
        five_edges = MOD.base.grid.make_edges(210.0, 269.9, 5.0)
        one_total = sum(round(16000 * (hi - lo)) for lo, hi in zip(one_edges, one_edges[1:]))
        five_total = sum(round(16000 * (hi - lo)) for lo, hi in zip(five_edges, five_edges[1:]))
        self.assertEqual(one_total, 958400)
        self.assertEqual(five_total, 958400)

    def test_configuration_is_limited_to_black_signal_support(self):
        MOD.configure_base()
        self.assertEqual(MOD.base.BENCHMARKS, ("black_ms360_dm1",))
        self.assertEqual(MOD.base.ROI_MIN_KEV, 210.0)
        self.assertEqual(MOD.base.ROI_MAX_KEV, 269.9)

    def test_custom_configuration_is_supported(self):
        MOD.configure_base(225.4, 269.9, ("black_ms360_dm1",))
        self.assertEqual(MOD.base.ROI_MIN_KEV, 225.4)
        self.assertEqual(MOD.base.ROI_MAX_KEV, 269.9)

    def test_invalid_interval_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "maximum must exceed"):
            MOD.configure_base(270.0, 269.9, ("black_ms360_dm1",))

    def test_empty_benchmark_set_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one benchmark"):
            MOD.configure_base(210.0, 269.9, ())


if __name__ == "__main__":
    unittest.main()
