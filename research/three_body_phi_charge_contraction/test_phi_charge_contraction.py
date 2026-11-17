import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import phi_charge_contraction as pc


class ChargeResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = pc.read_csv(pc.INPUT / "afh_vv_phi_xe131_full_grid_pr54_snapshot.csv")
        cls.selected = pc.read_csv(pc.INPUT / "afh_vv_phi_xe131_selected_points_pr54_snapshot.csv")
        cls.pr53 = pc.read_csv(
            pc.ROOT / "research/vector_current_response_audit/results/2026-11-18/"
            / "vector_current_response_audit.csv"
        )

    def test_afh_grid_identity_and_psd(self):
        stats = pc.validate_grid(self.grid)
        self.assertEqual(stats["points"], 2401)
        self.assertAlmostEqual(stats["dq_GeV"], 0.00025, places=10)
        self.assertLessEqual(stats["max_interference_correlation"], 1.0 + 2e-6)

    def test_zero_transfer_reduces_to_M_only(self):
        result = pc.charge_response_terms(0.0, 10.0, 2.0, -1.0, -0.15)
        self.assertAlmostEqual(result["eta"], 0.0)
        self.assertAlmostEqual(result["R_charge_over_M"], 1.0)

    def test_common_AFH_normalization_cancels(self):
        a = pc.charge_response_terms(0.255, 0.001, 0.02, -0.002, -0.15)
        b = pc.charge_response_terms(0.255, 0.004, 0.08, -0.008, -0.15)
        self.assertAlmostEqual(a["R_charge_over_M"], b["R_charge_over_M"], places=14)

    def test_200_keV_three_body_point(self):
        q = 0.22093060215101032
        r = pc.interpolate_response(self.grid, q, 8)
        out = pc.charge_response_terms(q, r["W_M00_AFH"], r["W_PhiPP_AFH"], r["W_MPhiPP_AFH"], -0.15)
        self.assertAlmostEqual(out["R_charge_over_M"], 0.9866406901, places=8)

    def test_267_keV_three_body_point(self):
        q = 0.2552681134213372
        r = pc.interpolate_response(self.grid, q, 8)
        out = pc.charge_response_terms(q, r["W_M00_AFH"], r["W_PhiPP_AFH"], r["W_MPhiPP_AFH"], -0.15)
        self.assertAlmostEqual(out["R_charge_over_M"], 0.8721076781, places=7)

    def test_benchmark_interpolation_converges(self):
        q = 0.2552681134213372
        r6, r8 = pc.interpolate_response(self.grid, q, 6), pc.interpolate_response(self.grid, q, 8)
        a = pc.charge_response_terms(q, r6["W_M00_AFH"], r6["W_PhiPP_AFH"], r6["W_MPhiPP_AFH"], -0.15)["R_charge_over_M"]
        b = pc.charge_response_terms(q, r8["W_M00_AFH"], r8["W_PhiPP_AFH"], r8["W_MPhiPP_AFH"], -0.15)["R_charge_over_M"]
        self.assertLess(abs(a - b), 1e-5)

    def test_exact_afh_minimum_uses_exact_selected_point(self):
        row = min(self.selected, key=lambda x: abs(float(x["q_min_MeV"]) - 256.271867617))
        q = float(row["q_min_MeV"]) / 1000.0
        out = pc.charge_response_terms(q, float(row["W_M00_AFH"]), float(row["W_PhiPP_AFH"]), float(row["W_MPhiPP_AFH"]), -0.15)
        self.assertAlmostEqual(out["R_charge_over_M"], 0.9688198375, places=8)

    def test_width_changes_I00_but_not_fixed_q_charge_ratio(self):
        rows = [x for x in self.pr53 if x["benchmark"] == "near_pole_362keV_g2_1"]
        self.assertEqual(len(rows), 3)
        qs = [float(x["qA_GeV"]) for x in rows]
        self.assertLess(max(qs) - min(qs), 1e-14)
        resp = pc.interpolate_response(self.grid, qs[0], 8)
        ratios = [pc.charge_response_terms(qs[0], resp["W_M00_AFH"], resp["W_PhiPP_AFH"], resp["W_MPhiPP_AFH"], -0.15)["R_charge_over_M"] for _ in rows]
        self.assertEqual(len(set(ratios)), 1)
        i00 = [float(x["I00"]) for x in rows]
        self.assertGreater(max(i00) / min(i00), 10.0)


if __name__ == "__main__":
    unittest.main()
