import importlib.util
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "compare_p3_spatial_multipoles_native.py"
SPEC = importlib.util.spec_from_file_location("p3_native_compare", SCRIPT)
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def make_pair(q=0.125, J=1):
    A, J_A, c0 = 129, 0.5, 1.0001103230777202
    amp_d, amp_s = 0.42, -0.17
    w_d, w_s, w_x = 0.25*amp_d**2, 0.25*amp_s**2, 0.25*amp_s*amp_d
    factor = 4.0*c0*4.0*math.pi/(2.0*J_A+1.0)
    p3 = {
        "A": A, "q_GeV": q, "multipole_J": J, "J_A": J_A,
        "M_Delta_J": amp_d, "M_SigmaPrime_J": amp_s,
        "W_Delta_J_AFH_package": w_d,
        "W_SigmaPrime_J_AFH_package": w_s,
        "W_SigmaPrimeDelta_J_AFH_package": w_x,
        "R_Delta_J_equal_pn": factor*w_d,
        "R_SigmaPrime_J_equal_pn": factor*w_s,
        "R_SigmaPrimeDelta_J_equal_pn": factor*w_x,
    }
    native = {
        "A": A, "q_GeV": q, "multipole_J": J, "y": 0.1,
        "M_Delta_J_native": amp_d, "M_SigmaPrime_J_native": amp_s,
        "Im_M_Delta_J_native": 0.0, "Im_M_SigmaPrime_J_native": 0.0,
    }
    return p3, native, c0


class NativeSpatialMultipoleComparisonTests(unittest.TestCase):
    def test_exact_native_amplitudes_and_signed_bilinears_pass(self):
        p3, native, c0 = make_pair()
        result = compare.compare_rankwise_multipole_rows(
            [p3], [native], {129: c0}
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["rows_compared"], 1)
        self.assertEqual(result["max_native_imaginary_residual"], 0.0)
        self.assertEqual(result["comparisons"]["W_SigmaPrimeDelta_J_AFH_package"]["failed"], 0)

    def test_sigma_prime_phase_flip_is_rejected(self):
        p3, native, c0 = make_pair()
        native["M_SigmaPrime_J_native"] *= -1.0
        result = compare.compare_rankwise_multipole_rows(
            [p3], [native], {129: c0}
        )
        self.assertFalse(result["passed"])
        self.assertGreater(
            result["comparisons"]["M_SigmaPrime_J"]["failed"], 0
        )
        self.assertGreater(
            result["comparisons"]["W_SigmaPrimeDelta_J_AFH_package"]["failed"], 0
        )

    def test_delta_phase_flip_is_rejected(self):
        p3, native, c0 = make_pair()
        native["M_Delta_J_native"] *= -1.0
        result = compare.compare_rankwise_multipole_rows(
            [p3], [native], {129: c0}
        )
        self.assertFalse(result["passed"])
        self.assertGreater(
            result["comparisons"]["W_SigmaPrimeDelta_J_AFH_package"]["failed"], 0
        )

    def test_native_imaginary_residual_above_tolerance_is_rejected(self):
        p3, native, c0 = make_pair()
        native["Im_M_Delta_J_native"] = 3.0e-12
        with self.assertRaises(ValueError):
            compare.compare_rankwise_multipole_rows([p3], [native], {129: c0})

    def test_missing_rank_row_is_rejected(self):
        p3, native, c0 = make_pair()
        with self.assertRaises(ValueError):
            compare.compare_rankwise_multipole_rows([p3], [], {129: c0})

    def test_c0_is_applied_once_to_physical_rank_responses(self):
        p3, native, c0 = make_pair()
        p3["R_Delta_J_equal_pn"] *= c0
        result = compare.compare_rankwise_multipole_rows(
            [p3], [native], {129: c0}
        )
        self.assertFalse(result["passed"])
        self.assertGreater(
            result["comparisons"]["R_Delta_J_equal_pn"]["failed"], 0
        )


if __name__ == "__main__":
    unittest.main()
