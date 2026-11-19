import unittest

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from fold_lz_2026_rate_level import (  # noqa: E402
    candidate_tail_bounds,
    integrate_piecewise_linear_product,
    integrate_weighted_rate,
    interpolate,
    read_efficiency_curves,
)


class LZ2026RateLevelFoldTests(unittest.TestCase):
    def test_candidate_tail_diagnostic_is_clipped_to_lz_roi(self):
        self.assertEqual(candidate_tail_bounds(5.4, 269.9), (225.0, 269.9))
        with self.assertRaises(ValueError):
            candidate_tail_bounds(272.0, 300.0)

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

    def test_piecewise_linear_rate_times_efficiency_is_integrated_exactly(self):
        raw, weighted = integrate_piecewise_linear_product(
            rate_x=[0.0, 2.0],
            rate_y=[1.0, 3.0],
            efficiency_x=[0.0, 2.0],
            efficiency_y=[0.2, 0.4],
            lo=0.0,
            hi=2.0,
        )
        # rate=1+x, efficiency=0.2+0.1*x; integral(rate)=4,
        # integral(rate*efficiency)=integral(0.2+0.3*x+0.1*x^2).
        self.assertAlmostEqual(raw, 4.0, places=14)
        self.assertAlmostEqual(weighted, 1.2666666666666666, places=14)

    def test_piecewise_exact_integral_uses_union_of_knots(self):
        raw, weighted = integrate_piecewise_linear_product(
            rate_x=[0.0, 1.0, 2.0],
            rate_y=[1.0, 2.0, 1.0],
            efficiency_x=[0.0, 2.0],
            efficiency_y=[0.5, 0.5],
            lo=0.0,
            hi=2.0,
        )
        self.assertAlmostEqual(raw, 3.0, places=14)
        self.assertAlmostEqual(weighted, 1.5, places=14)

    def test_piecewise_exact_integral_rejects_roi_extrapolation(self):
        with self.assertRaises(ValueError):
            integrate_piecewise_linear_product(
                rate_x=[1.0, 2.0],
                rate_y=[1.0, 1.0],
                efficiency_x=[0.0, 2.0],
                efficiency_y=[0.5, 0.5],
                lo=0.5,
                hi=1.5,
            )

    def test_read_efficiency_curves_preserves_gray_envelope(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "efficiency.csv"
            path.write_text(
                "ER_keV,efficiency_final_WS_ROI,efficiency_lower_envelope,efficiency_upper_envelope\n"
                "0,0.0,0.0,0.0\n"
                "100,0.9,0.8,0.95\n"
                "300,0.4,0.3,0.5\n",
                encoding="utf-8",
            )
            xs, central, lower, upper = read_efficiency_curves(path)
        self.assertEqual(xs, [0.0, 100.0, 300.0])
        self.assertEqual(central, [0.0, 0.9, 0.4])
        self.assertEqual(lower, [0.0, 0.8, 0.3])
        self.assertEqual(upper, [0.0, 0.95, 0.5])

    def test_read_efficiency_curves_falls_back_to_central_if_no_envelope(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "efficiency.csv"
            path.write_text(
                "ER_keV,efficiency_final_WS_ROI\n"
                "0,0.0\n"
                "100,0.9\n",
                encoding="utf-8",
            )
            xs, central, lower, upper = read_efficiency_curves(path)
        self.assertEqual(lower, central)
        self.assertEqual(upper, central)

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
