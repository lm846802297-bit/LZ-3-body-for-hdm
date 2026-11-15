import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "audit_lz_2026_s1_mode_roi_migration.py"
SPEC = importlib.util.spec_from_file_location("s1_mode_roi_migration", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

def row(i, pp, fp, ps, fs):
    return {
        "event": float(i), "energy_bin_index": 0.0,
        "energy_bin_low_keV": 5.4, "energy_bin_high_keV": 6.4,
        "energy_keV": 5.8, "x_mm": 0.0, "y_mm": 0.0, "z_mm": 100.0,
        "field_V_cm": 96.5, "drift_time_us": 500.0,
        "n_photons": 100.0, "n_electrons": 50.0,
        "s1_param_signed_phd": ps if pp else -ps, "s1_param_abs_phd": ps,
        "s1_param_spike_count": 5.0, "s1_param_pass": float(pp),
        "s1_full_signed_phd": fs if fp else -fs, "s1_full_abs_phd": fs,
        "s1_full_spike_count": 5.0, "s1_full_pass": float(fp),
    }

class S1ModeROIMigrationTests(unittest.TestCase):
    def test_s1_roi_efficiency_includes_coincidence_and_s1_window_once(self):
        rows = [row(0,1,1,100,110), row(1,1,1,650,550), row(2,0,1,250,300), row(3,1,1,20,20)]
        result = MOD.summarize_bin(0, rows)
        self.assertAlmostEqual(result["parametric_s1_roi_efficiency"], 0.5)
        self.assertAlmostEqual(result["full_s1_roi_efficiency"], 1.0)
        self.assertAlmostEqual(result["full_minus_parametric_s1_roi_pp"], 50.0)
        self.assertEqual(result["n_parametric_only_s1_roi"], 0)
        self.assertEqual(result["n_full_only_s1_roi"], 2)

    def test_histogram_tv_is_zero_for_identical_samples(self):
        values = [2.0, 10.0, 10.1, 23.0, 55.0]
        self.assertEqual(MOD.histogram_tv(values, values), 0.0)

    def test_roi_boundaries_are_inclusive_and_coincidence_is_required(self):
        self.assertTrue(MOD.selected(1, 3.0))
        self.assertTrue(MOD.selected(1, 600.0))
        self.assertFalse(MOD.selected(0, 100.0))
        self.assertFalse(MOD.selected(1, 600.0001))

    def test_zero_discordance_keeps_nonzero_paired_interval(self):
        lo, hi = MOD.base.paired_difference_wilson_interval(0, 0, 10000)
        self.assertLess(lo, 0.0)
        self.assertGreater(hi, 0.0)

if __name__ == "__main__":
    unittest.main()
