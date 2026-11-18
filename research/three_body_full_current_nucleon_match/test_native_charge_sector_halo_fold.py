import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import native_charge_sector_halo_fold as fold


class NativeChargeSectorHaloFoldTests(unittest.TestCase):
    def test_exact_q_uses_isotope_mass_shell_relation(self):
        mA = 121.90971983538435
        q200 = fold.exact_qA_GeV(mA, 200.0)
        q267 = fold.exact_qA_GeV(mA, 267.0)
        # These values use the full AME2020-derived nuclear mass above.
        # The previous constants corresponded to the rounded mass 121.909719835 GeV.
        self.assertAlmostEqual(q200, 0.22082555996567457, delta=1.0e-15)
        self.assertAlmostEqual(q267, 0.25514674538605275, delta=1.0e-15)

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

    def _write_valid_native_artifact(self, root: Path):
        native = root / "native"
        native.mkdir(parents=True)
        comparison = {
            "status": "PASS",
            "scope": "pointwise Python versus native AFH v6.0 ResponseNuclear comparison",
            "native_afh_validated": True,
            "isotopes": list(fold.ISOTOPES),
            "expected_points_per_isotope": 2401,
            "expected_rows": 16807,
            "python_rows": 16807,
            "native_rows": 16807,
            "rows_compared": 16807,
            "rtol": 5e-7,
            "atol": 2e-12,
            "imaginary_atol": 2e-12,
            "max_differences": {
                name: {"max_abs": 0.0, "max_rel": 0.0, "worst_key": None}
                for name in fold.NATIVE_RESPONSE_INDEX_MAP
            },
            "failures": [],
        }
        manifest = {
            "repository": fold.NATIVE_AFH_REPOSITORY,
            "source_commit": fold.NATIVE_AFH_SOURCE_COMMIT,
            "control_run_id": "44222502400",
            "control_run_attempt": "2",
            "native_package": "AFH DMFormFactor v6.0",
            "wolfram_version": "Wolfram 14.2.0",
            "python_version": "Python 3.12.0",
            "isotopes": list(fold.ISOTOPES),
            "response_indices": fold.NATIVE_RESPONSE_INDEX_MAP,
            "q_grid": {
                "points": 2401,
                "q_min_GeV": 0.0,
                "q_max_GeV": 0.6,
                "step_GeV": 0.00025,
            },
            "comparison": comparison,
        }
        (root / "native-comparison.json").write_text(
            json.dumps(comparison), encoding="utf-8"
        )
        (root / "run_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )
        (native / "native_metadata.txt").write_text(
            "Wolfram 14.2.0 native AFH v6.0 export", encoding="utf-8"
        )
        fieldnames = (
            ["A", "q_GeV", "y"]
            + list(fold.NATIVE_RESPONSE_W_COLUMNS.values())
            + [f"Im_{column}" for column in fold.NATIVE_RESPONSE_W_COLUMNS.values()]
        )
        for A in fold.ISOTOPES:
            path = native / f"afh_v6_xe{A}_eight_response_native.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fieldnames)
                writer.writeheader()
                for i in range(2401):
                    q = 0.6 * i / 2400.0
                    row = {"A": A, "q_GeV": q, "y": q * q}
                    for column in fold.NATIVE_RESPONSE_W_COLUMNS.values():
                        row[column] = 1.0
                        row[f"Im_{column}"] = 0.0
                    writer.writerow(row)
        files = [
            root / "native-comparison.json",
            root / "run_manifest.json",
            native / "native_metadata.txt",
            *sorted(native.glob("afh_v6_xe*_eight_response_native.csv")),
        ]
        lines = []
        for path in files:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.relative_to(root).as_posix()}")
        (root / "SHA256SUMS.txt").write_text(
            "\n".join(lines) + "\n", encoding="ascii"
        )

    def test_native_gate_accepts_only_16807_pointwise_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_native_artifact(root)
            bundle, gate = fold.load_native_response_bundle(root)
            self.assertEqual(tuple(sorted(bundle)), fold.ISOTOPES)
            self.assertEqual(len(gate["sha256_verified_files"]), 10)
            self.assertEqual(
                gate["provenance"]["source_commit"],
                fold.NATIVE_AFH_SOURCE_COMMIT,
            )
            self.assertAlmostEqual(
                bundle[131]["physical"]["M"][0],
                4.0 * math.pi / 4.0 * 4.0,
                places=12,
            )

    def test_native_gate_rejects_wrong_pinned_source_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_native_artifact(root)
            manifest_path = root / "run_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["source_commit"] = "0" * 40
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "source_commit mismatch"):
                fold.load_native_response_bundle(root)

    def test_native_gate_rejects_missing_eight_response_channel(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_native_artifact(root)
            comparison_path = root / "native-comparison.json"
            comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
            comparison["max_differences"].pop("SigmaPrimeDelta")
            comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "all eight AFH response channels"):
                fold.load_native_response_bundle(root)

    def test_native_gate_rejects_modified_native_csv_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_native_artifact(root)
            path = root / "native" / "afh_v6_xe131_eight_response_native.csv"
            path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SHA-256 mismatch"):
                fold.load_native_response_bundle(root)


if __name__ == "__main__":
    unittest.main()
