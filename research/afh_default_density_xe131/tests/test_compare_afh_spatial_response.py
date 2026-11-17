import unittest

from research.afh_default_density_xe131.compare_afh_spatial_response import compare_records


def row(A, q, wm=10.0, sigma=4.0, delta=9.0, mix=6.0):
    return {
        "A": A,
        "q_GeV": q,
        "W_M00_AFH": wm,
        "W_SigmaPrime00_AFH": sigma,
        "W_Delta00_AFH_literal": delta,
        "W_SigmaPrimeDelta00_AFH_literal": mix,
        "W_Delta00_AFH": delta,
        "W_SigmaPrimeDelta00_AFH": mix,
    }


class AFHSpatialNativeComparatorTests(unittest.TestCase):
    def test_exact_two_isotope_comparison_passes(self):
        py = [row(129, 0.0), row(131, 0.05)]
        native = [row(129, 0.0), row(131, 0.05)]
        result = compare_records(py, native)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["rows"], 2)
        self.assertEqual(result["isotopes"], [129, 131])

    def test_response_mismatch_fails(self):
        py = [row(131, 0.1)]
        native = [row(131, 0.1, delta=8.0)]
        result = compare_records(py, native)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Delta mismatch" in item for item in result["failures"]))

    def test_interference_cauchy_schwarz_is_enforced(self):
        py = [row(131, 0.1, mix=7.0)]
        native = [row(131, 0.1, mix=7.0)]
        result = compare_records(py, native)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("Cauchy-Schwarz" in item for item in result["failures"]))

    def test_q_grid_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "q-grid mismatch"):
            compare_records([row(131, 0.1)], [row(131, 0.2)])

    def test_duplicate_rows_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            compare_records([row(131, 0.1), row(131, 0.1)], [row(131, 0.1)])


if __name__ == "__main__":
    unittest.main()
