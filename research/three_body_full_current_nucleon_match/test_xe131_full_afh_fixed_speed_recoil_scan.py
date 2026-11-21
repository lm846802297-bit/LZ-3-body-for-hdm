import unittest

import csv
import hashlib
import json
import tempfile
from pathlib import Path

import numpy as np

from xe131_full_afh_fixed_speed_recoil_scan import (
    EXPECTED_CHARGE_RATIOS,
    FORMAL_WIDTH_SCHEMES,
    RESPONSE_NAMES,
    contract_six_channels,
    recoil_cases,
    overlay_dense_native_charge_grid,
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
            result["C_charge_only"] + result["spatial_candidate"],
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

    def test_dense_native_grid_replaces_coarse_dip_nodes_and_preserves_normalization(self):
        q_coarse = np.linspace(0.0, 0.6, 2401)
        native = {
            "q": q_coarse,
            "responses": {
                "M": 100.0 + q_coarse,
                "PhiPP": 10.0 + q_coarse,
                "MPhiPP": -2.0 - q_coarse,
            },
        }
        provenance = {"common_matrix_normalization_C0": 1.1}
        q_dense = 0.2545 + np.arange(121) * 0.000025
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "dense.csv"
            meta_path = root / "dense.txt"
            validation_path = root / "validation.json"
            rows = []
            for q in q_dense:
                rows.append({
                    "A": 131, "q_GeV": f"{q:.12g}", "y": "0.0",
                    "W_M00_AFH": "1.0", "W_PhiPP00_AFH": "2.0",
                    "W_MPhiPP00_AFH": "-0.5",
                    "Im_W_M00_AFH": "0", "Im_W_PhiPP00_AFH": "0",
                    "Im_W_MPhiPP00_AFH": "0",
                })
            with csv_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            meta = (
                "source=AFH DMFormFactor v6.0 native Wolfram execution\n"
                "isotope=Xe-131\nZ=54\n"
                "response_map=M=1;PhiPP=4;MPhiPP=7\n"
                "q_grid=121 uniform nodes from 0.2545 to 0.2575 GeV, step 0.000025 GeV\n"
                "normalization=raw AFH package response; no physical equal-p/n factor-four rescaling\n"
                "AFH_source_sha256=dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372\n"
                "rows=121\nmax_imaginary_residual=0\n"
            )
            meta_path.write_text(meta, encoding="utf-8")
            validation = {
                "status": "PASS_NATIVE_XE131_DENSE_CHARGE_DIP",
                "rows": 121, "common_nodes_compared": 13,
                "max_imaginary_residual": 0.0,
                "AFH_source_sha256": "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372",
                "dense_csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
                "dense_metadata_sha256": hashlib.sha256(meta_path.read_bytes()).hexdigest(),
                "common_node_max_relative_difference": {"M": 0.0, "PhiPP": 0.0, "MPhiPP": 0.0},
            }
            validation_path.write_text(json.dumps(validation), encoding="utf-8")
            merged, updated_provenance = overlay_dense_native_charge_grid(
                native, provenance, csv_path, meta_path, validation_path
            )
        self.assertEqual(len(merged["q"]), 2509)
        self.assertEqual(updated_provenance["dense_native_points"], 121)
        self.assertEqual(updated_provenance["merged_response_grid_points"], 2509)
        factor = 4.0 * np.pi * 1.1
        first = int(np.argmin(np.abs(merged["q"] - 0.2545)))
        self.assertAlmostEqual(merged["responses"]["M"][first], factor)
        self.assertAlmostEqual(merged["responses"]["PhiPP"][first], 2.0 * factor)
        self.assertAlmostEqual(merged["responses"]["MPhiPP"][first], -0.5 * factor)

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
