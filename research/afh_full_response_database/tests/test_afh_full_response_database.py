import csv
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import run_afh_full_response_database as db
from validate_afh_full_response_database import validate_records
from compare_native_afh_full_response import compare_records


class AFHFullResponseDatabaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrices = {A: db.base.load_matrix(A) for A in db.ISOTOPES}

    def test_all_seven_default_density_matrices_are_available(self):
        self.assertEqual(tuple(self.matrices), db.ISOTOPES)
        self.assertEqual(len(self.matrices[129]), 39)
        self.assertEqual(len(self.matrices[131]), 67)
        self.assertTrue(all(len(rows) > 0 for rows in self.matrices.values()))

    def test_response_index_map_contains_all_eight_afh_channels(self):
        self.assertEqual(
            list(db.RESPONSE_COLUMNS.values()),
            [
                "W_M00_AFH",
                "W_SigmaDoublePrime00_AFH",
                "W_SigmaPrime00_AFH",
                "W_PhiPP00_AFH",
                "W_PhiTildePrime00_AFH",
                "W_Delta00_AFH",
                "W_MPhiPP00_AFH",
                "W_SigmaPrimeDelta00_AFH",
            ],
        )

    def test_new_operator_elements_are_finite(self):
        for A in (129, 131):
            for q in (0.0, 0.158, 0.25625):
                rows = self.matrices[A]
                amps, _, _, _ = db.multipole_amplitudes(A, q, rows)
                for family in ("SigmaDoublePrime", "PhiTildePrime"):
                    self.assertTrue(
                        all(math.isfinite(v) for v in amps[family].values()),
                        msg=f"Xe-{A}, q={q}, {family}",
                    )

    def test_all_eight_responses_are_finite_and_obey_matrix_bounds(self):
        for A in db.ISOTOPES:
            record = db.response_bundle(A, 0.158, self.matrices[A])
            for column in db.RESPONSE_COLUMNS.values():
                self.assertTrue(math.isfinite(record[column]), (A, column))
            for name in db.DIAGONAL_FAMILIES:
                self.assertGreaterEqual(record[db.RESPONSE_COLUMNS[name]], -2e-12)
            self.assertLessEqual(
                record["W_MPhiPP00_AFH"] ** 2,
                record["W_M00_AFH"] * record["W_PhiPP00_AFH"] + 1e-9,
            )
            self.assertLessEqual(
                record["W_SigmaPrimeDelta00_AFH"] ** 2,
                record["W_SigmaPrime00_AFH"] * record["W_Delta00_AFH"] + 1e-9,
            )

    def test_q0_m_normalization_for_all_seven_isotopes(self):
        for A in db.ISOTOPES:
            record = db.response_bundle(A, 0.0, self.matrices[A])
            relative = abs(record["R_M_raw"] - A * A / 4.0) / (A * A / 4.0)
            self.assertLess(relative, 3e-4, f"Xe-{A}: {relative}")

    def test_factor_four_is_applied_only_in_physical_columns(self):
        record = db.response_bundle(131, 0.158, self.matrices[131])
        for name in db.RESPONSE_COLUMNS:
            self.assertAlmostEqual(
                record[f"R_{name}_physical_equal_pn"],
                4.0 * record[f"R_{name}_raw"],
                delta=1e-11 * max(1.0, abs(record[f"R_{name}_raw"])),
            )

    def test_m_phi_native_xe131_anchors_are_preserved(self):
        native_path = (
            HERE.parent / "afh_default_density_xe131" / "output"
            / "phi_response_native" / "afh_default_xe131_M_PhiPP_native.csv"
        )
        with native_path.open(newline="", encoding="utf-8") as stream:
            native = {
                round(float(row["q_GeV"]), 8): row
                for row in csv.DictReader(stream)
            }
        rows = self.matrices[131]
        for q in (0.0, 0.05, 0.158, 0.25625, 0.365, 0.60):
            result = db.response_bundle(131, q, rows)
            reference = native[round(q, 8)]
            for column in ("W_M00_AFH", "W_PhiPP00_AFH", "W_MPhiPP00_AFH"):
                self.assertTrue(
                    math.isclose(
                        result[column],
                        float(reference[column]),
                        rel_tol=5e-9,
                        abs_tol=2e-13,
                    ),
                    msg=f"q={q}, {column}: {result[column]} vs {reference[column]}",
                )

    def test_validator_accepts_consistent_normalized_seven_isotope_grid(self):
        records = []
        for A in db.ISOTOPES:
            conversion = 4.0 * math.pi / (2.0 * db.J_BY_A[A] + 1.0)
            for q in (0.0, 0.00025):
                row = {
                    "A": A, "J_A": db.J_BY_A[A], "q_GeV": q,
                    "y": q * q, "b_A_fm": 2.3, "b_A_GeV_inverse": 11.65,
                }
                for name, column in db.RESPONSE_COLUMNS.items():
                    w = 1.0
                    if name == "M":
                        w = (A * A / 4.0) / conversion
                    elif name in ("MPhiPP", "SigmaPrimeDelta"):
                        w = 0.1
                    row[column] = w
                    row[f"R_{name}_raw"] = conversion * w
                    row[f"R_{name}_physical_equal_pn"] = 4.0 * conversion * w
                records.append(row)
        result = validate_records(
            records, expected_points=2, q_min=0.0, q_max=0.00025
        )
        self.assertEqual(result["status"], "PASS", result["failures"])
        self.assertFalse(result["native_afh_validated"])

    def test_validator_rejects_cauchy_schwarz_violation(self):
        records = []
        for A in db.ISOTOPES:
            conversion = 4.0 * math.pi / (2.0 * db.J_BY_A[A] + 1.0)
            for q in (0.0, 0.00025):
                row = {
                    "A": A, "J_A": db.J_BY_A[A], "q_GeV": q,
                    "y": q * q, "b_A_fm": 2.3, "b_A_GeV_inverse": 11.65,
                }
                for name, column in db.RESPONSE_COLUMNS.items():
                    w = 1.0
                    if name == "M":
                        w = (A * A / 4.0) / conversion
                    elif name == "MPhiPP":
                        w = 0.1
                    elif name == "SigmaPrimeDelta":
                        w = 2.0
                    row[column] = w
                    row[f"R_{name}_raw"] = conversion * w
                    row[f"R_{name}_physical_equal_pn"] = 4.0 * conversion * w
                records.append(row)
        result = validate_records(
            records, expected_points=2, q_min=0.0, q_max=0.00025
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Cauchy-Schwarz" in item for item in result["failures"]))

    def test_native_comparator_rejects_missing_response_rows(self):
        row = {
            "A": 128, "q_GeV": 0.0, "y": 0.0,
            **{column: 0.0 for column in db.RESPONSE_COLUMNS.values()},
            **{f"Im_{column}": 0.0 for column in db.RESPONSE_COLUMNS.values()},
        }
        result = compare_records(
            [row], [row], expected_isotopes=(128,), expected_points=2
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertFalse(result["native_afh_validated"])


if __name__ == "__main__":
    unittest.main()
