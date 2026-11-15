import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "fold_lz_2026_paired_s1_mode_2d_response.py"
SPEC = importlib.util.spec_from_file_location("paired_s1_mode_2d_response", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

FIELDS = [
    "event", "replica", "energy_bin_index", "energy_bin_low_keV",
    "energy_bin_high_keV", "energy_keV", "s1_param_signed_phd",
    "s1_param_abs_phd", "s1_param_pass", "s1_full_signed_phd",
    "s1_full_abs_phd", "s1_full_pass", "s2_signed_phd", "s2_abs_phd",
    "s2_raw_phd", "s2_threshold_pass",
]

def make_row(event, replica, p_pass, f_pass, p_s1, f_s1, s2_pass=1, s2_raw=1000.0):
    return {
        "event": event, "replica": replica, "energy_bin_index": 0,
        "energy_bin_low_keV": 35.0, "energy_bin_high_keV": 36.0,
        "energy_keV": 35.5,
        "s1_param_signed_phd": p_s1 if p_pass else -p_s1,
        "s1_param_abs_phd": p_s1, "s1_param_pass": p_pass,
        "s1_full_signed_phd": f_s1 if f_pass else -f_s1,
        "s1_full_abs_phd": f_s1, "s1_full_pass": f_pass,
        "s2_signed_phd": 1000.0 if s2_pass else -1000.0,
        "s2_abs_phd": 1000.0, "s2_raw_phd": s2_raw,
        "s2_threshold_pass": s2_pass,
    }

class PairedS1Mode2DResponseTests(unittest.TestCase):
    def test_weighted_efficiency_and_paired_difference(self):
        p, _ = MOD.weighted_efficiency(6.0, 14.0, 4.0, 10.0)
        d, _ = MOD.paired_difference(6.0, 14.0, -1.0, -3.0, 5.0)
        self.assertAlmostEqual(p, 2.0/3.0)
        self.assertAlmostEqual(d, -1.0/6.0)

    def test_total_variation(self):
        self.assertEqual(MOD.total_variation({(1, 2): 1.0}, {(1, 2): 4.0}), 0.0)
        self.assertAlmostEqual(
            MOD.total_variation({(1, 2): 1.0}, {(3, 4): 1.0}), 1.0
        )

    def test_accumulate_and_fold_paired_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.csv"
            rows = [
                make_row(0, 0, 1, 1, 100.0, 100.0),
                make_row(1, 1, 1, 0, 200.0, 300.0),
            ]
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            spectra = {("red_ms200_dm1", "GCN"): ([35.0, 36.0], [1.0, 1.0])}
            with patch.object(MOD.grid, "make_edges", return_value=[35.0, 36.0]):
                stats, maps, edges = MOD.accumulate_events(path, spectra, 2)
            self.assertEqual(edges, {0: (35.0, 36.0)})
            bins, summaries, map_rows = MOD.fold(spectra, stats, maps)
            self.assertEqual(len(bins), 1)
            self.assertEqual(len(summaries), 2)
            ws = next(row for row in summaries if row["stage"] == "ws_roi")
            self.assertAlmostEqual(ws["full_vs_parametric_relative_rate_difference"], -0.5)
            self.assertAlmostEqual(ws["full_vs_parametric_2d_total_variation"], 0.5)
            self.assertGreater(len(map_rows), 0)

    def test_raw_s2_roi_cannot_pass_if_nest_s2_threshold_flag_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.csv"
            row = make_row(0, 0, 1, 1, 100.0, 100.0, s2_pass=0, s2_raw=1000.0)
            row2 = make_row(1, 1, 1, 1, 100.0, 100.0)
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows([row, row2])
            spectra = {("red_ms200_dm1", "GCN"): ([35.0, 36.0], [1.0, 1.0])}
            with patch.object(MOD.grid, "make_edges", return_value=[35.0, 36.0]):
                with self.assertRaisesRegex(ValueError, "raw-S2 ROI passed"):
                    MOD.accumulate_events(path, spectra, 2)

if __name__ == "__main__":
    unittest.main()
