import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from validate_afh_spatial_multipoles_native import (  # noqa: E402
    EXPECTED_PER_ISOTOPE,
    Q_MIN,
    Q_STEP,
    RANKS,
    _expected_y,
    validate_records,
)


def make_rows():
    rows = []
    for A, ranks in RANKS.items():
        for i in range(EXPECTED_PER_ISOTOPE):
            q = Q_MIN + i * Q_STEP
            for J in ranks:
                rows.append({
                    "A": A,
                    "q_GeV": repr(q),
                    "y": repr(_expected_y(A, q)),
                    "multipole_J": J,
                    "M_Delta_J_native": "1.0",
                    "M_SigmaPrime_J_native": "2.0",
                    "Im_M_Delta_J_native": "0.0",
                    "Im_M_SigmaPrime_J_native": "0.0",
                })
    return rows


class SpatialMultipoleValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = make_rows()

    def test_full_grid_and_rank_set_pass(self):
        result = validate_records(self.rows)
        self.assertEqual(result["status"], "PASS_NATIVE_AFH_SPATIAL_MULTIPOLES")
        self.assertEqual(result["rows"], 9604)
        self.assertEqual(result["isotope_summaries"]["129"]["ranks"], [1])
        self.assertEqual(result["isotope_summaries"]["131"]["ranks"], [1, 2, 3])

    def test_imaginary_residual_above_tolerance_fails(self):
        bad = [dict(row) for row in self.rows]
        bad[0]["Im_M_Delta_J_native"] = "3e-12"
        result = validate_records(bad)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("imaginary residual" in f for f in result["failures"]))

    def test_missing_rank_fails(self):
        bad = [row for row in self.rows if not (row["A"] == 131 and row["multipole_J"] == 3)]
        result = validate_records(bad)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Xe-131" in f for f in result["failures"]))

    def test_metadata_q0_limit_is_documented(self):
        meta = {
            "rows": 9604,
            "isotopes": "129,131",
            "q_grid": "2401 uniform nodes from 0 to 0.6 GeV; q=0 value is the analytic y=0 limit",
            "max_imaginary_residual": 0.0,
        }
        result = validate_records(self.rows, metadata=meta)
        self.assertEqual(result["status"], "PASS_NATIVE_AFH_SPATIAL_MULTIPOLES")


if __name__ == "__main__":
    unittest.main()
