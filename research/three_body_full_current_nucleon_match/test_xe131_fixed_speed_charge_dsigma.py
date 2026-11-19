import unittest

from xe131_fixed_speed_charge_dsigma import (
    MA_XE131_GEV,
    MN_GEV,
    WIDTH_SCHEMES,
    canonical_sha256,
    exact_qA_GeV,
    charge_sector_kernels,
    xe131_common_matrix_normalization_c0,
    apply_xe131_common_matrix_normalization,
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

    def test_native_AFH_A_B_C_ratio_anchors(self):
        # PCHIP response ratios from the provenance-pinned native AFH v6.0
        # Xe-131 grid. The common C0 and factor-four normalizations cancel.
        anchors = {
            200.0: (0.036955940801758985, -0.19120929699010936,
                    0.7398828761262942, 0.9969554024414953, 0.7376302305280606),
            267.0: (19.84506258174282, -4.282964386166763,
                    0.6621749872241893, 0.9146368782933962, 0.6056496631987021),
        }
        for er_keV, (wphi_over_wm, wmphi_over_wm, expected_ba,
                     expected_cb, expected_ca) in anchors.items():
            qA = exact_qA_GeV(MA_XE131_GEV, er_keV)
            result = charge_sector_kernels(
                1.0, qA,
                {"M": 1.0, "PhiPP": wphi_over_wm, "MPhiPP": wmphi_over_wm},
                ER_keV=er_keV,
            )
            self.assertAlmostEqual(result["B_over_A_reference"], expected_ba, places=11)
            self.assertAlmostEqual(result["C_over_B_baseline"], expected_cb, places=11)
            self.assertAlmostEqual(result["C_over_A_reference"], expected_ca, places=11)

    def test_native_C0_is_derived_from_raw_M_zero_anchor(self):
        raw_m_zero = 4289.895955714992
        c0 = xe131_common_matrix_normalization_c0(raw_m_zero)
        self.assertAlmostEqual(c0, 1.0000825298069376, places=14)

    def test_native_C0_is_applied_once_to_all_three_physical_channels(self):
        raw_m_zero = 4289.895955714992
        c0 = xe131_common_matrix_normalization_c0(raw_m_zero)
        physical_before = {
            "M": [4.0 * raw_m_zero, 4.0 * 149.2743467449586],
            "PhiPP": [4.0 * 149.2743467449586, 4.0 * 120.0],
            "MPhiPP": [4.0 * -799.9643348289546, 4.0 * -500.0],
        }
        physical_after, used_c0 = apply_xe131_common_matrix_normalization(
            physical_before, raw_m_zero
        )
        self.assertAlmostEqual(used_c0, c0, places=15)
        self.assertAlmostEqual(physical_after["M"][0], 131.0**2, places=10)
        for name in ("M", "PhiPP", "MPhiPP"):
            for before, after in zip(physical_before[name], physical_after[name]):
                self.assertAlmostEqual(after / before, c0, places=14)

    def test_native_csv_hash_is_line_ending_stable(self):
        lf = b"q,value\n0.1,2\n"
        crlf = b"q,value\r\n0.1,2\r\n"
        self.assertEqual(canonical_sha256(lf), canonical_sha256(crlf))


if __name__ == "__main__":
    unittest.main()
