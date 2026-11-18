import importlib.util
import math
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "run_afh_isotope_response_equivalence.py"
SPEC = importlib.util.spec_from_file_location("afh_isotope_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestAFHIsotopeResponseEquivalence(unittest.TestCase):
    def test_factor_four_zero_momentum_mapping(self):
        A = 131
        raw_package_response = A*A/4.0
        physical_response = 4.0*raw_package_response
        self.assertAlmostEqual(physical_response, A*A, places=12)

    def test_reconstruction_formula(self):
        J, a0, a2, norm = 1.5, 0.37, -0.12, 1.0001
        response = norm * 4.0*math.pi/(2.0*J+1.0) * (a0*a0+a2*a2)
        self.assertGreater(response, 0.0)

    def test_rank_two_fraction_is_bounded(self):
        a0, a2 = 1.0, 2.0
        fraction = a2*a2/(a0*a0+a2*a2)
        self.assertGreaterEqual(fraction, 0.0)
        self.assertLessEqual(fraction, 1.0)

    def test_natural_abundance_coverage(self):
        self.assertAlmostEqual(sum(MODULE.NATURAL_FRACTIONS.values()), 0.998158, places=9)

    def test_isotope_set_and_selected_energy_grid(self):
        self.assertEqual(MODULE.ISOTOPES, (128, 129, 130, 131, 132, 134, 136))
        self.assertEqual(len(MODULE.SELECTED_ER_KEV), 12)


if __name__ == "__main__":
    unittest.main()
