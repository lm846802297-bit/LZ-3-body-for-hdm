from __future__ import annotations

import math
import unittest
from pathlib import Path

import numpy as np

from run_afh7_hybrid9_continuous_spectrum import (
    AFH_ISOTOPES,
    ALL_ISOTOPES,
    ROOT,
    SCENARIOS,
    build_response_tables,
    eq6,
    global_wmax2,
    helm_form_factor,
    helm_response,
    integrate_i6_threshold_u2,
    recoil_grid,
    scenario_response,
    stable_build_point,
    shm_truncated_pdf,
    speed_nodes,
)
from generate_afh_default_xenon_response_grid import read_natural_xenon_masses


class AFHHybrid9ContinuousSpectrumTests(unittest.TestCase):
    def test_helm_zero_momentum_normalization(self):
        for A in ALL_ISOTOPES:
            self.assertAlmostEqual(helm_form_factor(0.0, A), 1.0, places=14)
            self.assertAlmostEqual(helm_response(0.0, A), float(A * A), places=10)

    def test_helm_response_is_finite_nonnegative_and_coherent_at_zero(self):
        for A in ALL_ISOTOPES:
            for q in (0.0, 0.05, 0.15, 0.30, 0.60):
                value = helm_response(q, A)
                self.assertTrue(math.isfinite(value))
                self.assertGreaterEqual(value, 0.0)
                self.assertLessEqual(value, A * A * (1.0 + 1.0e-12))

    def test_response_scenario_composition_is_explicit(self):
        for A in AFH_ISOTOPES:
            self.assertEqual(scenario_response("AFH-7", A, 0.25 * A * A, 0.5 * A * A), 0.25 * A * A)
            self.assertEqual(
                scenario_response("Hybrid-9 (AFH-7 + Helm-2)", A, 0.25 * A * A, 0.5 * A * A),
                0.25 * A * A,
            )
            self.assertEqual(
                scenario_response("AFH-7 + A2-2 ceiling", A, 0.25 * A * A, 0.5 * A * A),
                0.25 * A * A,
            )
        for A in (124, 126):
            self.assertEqual(scenario_response("AFH-7", A, None, 0.5 * A * A), 0.0)
            self.assertEqual(
                scenario_response("Hybrid-9 (AFH-7 + Helm-2)", A, None, 0.5 * A * A),
                0.5 * A * A,
            )
            self.assertEqual(
                scenario_response("AFH-7 + A2-2 ceiling", A, None, 0.5 * A * A),
                float(A * A),
            )
            self.assertEqual(scenario_response("Helm-9", A, None, 0.5 * A * A), 0.5 * A * A)
        self.assertEqual(len(SCENARIOS), 4)

    def test_speed_quadrature_splits_shm_pdf_kink_and_normalizes(self):
        v0, ve, vesc = 220.0, 232.0, 544.0
        kink, vmax = vesc - ve, vesc + ve
        nodes, weights = speed_nodes(0.0, vmax, 24, breakpoints=(kink,))
        self.assertEqual(len(nodes), 48)
        self.assertLess(float(np.max(nodes[:24])), kink)
        self.assertGreater(float(np.min(nodes[24:])), kink)
        normalization = sum(
            float(w) * shm_truncated_pdf(float(v), v0, ve, vesc)
            for v, w in zip(nodes, weights)
        )
        self.assertAlmostEqual(normalization, 1.0, places=12)

    def test_recoil_grid_is_sorted_unique_and_contains_anchor_points(self):
        energies = recoil_grid()
        self.assertEqual(energies, sorted(set(energies)))
        for value in (5.0, 101.0, 200.0, 267.0, 270.0, 542.0, 800.0):
            self.assertIn(value, energies)

    def test_global_wmax_formula_matches_direct_kinematic_limit(self):
        mchi, mA, speed = 1000.0, 122.0, 776.0
        wmax2, er_star = global_wmax2(mchi, mA, speed)
        direct = eq6.limits(mchi, 0.0003, mA, er_star, speed)[1]
        self.assertGreater(er_star, 0.0)
        self.assertAlmostEqual(wmax2, direct, delta=2.0e-9)

    def test_stable_point_closes_four_momentum_and_mass_shells(self):
        mchi, ms, mA, ER, speed = 1000.0, 0.0003, 122.0, 0.0002, 776.0
        wmin2, wmax2 = eq6.limits(mchi, ms, mA, ER, speed)
        delta_w2 = 0.5 * (wmax2 - wmin2)
        point = stable_build_point(mchi, ms, mA, ER, speed, delta_w2, 0.2, 1.1)
        residual = eq6.residuals(point, mchi, ms, mA)
        self.assertLess(abs(residual["p2-mchi2"]), 2.0e-7)
        self.assertLess(abs(residual["pprime2-mchi2"]), 2.0e-7)
        self.assertLess(abs(residual["k2-ms2"]), 2.0e-7)
        self.assertLess(abs(residual["Pprime2-mA2"]), 2.0e-7)
        self.assertLess(residual["four_momentum_max"], 2.0e-9)
        self.assertLess(abs(residual["K2-W2"]), 2.0e-7)

    def test_threshold_u2_kernel_is_positive_and_convergent(self):
        args = (1000.0, 0.0003, 0.001, 122.0, 0.0002, 776.0)
        low = integrate_i6_threshold_u2(*args, nW=6, nz=6, nphi=4, g2=1.0)
        high = integrate_i6_threshold_u2(*args, nW=12, nz=12, nphi=6, g2=1.0)
        self.assertGreater(low, 0.0)
        self.assertGreater(high, 0.0)
        self.assertTrue(math.isfinite(low))
        self.assertTrue(math.isfinite(high))
        self.assertLess(abs(high / low - 1.0), 2.0e-6)

    def test_full_direct_response_table_has_seven_afh_and_two_helm_only_isotopes(self):
        base = ROOT / "research" / "afh_default_density_natural_xenon_halo"
        weights = base / "input" / "natural_xenon_isotope_weights.csv"
        source = ROOT / "v6" / "dmformfactor-V6.m"
        response_dir = base / "results" / "full_afh_v6_default_7_isotope_response"
        masses = read_natural_xenon_masses(weights)
        lookup, rows, summaries = build_response_tables(
            energies=[101.0], masses=masses, source_path=source,
            weights_path=weights, response_dir=response_dir,
        )
        self.assertEqual(len(rows), 9)
        self.assertEqual(set(summaries), {str(A) for A in AFH_ISOTOPES})
        for A in AFH_ISOTOPES:
            item = lookup[(A, 101.0)]
            self.assertIsNotNone(item["R_AFH"])
            self.assertGreaterEqual(item["R_AFH"], 0.0)
        for A in (124, 126):
            item = lookup[(A, 101.0)]
            self.assertIsNone(item["R_AFH"])
            self.assertGreater(item["R_Helm"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
