import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

import native_charge_sector_halo_fold as fold


class NativeChargeSectorHaloFoldTests(unittest.TestCase):
    def test_exact_q_uses_isotope_mass_shell_relation(self):
        mA = 121.90971983538435
        q200 = fold.exact_qA_GeV(mA, 200.0)
        q267 = fold.exact_qA_GeV(mA, 267.0)
        self.assertAlmostEqual(q200, 0.22082555996532646, places=13)
        self.assertAlmostEqual(q267, 0.2551467453856506, places=13)

    def test_charge_kernel_decomposes_exactly(self):
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_L00(
            2.5, 0.22, responses, "pointlike"
        )
        expected = sum(result["terms"].values())
        self.assertAlmostEqual(result["charge_sector"], expected, places=14)
        self.assertAlmostEqual(
            result["pointlike_M"], 9.0 * 2.5 * responses["M"], places=14
        )

    def test_zero_momentum_form_factor_anchor(self):
        f1, f2 = fold.form_factor_values(0.0, "isoscalar_zexp")
        self.assertAlmostEqual(f1, 3.0, places=10)
        self.assertAlmostEqual(f2, -0.552, places=10)

    def test_native_physical_conversion_factor(self):
        q = np.linspace(0.0, 0.6, 2401)
        entry = {
            "q": q,
            "physical": {
                "M": np.ones_like(q),
                "PhiPP": np.ones_like(q),
                "MPhiPP": np.ones_like(q),
            },
        }
        out = fold.interpolate_native_response(entry, 0.2551467453856506)
        for name in fold.RESPONSE_NAMES:
            self.assertTrue(math.isfinite(out["physical_equal_pn"][name]))
            self.assertAlmostEqual(
                out["pchip_linear_relative_difference"][name], 0.0, places=12
            )

    def test_native_gate_rejects_unvalidated_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "native-comparison.json").write_text(
                json.dumps({
                    "status": "PASS",
                    "native_afh_validated": False,
                    "rows_compared": 16807,
                }),
                encoding="utf-8",
            )
            with self.assertRaises(RuntimeError):
                fold.load_native_response_bundle(root)

    def test_native_gate_accepts_only_16807_pointwise_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "native-comparison.json").write_text(
                json.dumps({
                    "status": "PASS",
                    "native_afh_validated": True,
                    "rows_compared": 16807,
                }),
                encoding="utf-8",
            )
            for A in fold.ISOTOPES:
                path = root / f"afh_v6_xe{A}_eight_response_native.csv"
                with path.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(
                        stream,
                        fieldnames=[
                            "A", "q_GeV", "y",
                            "W_M00_AFH", "W_SigmaDoublePrime00_AFH",
                            "W_SigmaPrime00_AFH", "W_PhiPP00_AFH",
                            "W_PhiTildePrime00_AFH", "W_Delta00_AFH",
                            "W_MPhiPP00_AFH", "W_SigmaPrimeDelta00_AFH",
                            "Im_W_M00_AFH", "Im_W_SigmaDoublePrime00_AFH",
                            "Im_W_SigmaPrime00_AFH", "Im_W_PhiPP00_AFH",
                            "Im_W_PhiTildePrime00_AFH", "Im_W_Delta00_AFH",
                            "Im_W_MPhiPP00_AFH", "Im_W_SigmaPrimeDelta00_AFH",
                        ],
                    )
                    writer.writeheader()
                    for i in range(2401):
                        q = 0.6 * i / 2400.0
                        row = {"A": A, "q_GeV": q, "y": q * q}
                        for name in fold.RESPONSE_W_COLUMNS.values():
                            row[name] = 1.0
                            row[f"Im_{name}"] = 0.0
                        writer.writerow(row)
            bundle, _ = fold.load_native_response_bundle(root)
            self.assertEqual(tuple(sorted(bundle)), fold.ISOTOPES)
            self.assertAlmostEqual(
                bundle[131]["physical"]["M"][0],
                4.0 * math.pi / 4.0 * 4.0,
                places=12,
            )


if __name__ == "__main__":
    unittest.main()
