import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import contract_three_body_afh_responses as contract


ISOTOPES = (128, 129, 130, 131, 132, 134, 136)


def synthetic_afh_rows(*, violate_cauchy=False):
    rows = []
    for A in ISOTOPES:
        for q in (0.0, 0.6):
            delta = 0.1
            sigma = 0.2
            cross = 0.1 if violate_cauchy else -0.1
            if violate_cauchy:
                cross = 0.3
            row = {
                "A": A,
                "J_A": 0.0 if A % 2 == 0 else 0.5,
                "q_GeV": q,
                "R_M_physical_equal_pn": 100.0,
                "R_PhiPP_physical_equal_pn": 1.0,
                "R_MPhiPP_physical_equal_pn": 0.5,
                "R_Delta_physical_equal_pn": delta,
                "R_SigmaPrime_physical_equal_pn": sigma,
                "R_SigmaPrimeDelta_physical_equal_pn": cross,
            }
            rows.append(row)
    return rows


def synthetic_weights():
    return {
        "status": "PASS_AFH_LEPTONIC_COEFFICIENT_EXTRACTION",
        "form_factor_input": {
            "status": "constant provisional q=0 anchors; finite-t dependence not included"
        },
        "benchmarks": [{
            "benchmark": "test",
            "width_scheme": "pole",
            "g2": 1.0,
            "ER_keV": 200.0,
            "speed_kms": 776.0,
            "afh_vector_coefficients": {
                "qA_GeV": 0.3,
                "C_M": 100.0,
                "C_PhiPP": 1.0,
                "C_MPhiPP": 2.0,
                "C_Delta": 0.2,
                "C_SigmaPrime": 0.1,
                "C_SigmaPrimeDelta": -0.2,
            },
        }],
    }


def synthetic_metadata():
    return {
        "status": "PROVISIONAL_PYTHON",
        "native_afh_validated": False,
        "source": "synthetic test data",
        "afh_source_commit": "test",
        "csv_sha256": "test",
        "natural_atom_fraction_coverage": 0.998158,
        "normalization": {
            "factor_four_applied_once_to_physical_columns": True
        },
    }


class ThreeBodyAFHContractionTests(unittest.TestCase):
    def test_seven_isotope_fixed_point_contraction_is_positive_and_provisional(self):
        result = contract.contract_archive(
            synthetic_afh_rows(),
            synthetic_weights(),
            synthetic_metadata(),
            expected_points=2,
        )
        self.assertEqual(result["status"], "PROVISIONAL_AFH_CONTRACTION_PASS")
        self.assertEqual(result["summary"]["contracted_rows"], 7)
        self.assertEqual(result["summary"]["positive_total_kernel_rows"], 7)
        self.assertFalse(result["afh_source"]["native_afh_validated"])
        self.assertEqual(result["benchmarks"][0]["A"], 128)
        self.assertAlmostEqual(
            result["benchmarks"][0]["spatial_sector"],
            0.2 * 0.1 + 0.1 * 0.2 + (-0.2) * (-0.1),
        )

    def test_interpolation_uses_qA_and_preserves_signed_interference(self):
        rows = synthetic_afh_rows()
        rows = [dict(row) for row in rows]
        for row in rows:
            if float(row["q_GeV"]) == 0.6:
                row["R_SigmaPrimeDelta_physical_equal_pn"] = -0.3
        result = contract.contract_archive(
            rows, synthetic_weights(), synthetic_metadata(), expected_points=2
        )
        first = result["benchmarks"][0]
        self.assertAlmostEqual(
            first["responses_physical_equal_pn"]["SigmaPrimeDelta"], -0.2
        )
        self.assertLess(first["coefficient_response_terms"]["SigmaPrimeDelta"], 0.0)

    def test_cauchy_violation_is_rejected(self):
        result = contract.contract_archive(
            synthetic_afh_rows(violate_cauchy=True),
            synthetic_weights(),
            synthetic_metadata(),
            expected_points=2,
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Cauchy" in item for item in result["summary"]["failures"]))

    def test_missing_physical_response_column_is_rejected(self):
        rows = synthetic_afh_rows()
        del rows[0]["R_SigmaPrimeDelta_physical_equal_pn"]
        with self.assertRaises(ValueError):
            contract.index_afh_rows(rows, expected_points=2)

    def test_incomplete_isotope_set_is_rejected(self):
        rows = [row for row in synthetic_afh_rows() if int(row["A"]) != 136]
        with self.assertRaises(ValueError):
            contract.index_afh_rows(rows, expected_points=2)


if __name__ == "__main__":
    unittest.main()
