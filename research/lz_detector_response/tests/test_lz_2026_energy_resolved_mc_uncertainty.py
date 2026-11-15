import csv
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_energy_resolved_mc_uncertainty.py"
)
SPEC = importlib.util.spec_from_file_location("energy_resolved_mc_uncertainty", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EnergyResolvedMCUncertaintyTests(unittest.TestCase):
    def test_weighted_efficiency_and_mc_error(self):
        p, se = MOD.weighted_efficiency(4.0, 10.0, 1.0, 1.0)
        self.assertAlmostEqual(p, 0.25)
        self.assertAlmostEqual(se, math.sqrt(1.125 / 16.0))

    def test_weighted_efficiency_equal_weight_binomial_limit(self):
        p, se = MOD.weighted_efficiency(2.0, 2.0, 1.0, 1.0)
        self.assertAlmostEqual(p, 0.5)
        self.assertAlmostEqual(se, math.sqrt(0.125))

    def test_effective_sample_size(self):
        self.assertAlmostEqual(MOD.effective_sample_size(4.0, 10.0), 1.6)
        self.assertEqual(MOD.effective_sample_size(0.0, 0.0), 0.0)

    def test_black_high_energy_bands_aggregate_rates_before_efficiencies(self):
        rows = {}
        for family in MOD.RESPONSE_FAMILIES:
            for nuclear in MOD.NUCLEAR_MODELS:
                for ibin, (_, low, high) in enumerate(MOD.BLACK_HIGH_ENERGY_BANDS_KEV):
                    rows[(family, "black_ms360_dm1", nuclear, ibin)] = {
                        "energy_low_keV": str(low),
                        "energy_high_keV": str(high),
                        "exact_raw_rate_events_kg_day": "10",
                        "nest_accepted_rate_events_kg_day": "10",
                        "ws_roi_accepted_rate_events_kg_day": "9",
                        "figs2_trigger_plus_s1_rate_events_kg_day": "10",
                        "figs2_trigger_plus_s1_ss_da_rate_events_kg_day": "8",
                        "figs2_final_plus_roi_rate_events_kg_day": "7",
                        "energy_resolved_factorized_rate_events_kg_day": "7.2",
                    }
        result = MOD.summarize_black_high_energy_bands(rows)
        self.assertEqual(len(result), 16)
        row = result[0]
        self.assertAlmostEqual(row["ws_roi_given_nest"], 0.9)
        self.assertAlmostEqual(row["figs2_ss_da_given_trigger_plus_s1"], 0.8)
        self.assertAlmostEqual(row["figs2_roi_given_ss_da"], 0.875)
        self.assertAlmostEqual(row["factorized_vs_figs2_final_relative_difference"], 7.2 / 7.0 - 1.0)
        self.assertAlmostEqual(row["figs2_final_fraction_of_black_total"], 0.25)

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
            spectra = {("red_ms200_dm1", "GCN"): ([5.4, 6.4], [1.0, 1.0])}
            with (
                patch.object(MOD.grid, "ROI_MIN_KEV", 5.4),
                patch.object(MOD.grid, "ROI_MAX_KEV", 6.4),
                patch.object(MOD, "EXPECTED_EVENTS_PER_REPLICA", 1),
            ):
                with self.assertRaisesRegex(ValueError, "raw-S2 cut passed but NEST S2 pulse threshold failed"):
                    MOD.accumulate_response(path, spectra)

    def test_weighted_efficiency_rejects_invalid_subset(self):
        with self.assertRaisesRegex(ValueError, "accepted weight exceeds"):
            MOD.weighted_efficiency(1.0, 1.0, 1.1, 1.0)
        with self.assertRaisesRegex(ValueError, "finite and non-negative"):
            MOD.weighted_efficiency(1.0, math.nan, 0.5, 0.5)

    def test_accumulator_and_bridge_diagnostic(self):
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
                    "s1_coincidence_pass": 1, "s2_threshold_pass": 1,
                })
                writer.writerow({
                    "replica": 1, "energy_bin_index": 0,
                    "energy_bin_low_keV": 5.4, "energy_bin_high_keV": 6.4,
                    "energy_keV": 5.9, "s1c_abs_phd": 100.0,
                    "s2c_abs_phd": 1000.0, "s2r_abs_phd": 1000.0,
                    "s1_coincidence_pass": 0, "s2_threshold_pass": 1,
                })
            spectra = {
                ("red_ms200_dm1", "GCN"): ([5.4, 6.4], [1.0, 1.0])
            }
            with (
                patch.object(MOD.grid, "ROI_MIN_KEV", 5.4),
                patch.object(MOD.grid, "ROI_MAX_KEV", 6.4),
                patch.object(MOD, "EXPECTED_EVENTS_PER_REPLICA", 1),
            ):
                stats = MOD.accumulate_response(path, spectra)
                bridge = {
                    ("eft2024", "red_ms200_dm1", "GCN", 0): {
                        "exact_raw_rate_events_kg_day": "2.0",
                        "figs2_ss_da_given_trigger_plus_s1": "0.8",
                        "figs2_final_plus_roi_rate_events_kg_day": "0.7",
                        "energy_resolved_factorized_rate_events_kg_day": "0.8",
                        "energy_low_keV": "5.4",
                        "energy_high_keV": "6.4",
                    }
                }
                bins, summaries = MOD.build_diagnostics(
                    "eft2024", spectra, stats, bridge
                )
            self.assertEqual(len(bins), 1)
            self.assertAlmostEqual(bins[0]["ws_roi_acceptance_pooled"], 0.5)
            self.assertAlmostEqual(bins[0]["ws_roi_acceptance_mc_se"], math.sqrt(0.125))
            self.assertAlmostEqual(bins[0]["factorized_rate_mc_se_events_kg_day"], 2.0 * 0.8 * math.sqrt(0.125))
            self.assertEqual(len(summaries), 1)
            self.assertAlmostEqual(summaries[0]["factorized_vs_figs2_final_relative_difference"], 0.1 / 0.7)


if __name__ == "__main__":
    unittest.main()
