import math
import sys
import unittest
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import eq6_kernel  # noqa: E402
from isotope_mass_schemes import isotope_mass_GeV as isotope_mass_with_scheme  # noqa: E402
from rate_kinematics import vmin_three_body_km_s  # noqa: E402
from run_natural_xenon_halo_fold import (  # noqa: E402
    C_KM_S,
    NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL,
    halo_pdf,
    mean_target_number_per_kg,
    rate_conversion_factor,
    shm_truncated_pdf,
    compute_isotope_halo_integrals,
)


class NaturalXenonHaloFoldTests(unittest.TestCase):
    def integrate_pdf(self, model, vmax, n=400):
        x, w = leggauss(n)
        velocities = 0.5 * vmax * (x + 1.0)
        weights = 0.5 * vmax * w
        return sum(
            float(weight) * halo_pdf(float(v), model, 220.0, 232.0, 544.0)
            for v, weight in zip(velocities, weights)
        )

    def test_untruncated_pdf_normalization(self):
        self.assertAlmostEqual(
            self.integrate_pdf("mb_untruncated", 1600.0),
            1.0,
            delta=2e-7,
        )

    def test_truncated_pdf_normalization_and_support(self):
        self.assertAlmostEqual(
            self.integrate_pdf("shm_cutoff", 776.0),
            1.0,
            delta=2e-7,
        )
        self.assertEqual(shm_truncated_pdf(776.0, 220.0, 232.0, 544.0), 0.0)
        self.assertEqual(shm_truncated_pdf(776.001, 220.0, 232.0, 544.0), 0.0)

    def test_truncated_pdf_is_continuous_at_escape_transition(self):
        v0, ve, vesc = 220.0, 232.0, 544.0
        transition = vesc - ve
        left = shm_truncated_pdf(transition - 1e-7, v0, ve, vesc)
        right = shm_truncated_pdf(transition + 1e-7, v0, ve, vesc)
        self.assertAlmostEqual(left, right, delta=2e-10)

    def test_analytic_three_body_vmin_closes_phase_space(self):
        mchi, ms, ER = 1000.0, 0.0003, 101.0e-6
        for A in (131, 136):
            mA = A * 0.93149410242
            vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
            wmin2, wmax2 = eq6_kernel.limits(mchi, ms, mA, ER, vmin)
            self.assertAlmostEqual(wmax2, wmin2, delta=3e-10)
            self.assertGreater(vmin, 0.0)

    def test_cutoff_threshold_selects_only_xe136_at_101_kev(self):
        mchi, ms, ER, vmax = 1000.0, 0.0003, 101.0e-6, 776.0
        thresholds = {
            A: vmin_three_body_km_s(
                mchi, ms, A * 0.93149410242, ER
            )
            for A in (128, 129, 130, 131, 132, 134, 136)
        }
        self.assertTrue(all(thresholds[A] > vmax for A in thresholds if A != 136))
        self.assertLess(thresholds[136], vmax)

    def test_conditional_pole_width_mode_uses_exact_response_q(self):
        rows = compute_isotope_halo_integrals(
            A=136,
            ER_keV=101.0,
            halo_model="shm_cutoff",
            mass_scheme="nist_nuclear",
            nv=4,
            mchi=1000.0,
            ms=0.0003,
            delta_m=0.001,
            speed_v0=220.0,
            speed_ve=232.0,
            speed_vesc=544.0,
            untruncated_vmax=1600.0,
            coupling_product_sq=1.0e-8,
            response_dir=HERE / "results" / "anand_wm_response",
            nw=4,
            nz=4,
            nphi=2,
            width_scheme="pole",
            g2=1.0,
            response_cache={},
        )
        self.assertEqual({row["width_scheme"] for row in rows}, {"pole"})
        self.assertEqual({row["g2"] for row in rows}, {1.0})
        mA = isotope_mass_with_scheme(136, "nist_nuclear")
        q_exact = math.sqrt(2.0 * mA * 101.0e-6 + (101.0e-6) ** 2)
        for row in rows:
            self.assertAlmostEqual(row["q_response_GeV"], q_exact, places=14)

    def test_per_kg_target_count_uses_nist_standard_atomic_weight(self):
        expected = 6.02214076e23 * 1000.0 / 131.293
        self.assertEqual(NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL, 131.293)
        self.assertAlmostEqual(mean_target_number_per_kg(), expected, places=6)

    def test_rate_conversion_factor_is_positive_and_scales_with_density(self):
        base = rate_conversion_factor(0.3, 1000.0)
        doubled = rate_conversion_factor(0.6, 1000.0)
        self.assertGreater(base, 0.0)
        self.assertAlmostEqual(doubled / base, 2.0, places=14)


if __name__ == "__main__":
    unittest.main()
