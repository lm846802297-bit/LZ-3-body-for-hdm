from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "research" / "figure2_full_reproduction"))

import run_python_full_dsigma_xe131 as runner
import phase_space_convergence as psc


class PythonFullDifferentialCrossSectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response = runner.load_response_table(
            HERE / "output" / "afh_default_xe131_WM00.csv"
        )

    def test_afh_response_factor_four_on_all_2401_nodes(self):
        response = self.response
        self.assertEqual(len(response.q_GeV), 2401)
        self.assertLessEqual(response.max_factor4_mapping_residual, 2.0e-12)
        self.assertAlmostEqual(response.R_physical[0], runner.A**2, delta=2.0e-8)
        self.assertAlmostEqual(
            response.R_package[0] / (runner.A**2 / 4.0),
            1.0,
            delta=2.0e-4,
        )
        self.assertAlmostEqual(response.C0, 1.0000825298069378, delta=2.0e-12)

    def test_factor_four_is_applied_once_in_cross_section(self):
        cross = runner.assemble_cross_sections(
            I6_GeV2=123.456,
            R_A_physical=float(runner.A**2),
            ER_GeV=200.0e-6,
        )
        self.assertGreater(cross["dsigma_dER_GeVminus3"], 0.0)
        self.assertAlmostEqual(cross["dsigma_factor4_ratio"], 4.0, delta=2.0e-14)
        self.assertAlmostEqual(
            cross["dsigma_without_factor4_GeVminus3"] * 4.0,
            cross["dsigma_dER_GeVminus3"],
            delta=abs(cross["dsigma_dER_GeVminus3"]) * 2.0e-14,
        )

    def test_gevm3_to_cm2_per_kev_conversion(self):
        cross = runner.assemble_cross_sections(
            I6_GeV2=1.25,
            R_A_physical=runner.A**2,
            ER_GeV=267.0e-6,
        )
        expected = (
            cross["dsigma_dER_GeVminus3"]
            * runner.GEV2_TO_CM2_PER_KEV
        )
        self.assertAlmostEqual(
            cross["dsigma_cm2_per_keV"],
            expected,
            delta=abs(expected) * 2.0e-15,
        )

    def test_exact_spatial_q_is_not_the_mediator_invariant(self):
        ER = 267.0e-6
        q = runner.exact_spatial_q_GeV(runner.M_A_GEV, ER)
        expected_q2 = 2.0 * runner.M_A_GEV * ER + ER**2
        denominator = runner.mediator_denominator_GeV4(
            runner.M_A_GEV, ER, runner.M_V_GEV
        )
        expected_denominator = (
            runner.M_V_GEV**2 + 2.0 * runner.M_A_GEV * ER
        ) ** 2
        self.assertAlmostEqual(q * q, expected_q2, delta=1.0e-15)
        self.assertAlmostEqual(denominator, expected_denominator, delta=1.0e-14)
        self.assertNotAlmostEqual(q * q, 2.0 * runner.M_A_GEV * ER, delta=1.0e-15)

    def test_python_eq6_and_raw_li_phase_space_azimuth_measure(self):
        benchmark = "green_ms300_dm1"
        ms, delta_m = runner.BENCHMARKS[benchmark]
        args = (
            runner.M_CHI_GEV,
            ms,
            delta_m,
            runner.M_A_GEV,
            200.0e-6,
            runner.SPEED_KM_S,
        )
        i6 = psc.integrate_i6(
            *args, nW=4, nz=4, nphi=4,
            mapping="threshold_u2", width_scheme="pole", g2=1.0,
        )
        raw = psc.integrate_raw_li_phase_space(
            *args, nW=4, nz=4, nphi=4,
            mapping="threshold_u2", width_scheme="pole", g2=1.0,
        )
        self.assertGreater(i6, 0.0)
        self.assertAlmostEqual(raw, 2.0 * math.pi * i6, delta=abs(raw) * 2.0e-11)

    def test_closed_phase_space_gives_exact_zero_cross_section(self):
        row = runner.evaluate_point(
            benchmark="green_ms300_dm1",
            ER_keV=1300.0,
            response=self.response,
            nW=4,
            nz=4,
            nphi=4,
        )
        self.assertEqual(row["phase_space_open"], 0)
        self.assertEqual(row["I6_GeV2"], 0.0)
        self.assertEqual(row["dsigma_dER_GeVminus3"], 0.0)
        self.assertLessEqual(row["q_exact_spatial_GeV"], 0.6)

    def test_open_benchmark_has_positive_pole_clearance(self):
        row = runner.evaluate_point(
            benchmark="green_ms300_dm1",
            ER_keV=267.0,
            response=self.response,
            nW=4,
            nz=4,
            nphi=4,
        )
        self.assertEqual(row["phase_space_open"], 1)
        self.assertGreater(row["chi2_pole_clearance_keV"], 0.0)
        self.assertAlmostEqual(row["dsigma_factor4_ratio"], 4.0, delta=2.0e-12)


if __name__ == "__main__":
    unittest.main()
