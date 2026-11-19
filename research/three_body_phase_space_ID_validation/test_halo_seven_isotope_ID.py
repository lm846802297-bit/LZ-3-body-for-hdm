import math
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from validate_halo_seven_isotope_ID import (
    i_of_d, shm_speed_pdf, d_nr, exact_speed_threshold,
    nr_speed_threshold, ISOTOPES, read_csv, ISOTOPE_WEIGHTS,
)
import phase_space_convergence as psc


class HaloSevenIsotopeApproximationTests(unittest.TestCase):
    def test_i_of_d_threshold_and_monotonicity(self):
        ms = 300e-6
        self.assertEqual(i_of_d(0.0, ms), 0.0)
        self.assertEqual(i_of_d(-1e-6, ms), 0.0)
        values = [i_of_d(x*1e-3, ms) for x in (0.1, 0.2, 0.5, 1.0)]
        self.assertTrue(all(b > a for a, b in zip(values[:-1], values[1:])))

    def test_truncated_shm_normalization(self):
        # Midpoint integration is sufficient for a lightweight normalization test.
        import numpy as np
        v = np.linspace(0.0, 776.0, 20001)
        f = np.asarray([shm_speed_pdf(float(x)) for x in v])
        self.assertLess(abs(float(np.trapezoid(f, v))-1.0), 2e-4)

    def test_seven_afh_isotopes_and_abundance_coverage(self):
        rows = read_csv(ISOTOPE_WEIGHTS)
        available = [r for r in rows if r["AFH_default_density_available"].lower()=="true"]
        self.assertEqual(tuple(int(r["A"]) for r in available), ISOTOPES)
        coverage = sum(float(r["natural_atom_fraction"]) for r in available)
        self.assertAlmostEqual(coverage, 0.998158, places=6)

    def test_nr_threshold_matches_dnr_zero(self):
        mchi, ms, mA, ER = 1000.0, 300e-6, 121.90971983538435, 248e-6
        vmin = nr_speed_threshold(ER, mchi, ms, mA)
        self.assertLess(abs(d_nr(ER, vmin, mchi, ms, mA)), 1e-12)

    def test_exact_threshold_is_finite_and_open_above(self):
        mchi, ms, mA, ER = 1000.0, 300e-6, 121.90971983538435, 248e-6
        vmin = exact_speed_threshold(ER, mchi, ms, mA)
        self.assertTrue(math.isfinite(vmin))
        self.assertGreater(eq_dummy := vmin, 0.0)
        self.assertLess(eq_dummy, 776.0)

    def test_threshold_regularized_full_kernel_converges(self):
        mchi, ms, delta_m = 1000.0, 300e-6, 10e-3
        mA, ER, speed = 121.90971983538435, 200e-6, 776.0
        coarse = psc.integrate_i6(
            mchi, ms, delta_m, mA, ER, speed,
            nW=6, nz=6, nphi=4, mapping="threshold_u2",
            width_scheme="zero",
        )
        reference = psc.integrate_i6(
            mchi, ms, delta_m, mA, ER, speed,
            nW=48, nz=24, nphi=16, mapping="threshold_u2",
            width_scheme="zero",
        )
        self.assertGreater(coarse, 0.0)
        self.assertLess(abs(coarse/reference-1.0), 2e-6)


if __name__ == "__main__":
    unittest.main()
