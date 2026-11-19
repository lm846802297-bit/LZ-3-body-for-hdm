import unittest

import numpy as np

from xe131_full_afh_fixed_speed_recoil_scan import (
    EXPECTED_ORIGINAL_AFH_RATIOS,
    FORMAL_WIDTH_SCHEMES,
    FORM_FACTOR_PRESCRIPTIONS,
    RESPONSE_NAMES,
    contract_six_channels,
    nucleon_form_factors,
    recoil_cases,
)


class Xe131FullAFHRecoilScanTests(unittest.TestCase):
    def setUp(self):
        self.q = 0.22
        self.ER = 200.0e-6
        self.F1 = 2.66
        self.F2 = -0.468
        self.L = np.diag([1.0e5, 1.0e-3, 1.0e-3, 1.0e-5]).astype(complex)
        self.responses = {
            "M": 100.0,
            "PhiPP": 5.0,
            "MPhiPP": -10.0,
            "Delta": 1.0,
            "SigmaPrime": 0.5,
            "SigmaPrimeDelta": -0.4,
        }

    def test_six_response_set_contains_all_diagonal_and_mixed_channels(self):
        self.assertEqual(
            set(RESPONSE_NAMES),
            {"M", "PhiPP", "MPhiPP", "Delta", "SigmaPrime", "SigmaPrimeDelta"},
        )

    def test_signed_interference_terms_are_retained(self):
        result = contract_six_channels(
            self.L, self.q, self.ER, self.responses, self.F1, self.F2
        )
        self.assertLess(result["charge_terms"]["MPhiPP"], 0.0)
        # C_{Sigma' Delta} and W_{Sigma' Delta} are both negative here.
        self.assertGreater(result["spatial_terms"]["SigmaPrimeDelta"], 0.0)
        self.assertAlmostEqual(
            result["full_six_channel_candidate"],
            result["charge_only"] + result["spatial_candidate"],
            places=10,
        )

    def test_common_phase_space_normalization_cancels_from_ratios(self):
        a = contract_six_channels(
            self.L, self.q, self.ER, self.responses, self.F1, self.F2
        )
        b = contract_six_channels(
            17.0 * self.L, self.q, self.ER, self.responses, self.F1, self.F2
        )
        for key in (
            "finite_t_M_over_original_AFH_M_baseline",
            "charge_only_over_finite_t_M",
            "full_over_finite_t_M",
            "PhiPP_over_finite_t_M_correction",
            "full_over_charge_only",
            "spatial_over_charge_only",
            "charge_only_over_original_AFH_M_baseline",
            "full_over_original_AFH_M_baseline",
        ):
            self.assertAlmostEqual(a[key], b[key], places=12, msg=key)

    def test_full_six_channel_ratio_uses_same_finite_t_M_baseline(self):
        result = contract_six_channels(
            self.L, self.q, self.ER, self.responses, self.F1, self.F2
        )
        self.assertAlmostEqual(
            result["charge_only_over_finite_t_M"],
            result["PhiPP_over_finite_t_M_correction"] + 1.0,
            places=14,
        )
        self.assertAlmostEqual(
            result["full_over_finite_t_M"],
            result["full_six_channel_candidate"] / result["finite_t_M"],
            places=14,
        )
        self.assertNotAlmostEqual(
            result["full_over_finite_t_M"],
            result["full_over_original_AFH_M_baseline"],
            places=6,
        )

    def test_original_afh_baseline_retains_finite_q_nuclear_response(self):
        result = contract_six_channels(
            self.L, self.q, self.ER, self.responses, self.F1, self.F2
        )
        LC = result["coefficients"]["L_C_continuity_adjusted_charge_weight"]
        self.assertAlmostEqual(
            result["original_AFH_M_baseline"],
            9.0 * LC * self.responses["M"],
            places=12,
        )
        self.assertAlmostEqual(
            result["q0_M_reference"], result["original_AFH_M_baseline"], places=14
        )

    def test_low_order_form_factor_uses_full_one_body_tN(self):
        qA = 0.22
        omega = 200.0e-6
        tN = omega * omega - qA * qA
        f1, f2 = nucleon_form_factors(
            qA, "bishara_linear", tN_GeV2=tN
        )
        self.assertAlmostEqual(f1, 3.0 - 8.392 * (-tN), places=13)
        self.assertAlmostEqual(f2, -0.552, places=13)

    def test_both_low_order_and_zexp_form_factor_inputs_are_available(self):
        self.assertEqual(FORM_FACTOR_PRESCRIPTIONS, ("bishara_linear", "isoscalar_zexp"))
        f1_linear, f2_linear = nucleon_form_factors(self.q, "bishara_linear")
        f1_zexp, f2_zexp = nucleon_form_factors(self.q, "isoscalar_zexp")
        self.assertNotAlmostEqual(f1_linear, f1_zexp, places=5)
        self.assertNotAlmostEqual(f2_linear, f2_zexp, places=5)

    def test_formal_six_channel_scan_uses_pole_width_only(self):
        self.assertEqual(FORMAL_WIDTH_SCHEMES, ("pole",))

    def test_two_recoil_anchors_are_not_mixed_into_one_benchmark(self):
        cases = {case["name"]: case for case in recoil_cases()}
        self.assertEqual(cases["off_pole_dm450"]["delta_m_GeV"], 450.0e-6)
        self.assertEqual(cases["near_pole_dm362"]["delta_m_GeV"], 362.0e-6)
        self.assertIn(
            ("isoscalar_zexp", "off_pole_dm450", 200.0),
            EXPECTED_ORIGINAL_AFH_RATIOS,
        )
        self.assertIn(
            ("isoscalar_zexp", "near_pole_dm362", 267.0),
            EXPECTED_ORIGINAL_AFH_RATIOS,
        )


if __name__ == "__main__":
    unittest.main()
