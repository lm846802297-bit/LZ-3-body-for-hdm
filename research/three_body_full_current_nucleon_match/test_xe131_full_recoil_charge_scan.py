"""Integrity and algebraic regression tests for the Xe-131 recoil scan."""
from __future__ import annotations

import csv
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "results" / "2026-11-18" / "xe131_charge_kernel_full_recoil_scan.csv"


class TestXe131FullRecoilChargeKernelScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with DATA.open("r", encoding="utf-8", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))

    def test_native_grid_point_count_and_recoil_coverage(self) -> None:
        self.assertEqual(len(self.rows), 943)
        er = [float(row["ER_keV"]) for row in self.rows]
        q = [float(row["q_GeV"]) for row in self.rows]
        self.assertTrue(all(b > a for a, b in zip(er, er[1:])))
        self.assertTrue(all(b > a for a, b in zip(q, q[1:])))
        self.assertAlmostEqual(er[0], 109.639485743, places=8)
        self.assertAlmostEqual(er[-1], 652.944547312, places=8)

    def test_interference_kernel_is_coherent(self) -> None:
        for row in self.rows:
            f = {key: float(value) for key, value in row.items()}
            expected = f["K_M_only"] + 2.0 * f["cM"] * f["cPhiPP"] * f["W_MPhiPP"]
            self.assertTrue(
                math.isclose(f["K_M_plus_interference"], expected, rel_tol=5e-10, abs_tol=1e-13),
                msg=f"interference identity failed at ER={f['ER_keV']}",
            )

    def test_full_charge_kernel_includes_phi_diagonal(self) -> None:
        for row in self.rows:
            f = {key: float(value) for key, value in row.items()}
            expected = f["K_M_plus_interference"] + f["cPhiPP"]**2 * f["W_PhiPP"]
            self.assertTrue(
                math.isclose(f["K_full_charge"], expected, rel_tol=5e-10, abs_tol=1e-13),
                msg=f"full charge identity failed at ER={f['ER_keV']}",
            )

    def test_ratio_columns_match_kernel_columns(self) -> None:
        for row in self.rows:
            f = {key: float(value) for key, value in row.items()}
            self.assertGreater(f["K_M_only"], 0.0)
            self.assertTrue(math.isclose(
                f["ratio_M_plus_int_over_M"],
                f["K_M_plus_interference"] / f["K_M_only"],
                rel_tol=5e-10,
            ))
            self.assertTrue(math.isclose(
                f["ratio_full_over_M"],
                f["K_full_charge"] / f["K_M_only"],
                rel_tol=5e-10,
            ))

    def test_sampled_ratio_extrema(self) -> None:
        ratios = [float(row["ratio_full_over_M"]) for row in self.rows]
        self.assertAlmostEqual(min(ratios), 0.86043801104, places=9)
        self.assertAlmostEqual(max(ratios), 1.11839839062, places=9)


if __name__ == "__main__":
    unittest.main()
