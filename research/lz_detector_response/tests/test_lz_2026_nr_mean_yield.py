import importlib.util
from pathlib import Path
import math
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "lz_2026_extended_nr" / "lz_2026_nr_mean_yield.py"
spec = importlib.util.spec_from_file_location("lz2026_nr_yield", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class TestLZ2026NRMeanYield(unittest.TestCase):
    def test_table_s5_vector_has_15_entries(self):
        self.assertEqual(len(module.LZ2026_NR_YIELD_PARAMETERS), 15)

    def test_high_energy_exponent_turn_on(self):
        p = module.LZ2026_NR_YIELD_PARAMETERS
        e0 = p[14]
        self.assertEqual(module.high_energy_p(e0), 0.5)
        self.assertEqual(module.high_energy_p(e0 - 1e-6), 0.5)
        self.assertGreater(module.high_energy_p(e0 + 1e-3), 0.5)
        self.assertGreater(module.high_energy_p(269.9), module.high_energy_p(100.0))

    def test_mean_quanta_are_nonnegative_and_additive(self):
        result = module.nr_mean_yield(
            energy_keV=248.0,
            field_V_cm=97.0,
            density_g_cm3=2.90,
            molar_mass_g_mol=131.293,
            isotope_mass_number=131,
            old_w13ev=True,
        )
        self.assertGreaterEqual(result.photons_mean, 0.0)
        self.assertGreaterEqual(result.electrons_mean, 0.0)
        self.assertAlmostEqual(
            result.total_quanta_mean,
            result.photons_mean + result.electrons_mean,
            places=12,
        )
        self.assertGreater(result.lindhard, 0.0)

    def test_isotope_mass_scaling(self):
        common = dict(
            energy_keV=150.0,
            field_V_cm=97.0,
            density_g_cm3=2.90,
            molar_mass_g_mol=131.293,
            old_w13ev=True,
        )
        xe128 = module.nr_mean_yield(isotope_mass_number=128, **common)
        xe136 = module.nr_mean_yield(isotope_mass_number=136, **common)
        expected = math.sqrt(136.0 / 128.0)
        self.assertAlmostEqual(xe128.photons_mean / xe136.photons_mean, expected, places=12)
        self.assertAlmostEqual(xe128.electrons_mean / xe136.electrons_mean, expected, places=12)

    def test_old_w_flag_is_explicit_and_changes_result(self):
        common = dict(
            energy_keV=248.0,
            field_V_cm=97.0,
            density_g_cm3=2.90,
            molar_mass_g_mol=131.293,
            isotope_mass_number=131,
        )
        old = module.nr_mean_yield(old_w13ev=True, **common)
        new = module.nr_mean_yield(old_w13ev=False, **common)
        self.assertNotEqual(old.work_function_eV, new.work_function_eV)
        self.assertNotEqual(old.electrons_mean, new.electrons_mean)

    def test_invalid_detector_inputs_fail(self):
        with self.assertRaises(ValueError):
            module.nr_mean_yield(100.0, 0.0, 2.9, 131.293, 131, True)
        with self.assertRaises(ValueError):
            module.high_energy_p(100.0, (1.0,) * 12)


if __name__ == "__main__":
    unittest.main()
