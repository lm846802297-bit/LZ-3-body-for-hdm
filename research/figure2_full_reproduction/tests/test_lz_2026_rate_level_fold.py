import unittest

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from fold_lz_2026_rate_level import integrate_weighted_rate, interpolate  # noqa: E402


class LZ2026RateLevelFoldTests(unittest.TestCase):
    def test_linear_interpolation(self):
        self.assertAlmostEqual(interpolate(1.0, [0.0, 2.0], [0.0, 4.0]), 2.0)
        self.assertAlmostEqual(interpolate(0.0, [0.0, 2.0], [1.0, 3.0]), 1.0)
        self.assertAlmostEqual(interpolate(2.0, [0.0, 2.0], [1.0, 3.0]), 3.0)

    def test_constant_rate_and_efficiency_integrate_analytically(self):
        raw, weighted = integrate_weighted_rate(
            rate_x=[0.0, 2.0],
            rate_y=[2.0, 2.0],
            efficiency_x=[0.0, 2.0],
            efficiency_y=[0.5, 0.5],
            lo=0.5,
            hi=1.5,
            n_steps=1000,
        )
        self.assertAlmostEqual(raw, 2.0, places=10)
        self.assertAlmostEqual(weighted, 1.0, places=10)

    def test_weighted_integral_never_exceeds_raw_for_efficiency_below_one(self):
        raw, weighted = integrate_weighted_rate(
            rate_x=[0.0, 10.0],
            rate_y=[1.0, 3.0],
            efficiency_x=[0.0, 10.0],
            efficiency_y=[0.2, 0.8],
            lo=1.0,
            hi=9.0,
            n_steps=1000,
        )
        self.assertGreater(raw, 0.0)
        self.assertGreaterEqual(weighted, 0.0)
        self.assertLessEqual(weighted, raw)


if __name__ == "__main__":
    unittest.main()
