import unittest

from research.lz_detector_response.summarize_lz_2026_selection_stage_rates import (
    integrate_piecewise_linear_product,
    validate_cumulative_curves,
)


class SelectionStageRateTests(unittest.TestCase):
    def test_exact_integral_of_product_of_two_linear_functions(self):
        # (1 + 2x)(0.5 + 0.25x), integrated from 0 to 2, is 29/6.
        result = integrate_piecewise_linear_product(
            [0.0, 2.0], [1.0, 5.0],
            [0.0, 2.0], [0.5, 1.0],
            0.0, 2.0,
        )
        self.assertAlmostEqual(result, 29.0 / 6.0, places=13)

    def test_union_of_nonmatching_knots(self):
        # r(x) has a knot at x=1 while epsilon(x) is linear over [0,2].
        # Exact piecewise integration gives 1.5.
        result = integrate_piecewise_linear_product(
            [0.0, 1.0, 2.0], [1.0, 2.0, 1.0],
            [0.0, 2.0], [1.0, 0.0],
            0.0, 2.0,
        )
        self.assertAlmostEqual(result, 1.5, places=13)

    def test_constant_efficiency_scales_raw_integral(self):
        raw = integrate_piecewise_linear_product(
            [0.0, 1.0, 2.0], [0.0, 2.0, 0.0],
            [0.0, 2.0], [1.0, 1.0],
            0.0, 2.0,
        )
        selected = integrate_piecewise_linear_product(
            [0.0, 1.0, 2.0], [0.0, 2.0, 0.0],
            [0.0, 2.0], [0.73, 0.73],
            0.0, 2.0,
        )
        self.assertAlmostEqual(selected, 0.73 * raw, places=13)

    def test_nested_cumulative_curves_are_accepted(self):
        rows = [{
            "ER_keV": "10",
            "trigger_cumulative": "1.0",
            "trigger_plus_s1_threshold_cumulative": "1.0",
            "trigger_plus_s1_ss_analysis_cumulative": "0.95",
            "final_plus_roi_cumulative": "0.90",
        }]
        validate_cumulative_curves(rows)

    def test_non_nested_cumulative_curves_are_rejected(self):
        rows = [{
            "ER_keV": "10",
            "trigger_cumulative": "0.90",
            "trigger_plus_s1_threshold_cumulative": "0.95",
            "trigger_plus_s1_ss_analysis_cumulative": "0.85",
            "final_plus_roi_cumulative": "0.80",
        }]
        with self.assertRaises(ValueError):
            validate_cumulative_curves(rows)


if __name__ == "__main__":
    unittest.main()
