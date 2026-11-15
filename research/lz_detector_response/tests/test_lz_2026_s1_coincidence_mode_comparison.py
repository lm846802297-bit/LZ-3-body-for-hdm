from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "summarize_lz_2026_s1_coincidence_mode_comparison.py"
SPEC = importlib.util.spec_from_file_location("s1_mode_compare", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def event_row(event, param_pass, full_pass, param_s1, full_s1):
    return {
        "event": event,
        "energy_bin_index": 0,
        "energy_bin_low_keV": 5.4,
        "energy_bin_high_keV": 6.4,
        "energy_keV": 5.5 + 0.1 * event,
        "x_mm": 1.0,
        "y_mm": 2.0,
        "z_mm": 3.0,
        "field_V_cm": 96.5,
        "drift_time_us": 500.0,
        "n_photons": 100 + event,
        "n_electrons": 50 + event,
        "s1_param_signed_phd": param_s1 if param_pass else -param_s1,
        "s1_param_abs_phd": param_s1,
        "s1_param_spike_count": 5,
        "s1_param_pass": int(param_pass),
        "s1_full_signed_phd": full_s1 if full_pass else -full_s1,
        "s1_full_abs_phd": full_s1,
        "s1_full_spike_count": 5,
        "s1_full_pass": int(full_pass),
    }


class S1CoincidenceModeComparisonTests(unittest.TestCase):
    def test_paired_difference_and_discordant_counts(self):
        rows = [
            event_row(0, True, True, 10.0, 11.0),
            event_row(1, True, False, 20.0, 0.0),
            event_row(2, False, True, 0.0, 30.0),
            event_row(3, False, False, 0.0, 0.0),
        ]
        result = MOD.summarize_bin(0, rows)
        self.assertEqual(result["n_generated"], 4)
        self.assertEqual(result["n_parametric_pass"], 2)
        self.assertEqual(result["n_full_pass"], 2)
        self.assertEqual(result["n_both_pass"], 1)
        self.assertEqual(result["n_parametric_only_pass"], 1)
        self.assertEqual(result["n_full_only_pass"], 1)
        self.assertEqual(result["n_both_fail"], 1)
        self.assertEqual(result["full_minus_parametric_efficiency"], 0.0)
        self.assertAlmostEqual(result["paired_discordance_fraction"], 0.5)
        self.assertAlmostEqual(result["paired_difference_standard_error"], (0.5 / 4) ** 0.5)
        self.assertAlmostEqual(result["parametric_s1c_mean_phd"], 15.0)
        self.assertAlmostEqual(result["full_s1c_mean_phd"], 20.5)

    def test_sign_and_pass_flag_must_agree(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.csv"
            row = event_row(0, True, True, 10.0, 11.0)
            row["s1_param_signed_phd"] = -10.0
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(row))
                writer.writeheader()
                writer.writerow(row)
            with self.assertRaises(ValueError):
                MOD.read_events(path)

    def test_wilson_interval_is_bounded(self):
        low, high = MOD.wilson_interval(0, 100)
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)
        self.assertLess(low, high)


if __name__ == "__main__":
    unittest.main()
