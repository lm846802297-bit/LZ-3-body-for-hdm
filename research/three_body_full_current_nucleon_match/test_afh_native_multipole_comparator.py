import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "afh_response_crosschecks"))

import compare_p3_multipoles_vs_native as comparator


ISOTOPES = (129, 131)
RANKS = {129: (1,), 131: (1, 2, 3)}


def synthetic_rows():
    p3, native = [], []
    for A in ISOTOPES:
        for i in range(2401):
            q = i * 0.00025
            y = q*q*0.5
            for J in RANKS[A]:
                delta = 1e-3 * (A/129.0) * (J+1) * (1.0+q)
                sigma = -2e-3 * (A/129.0) * (J+1) * (1.0+0.5*q)
                p3.append({
                    "A": A, "q_GeV": q, "y": y, "multipole_J": J,
                    "M_Delta_J": delta, "M_SigmaPrime_J": sigma,
                })
                native.append({
                    "A": A, "q_GeV": q, "y": y, "multipole_J": J,
                    "M_Delta_J_native": delta,
                    "M_SigmaPrime_J_native": sigma,
                    "Im_M_Delta_J_native": 0.0,
                    "Im_M_SigmaPrime_J_native": 0.0,
                })
    return p3, native


def synthetic_provenance():
    p3meta = {
        "source_file_sha256": comparator.EXPECTED_AFH_SOURCE_SHA256,
        "rankwise_amplitudes_and_signed_interference_saved": True,
        "multipole_file_sha256": "p3-multipole-sha",
    }
    nmeta = {
        "AFH_source_sha256": comparator.EXPECTED_AFH_SOURCE_SHA256,
        "source_commit": comparator.EXPECTED_NATIVE_SOURCE_COMMIT,
        "rows": "9604",
        "isotopes": "129,131",
        "q_grid": "2401 uniform nodes from 0 to 0.6 GeV, step 0.00025 GeV",
        "normalization": "raw AFH package amplitudes; no equal-p/n factor-four conversion",
        "imaginary_parts": "exported separately for both amplitude channels",
        "max_imaginary_residual": "0",
    }
    manifest = {
        "source_commit": comparator.EXPECTED_NATIVE_SOURCE_COMMIT,
        "comparison": {
            "status": "PASS", "native_afh_validated": True,
            "rows_compared": 16807,
        },
        "native_spatial_multipoles": {
            "rows": 9604, "csv_sha256": "native-csv-sha",
            "metadata_sha256": "native-meta-sha",
        },
    }
    return p3meta, nmeta, manifest


class NativeAFHMultipoleComparatorTests(unittest.TestCase):
    def test_identical_native_and_python_multipoles_pass(self):
        p3, native = synthetic_rows()
        p3meta, nmeta, manifest = synthetic_provenance()
        result = comparator.compare_rows(p3, native, p3meta, nmeta, manifest)
        self.assertEqual(result["status"], "PASS_NATIVE_AFH_MULTIPOLE_AMPLITUDE_CROSSCHECK")
        self.assertEqual(result["rows_compared"], 9604)
        self.assertTrue(result["native_afh_multipole_amplitudes_validated"])
        self.assertEqual(result["amplitude_comparisons"]["Delta"]["failed_points"], 0)
        self.assertEqual(result["amplitude_comparisons"]["SigmaPrime"]["failed_points"], 0)

    def test_signed_amplitude_mismatch_is_detected(self):
        p3, native = synthetic_rows()
        native[0]["M_SigmaPrime_J_native"] *= -1.0
        p3meta, nmeta, manifest = synthetic_provenance()
        result = comparator.compare_rows(p3, native, p3meta, nmeta, manifest)
        self.assertEqual(result["status"], "FAIL")
        self.assertGreater(result["amplitude_comparisons"]["SigmaPrime"]["failed_points"], 0)

    def test_native_imaginary_residual_is_rejected(self):
        p3, native = synthetic_rows()
        native[0]["Im_M_Delta_J_native"] = 3e-12
        p3meta, nmeta, manifest = synthetic_provenance()
        with self.assertRaises(ValueError):
            comparator.compare_rows(p3, native, p3meta, nmeta, manifest)

    def test_native_source_commit_mismatch_is_rejected(self):
        p3, native = synthetic_rows()
        p3meta, nmeta, manifest = synthetic_provenance()
        nmeta["source_commit"] = "wrong"
        with self.assertRaises(ValueError):
            comparator.compare_rows(p3, native, p3meta, nmeta, manifest)


if __name__ == "__main__":
    unittest.main()
