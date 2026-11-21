import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validate_xe131_dense_charge_dip import AFH_SHA256, CHANNELS, validate


class ValidateXe131DenseChargeDipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dense_csv = self.root / "dense.csv"
        self.meta_txt = self.root / "dense_metadata.txt"
        self.coarse_csv = self.root / "coarse.csv"

        fields = ["A", "q_GeV", "y"]
        for real_col, imag_col in CHANNELS.values():
            fields.extend([real_col, imag_col])

        def values(q):
            return {
                "W_M00_AFH": 1.0 + q,
                "W_PhiPP00_AFH": 0.2 + 0.1*q,
                "W_MPhiPP00_AFH": 0.05 + 0.02*q,
                "Im_W_M00_AFH": 0.0,
                "Im_W_PhiPP00_AFH": 0.0,
                "Im_W_MPhiPP00_AFH": 0.0,
            }

        with self.coarse_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for i in range(2401):
                q = i*0.00025
                row = {"A": 131, "q_GeV": f"{q:.12g}", "y": f"{q*q:.16g}"}
                row.update({k: f"{v:.16g}" for k, v in values(q).items()})
                writer.writerow(row)

        with self.dense_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for i in range(121):
                q = 0.2545 + i*0.000025
                row = {"A": 131, "q_GeV": f"{q:.12g}", "y": f"{q*q:.16g}"}
                row.update({k: f"{v:.16g}" for k, v in values(q).items()})
                writer.writerow(row)

        metadata = {
            "source": "AFH DMFormFactor v6.0 native Wolfram execution",
            "isotope": "Xe-131",
            "Z": "54",
            "responses": "ResponseNuclear[y,index,0,0], indices=1,4,7",
            "response_map": "M=1;PhiPP=4;MPhiPP=7",
            "q_grid": "121 uniform nodes from 0.2545 to 0.2575 GeV, step 0.000025 GeV",
            "isospin": "tau1=tau2=0; raw AFH isoscalar package convention",
            "normalization": "raw AFH package response; no physical equal-p/n factor-four rescaling",
            "AFH_source_sha256": AFH_SHA256,
            "rows": "121",
            "max_imaginary_residual": "0.0",
            "wolfram_version": "14.2.0 for Microsoft Windows (64-bit)",
            "source_commit": "test-source-commit",
        }
        self.meta_txt.write_text(
            "\n".join(f"{k}={v}" for k, v in metadata.items()) + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_accepts_dense_grid_and_13_coarse_overlap_nodes(self):
        result = validate(self.dense_csv, self.meta_txt, self.coarse_csv)
        self.assertEqual(result["status"], "PASS_NATIVE_XE131_DENSE_CHARGE_DIP")
        self.assertEqual(result["rows"], 121)
        self.assertEqual(result["common_nodes_compared"], 13)
        self.assertTrue(result["native_afh_dense_q_validated"])

    def test_accepts_legacy_coarse_imaginary_column_names(self):
        with self.coarse_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        fields = list(rows[0])
        alias = {
            "Im_W_M00_AFH": "Im_W_M00",
            "Im_W_PhiPP00_AFH": "Im_W_PhiPP00",
            "Im_W_MPhiPP00_AFH": "Im_W_MPhiPP00",
        }
        legacy_fields = [alias.get(name, name) for name in fields]
        with self.coarse_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=legacy_fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({alias.get(k, k): v for k, v in row.items()})

        result = validate(self.dense_csv, self.meta_txt, self.coarse_csv)
        self.assertEqual(result["status"], "PASS_NATIVE_XE131_DENSE_CHARGE_DIP")
        self.assertEqual(result["common_nodes_compared"], 13)

    def test_rejects_mismatched_common_native_node(self):
        with self.dense_csv.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows[0]["W_M00_AFH"] = str(float(rows[0]["W_M00_AFH"]) + 1e-3)
        with self.dense_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            validate(self.dense_csv, self.meta_txt, self.coarse_csv)


if __name__ == "__main__":
    unittest.main()
