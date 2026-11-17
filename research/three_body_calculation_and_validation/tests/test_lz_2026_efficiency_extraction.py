import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))

from extract_lz_2026_nr_efficiency import (  # noqa: E402
    extract_curve,
    extract_uncertainty_envelope,
    interpolate,
)


SVG = REPO / "research" / "lz_detector_response" / "lz_2026_extended_nr" / "lz_2026_figS2.svg"


class LZ2026EfficiencyExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.central = extract_curve(SVG)
        cls.lower, cls.upper, cls.band_point_count = extract_uncertainty_envelope(SVG)

    def test_central_curve_matches_independent_digitization_at_candidate(self):
        self.assertAlmostEqual(interpolate(self.central, 248.0), 0.9457, delta=1.0e-3)

    def test_gray_envelope_matches_independent_digitization_at_candidate(self):
        self.assertAlmostEqual(interpolate(self.lower, 248.0), 0.8835, delta=1.0e-3)
        self.assertAlmostEqual(interpolate(self.upper, 248.0), 0.9800, delta=1.0e-3)
        self.assertGreater(self.band_point_count, 1000)

    def test_central_curve_stays_inside_gray_envelope(self):
        for energy in range(0, 301, 5):
            central = interpolate(self.central, float(energy))
            lower = interpolate(self.lower, float(energy))
            upper = interpolate(self.upper, float(energy))
            self.assertLessEqual(lower, central + 2.0e-3)
            self.assertLessEqual(central, upper + 2.0e-3)

    def test_published_upper_roi_efficiency_anchor(self):
        self.assertAlmostEqual(interpolate(self.central, 269.9), 0.4988, delta=1.0e-3)


if __name__ == "__main__":
    unittest.main()
