import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phase_space_tensor_convergence as conv


class PhaseSpaceTensorConvergenceTests(unittest.TestCase):
    def test_formal_convergence_scan_uses_pole_width_only(self):
        self.assertEqual(conv.WIDTH_SCHEMES, ("pole",))
    def test_complex_pair_decoder_preserves_shape_and_phase(self):
        pairs = np.asarray([
            [[1.0, 2.0], [3.0, -4.0]],
            [[0.0, 0.0], [-2.0, 0.5]],
        ])
        decoded = conv.complex_from_pairs(pairs)
        self.assertEqual(decoded.shape, (2, 2))
        np.testing.assert_allclose(
            decoded,
            np.asarray([[1 + 2j, 3 - 4j], [0j, -2 + 0.5j]]),
        )

    def test_identical_tensors_pass_all_convergence_metrics(self):
        value = np.arange(1, 17, dtype=float).reshape(4, 4) * (1 + 0.25j)
        result = conv.convergence_metrics(value, value.copy())
        self.assertTrue(result["pass"])
        self.assertEqual(result["frobenius_relative_difference"], 0.0)
        self.assertEqual(result["max_active_component_relative_difference"], 0.0)
        self.assertEqual(result["active_component_count"], 16)

    def test_metrics_are_json_serializable(self):
        reference = np.eye(4, dtype=complex)
        coarse = reference.copy()
        coarse[1, 2] += 0.001j
        payload = conv.convergence_metrics(coarse, reference)
        encoded = json.dumps(payload)
        self.assertIn('"worst_active_component_index"', encoded)

    def test_componentwise_metric_detects_a_small_but_active_entry(self):
        reference = np.eye(4, dtype=complex)
        coarse = reference.copy()
        coarse[2, 2] *= 1.02
        result = conv.convergence_metrics(
            coarse, reference,
            frobenius_tolerance=0.03,
            active_component_tolerance=0.01,
        )
        self.assertTrue(result["frobenius_relative_difference"] < 0.03)
        self.assertFalse(result["pass"])
        self.assertAlmostEqual(
            result["max_active_component_relative_difference"], 0.02
        )
        self.assertEqual(result["worst_active_component_index"], [2, 2])

    def test_shape_mismatch_and_nonfinite_values_are_rejected(self):
        with self.assertRaises(ValueError):
            conv.convergence_metrics(np.zeros((2, 2)), np.zeros((3, 3)))
        bad = np.zeros((2, 2), dtype=complex)
        bad[0, 0] = np.nan
        with self.assertRaises(ValueError):
            conv.convergence_metrics(bad, np.zeros((2, 2), dtype=complex))

    def test_stress_benchmarks_cover_narrow_and_off_pole_regimes(self):
        names = {case["name"] for case in conv.CASES}
        self.assertEqual(
            names,
            {
                "near_pole_g2_0p1",
                "near_pole_g2_1",
                "green_450keV_g2_1",
            },
        )
        for case in conv.CASES:
            self.assertEqual(len(case["orders"]), 3)
            self.assertEqual(tuple(sorted(case["orders"])), case["orders"])
            self.assertEqual(case["orders"][-1][0] > case["orders"][0][0], True)

    def test_eigen_summary_reports_hermiticity_and_spectrum(self):
        gram = np.eye(16, dtype=complex).reshape(4, 4, 4, 4)
        tensor = np.eye(4, dtype=complex)
        result = conv._tensor_eigen_summary(gram, tensor)
        self.assertEqual(result["gram_min_eigenvalue"], 1.0)
        self.assertEqual(result["tensor_min_eigenvalue"], 1.0)
        self.assertEqual(result["gram_hermiticity_residual"], 0.0)
        self.assertEqual(result["tensor_hermiticity_residual"], 0.0)


if __name__ == "__main__":
    unittest.main()
