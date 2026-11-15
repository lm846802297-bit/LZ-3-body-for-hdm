import importlib.util
import math
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_energy_resolved_selection_bridge.py"
)
SPEC = importlib.util.spec_from_file_location("energy_resolved_selection_bridge", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EnergyResolvedSelectionBridgeTests(unittest.TestCase):
    def test_pooled_acceptance_uses_rate_weighted_replica_denominators(self):
        value = MOD.pooled_acceptance([10.0, 30.0], [5.0, 3.0])
        self.assertAlmostEqual(value, 0.2)
        self.assertNotAlmostEqual(value, (0.5 + 0.1) / 2.0)

    def test_pooled_acceptance_handles_empty_bins(self):
        self.assertEqual(MOD.pooled_acceptance([0.0, 0.0], [0.0, 0.0]), 0.0)
        with self.assertRaisesRegex(ValueError, "zero total response weight"):
            MOD.pooled_acceptance([0.0, 0.0], [0.1, 0.0])

    def test_conditional_efficiency_is_green_over_orange(self):
        self.assertAlmostEqual(MOD.conditional_efficiency(0.8, 1.0), 0.8)
        self.assertEqual(MOD.conditional_efficiency(0.0, 0.0), 0.0)

    def test_energy_resolved_factorization_multiplies_only_ss_da_residual(self):
        spectra = {
            ("red_ms200_dm1", "GCN"): ([0.0, 1.0, 2.0], [1.0, 1.0, 1.0])
        }
        sums = {}
        for ibin in (0, 1):
            sums[(("red_ms200_dm1", "GCN"), ibin)] = {
                "raw": [1.0, 1.0],
                "nest": [1.0, 1.0],
                "ws_roi": [0.8, 0.8],
                "n": [2, 2],
            }
        efficiency_curves = {
            "trigger_cumulative": [1.0, 1.0, 1.0],
            "trigger_plus_s1_threshold_cumulative": [1.0, 1.0, 1.0],
            "trigger_plus_s1_ss_analysis_cumulative": [0.9, 0.8, 0.7],
            "final_plus_roi_cumulative": [0.7, 0.6, 0.5],
        }
        bins, summary = MOD.build_energy_resolved_rows(
            "eft2024",
            spectra,
            sums,
            {0: (0.0, 1.0), 1: (1.0, 2.0)},
            [0.0, 1.0, 2.0],
            [0.0, 1.0, 2.0],
            efficiency_curves,
        )
        self.assertEqual(len(bins), 2)
        self.assertAlmostEqual(bins[0]["ws_roi_accepted_rate_events_kg_day"], 0.8)
        self.assertAlmostEqual(bins[0]["figs2_ss_da_given_trigger_plus_s1"], 0.85)
        self.assertAlmostEqual(
            bins[0]["energy_resolved_factorized_rate_events_kg_day"], 0.68
        )
        self.assertAlmostEqual(summary[0]["global_factorized_vs_figs2_final_relative_difference"], 0.06666666666666665)
        self.assertAlmostEqual(summary[0]["energy_resolved_factorized_vs_figs2_final_relative_difference"], 0.06666666666666665)

    def test_piecewise_product_integral_is_additive_across_energy_bins(self):
        sx = [0.0, 1.0, 2.0]
        sy = [1.0, 2.0, 1.0]
        ex = [0.0, 0.5, 1.5, 2.0]
        ey = [0.5, 0.7, 0.8, 0.9]
        full = MOD.integrate_piecewise_linear_product(sx, sy, ex, ey, 0.0, 2.0)
        split = (
            MOD.integrate_piecewise_linear_product(sx, sy, ex, ey, 0.0, 1.0)
            + MOD.integrate_piecewise_linear_product(sx, sy, ex, ey, 1.0, 2.0)
        )
        self.assertAlmostEqual(full, split, places=13)

    def test_summary_labels_rate_level_diagnostic_only(self):
        self.assertIn("RATE_LEVEL", MOD.__doc__)


if __name__ == "__main__":
    unittest.main()
