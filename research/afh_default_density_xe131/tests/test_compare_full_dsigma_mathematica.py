from __future__ import annotations

import sys
import unittest
from pathlib import Path

STUDY_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY_DIR))

import compare_full_dsigma_mathematica as comparator


class FullDsigmComparatorUnitConversionTests(unittest.TestCase):
    def test_each_implementation_conversion_identity_is_checked_independently(self):
        dsigma = 2.3342413335246e-11
        converted = dsigma * comparator.GEV3_TO_CM2_PER_KEV
        residual = comparator.conversion_identity_residual(converted, dsigma, True)
        self.assertLessEqual(residual, comparator.CONVERSION_IDENTITY_RTOL)

    def test_cross_code_rate_difference_is_not_misclassified_as_conversion_error(self):
        native = 2.3342413335246e-11
        python = native * (1.0 + 2.5763244333493e-9)
        native_cm = native * comparator.GEV3_TO_CM2_PER_KEV
        python_cm = python * comparator.GEV3_TO_CM2_PER_KEV
        cross_code_relative_difference = comparator.rel(native_cm, python_cm)
        native_conversion_residual = comparator.conversion_identity_residual(
            native_cm, native, True
        )
        python_conversion_residual = comparator.conversion_identity_residual(
            python_cm, python, True
        )
        self.assertLessEqual(cross_code_relative_difference, 2.0e-7)
        self.assertLessEqual(native_conversion_residual, 2.0e-12)
        self.assertLessEqual(python_conversion_residual, 2.0e-12)

    def test_wrong_conversion_constant_fails_identity_gate(self):
        dsigma = 1.0e-12
        wrong_converted = dsigma * comparator.GEV3_TO_CM2_PER_KEV * (1.0 + 1.0e-8)
        residual = comparator.conversion_identity_residual(wrong_converted, dsigma, True)
        self.assertGreater(residual, comparator.CONVERSION_IDENTITY_RTOL)

    def test_closed_phase_space_zero_is_exact(self):
        self.assertEqual(comparator.conversion_identity_residual(0.0, 0.0, False), 0.0)


if __name__ == "__main__":
    unittest.main()
