from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from compare_er_grid_convergence import (
    BENCHMARKS,
    load_grid,
    summarize_benchmark,
)


def synthetic_grid(step_keV: int) -> pd.DataFrame:
    rows = []
    energies = np.arange(5.0, 800.0 + 0.5 * step_keV, float(step_keV))
    for benchmark in BENCHMARKS:
        for er in energies:
            response_shape = (
                1.0
                - 0.10 * np.exp(-((er - 102.0) / 5.0) ** 2)
                - 0.20 * np.exp(-((er - 269.0) / 6.0) ** 2)
                - 0.15 * np.exp(-((er - 546.0) / 7.0) ** 2)
            )
            dsigma = 1.0e-33 * (1.0 + 1.0e-4 * er)
            rows.append({
                "benchmark": benchmark,
                "ER_keV": er,
                "phase_space_open": 1,
                "R_A_physical_normalized": 131.0**2 * response_shape,
                "C0": 1.0000825298069378,
                "I6_GeV2": 1.0e-4 * (1.0 + 1.0e-4 * er),
                "width_scheme": "pole",
                "W2_mapping": "threshold_u2",
                "g2": 1.0,
                "nW": 16,
                "nz": 16,
                "nphi": 8,
                "dsigma_dER_GeVminus3": dsigma,
                "dsigma_without_factor4_GeVminus3": dsigma / 4.0,
                "dsigma_factor4_ratio": 4.0,
                "dsigma_cm2_per_keV": dsigma * 0.3893793721e-33,
            })
    return pd.DataFrame(rows)


class TestERGridConvergence(unittest.TestCase):
    def test_exact_5kev_and_1kev_grids_pass_for_smooth_spectrum(self):
        coarse = synthetic_grid(5)
        fine = synthetic_grid(1)
        result = summarize_benchmark(coarse, fine, BENCHMARKS[0])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["rows_5keV"], 160)
        self.assertEqual(result["rows_1keV"], 796)
        self.assertEqual(result["common_node_max_rel_dsigma"], 0.0)
        self.assertLessEqual(result["integral_relative_difference"], 1e-3)

    def test_fine_grid_area_change_is_detected(self):
        coarse = synthetic_grid(5)
        fine = synthetic_grid(1)
        mask = (fine["ER_keV"] % 5.0) != 0.0
        fine.loc[mask, "dsigma_cm2_per_keV"] *= 1.02
        result = summarize_benchmark(coarse, fine, BENCHMARKS[0])
        self.assertEqual(result["status"], "FAIL")
        self.assertGreater(result["integral_relative_difference"], 1e-3)

    def test_loader_rejects_wrong_energy_spacing(self):
        wrong = synthetic_grid(5)
        wrong = wrong.loc[wrong["ER_keV"] != 10.0]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "wrong_grid.csv"
            wrong.to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_grid(path, 5)


if __name__ == "__main__":
    unittest.main()
