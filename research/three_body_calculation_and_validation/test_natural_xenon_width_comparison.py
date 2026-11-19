import unittest

import run_natural_xenon_width_comparison as width_scan


class NaturalXenonWidthComparisonTests(unittest.TestCase):
    def test_benchmark_and_energy_anchors(self):
        self.assertEqual(width_scan.MS_MEV, 0.300)
        self.assertEqual(width_scan.DELTA_M_MEV, 1.0)
        self.assertEqual(width_scan.ER_POINTS_KEV, (101.0, 200.0, 267.0, 542.0))

    def test_width_schemes_are_explicit(self):
        self.assertEqual(width_scan.WIDTH_SCHEMES, ("zero", "pole", "running"))

    def test_natural_xenon_abundance_coverage_is_not_renormalized(self):
        coverage = sum(width_scan.NATURAL_ABUNDANCE[A] for A in width_scan.AVAILABLE)
        self.assertGreater(coverage, 0.99)
        self.assertLess(coverage, 1.0)


if __name__ == "__main__":
    unittest.main()
