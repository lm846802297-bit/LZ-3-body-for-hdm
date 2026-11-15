import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "audit_lz_2026_paired_s1_upper_tail_all_benchmarks.py"
SPEC = importlib.util.spec_from_file_location("paired_s1_upper_tail_all_benchmarks", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class MultiBenchmarkPairedS1UpperTailTests(unittest.TestCase):
    def rates(self, first_bin):
        return {
            "GCN": {index: (index + 1) * 1e-12 if index >= first_bin else 0.0 for index in range(235)},
            "JJ55": {index: (index + 2) * 1e-12 if index >= first_bin else 0.0 for index in range(235)},
        }

    def test_red_support_and_lower_energy_bands(self):
        support, bands = MOD.build_benchmark_energy_bands(self.rates(0))
        self.assertEqual(support, list(range(235)))
        self.assertEqual(bands["full_support"], (35.0, 269.9))
        self.assertIn("band_35_100", bands)
        self.assertIn("band_100_150", bands)
        self.assertIn("common_support_205_269p9", bands)

    def test_green_and_blue_support_starts_at_100_kev(self):
        support, bands = MOD.build_benchmark_energy_bands(self.rates(65))
        self.assertEqual(support, list(range(65, 235)))
        self.assertEqual(bands["full_support"], (100.0, 269.9))
        self.assertNotIn("band_35_100", bands)
        self.assertIn("band_100_150", bands)

    def test_black_support_starts_at_205_kev(self):
        support, bands = MOD.build_benchmark_energy_bands(self.rates(170))
        self.assertEqual(support, list(range(170, 235)))
        self.assertEqual(bands["full_support"], (205.0, 269.9))
        self.assertEqual(bands["common_support_205_269p9"], (205.0, 269.9))
        self.assertNotIn("band_150_200", bands)

    def test_model_support_mismatch_is_rejected(self):
        rates = self.rates(0)
        rates["JJ55"].pop(234)
        with self.assertRaises(ValueError):
            MOD.build_benchmark_energy_bands(rates)

    def test_noncontiguous_support_is_rejected(self):
        rates = self.rates(0)
        rates["GCN"][100] = 0.0
        rates["JJ55"][100] = 0.0
        with self.assertRaises(ValueError):
            MOD.build_benchmark_energy_bands(rates)

    def test_output_filenames_are_multi_benchmark_specific(self):
        self.assertIn("multi_benchmark", MOD.OUTPUT_FILES["summary"])
        self.assertIn("multi_benchmark", MOD.OUTPUT_FILES["metadata"])


if __name__ == "__main__":
    unittest.main()
