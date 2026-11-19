import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run_user_l00_benchmark import calculate_benchmark


class UserL00BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = calculate_benchmark(nw=24, nz=24, nphi=16)

    def test_supplied_model_parameters(self):
        b = self.result["benchmark"]
        self.assertEqual((b["g1"], b["g2"], b["gVN"]), (1.0, 1.0, 1.0))
        self.assertEqual(b["mchi1_GeV"], 1000.0)
        self.assertAlmostEqual(b["delta_m_keV"], 450.0, places=12)
        self.assertAlmostEqual(b["mchi2_GeV"], 1000.00045, places=12)
        self.assertAlmostEqual(b["mV_GeV"], 10.0, places=12)
        self.assertAlmostEqual(b["ms_keV"], 300.0, places=12)

    def test_selected_point_is_open_but_chi2_remains_off_shell(self):
        p = self.result["phase_space"]
        self.assertGreater(p["Wmax2_GeV2"], p["Wmin2_GeV2"])
        self.assertFalse(p["on_shell_chi2_accessible"])
        self.assertAlmostEqual(
            p["mchi2_minus_sqrt_Wmax_keV"], 102.58965596676717, delta=2e-6
        )

    def test_conditional_scalar_width(self):
        width = self.result["conditional_scalar_width"]["Gamma_chi2_GeV"]
        self.assertAlmostEqual(width, 5.3382154723487404e-5, delta=2e-15)
        self.assertAlmostEqual(width * 1.0e6, 53.3821547234874, delta=2e-9)

    def test_target_rest_frame_L00_regression(self):
        traces = self.result["L00_at_W2_midpoint"]
        zero = traces["zero_width"]
        pole = traces["conditional_scalar_pole_width"]
        self.assertAlmostEqual(
            zero["total"] / 3.3933323920783375e14, 1.0, delta=2e-10
        )
        self.assertAlmostEqual(
            pole["total"] / 3.251108265679228e14, 1.0, delta=2e-10
        )
        self.assertAlmostEqual(
            zero["before"] + zero["after"] + zero["interference"],
            zero["total"],
            delta=1e-12 * zero["total"],
        )
        self.assertLess(
            pole["imaginary_residual"] / pole["total"], 1e-14
        )

    def test_integrated_eq6_benchmark_regression(self):
        result = self.result["Eq6_integral"]
        self.assertAlmostEqual(
            result["I6_zero_width_GeV2"] / 16218203.04240416,
            1.0,
            delta=2e-6,
        )
        self.assertAlmostEqual(
            result["I6_conditional_scalar_pole_width_GeV2"]
            / 15439557.38669752,
            1.0,
            delta=2e-6,
        )
        self.assertAlmostEqual(
            result["relative_pole_vs_zero"],
            -0.04801059979769595,
            delta=2e-6,
        )

    def test_cross_section_prefactor_uses_supplied_mediator_and_couplings(self):
        result = self.result["differential_cross_section"]
        self.assertAlmostEqual(
            result["prefactor_times_I6_over_RA_GeVminus3_zero_width"],
            3.716757838355961,
            delta=2e-6,
        )
        self.assertAlmostEqual(
            result["prefactor_times_I6_over_RA_GeVminus3_pole_width"],
            3.5383140652337035,
            delta=2e-6,
        )


if __name__ == "__main__":
    unittest.main()
