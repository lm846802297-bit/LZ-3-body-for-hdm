import csv
import importlib.util
import math
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "fold_lz_2026_three_body_2d_response.py"
SPEC = importlib.util.spec_from_file_location("fold_response", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ThreeBodyResponseFoldTests(unittest.TestCase):
    def test_integrate_linear_constant(self):
        self.assertAlmostEqual(MOD.integrate_linear([0.0, 10.0], [2.0, 2.0], 2.0, 8.0), 12.0)

    def test_integrate_linear_ramp(self):
        # Integral of y=x from 2 to 8 is (8^2-2^2)/2 = 30.
        self.assertAlmostEqual(MOD.integrate_linear([0.0, 10.0], [0.0, 10.0], 2.0, 8.0), 30.0)

    def test_response_keeps_positive_probability_unrenormalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "events.csv"
            with p.open("w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["energy_keV", "s1c_signed_phd", "s2c_signed_phd"])
                w.writerow([6.0, 15.0, 1000.0])
                w.writerow([7.0, 0.0, 1000.0])
                w.writerow([8.0, 25.0, 0.0])
                w.writerow([9.0, 35.0, 10000.0])
            obj = MOD.read_response(p)
            b = obj["energy_bins"][0.0]
            self.assertEqual(b["n_generated"], 4)
            self.assertEqual(b["n_valid_positive"], 2)
            self.assertAlmostEqual(b["positive_fraction"], 0.5)
            total_cell_probability = sum(b["cells"].values()) / b["n_generated"]
            self.assertAlmostEqual(total_cell_probability, 0.5)

    def test_roi_edges_are_integrated_as_partial_bins(self):
        xs = [0.0, 10.0, 20.0]
        ys = [1.0, 1.0, 1.0]
        self.assertAlmostEqual(MOD.integrate_linear(xs, ys, 5.4, 19.9), 14.5)


if __name__ == "__main__":
    unittest.main()
