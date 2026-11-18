import unittest

import numpy as np

from audit_xe131_six_channel_interpolation import local_chebyshev_value


class LocalChebyshevInterpolationTests(unittest.TestCase):
    def test_exact_reproduction_of_quadratic(self):
        q = np.linspace(0.0, 0.6, 101)
        y = 1.0 + 2.0 * q + 3.0 * q**2
        target = 0.27341
        actual = local_chebyshev_value(q, y, target, degree=2, n_points=7)
        expected = 1.0 + 2.0 * target + 3.0 * target**2
        self.assertAlmostEqual(actual, expected, places=13)

    def test_degree_eight_and_ten_stability_for_smooth_response(self):
        q = np.linspace(0.0, 0.6, 2401)
        y = 0.2 + np.exp(-3.0 * q) * np.cos(11.0 * q)
        targets = (0.1847558961, 0.2558624467, 0.2563384708, 0.2962686752)
        for target in targets:
            c8 = local_chebyshev_value(q, y, target, degree=8, n_points=11)
            c10 = local_chebyshev_value(q, y, target, degree=10, n_points=13)
            self.assertAlmostEqual(c8, c10, delta=2e-11)

    def test_rejects_extrapolation(self):
        q = np.linspace(0.0, 0.6, 31)
        y = 1.0 + q
        with self.assertRaises(ValueError):
            local_chebyshev_value(q, y, -1e-6, degree=4, n_points=7)

    def test_rejects_underdetermined_fit(self):
        q = np.linspace(0.0, 0.6, 31)
        y = 1.0 + q
        with self.assertRaises(ValueError):
            local_chebyshev_value(q, y, 0.2, degree=7, n_points=7)


if __name__ == "__main__":
    unittest.main()
