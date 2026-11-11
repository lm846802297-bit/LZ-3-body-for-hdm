import math
import unittest
from scipy.integrate import quad

from rate_kinematics import (
    C_KM_S,
    mb_lab_speed_pdf,
    vmin_three_body_beta,
    vmin_three_body_km_s,
    wmax_squared,
)


class ThreeBodyKinematicsTests(unittest.TestCase):
    def test_vmin_solves_wmax_threshold(self):
        mchi, ms, mA, ER = 1000.0, 360e-6, 122.0, 258.178251676e-6
        vmin = vmin_three_body_km_s(mchi, ms, mA, ER)
        self.assertAlmostEqual(vmin, 776.0, places=5)
        w2 = wmax_squared(mchi, mA, ER, vmin)
        self.assertAlmostEqual(w2, (mchi + ms) ** 2, delta=2e-8)

    def test_keV_and_MeV_are_physically_distinct(self):
        v_keV = vmin_three_body_km_s(1000.0, 360e-6, 122.0, 270e-6)
        v_MeV = vmin_three_body_km_s(1000.0, 360e-3, 122.0, 270e-6)
        self.assertAlmostEqual(v_keV, 774.3, delta=0.2)
        self.assertGreater(v_MeV / C_KM_S, 0.7)

    def test_zero_scalar_mass_reduces_to_elastic_nonrelativistic_limit(self):
        beta = vmin_three_body_beta(1000.0, 0.0, 122.0, 100e-6)
        mu = 1000.0 * 122.0 / (1000.0 + 122.0)
        beta_el = math.sqrt(122.0 * 100e-6 / (2.0 * mu**2))
        self.assertAlmostEqual(beta, beta_el, delta=2e-6)

    def test_untruncated_mb_pdf_normalizes(self):
        norm, err = quad(lambda v: mb_lab_speed_pdf(v), 0.0, 3000.0, epsabs=1e-10)
        self.assertAlmostEqual(norm, 1.0, places=8)

    def test_speed_pdf_is_nonnegative(self):
        for v in (0.0, 100.0, 232.0, 500.0, 1000.0, 2000.0):
            self.assertGreaterEqual(mb_lab_speed_pdf(v), 0.0)


if __name__ == "__main__":
    unittest.main()
