import math
import sys
import unittest
from pathlib import Path

from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))
sys.path.insert(0, str(HERE))

from isotope_mass_schemes import isotope_mass_GeV
from run_ame2020_xe131_halo_partial import (
    A,
    load_afh_response,
    mb_untruncated_pdf,
    shm_truncated_pdf,
    compute_partial_rate,
)


class Ame2020Xe131PartialRateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response_csv = HERE / "output" / "afh_default_xe131_WM00.csv"
        cls.response_interp, cls.q, cls.r = load_afh_response(cls.response_csv)

    def test_mass_is_the_ame2020_cod2022_value(self):
        self.assertAlmostEqual(
            isotope_mass_GeV(131, "ame2020_nuclear"),
            121.9099223838014,
            places=10,
        )

    def test_afh_response_grid_has_physical_zero_momentum_normalization(self):
        self.assertEqual(len(self.q), 2401)
        self.assertAlmostEqual(float(self.r[0]), A * A, places=7)
        self.assertTrue(math.isfinite(float(self.response_interp(0.157))))

    def test_halo_speed_pdfs_are_normalized(self):
        shm_norm = quad(
            lambda v: shm_truncated_pdf(v, 220.0, 232.0, 544.0),
            0.0,
            776.0,
            epsabs=1e-12,
            epsrel=1e-12,
            points=[312.0],
        )[0]
        mb_norm = quad(
            lambda v: mb_untruncated_pdf(v, 220.0, 232.0),
            0.0,
            3000.0,
            epsabs=1e-12,
            epsrel=1e-12,
        )[0]
        self.assertAlmostEqual(shm_norm, 1.0, delta=2e-10)
        self.assertAlmostEqual(mb_norm, 1.0, delta=2e-10)

    def test_exact_recoil_momentum_is_used_for_afh_response(self):
        row = compute_partial_rate(
            benchmark="black_ms360_dm1",
            er_keV=101.0,
            halo_model="shm_cutoff",
            nv=8,
            nw=8,
            nz=8,
            nphi=4,
            response_interp=self.response_interp,
            mchi=1000.0,
            mV=10.0,
            coupling_product_sq=1.0e-8,
            g2=1.0,
            rho_dm=0.3,
            v0=220.0,
            ve=232.0,
            vesc=544.0,
            untruncated_vmax=1600.0,
        )
        mA = isotope_mass_GeV(131, "ame2020_nuclear")
        ER = 101.0e-6
        q_exact = math.sqrt(2.0 * mA * ER + ER * ER)
        q_nr = math.sqrt(2.0 * mA * ER)
        self.assertAlmostEqual(row["q_response_exact_GeV"], q_exact, places=14)
        self.assertAlmostEqual(
            row["q_response_NR_diagnostic_GeV"], q_nr, places=14
        )
        self.assertGreater(row["q_response_exact_GeV"], row["q_response_NR_diagnostic_GeV"])
        self.assertFalse(row["speed_support_open"])
        self.assertEqual(row["Xe131_partial_rate_events_kg_day_keV"], 0.0)


if __name__ == "__main__":
    unittest.main()
