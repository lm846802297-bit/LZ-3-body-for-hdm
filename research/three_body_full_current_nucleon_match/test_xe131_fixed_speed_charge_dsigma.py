import unittest

from xe131_fixed_speed_charge_dsigma import (
    MA_XE131_GEV,
    MN_GEV,
    WIDTH_SCHEMES,
    canonical_sha256,
    exact_qA_GeV,
    charge_sector_kernels,
)


class TestXe131FixedSpeedChargeDifferentialCrossSection(unittest.TestCase):
    def test_formal_fixed_speed_run_uses_pole_width_only(self):
        self.assertEqual(WIDTH_SCHEMES, ("pole",))

    def test_exact_recoil_momenta(self):
        self.assertAlmostEqual(MA_XE131_GEV, 121.90971983538435, places=12)
        self.assertAlmostEqual(
            exact_qA_GeV(MA_XE131_GEV, 200.0),
            0.22082555996567457,
            places=13,
        )
        self.assertAlmostEqual(
            exact_qA_GeV(MA_XE131_GEV, 267.0),
            0.25514674538605275,
            places=13,
        )

    def test_A_B_C_ratios_are_independent_of_common_LC(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        qA = exact_qA_GeV(MA_XE131_GEV, 200.0)
        a = charge_sector_kernels(1.0, qA, responses, ER_keV=200.0)
        b = charge_sector_kernels(1.0e8, qA, responses, ER_keV=200.0)
        for key in (
            "B_over_A_reference",
            "C_over_B_baseline",
            "C_over_A_reference",
        ):
            self.assertAlmostEqual(a[key], b[key], places=13)

    def test_formal_tN_is_tA_not_minus_spatial_qA2(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        er_keV = 200.0
        qA = exact_qA_GeV(MA_XE131_GEV, er_keV)
        out = charge_sector_kernels(1.0, qA, responses, ER_keV=er_keV)
        expected_tN = -2.0 * MA_XE131_GEV * er_keV * 1.0e-6
        self.assertAlmostEqual(out["tN_GeV2"], expected_tN, places=15)
        self.assertNotAlmostEqual(out["tN_GeV2"], -(qA * qA), places=10)
        self.assertAlmostEqual(
            out["F1N_effective"], out["F1V_quark_sum"] / 3.0, places=14
        )
        self.assertAlmostEqual(
            out["F2N_effective"], out["F2V_quark_sum"] / 3.0, places=14
        )

    def test_B_over_A_reproduces_adopted_bishara_baseline(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        expected = {200.0: 0.7398828761262942, 267.0: 0.6621749872241893}
        for er_keV, value in expected.items():
            qA = exact_qA_GeV(MA_XE131_GEV, er_keV)
            out = charge_sector_kernels(1.0, qA, responses, ER_keV=er_keV)
            self.assertAlmostEqual(out["B_over_A_reference"], value, places=12)

    def test_interference_is_signed_and_retained(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        out = charge_sector_kernels(
            1.0, exact_qA_GeV(MA_XE131_GEV, 200.0), responses, ER_keV=200.0
        )
        terms = out["kernels_with_common_LC"]
        self.assertLess(terms["M_Phi_interference"], 0.0)
        self.assertGreater(terms["C_M_plus_PhiPP"], 0.0)

    def test_native_csv_hash_is_line_ending_stable(self):
        lf = b"q,value\n0.1,2\n"
        crlf = b"q,value\r\n0.1,2\r\n"
        self.assertEqual(canonical_sha256(lf), canonical_sha256(crlf))


if __name__ == "__main__":
    unittest.main()
