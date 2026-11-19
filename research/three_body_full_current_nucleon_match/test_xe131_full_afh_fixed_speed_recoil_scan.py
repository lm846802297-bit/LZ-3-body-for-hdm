import unittest

import numpy as np

from xe131_full_afh_fixed_speed_recoil_scan import (
    EXPECTED_CHARGE_RATIOS,
    FORMAL_WIDTH_SCHEMES,
    RESPONSE_NAMES,
    contract_six_channels,
    recoil_cases,
)


class Xe131FullAFHRecoilScanTests(unittest.TestCase):
    def setUp(self):
        self.q = 0.22
        self.ER = 200.0e-6
        self.F1 = 2.66 / 3.0
        self.F2 = -0.468 / 3.0
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
            result["D_full_six_channel_candidate"],
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
            "B_over_A_reference",
            "C_over_A_reference",
            "PhiPP_over_B_correction",
            "D_over_C_charge_only",
            "spatial_over_C_charge_only",
            "D_over_A_reference",
        ):
            self.assertAlmostEqual(a[key], b[key], places=12, msg=key)

    def test_A_B_C_D_hierarchy_is_normalized_to_effective_nucleon_current(self):
        result = contract_six_channels(
            self.L, self.q, self.ER, self.responses, self.F1, self.F2
        )
        self.assertAlmostEqual(
            result["B_over_A_reference"],
            result["coefficients"]["C_M"] * self.responses["M"] /
            (result["A_reference_M"]),
            places=13,
        )
        self.assertAlmostEqual(
            result["D_over_A_reference"],
            result["D_full_six_channel_candidate"] /
            result["A_reference_M"],
            places=13,
        )
        self.assertGreater(result["A_reference_M"], 0.0)

    def test_formal_six_channel_scan_uses_pole_width_only(self):
        self.assertEqual(FORMAL_WIDTH_SCHEMES, ("pole",))

    def test_two_recoil_anchors_are_not_mixed_into_one_benchmark(self):
        cases = {case["name"]: case for case in recoil_cases()}
        self.assertEqual(cases["off_pole_dm450"]["delta_m_GeV"], 450.0e-6)
        self.assertEqual(cases["near_pole_dm362"]["delta_m_GeV"], 362.0e-6)
        self.assertIn(("off_pole_dm450", 200.0), EXPECTED_CHARGE_RATIOS)
        self.assertIn(("near_pole_dm362", 267.0), EXPECTED_CHARGE_RATIOS)


if __name__ == "__main__":
    unittest.main()
