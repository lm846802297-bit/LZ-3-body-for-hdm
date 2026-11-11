import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from joint_xe131 import (  # noqa: E402
    differential_cross_section,
    isotope_mass_GeV,
    load_nuclear_response,
)


RESPONSE_DIR = HERE / "results" / "anand_wm_response"


class JointXe131Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gcn = load_nuclear_response(
            RESPONSE_DIR / "xe131_GCN_WM.csv", 131, "gcn"
        )
        cls.jj55 = load_nuclear_response(
            RESPONSE_DIR / "xe131_JJ55_WM.csv", 131, "jj55"
        )
        cls.mA = isotope_mass_GeV(131)

    def evaluate(self, response, ER_keV=200.0, mV_GeV=None, coupling_sq=1e-8):
        return differential_cross_section(
            response,
            mchi_GeV=1000.0,
            ms_GeV=0.0003,
            delta_m_GeV=0.001,
            ER_GeV=ER_keV * 1e-6,
            speed_km_s=776.0,
            coupling_product_sq=coupling_sq,
            mV_GeV=mV_GeV,
            width_scheme="zero",
            nw=8,
            nz=8,
            nphi=4,
        )

    def test_zero_momentum_normalization(self):
        self.assertAlmostEqual(self.gcn.R0, 131.0**2, delta=0.03)
        self.assertAlmostEqual(self.jj55.R0, 131.0**2, delta=0.03)

    def test_response_uses_manuscript_y_convention(self):
        ER = 200.0e-6
        R, q_response = self.gcn.at_recoil(ER, self.mA)
        self.assertAlmostEqual(q_response, math.sqrt(2.0 * self.mA * ER), places=14)
        q_exact = math.sqrt(2.0 * self.mA * ER + ER * ER)
        self.assertGreater(q_exact, q_response)
        self.assertGreater(R, 0.0)

    def test_joint_cross_section_is_finite_and_factorized(self):
        result = self.evaluate(self.gcn, mV_GeV=0.1)
        self.assertTrue(result["phase_space_open"])
        self.assertTrue(result["chi2_on_shell_closed"])
        self.assertGreater(result["R_A"], 0.0)
        self.assertGreater(result["I6_GeV2"], 0.0)
        self.assertGreater(result["C_A_GeV"], 0.0)
        self.assertGreater(result["dsigma_dER_GeVminus3"], 0.0)
        self.assertAlmostEqual(
            result["dsigma_dER_GeVminus3"]
            * result["propagator_denominator_GeV4"],
            result["C_A_GeV"],
            delta=abs(result["C_A_GeV"]) * 2e-13,
        )

    def test_mediator_mass_is_not_silently_assumed(self):
        result = self.evaluate(self.gcn, mV_GeV=None)
        self.assertIsNone(result["dsigma_dER_GeVminus3"])
        self.assertIsNone(result["propagator_denominator_GeV4"])
        self.assertGreater(result["C_A_GeV"], 0.0)

    def test_gcn_and_jj55_share_three_body_kernel(self):
        gcn = self.evaluate(self.gcn)
        jj55 = self.evaluate(self.jj55)
        self.assertAlmostEqual(gcn["I6_GeV2"], jj55["I6_GeV2"], places=12)
        self.assertAlmostEqual(
            jj55["C_A_GeV"] / gcn["C_A_GeV"],
            jj55["R_A"] / gcn["R_A"],
            places=11,
        )

    def test_three_body_kinematic_closure(self):
        # At this recoil and speed, a 300 keV scalar is not kinematically open.
        result = self.evaluate(self.gcn, ER_keV=101.0)
        self.assertFalse(result["phase_space_open"])
        self.assertEqual(result["I6_GeV2"], 0.0)
        self.assertEqual(result["C_A_GeV"], 0.0)


if __name__ == "__main__":
    unittest.main()
