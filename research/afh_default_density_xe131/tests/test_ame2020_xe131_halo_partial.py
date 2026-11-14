import math
import sys
import unittest
from pathlib import Path

from scipy.integrate import quad

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / "figure2_full_reproduction"))
sys.path.insert(0, str(HERE))

from isotope_mass_schemes import isotope_mass_GeV
from run_ame2020_xe131_halo_partial import (
    A,
    AFH_DEFAULT_XE_ISOTOPES,
    AFH_FULL_RESPONSE_GRID_ARCHIVED_ISOTOPES,
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

    def test_afh_default_density_isotope_set_is_distinct_from_archived_grid(self):
        self.assertEqual(
            AFH_DEFAULT_XE_ISOTOPES,
            {128, 129, 130, 131, 132, 134, 136},
        )
        self.assertNotIn(124, AFH_DEFAULT_XE_ISOTOPES)
        self.assertNotIn(126, AFH_DEFAULT_XE_ISOTOPES)
        # The present partial fold only loads the full Xe-131 q-grid.
        self.assertEqual(AFH_FULL_RESPONSE_GRID_ARCHIVED_ISOTOPES, {131})
        self.assertEqual(A, 131)

    def test_mass_is_the_ame2020_cod2022_value(self):
        self.assertAlmostEqual(
            isotope_mass_GeV(131, "ame2020_nuclear"),
            121.90992244721734,
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

    def test_nr_approx_momentum_is_diagnostic_only(self):
        row = compute_partial_rate(
            benchmark="black_ms360_dm1",
            er_keV=101.0,
            halo_model="shm_cutoff",
            mass_scheme="ame2020_nuclear",
            response_q_convention="nr_approx",
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
        self.assertAlmostEqual(row["q_response_used_GeV"], q_nr, places=14)
        self.assertAlmostEqual(row["q_response_NR_GeV"], q_nr, places=14)
        self.assertAlmostEqual(row["q_kinematics_exact_GeV"], q_exact, places=14)
        self.assertGreater(row["q_kinematics_exact_GeV"], row["q_response_used_GeV"])
        self.assertAlmostEqual(
            row["R_A_AFH_equal_pn"], float(self.response_interp(q_nr)), places=10
        )
        self.assertFalse(row["speed_support_open"])
        self.assertEqual(row["Xe131_partial_rate_events_kg_day_keV"], 0.0)


    def test_exact_spatial_and_nr_approx_response_q_are_separate_but_kinematics_identical(self):
        common = dict(
            benchmark="green_ms300_dm1",
            er_keV=267.0,
            halo_model="shm_cutoff",
            mass_scheme="ame2020_nuclear",
            nv=4,
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
        nr = compute_partial_rate(
            **common, response_q_convention="nr_approx"
        )
        exact = compute_partial_rate(
            **common, response_q_convention="exact_spatial"
        )
        self.assertAlmostEqual(
            nr["q_response_used_GeV"],
            math.sqrt(2.0 * nr["mA_GeV"] * 267.0e-6),
            places=14,
        )
        self.assertAlmostEqual(
            exact["q_response_used_GeV"],
            math.sqrt(2.0 * exact["mA_GeV"] * 267.0e-6 + (267.0e-6)**2),
            places=14,
        )
        self.assertGreater(
            exact["q_response_used_GeV"], nr["q_response_used_GeV"]
        )
        self.assertAlmostEqual(
            nr["vmin_km_s"], exact["vmin_km_s"], places=12
        )
        self.assertAlmostEqual(
            nr["R_A_AFH_equal_pn"],
            float(self.response_interp(nr["q_response_used_GeV"])),
            places=10,
        )
        self.assertAlmostEqual(
            exact["R_A_AFH_equal_pn"],
            float(self.response_interp(exact["q_response_used_GeV"])),
            places=10,
        )
        self.assertNotEqual(
            nr["R_A_AFH_equal_pn"], exact["R_A_AFH_equal_pn"]
        )
        self.assertTrue(nr["speed_support_open"])
        self.assertTrue(exact["speed_support_open"])


if __name__ == "__main__":
    unittest.main()
