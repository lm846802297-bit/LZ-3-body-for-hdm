import unittest

from run_natural_xenon_continuous_spectrum import (
    BENCHMARKS,
    SELECTED_CHECK_ENERGIES_KEV,
    recoil_grid,
    relative_difference,
)


class ContinuousNaturalXenonSpectrumTests(unittest.TestCase):
    def test_recoil_grid_contains_selected_comparison_points(self):
        grid = recoil_grid(5.0, 800.0, 5.0)
        self.assertEqual(grid[0], 5.0)
        self.assertEqual(grid[-1], 800.0)
        self.assertEqual(len(grid), 163)
        for energy in SELECTED_CHECK_ENERGIES_KEV:
            self.assertIn(energy, grid)

    def test_all_four_figure2_benchmarks_are_defined(self):
        self.assertEqual(
            set(BENCHMARKS),
            {"red_ms200_dm1", "green_ms300_dm1", "black_ms360_dm1", "blue_ms300_dm10"},
        )
        self.assertEqual(BENCHMARKS["red_ms200_dm1"]["ms_MeV"], 0.200)
        self.assertEqual(BENCHMARKS["blue_ms300_dm10"]["delta_m_MeV"], 10.0)

    def test_relative_difference_handles_closed_channels(self):
        self.assertEqual(relative_difference(0.0, 0.0), 0.0)
        self.assertAlmostEqual(relative_difference(2.0, 2.01), 0.005)
        self.assertTrue(relative_difference(0.0, 1.0) == float("inf"))


if __name__ == "__main__":
    unittest.main()
