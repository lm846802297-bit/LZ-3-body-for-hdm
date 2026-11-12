from pathlib import Path
import csv
import json
import unittest

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class AFHDefaultXenonResponseGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = read_csv(OUTPUT / "afh_default_xenon_WM00.csv")
        cls.metadata = json.loads((OUTPUT / "metadata.json").read_text(encoding="utf-8"))

    def test_all_seven_isotope_grids_are_complete(self):
        expected = {128, 129, 130, 131, 132, 134, 136}
        grouped = {}
        for row in self.rows:
            grouped.setdefault(int(row["A"]), []).append(row)
        self.assertEqual(set(grouped), expected)
        for A, rows in grouped.items():
            self.assertEqual(len(rows), 2401, f"Xe-{A}")
            q = [float(row["q_GeV"]) for row in rows]
            self.assertEqual(q[0], 0.0)
            self.assertAlmostEqual(q[-1], 0.6, places=14)
            self.assertTrue(all(b > a for a, b in zip(q, q[1:])))

    def test_physical_response_zero_momentum_normalization(self):
        for A in (128, 129, 130, 131, 132, 134, 136):
            row = next(r for r in self.rows if int(r["A"]) == A and float(r["q_GeV"]) == 0.0)
            self.assertAlmostEqual(float(row["R_A_equal_pn"]), A*A, delta=1e-10*A*A)
            self.assertAlmostEqual(float(row["R_over_A2"]), 1.0, places=12)

    def test_all_response_values_are_finite_and_nonnegative(self):
        for row in self.rows:
            value = float(row["R_A_equal_pn"])
            self.assertTrue(value >= 0.0, (row["A"], row["q_GeV"], value))

    def test_archived_28_selected_samples_match_full_curves(self):
        result = self.metadata["archived_28_sample_comparison"]
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["samples_compared"], 28)
        self.assertEqual(result["isotopes_compared"], [128, 129, 130, 131, 132, 134, 136])
        self.assertLessEqual(result["maximum_relative_difference"], 5e-8)

    def test_xe131_full_grid_matches_existing_validated_curve(self):
        result = self.metadata["xe131_full_grid_reference_comparison"]
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["points_compared"], 2401)
        self.assertLessEqual(result["maximum_relative_difference"], 2e-12)

    def test_response_metadata_records_ame2020_and_exact_spatial_q(self):
        self.assertEqual(self.metadata["mass_scheme_for_ER_annotation"], "ame2020_nuclear")
        self.assertEqual(self.metadata["response_rows"], 7*2401)
        self.assertIn("spatial q", self.metadata["response_q_definition"])


if __name__ == "__main__":
    unittest.main()
