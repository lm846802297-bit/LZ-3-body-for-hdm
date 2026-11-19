import unittest

import numpy as np

from fold_lz_2026_rate_level import integrate_piecewise_linear_product
from propagate_B_covariance_to_lz_yields import integrate_draw_matrix


class PropagateBDetectorCovarianceTests(unittest.TestCase):
    def test_vectorized_draw_integral_matches_scalar_exact_integral(self):
        rate_x = [0.0, 1.0, 2.0]
        rate_draws = np.asarray([
            [1.0, 2.0, 3.0],
            [2.0, 4.0, 6.0],
            [0.5, 1.0, 1.5],
        ])
        efficiency_x = [0.0, 0.5, 1.5, 2.0]
        efficiency_y = [0.2, 0.4, 0.8, 0.9]
        lo, hi = 0.25, 1.75

        raw, weighted = integrate_draw_matrix(
            rate_x, rate_draws, efficiency_x, efficiency_y, lo, hi
        )
        self.assertEqual(raw.shape, (3,))
        self.assertEqual(weighted.shape, (3,))

        for i in range(rate_draws.shape[0]):
            raw_ref, weighted_ref = integrate_piecewise_linear_product(
                rate_x, rate_draws[i].tolist(),
                efficiency_x, efficiency_y, lo, hi,
            )
            self.assertAlmostEqual(raw[i], raw_ref, places=13)
            self.assertAlmostEqual(weighted[i], weighted_ref, places=13)

    def test_invalid_draw_shape_is_rejected(self):
        with self.assertRaises(ValueError):
            integrate_draw_matrix(
                [0.0, 1.0], np.ones((3, 3)), [0.0, 1.0], [1.0, 1.0], 0.0, 1.0
            )

    def test_negative_rate_draw_is_rejected(self):
        with self.assertRaises(ValueError):
            integrate_draw_matrix(
                [0.0, 1.0], np.asarray([[1.0, -1.0]]),
                [0.0, 1.0], [1.0, 1.0], 0.0, 1.0
            )


if __name__ == "__main__":
    unittest.main()
