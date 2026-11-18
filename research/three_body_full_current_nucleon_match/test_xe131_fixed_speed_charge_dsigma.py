import unittest

from xe131_fixed_speed_charge_dsigma import (
    MA_XE131_GEV,
    canonical_sha256,
    exact_qA_GeV,
    charge_sector_kernels,
)


class TestXe131FixedSpeedChargeDifferentialCrossSection(unittest.TestCase):
    def test_exact_recoil_momenta(self):
        self.assertAlmostEqual(MA_XE131_GEV, 121.90971983538435, places=12)
        self.assertAlmostEqual(exact_qA_GeV(MA_XE131_GEV, 200.0), 0.22082555996567457, places=13)
        self.assertAlmostEqual(exact_qA_GeV(MA_XE131_GEV, 267.0), 0.25514674538605275, places=13)

    def test_ratio_is_independent_of_common_LC(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        a = charge_sector_kernels(1.0, 0.22, responses)
        b = charge_sector_kernels(1.0e8, 0.22, responses)
        self.assertAlmostEqual(
            a["full_charge_over_pointlike_M"],
            b["full_charge_over_pointlike_M"],
            places=13,
        )

    def test_interference_is_signed_and_retained(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        out = charge_sector_kernels(1.0, 0.22, responses)
        terms = out["kernels_with_common_LC"]
        self.assertLess(terms["M_Phi_interference"], 0.0)
        self.assertGreater(terms["finite_t_M_plus_PhiPP"], 0.0)

    def test_native_csv_hash_is_line_ending_stable(self):
        lf = b"q,value\n0.1,2\n"
        crlf = b"q,value\r\n0.1,2\r\n"
        self.assertEqual(canonical_sha256(lf), canonical_sha256(crlf))

    def test_normalization_audit_distinguishes_cM_from_F1(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        out = charge_sector_kernels(1.0, 0.22, responses)
        self.assertNotAlmostEqual(
            out["full_charge_over_pointlike_M"],
            out["legacy_F1_squared_ratio_for_normalization_audit"],
            places=6,
        )


if __name__ == "__main__":
    unittest.main()
