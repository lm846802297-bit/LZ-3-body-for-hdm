import math
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import eq6_kernel as eq6
import phase_space_convergence as psc


class PhaseSpaceConvergenceTests(unittest.TestCase):
    def setUp(self):
        self.mchi = 1000.0
        self.ms = 300e-6
        self.dm = 1e-3
        self.mA = 122.0
        self.ER = 200e-6
        self.speed = 776.0

    def test_threshold_mapping_regularizes_w2_endpoint(self):
        reference = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=48, nz=24, nphi=16, mapping="threshold_u2",
        )
        mapped = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=6, nz=6, nphi=4, mapping="threshold_u2",
        )
        self.assertLess(abs(mapped / reference - 1.0), 2e-6)

    def test_w_and_w2_jacobians_agree(self):
        w2 = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=8, nz=8, nphi=4, mapping="linear_w2",
        )
        w = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=8, nz=8, nphi=4, mapping="linear_w",
        )
        self.assertLess(abs(w / w2 - 1.0), 1e-7)

    def test_near_threshold_stable_kallen_and_quadrature(self):
        mchi, ms, dm, mA, ER = 1000.0, 300e-6, 1e-3, 122.0, 542e-6
        vmin = psc._vmin_kms(mchi, ms, mA, ER)
        speed = vmin + 0.1
        coarse = psc.integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=8, nz=4, nphi=4, mapping="threshold_u2",
        )
        reference = psc.integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=24, nz=4, nphi=4, mapping="threshold_u2",
        )
        self.assertGreater(coarse, 0.0)
        self.assertLess(abs(coarse / reference - 1.0), 1e-6)

    def test_z_and_phi_quadrature_are_separately_converged(self):
        reference = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=8, nz=24, nphi=16, mapping="threshold_u2",
        )
        low_order = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=8, nz=2, nphi=2, mapping="threshold_u2",
        )
        self.assertLess(abs(low_order / reference - 1.0), 1e-8)

    def test_raw_li_phase_space_reconstructs_eq6_prefactor(self):
        i6 = psc.integrate_i6(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=8, nz=8, nphi=4, mapping="threshold_u2",
        )
        raw = psc.integrate_raw_li_phase_space(
            self.mchi, self.ms, self.dm, self.mA, self.ER, self.speed,
            nW=8, nz=8, nphi=4, mapping="threshold_u2",
        )
        self.assertAlmostEqual(raw / (2.0 * math.pi * i6), 1.0, places=13)
        ds_eq6 = psc.cross_section_eq6(
            i6, self.mchi, self.mA, self.ER, self.speed
        )
        ds_li = psc.cross_section_direct_li(
            raw, self.mchi, self.mA, self.ER, self.speed
        )
        self.assertAlmostEqual(ds_li / ds_eq6, 1.0, places=13)

    def test_historical_800km_s_linear_W2_offset_and_threshold_mapping(self):
        mchi, ms, dm = 1000.0, 300e-6, 1e-3
        mA = 131.0 * 0.93149410242
        ER, speed = 200e-6, 800.0
        archived_i6 = 1433678.0722867665

        legacy = eq6.reduced_kernel(
            mchi, ms, dm, mA, ER, speed,
            nw=16, nz=16, nphi=8, width_scheme="pole", g2=1.0,
        )
        independent_linear = psc.integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=16, nz=16, nphi=8, mapping="linear_w2",
        )
        self.assertAlmostEqual(independent_linear / legacy, 1.0, delta=2e-8)

        high_order = psc.integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=48, nz=40, nphi=24, mapping="threshold_u2",
        )
        threshold_mapped = psc.integrate_i6(
            mchi, ms, dm, mA, ER, speed,
            nW=16, nz=16, nphi=8, mapping="threshold_u2",
        )
        self.assertLess(abs(threshold_mapped / high_order - 1.0), 1e-8)

        archived_offset = abs(legacy / archived_i6 - 1.0)
        print(
            "800 km/s historical anchor:",
            {
                "legacy_linear_W2_I6": legacy,
                "independent_linear_W2_I6": independent_linear,
                "threshold_u2_16x16x8_I6": threshold_mapped,
                "threshold_u2_48x40x24_I6": high_order,
                "archived_I6": archived_i6,
                "legacy_relative_offset_to_archive": legacy / archived_i6 - 1.0,
                "high_order_relative_offset_to_archive": high_order / archived_i6 - 1.0,
            },
        )
        self.assertGreater(archived_offset, 3e-5)
        self.assertLess(archived_offset, 5e-5)

    def test_threshold_stable_point_preserves_mass_shells(self):
        wmin2, wmax2 = eq6.limits(
            self.mchi, self.ms, self.mA, self.ER, self.speed
        )
        delta = 0.5 * (wmax2 - wmin2)
        point = psc._stable_build_point(
            self.mchi, self.ms, self.mA, self.ER, self.speed,
            delta, z=0.23, phi=1.17,
        )
        P = np.array([self.mA, 0.0, 0.0, 0.0])
        Pprime = P + point.q
        closure = point.p - point.p_prime - point.k - point.q
        residuals = (
            eq6.dot(point.p, point.p) - self.mchi**2,
            eq6.dot(point.p_prime, point.p_prime) - self.mchi**2,
            eq6.dot(point.k, point.k) - self.ms**2,
            eq6.dot(Pprime, Pprime) - self.mA**2,
            np.max(np.abs(closure)),
            eq6.dot(point.K, point.K) - point.W2,
        )
        self.assertLess(max(abs(float(x)) for x in residuals), 2e-8)


if __name__ == "__main__":
    unittest.main()
