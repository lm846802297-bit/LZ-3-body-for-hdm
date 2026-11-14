import sys
import unittest
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from compute_four_benchmark_dsigma import build, validate

BASE = HERE / "input" / "figure2_recalc_mV10_g2_1_v800_Xe131_full_5keV.csv"
AFH = HERE / "output" / "afh_default_xe131_WM00.csv"

class TestFourBenchmarkDifferentialCrossSections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build(BASE, AFH)

    def test_full_grid(self):
        self.assertEqual(len(self.data), 1920)
        self.assertEqual(self.data.benchmark.nunique(), 4)
        self.assertEqual(set(self.data.model), {"AFH_default", "GCN", "JJ55"})
        self.assertTrue(self.data.groupby(["benchmark","model"]).size().eq(160).all())

    def test_afh_response_is_not_stale_gcn_column(self):
        row = self.data[(self.data.benchmark=="red_ms200_dm1") &
                        (self.data.model=="AFH_default") &
                        (self.data.ER_keV==200)].iloc[0]
        self.assertAlmostEqual(row.R_A, 9.567669856, places=7)
        gcn = self.data[(self.data.benchmark=="red_ms200_dm1") &
                        (self.data.model=="GCN") &
                        (self.data.ER_keV==200)].iloc[0]
        self.assertNotAlmostEqual(row.R_A, gcn.R_A, places=5)

    def test_i6_is_shared(self):
        for _, group in self.data.groupby("benchmark"):
            arrays=[group[group.model==m].sort_values("ER_keV").I6_GeV2.to_numpy()
                    for m in ["AFH_default","GCN","JJ55"]]
            self.assertTrue(all(np.allclose(arrays[0],x,rtol=1e-12,atol=1e-12)
                                for x in arrays[1:]))

    def test_expected_phase_space_onsets(self):
        expected={"red_ms200_dm1":35.0,"green_ms300_dm1":100.0,
                  "black_ms360_dm1":190.0,"blue_ms300_dm10":100.0}
        for benchmark, energy in expected.items():
            g=self.data[(self.data.benchmark==benchmark)&(self.data.model=="GCN")]
            opened=g[g.phase_space_open]
            self.assertEqual(float(opened.ER_keV.min()),energy)

    def test_direct_eq6_reconstruction(self):
        validate(self.data)

if __name__=="__main__":
    unittest.main()
