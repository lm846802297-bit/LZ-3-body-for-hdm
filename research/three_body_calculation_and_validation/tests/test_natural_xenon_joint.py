import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from joint_xe131 import load_nuclear_response  # noqa: E402
from run_natural_xenon_joint import AVAILABLE, NATURAL_ABUNDANCE  # noqa: E402


RESPONSE_DIR = HERE / "results" / "anand_wm_response"


class NaturalXenonInputTests(unittest.TestCase):
    def test_available_isotope_abundance_is_not_renormalized(self):
        coverage = sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE)
        self.assertAlmostEqual(coverage, 0.998158, places=9)
        self.assertAlmostEqual(1.0 - coverage, 0.001842, places=9)
        self.assertNotAlmostEqual(coverage, 1.0, places=6)

    def test_each_available_isotope_has_both_response_models(self):
        for A in AVAILABLE:
            for model in ("gcn", "jj55"):
                path = RESPONSE_DIR / f"xe{A}_{model.upper()}_WM.csv"
                response = load_nuclear_response(path, A, model)
                self.assertAlmostEqual(response.R0, A * A, delta=A * A * 2e-5)

    def test_available_isotopes_are_ordered(self):
        self.assertEqual(tuple(sorted(AVAILABLE)), AVAILABLE)
        self.assertTrue(all(A in NATURAL_ABUNDANCE for A in AVAILABLE))


if __name__ == "__main__":
    unittest.main()
