from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_afh_phi_response", HERE / "validate_afh_phi_response.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def fixture():
    factor = math.pi  # 4 pi/(2 J+1), with J=3/2
    q_values = (0.0, 0.00025, 0.00050)
    raw = (
        (131.0**2 / 4.0, 25.0, 100.0),
        (3000.0, 20.0, -100.0),
        (1500.0, 10.0, 100.0),
    )
    rows = []
    for q, (rm, rphi, rmphi) in zip(q_values, raw):
        y = (q * 10.0 / 2.0) ** 2
        rows.append({
            "q_GeV": str(q),
            "y": str(y),
            "W_M00_AFH": str(rm / factor),
            "W_PhiPP00_AFH": str(rphi / factor),
            "W_MPhiPP00_AFH": str(rmphi / factor),
            "R_M_raw": str(rm),
            "R_PhiPP_raw": str(rphi),
            "R_MPhiPP_raw": str(rmphi),
            "R_M_physical_equal_pn": str(4.0 * rm),
            "R_PhiPP_physical_equal_pn": str(4.0 * rphi),
            "R_MPhiPP_physical_equal_pn": str(4.0 * rmphi),
            "Im_W_M00": "0.0",
            "Im_W_PhiPP00": "0.0",
            "Im_W_MPhiPP00": "0.0",
        })
    metadata = {
        "status": "COMPLETED",
        "source": "AFH DMFormFactor v6.0 native Wolfram execution",
        "afh_source_sha256": validator.EXPECTED_SOURCE_SHA256,
        "density_matrix_csv_sha256": validator.EXPECTED_MATRIX_SHA256,
        "isotope_A": 131,
        "Z": 54,
        "J_A": 1.5,
        "response_indices": {"M": 1, "PhiPP": 4, "M_PhiPP": 7},
        "isospin": "tau1=tau2=0; raw AFH isoscalar package convention",
        "factor_four_applied_once": True,
        "shape_renormalization_applied": False,
        "q_min_GeV": 0.0,
        "q_max_GeV": 0.0005,
        "dq_GeV": 0.00025,
        "grid_points": 3,
        "b_A_GeV_inverse": 10.0,
    }
    return rows, metadata


class AFHPhiResponseValidationTests(unittest.TestCase):
    def test_valid_response_matrix_and_factor_four(self):
        rows, metadata = fixture()
        result = validator.validate_rows(rows, metadata, require_full_grid=False)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["rows"], 3)
        self.assertLess(result["max_response_factor_residual"], 1e-14)
        self.assertLess(result["max_factor_four_residual"], 1e-14)

    def test_factor_four_must_be_applied_exactly_once(self):
        rows, metadata = fixture()
        rows[1]["R_PhiPP_physical_equal_pn"] = str(
            3.0 * float(rows[1]["R_PhiPP_raw"])
        )
        with self.assertRaisesRegex(ValueError, "factor-four mapping"):
            validator.validate_rows(rows, metadata, require_full_grid=False)

    def test_signed_interference_must_obey_cauchy_schwarz(self):
        rows, metadata = fixture()
        rows[2]["R_MPhiPP_raw"] = "1000.0"
        rows[2]["R_MPhiPP_physical_equal_pn"] = "4000.0"
        rows[2]["W_MPhiPP00_AFH"] = str(1000.0 / math.pi)
        with self.assertRaisesRegex(ValueError, "Cauchy-Schwarz"):
            validator.validate_rows(rows, metadata, require_full_grid=False)

    def test_afh_y_must_use_spatial_qA(self):
        rows, metadata = fixture()
        rows[1]["y"] = "0.5"
        with self.assertRaisesRegex(ValueError, "y="):
            validator.validate_rows(rows, metadata, require_full_grid=False)

    def test_zero_momentum_m_normalization_is_locked(self):
        rows, metadata = fixture()
        rows[0]["R_M_raw"] = "4000.0"
        rows[0]["R_M_physical_equal_pn"] = "16000.0"
        rows[0]["W_M00_AFH"] = str(4000.0 / math.pi)
        with self.assertRaisesRegex(ValueError, "q=0 M normalization"):
            validator.validate_rows(rows, metadata, require_full_grid=False)

    def test_response_index_mapping_is_locked(self):
        rows, metadata = fixture()
        metadata["response_indices"]["PhiPP"] = 5
        with self.assertRaisesRegex(ValueError, "response-index mapping"):
            validator.validate_rows(rows, metadata, require_full_grid=False)


if __name__ == "__main__":
    unittest.main()
