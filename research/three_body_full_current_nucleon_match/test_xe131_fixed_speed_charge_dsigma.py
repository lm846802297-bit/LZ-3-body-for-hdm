import unittest

from xe131_fixed_speed_charge_dsigma import (
    MA_XE131_GEV,
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
        self.assertAlmostEqual(exact_qA_GeV(MA_XE131_GEV, 200.0), 0.22082555996567457, places=13)
        self.assertAlmostEqual(exact_qA_GeV(MA_XE131_GEV, 267.0), 0.25514674538605275, places=13)

    def test_ratio_is_independent_of_common_LC(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        a = charge_sector_kernels(1.0, 0.22, responses)
        b = charge_sector_kernels(1.0e8, 0.22, responses)
        self.assertAlmostEqual(
            a["full_charge_over_finite_t_M"],
            b["full_charge_over_finite_t_M"],
            places=13,
        )
        self.assertAlmostEqual(
            a["full_charge_over_AFH_finite_size_M_baseline"],
            b["full_charge_over_AFH_finite_size_M_baseline"],
            places=13,
        )
        self.assertAlmostEqual(
            a["full_charge_over_AFH_finite_size_M_baseline"],
            b["full_charge_over_AFH_finite_size_M_baseline"],
            places=13,
        )

    def test_bishara_form_factor_uses_full_one_body_tN(self):
        qA = exact_qA_GeV(MA_XE131_GEV, 200.0)
        ER = 200.0e-6
        tN = ER * ER - qA * qA
        result = charge_sector_kernels(
            1.0, qA, {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3},
            "bishara_linear", tN_GeV2=tN,
        )
        QN2 = -tN
        self.assertAlmostEqual(result["F1V_quark_finite_t"], 3.0 - 8.392 * QN2, places=13)
        self.assertAlmostEqual(result["F2V_quark_finite_t"], -0.552, places=13)
        self.assertAlmostEqual(result["F1N_effective_finite_t"], result["F1V_quark_finite_t"] / 3.0, places=14)
        self.assertAlmostEqual(result["F2N_effective_finite_t"], result["F2V_quark_finite_t"] / 3.0, places=14)
        self.assertNotAlmostEqual(QN2, qA * qA, places=12)

    def test_low_q2_and_zexp_form_factors_are_distinct_inputs(self):
        f1_linear, f2_linear = charge_sector_kernels(
            1.0, 0.22, {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3},
            "bishara_linear",
        )["F1V_quark_finite_t"], charge_sector_kernels(
            1.0, 0.22, {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3},
            "bishara_linear",
        )["F2V_quark_finite_t"]
        f1_zexp, f2_zexp = charge_sector_kernels(
            1.0, 0.22, {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3},
            "isoscalar_zexp",
        )["F1V_quark_finite_t"], charge_sector_kernels(
            1.0, 0.22, {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3},
            "isoscalar_zexp",
        )["F2V_quark_finite_t"]
        self.assertNotAlmostEqual(f1_linear, f1_zexp, places=5)
        self.assertNotAlmostEqual(f2_linear, f2_zexp, places=5)

    def test_interference_is_signed_and_retained(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        out = charge_sector_kernels(1.0, 0.22, responses)
        terms = out["kernels_with_common_LC"]
        self.assertLess(terms["M_Phi_interference"], 0.0)
        self.assertGreater(terms["finite_t_M_plus_PhiPP"], 0.0)
        self.assertAlmostEqual(
            terms["AFH_finite_size_M_baseline"],
            out["AFH_finite_size_M_baseline_kernel"],
            places=14,
        )
        self.assertAlmostEqual(
            out["full_charge_over_AFH_finite_size_M_baseline"],
            out["kernels_with_common_LC"]["finite_t_M_plus_PhiPP"]
            / out["kernels_with_common_LC"]["AFH_finite_size_M_baseline"],
            places=14,
        )

    def test_native_csv_hash_is_line_ending_stable(self):
        lf = b"q,value\n0.1,2\n"
        crlf = b"q,value\r\n0.1,2\r\n"
        self.assertEqual(canonical_sha256(lf), canonical_sha256(crlf))

    def test_gVN_basis_removes_the_quark_factor_three_from_absolute_kernel(self):
        responses = {"M": 2.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        out = charge_sector_kernels(1.0, 0.22, responses, "q0_anchor")
        self.assertAlmostEqual(
            out["AFH_finite_size_M_baseline_kernel"],
            1.0 * responses["M"],
            places=14,
        )
        self.assertAlmostEqual(
            out["nucleon_q0_M_only_kernel"],
            out["AFH_finite_size_M_baseline_kernel"],
            places=14,
        )
        self.assertAlmostEqual(
            out["F1N_effective_finite_t"], 1.0, places=14
        )
        self.assertAlmostEqual(
            out["F2N_effective_finite_t"], -0.184, places=14
        )
        self.assertAlmostEqual(
            out["full_charge_over_nucleon_finite_t_M_only"],
            out["full_charge_over_finite_t_M"],
            places=14,
        )
        self.assertAlmostEqual(
            out["full_charge_over_AFH_finite_size_M_baseline"],
            out["kernels_with_common_LC"]["finite_t_M_plus_PhiPP"]
            / out["kernels_with_common_LC"]["AFH_finite_size_M_baseline"],
            places=14,
        )


if __name__ == "__main__":
    unittest.main()
