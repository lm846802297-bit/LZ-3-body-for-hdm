import unittest
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from recompute_afh_four_benchmarks import M_A_GEV, recompute, validate
BASE = HERE / "input" / "figure2_recalc_mV10_g2_1_v800_Xe131_full_5keV.csv"
AFH = HERE / "output" / "afh_default_xe131_WM00.csv"


class TestAFHFourBenchmarks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.long, cls.wide = recompute(BASE, AFH)

    def test_row_counts_and_benchmarks(self):
        self.assertEqual(len(self.long), 1920)
        self.assertEqual(len(self.wide), 640)
        self.assertEqual(self.long["benchmark"].nunique(), 4)
        self.assertEqual(set(self.long["model"]), {"AFH_default", "GCN", "JJ55"})

    def test_response_momentum_uses_exact_nuclear_mass_shell(self):
        er_GeV = self.long["ER_keV"].to_numpy(dtype=float) * 1e-6
        q_exact = np.sqrt(2.0 * M_A_GEV * er_GeV + er_GeV**2)
        np.testing.assert_allclose(
            self.long["q_response_GeV"].to_numpy(dtype=float),
            q_exact,
            rtol=2e-12,
            atol=2e-14,
        )

    def test_response_is_not_stale_gcn_copy(self):
        row = self.wide[self.wide["ER_keV"] == 200].iloc[0]
        self.assertNotAlmostEqual(row["R_A_AFH"], row["R_A_GCN"], places=5)
        self.assertAlmostEqual(row["R_A_AFH"] / row["R_A_GCN"], 0.95244612, places=6)

    def test_afh_cross_section_uses_physical_response_ratio(self):
        for benchmark, group in self.long.groupby("benchmark"):
            g = group[group["model"] == "GCN"].sort_values("ER_keV")
            a = group[group["model"] == "AFH_default"].sort_values("ER_keV")
            mask = g["phase_space_open"].astype(bool).to_numpy()
            ratio_sigma = a.loc[mask, "dsigma_GeVminus3"].to_numpy() / g.loc[
                mask, "dsigma_GeVminus3"
            ].to_numpy()
            ratio_response = a.loc[mask, "R_A"].to_numpy() / g.loc[mask, "R_A"].to_numpy()
            self.assertTrue(np.allclose(ratio_sigma, ratio_response, rtol=2e-12, atol=2e-12))

    def test_three_body_integral_is_shared(self):
        for benchmark, group in self.long.groupby("benchmark"):
            values = [
                group[group["model"] == model].sort_values("ER_keV")["I6_GeV2"].to_numpy()
                for model in ["AFH_default", "GCN", "JJ55"]
            ]
            self.assertTrue(np.allclose(values[0], values[1], rtol=1e-12, atol=1e-12))
            self.assertTrue(np.allclose(values[1], values[2], rtol=1e-12, atol=1e-12))

    def test_expected_first_open_grid_points(self):
        expected = {
            "red_ms200_dm1": 35.0,
            "green_ms300_dm1": 100.0,
            "black_ms360_dm1": 190.0,
            "blue_ms300_dm10": 100.0,
        }
        for benchmark, energy in expected.items():
            group = self.long[
                (self.long["benchmark"] == benchmark) & (self.long["model"] == "GCN")
            ]
            opened = group[group["phase_space_open"].astype(bool)]
            self.assertEqual(float(opened["ER_keV"].min()), energy)

    def test_validate_accepts_archived_tables(self):
        validate(self.long, self.wide)


if __name__ == "__main__":
    unittest.main()
