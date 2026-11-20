import math
import sys
import unittest
from pathlib import Path

import numpy as np

CALC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CALC))
from charge_longitudinal import project_charge as projection
import eq6_kernel as eq6
import phase_space_convergence as phase


class ChargeProjectionTests(unittest.TestCase):
    def test_projected_trace_matches_explicit_spins_at_tilted_transfer(self):
        mass, scalar, target, gap = 1000., .0003, 121.90971983538435, .00045
        recoil = .0002
        point = phase._stable_build_point(mass, scalar, target, recoil, 776., .046, .37, 1.13)
        width = eq6.chi2_width_dirac_scalar(mass, scalar, gap, 1.)
        got = projection.point_traces(point, .046, width)
        self.assertLess(max(abs(value) for value in eq6.residuals(point, mass, scalar, target).values()), 1e-8)
        self.assertGreater(abs(point.q_A[1]), .01)
        dirac_time = eq6.GAMMA[0]

        def spinors(momentum):
            sigma_p = sum(component * sigma for component, sigma in zip(momentum[1:], (eq6.s1, eq6.s2, eq6.s3)))
            return math.sqrt(momentum[0] + mass) * np.vstack((np.eye(2), sigma_p / (momentum[0] + mass)))

        lower = spinors(point.p_prime).conj().T @ dirac_time
        upper = spinors(point.p)
        before, after = eq6.chi2_internal_momenta(point)
        heavy = mass + gap
        components = []
        for gamma in eq6.GAMMA:
            first = gamma @ (eq6.slash(before) + heavy * eq6.ID4) / (eq6.dot(before, before) - heavy**2)
            second = (eq6.slash(after) + heavy * eq6.ID4) @ gamma / (point.W2 - heavy**2 + 1j * heavy * width)
            components.append(lower @ (first + second) @ upper)
        time = components[0]
        longitudinal = sum(direction * current for direction, current in zip(point.q_A[1:] / point.Q_A, components[1:]))
        projected = time - recoil / point.Q_A * longitudinal
        expected = [np.vdot(time, time).real, np.vdot(longitudinal, time).real,
                    np.vdot(longitudinal, longitudinal).real, np.vdot(projected, projected).real]
        np.testing.assert_allclose(got[:4], np.asarray(expected) / 2, rtol=2e-8)

    def test_full_integral_and_two_distinct_interferences(self):
        row = projection.integrate(200., order=(12, 6, 4))
        self.assertAlmostEqual(row['L00_GeV2'] / 16087108.515505519, 1., delta=3e-8)
        self.assertAlmostEqual(row['LC_GeV2'] / 16087038.51319305, 1., delta=3e-8)
        self.assertLess(row['mix_0L_GeV2'], 0.)
        self.assertGreater(row['LL_weighted_GeV2'], 0.)
        self.assertGreater(row['LC_ab_interference_GeV2'] / row['LC_GeV2'], .1)
        self.assertAlmostEqual((row['L00_GeV2'] + row['mix_0L_GeV2'] + row['LL_weighted_GeV2']) / row['LC_GeV2'], 1., places=12)
        self.assertAlmostEqual((row['LC_a_GeV2'] + row['LC_b_GeV2'] + row['LC_ab_interference_GeV2']) / row['LC_GeV2'], 1., places=12)

    def test_closed_phase_space_and_undefined_ratio(self):
        for recoil, speed in [(100., 776.), (200., 600.), (700., 776.)]:
            row = projection.integrate(recoil, speed=speed)
            self.assertEqual(row['LC_GeV2'], 0.)
            self.assertEqual(row['LL_GeV2'], 0.)
            self.assertIsNone(row['LC_over_L00'])

    def test_pole_width_and_zero_width_are_not_interchangeable(self):
        zero = projection.integrate(267., order=(12, 6, 4))
        pole = projection.integrate(267., order=(12, 6, 4), pole=True)
        self.assertTrue(.8 < pole['LC_GeV2'] / zero['LC_GeV2'] < .99)
        self.assertTrue(85. < zero['pole_clearance_keV'] < 95.)
        with self.assertRaises(ValueError):
            projection.integrate(330., speed=900., order=(4, 4, 4))


if __name__ == '__main__':
    unittest.main()
