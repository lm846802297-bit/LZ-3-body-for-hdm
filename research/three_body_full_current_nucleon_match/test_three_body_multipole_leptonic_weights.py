import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import three_body_multipole_leptonic_weights as weights


class LeptonicMultipoleWeightTests(unittest.TestCase):
    def test_symmetric_tensor_has_zero_helicity_odd_weight(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        result = weights.extract_leptonic_weights(L)
        self.assertEqual(result["charge_L00"], 100.0)
        self.assertEqual(result["longitudinal_L33"], 3.0)
        self.assertEqual(result["transverse_even_half_sum"], 4.0)
        self.assertEqual(
            result["transverse_helicity_odd_minus_2i_L12_minus_L21"], 0.0
        )
        self.assertEqual(result["transverse_even_over_charge"], 0.04)

    def test_circular_transverse_tensor_has_expected_helicity_weight(self):
        L = np.diag([10.0, 2.0, 2.0, 1.0]).astype(complex)
        L[1, 2] = 0.2j
        L[2, 1] = -0.2j
        result = weights.extract_leptonic_weights(L)
        self.assertAlmostEqual(
            result["transverse_helicity_odd_minus_2i_L12_minus_L21"], 0.8
        )
        self.assertAlmostEqual(
            result["transverse_helicity_odd_over_transverse_sum"], 0.2
        )

    def test_weights_are_invariant_under_transverse_axis_rotation(self):
        L = np.asarray([
            [10, 0, 0, 0],
            [0, 3, 0.4j, 0],
            [0, -0.4j, 2, 0],
            [0, 0, 0, 1],
        ], dtype=complex)
        angle = 0.731
        c, s = np.cos(angle), np.sin(angle)
        rotation = np.eye(4)
        rotation[1:3, 1:3] = [[c, -s], [s, c]]
        rotated = rotation @ L @ rotation.T
        original = weights.extract_leptonic_weights(L)
        transformed = weights.extract_leptonic_weights(rotated)
        for key in (
            "transverse_even_half_sum",
            "transverse_helicity_odd_minus_2i_L12_minus_L21",
            "transverse_even_over_charge",
            "transverse_helicity_odd_over_transverse_sum",
        ):
            self.assertAlmostEqual(original[key], transformed[key], places=12)

    def test_nonhermitian_or_wrong_shape_tensor_is_rejected(self):
        bad = np.eye(4, dtype=complex)
        bad[0, 1] = 1j
        with self.assertRaises(ValueError):
            weights.extract_leptonic_weights(bad)
        with self.assertRaises(ValueError):
            weights.extract_leptonic_weights(np.eye(3))

    def test_archive_summary_preserves_width_benchmarks(self):
        L = np.diag([100.0, 2.0, 6.0, 3.0]).astype(complex)
        pairs = np.stack((L.real, L.imag), axis=-1).tolist()
        archive = {
            "status": "PASS_SPIN_RESOLVED_DM_TENSOR",
            "benchmarks": [
                {
                    "benchmark": "test",
                    "width_scheme": "pole",
                    "g2": 1.0,
                    "ER_keV": 200.0,
                    "speed_kms": 776.0,
                    "nw": 24,
                    "nz": 16,
                    "nphi": 8,
                    "L_q_aligned_real_imag": pairs,
                }
            ],
        }
        result = weights.analyze_tensor_archive(archive)
        self.assertEqual(result["status"], "PASS_LEPTONIC_MULTIPOLE_WEIGHTS")
        self.assertEqual(result["summary"]["benchmark_count"], 1)
        self.assertEqual(result["benchmarks"][0]["width_scheme"], "pole")


if __name__ == "__main__":
    unittest.main()
