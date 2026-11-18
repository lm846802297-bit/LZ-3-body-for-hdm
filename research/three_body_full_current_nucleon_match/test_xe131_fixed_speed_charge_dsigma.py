import unittest

from xe131_fixed_speed_charge_dsigma import exact_qA_GeV, charge_sector_kernels


class TestXe131FixedSpeedChargeDifferentialCrossSection(unittest.TestCase):
    def test_exact_recoil_momenta(self):
        mA = 121.9099224472
        self.assertAlmostEqual(exact_qA_GeV(mA, 200.0), 0.2208257434695511, places=13)
        self.assertAlmostEqual(exact_qA_GeV(mA, 267.0), 0.25514695741043986, places=13)

    def test_ratio_is_independent_of_common_L00(self):
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
        terms = out["kernels_with_common_L00"]
        self.assertLess(terms["M_Phi_interference"], 0.0)
        self.assertGreater(terms["finite_t_M_plus_PhiPP"], 0.0)

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
