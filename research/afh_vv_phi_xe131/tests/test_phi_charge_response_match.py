import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from phi_charge_response_match import (
    charge_coefficients,
    matched_charge_response,
)


class PhiChargeResponseMatchTests(unittest.TestCase):
    def test_zero_transfer_has_no_phi_piece(self):
        c_m, c_phi = charge_coefficients(0.0)
        self.assertEqual(c_m, 3.0)
        self.assertEqual(c_phi, 0.0)

    def test_zero_phi_coupling_reduces_to_m_only(self):
        result = matched_charge_response(
            0.25, 0.2, 0.3, -0.1, f1=3.0, f2=-1.5
        )
        self.assertAlmostEqual(result["Q_Phi_over_Monly"], 1.0, places=14)
        self.assertAlmostEqual(
            result["M_Phi_interference_piece"], 0.0, places=14
        )
        self.assertAlmostEqual(
            result["PhiPP_squared_piece"], 0.0, places=14
        )

    def test_selected_second_wm_minimum(self):
        result = matched_charge_response(
            0.256271867617,
            8.6583324328133883e-5,
            1.0034095063316312e-2,
            -1.2662724509632033e-4,
        )
        self.assertAlmostEqual(result["eta_Phi_over_M"], 0.011840421386958, places=13)
        self.assertAlmostEqual(
            result["Q_Phi_over_Monly"], 0.981614194984591, places=12
        )
        self.assertAlmostEqual(
            result["delta_full_over_F1zero2_WM_percent"],
            -2.990612598663, places=10
        )

    def test_positive_semidefinite_response(self):
        result = matched_charge_response(
            0.256, 0.2, 0.3, -0.1
        )
        self.assertGreaterEqual(result["matched_charge_response"], 0.0)
        self.assertGreaterEqual(result["cauchy_schwarz_margin"], -1e-12)

    def test_rejects_cauchy_schwarz_violation(self):
        with self.assertRaises(ValueError):
            matched_charge_response(0.2, 1.0, 1.0, 1.01)


if __name__ == "__main__":
    unittest.main()
