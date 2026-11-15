import unittest
import numpy as np

from research.lz_detector_response.paired_s1_ensemble_tv_bootstrap import (
    exact_paired_permutation,
    holm_adjust,
    total_variation,
)


class TestTotalVariation(unittest.TestCase):
    def test_known_tv(self):
        self.assertAlmostEqual(total_variation(np.array([0.5, 0.5]), np.array([1.0, 0.0])), 0.5)

    def test_scale_invariance(self):
        a = np.array([2.0, 3.0, 5.0])
        b = np.array([1.0, 4.0, 5.0])
        self.assertAlmostEqual(total_variation(a, b), total_variation(7.0 * a, 0.2 * b))

    def test_rejects_negative_weights(self):
        with self.assertRaises(ValueError):
            total_variation(np.array([1.0, -0.1]), np.array([1.0, 1.0]))


class TestPairedPermutation(unittest.TestCase):
    def test_enumerates_all_swaps_and_is_complement_symmetric(self):
        p = np.array([[0.8, 0.2], [0.7, 0.3], [0.9, 0.1]])
        f = np.array([[0.7, 0.3], [0.6, 0.4], [0.8, 0.2]])
        result = exact_paired_permutation(p, f)
        self.assertEqual(result["n_permutations"], 8)
        self.assertGreaterEqual(result["exact_p_value"], 2.0 / 8.0)
        self.assertLessEqual(result["exact_p_value"], 1.0)


class TestHolm(unittest.TestCase):
    def test_known_adjustment(self):
        self.assertEqual(holm_adjust([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


if __name__ == "__main__":
    unittest.main()
