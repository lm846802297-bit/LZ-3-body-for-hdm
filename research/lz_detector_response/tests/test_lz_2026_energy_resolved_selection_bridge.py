import csv
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_pooled_acceptance_rejects_nonfinite_or_non_subset_weights(self):
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            MOD.pooled_acceptance([1.0, math.nan], [0.5, 0.0])
        with self.assertRaisesRegex(ValueError, "exceeds its total"):
            MOD.pooled_acceptance([1.0, 2.0], [1.1, 0.0])

    def test_conditional_efficiency_is_green_over_orange(self):
        self.assertAlmostEqual(MOD.conditional_efficiency(0.8, 1.0), 0.8)
        self.assertEqual(MOD.conditional_efficiency(0.0, 0.0), 0.0)
        with self.assertRaisesRegex(ValueError, "zero denominator"):
            MOD.conditional_efficiency(0.1, 0.0)
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            MOD.conditional_efficiency(math.nan, 1.0)

    def test_energy_resolved_factorization_is_not_global_factorization(self):
        spectra = {
            ("red_ms200_dm1", "GCN"): ([0.0, 1.0, 2.0], [1.0, 1.0, 1.0])
        }
        sums = {
            (("red_ms200_dm1", "GCN"), 0): {
                "raw": [1.0, 1.0],
                "nest": [1.0, 1.0],
                "ws_roi": [0.9, 0.9],
                "n": [2, 2],
            },
            (("red_ms200_dm1", "GCN"), 1): {
                "raw": [1.0, 1.0],
                "nest": [1.0, 1.0],
                "ws_roi": [0.7, 0.7],
                "n": [2, 2],
            },
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
        self.assertAlmostEqual(bins[0]["ws_roi_accepted_rate_events_kg_day"], 0.9)
        self.assertAlmostEqual(bins[1]["ws_roi_accepted_rate_events_kg_day"], 0.7)
        self.assertAlmostEqual(bins[0]["figs2_ss_da_given_trigger_plus_s1"], 0.85)
        self.assertAlmostEqual(bins[0]["figs2_roi_given_ss_da"], 0.65 / 0.85)
        self.assertAlmostEqual(
            bins[0]["energy_resolved_factorized_rate_events_kg_day"], 0.765
        )
        self.assertAlmostEqual(
            summary[0]["global_factorized_vs_figs2_final_relative_difference"],
            0.06666666666666665,
        )
        self.assertAlmostEqual(
            summary[0]["energy_resolved_factorized_vs_figs2_final_relative_difference"],
            0.075,
        )
        self.assertNotAlmostEqual(
            summary[0]["global_factorized_rate_events_kg_day"],
            summary[0]["energy_resolved_factorized_rate_events_kg_day"],
        )

    def test_positive_exact_bin_rate_requires_positive_sampled_spectrum_weight(self):
        spectra = {
            ("red_ms200_dm1", "GCN"): ([0.0, 1.0], [1.0, 1.0])
        }
        sums = {
            (("red_ms200_dm1", "GCN"), 0): {
                "raw": [0.0, 0.0],
                "nest": [0.0, 0.0],
                "ws_roi": [0.0, 0.0],
                "n": [2, 2],
            }
        }
        efficiencies = {
            "trigger_cumulative": [1.0, 1.0],
            "trigger_plus_s1_threshold_cumulative": [1.0, 1.0],
            "trigger_plus_s1_ss_analysis_cumulative": [0.9, 0.9],
            "final_plus_roi_cumulative": [0.8, 0.8],
        }
        with self.assertRaisesRegex(ValueError, "zero sampled response weight"):
            MOD.build_energy_resolved_rows(
                "eft2024", spectra, sums, {0: (0.0, 1.0)}, [0.0, 1.0],
                [0.0, 1.0], efficiencies,
            )

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

    def test_efficiency_reader_rejects_nonmonotonic_energy_knots(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "efficiency.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "ER_keV", *MOD.CURVE_COLUMNS
                ])
                writer.writeheader()
                writer.writerow({
                    "ER_keV": 1.0,
                    "trigger_cumulative": 1.0,
                    "trigger_plus_s1_threshold_cumulative": 0.9,
                    "trigger_plus_s1_ss_analysis_cumulative": 0.8,
                    "final_plus_roi_cumulative": 0.7,
                })
                writer.writerow({
                    "ER_keV": 1.0,
                    "trigger_cumulative": 1.0,
                    "trigger_plus_s1_threshold_cumulative": 0.9,
                    "trigger_plus_s1_ss_analysis_cumulative": 0.8,
                    "final_plus_roi_cumulative": 0.7,
                })
            with self.assertRaisesRegex(ValueError, "strictly increasing"):
                MOD.read_efficiency_curves(path)

    def test_reference_bridge_rejects_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "reference.csv"
            fields = [
                "benchmark", "nuclear_model", "response_family",
                "relative_difference_factorized_vs_figs2",
            ]
            row = {
                "benchmark": "red_ms200_dm1",
                "nuclear_model": "GCN",
                "response_family": "eft2024",
                "relative_difference_factorized_vs_figs2": "0.01",
            }
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow(row)
                writer.writerow(row)
            with self.assertRaisesRegex(ValueError, "duplicate reference-bridge"):
                MOD.read_reference_bridge(path)

    def test_accumulator_matches_two_replica_event_weighting(self):
        fields = [
            "replica", "energy_bin_index", "energy_bin_low_keV",
            "energy_bin_high_keV", "energy_keV", "s1c_abs_phd",
            "s2c_abs_phd", "s2r_abs_phd", "s1_coincidence_pass",
            "s2_threshold_pass",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "response.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                for replica in (0, 1):
                    for event in range(2000):
                        writer.writerow({
                            "replica": replica,
                            "energy_bin_index": 0,
                            "energy_bin_low_keV": 5.4,
                            "energy_bin_high_keV": 6.4,
                            "energy_keV": 5.4 + (event + 0.5) / 2000.0,
                            "s1c_abs_phd": 100.0,
                            "s2c_abs_phd": 1000.0,
                            "s2r_abs_phd": 1000.0,
                            "s1_coincidence_pass": 1 if replica == 0 else 0,
                            "s2_threshold_pass": 1,
                        })
            spectra = {
                ("red_ms200_dm1", "GCN"): ([5.0, 7.0], [2.0, 2.0])
            }
            with (
                patch.object(MOD.grid, "ROI_MIN_KEV", 5.4),
                patch.object(MOD.grid, "ROI_MAX_KEV", 6.4),
            ):
                sums, edges, energy_edges = MOD.accumulate_weighted_response(
                    path, spectra
                )
            bucket = sums[(("red_ms200_dm1", "GCN"), 0)]
            self.assertEqual(bucket["n"], [2000, 2000])
            self.assertEqual(energy_edges, [5.4, 6.4])
            self.assertAlmostEqual(MOD.pooled_acceptance(
                bucket["raw"], bucket["nest"]
            ), 0.5)
            self.assertAlmostEqual(MOD.pooled_acceptance(
                bucket["raw"], bucket["ws_roi"]
            ), 0.5)

    def test_accumulator_rejects_event_outside_declared_energy_bin(self):
        fields = [
            "replica", "energy_bin_index", "energy_bin_low_keV",
            "energy_bin_high_keV", "energy_keV", "s1c_abs_phd",
            "s2c_abs_phd", "s2r_abs_phd", "s1_coincidence_pass",
            "s2_threshold_pass",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "response.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "replica": 0,
                    "energy_bin_index": 0,
                    "energy_bin_low_keV": 5.4,
                    "energy_bin_high_keV": 6.4,
                    "energy_keV": 6.5,
                    "s1c_abs_phd": 100.0,
                    "s2c_abs_phd": 1000.0,
                    "s2r_abs_phd": 1000.0,
                    "s1_coincidence_pass": 1,
                    "s2_threshold_pass": 1,
                })
            with (
                patch.object(MOD.grid, "ROI_MIN_KEV", 5.4),
                patch.object(MOD.grid, "ROI_MAX_KEV", 6.4),
            ):
                with self.assertRaisesRegex(ValueError, "outside its declared bin"):
                    MOD.accumulate_weighted_response(
                        path, {("red_ms200_dm1", "GCN"): ([5.0, 7.0], [1.0, 1.0])}
                    )

    def test_ws_roi_raw_s2_cut_must_nest_nest_s2_threshold(self):
        fields = [
            "replica", "energy_bin_index", "energy_bin_low_keV",
            "energy_bin_high_keV", "energy_keV", "s1c_abs_phd",
            "s2c_abs_phd", "s2r_abs_phd", "s1_coincidence_pass",
            "s2_threshold_pass",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "response.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerow({
                    "replica": 0, "energy_bin_index": 0,
                    "energy_bin_low_keV": 5.4, "energy_bin_high_keV": 6.4,
                    "energy_keV": 5.9, "s1c_abs_phd": 100.0,
                    "s2c_abs_phd": 1000.0, "s2r_abs_phd": 1000.0,
                    "s1_coincidence_pass": 1, "s2_threshold_pass": 0,
                })
            with (
                patch.object(MOD.grid, "ROI_MIN_KEV", 5.4),
                patch.object(MOD.grid, "ROI_MAX_KEV", 6.4),
            ):
                with self.assertRaisesRegex(ValueError, "raw-S2 cut passed but NEST S2 pulse threshold failed"):
                    MOD.accumulate_weighted_response(
                        path, {("red_ms200_dm1", "GCN"): ([5.0, 7.0], [1.0, 1.0])}
                    )

    def test_summary_labels_rate_level_diagnostic_only(self):
        self.assertIn("rate-level diagnostic", MOD.__doc__)


if __name__ == "__main__":
    unittest.main()
