from pathlib import Path
import csv
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("afh_runner", HERE / "run_afh_default_xe131.py")
afh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(afh)


class AFHDefaultXe131Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = afh.read_density_matrix_csv(HERE / "input" / "afh_default_xe131_density_matrix.csv")
        cls.b_fm = math.sqrt(41.467 / (45*131**(-1/3) - 25*131**(-2/3)))
        cls.b = cls.b_fm * 5.0677
        cls.Tiso = abs(131/2 - 54)

    def test_density_matrix_inventory(self):
        self.assertEqual(len(self.rows), 67)
        self.assertEqual(sum(r["rank"] == 0 and r["isospin"] == 0 for r in self.rows), 16)
        self.assertEqual(sum(r["rank"] == 2 and r["isospin"] == 0 for r in self.rows), 8)

    def test_default_oscillator_length(self):
        self.assertAlmostEqual(self.b_fm, 2.2923417985218975, places=12)

    def test_official_v6_default_xenon_dispatch_coverage(self):
        source_path = HERE.parents[1] / "v6" / "dmformfactor-V6.m"
        source = source_path.read_text(encoding="utf-8")
        marker = "If[Ziso==54&&Mxx=="
        masses = []
        for line in source.splitlines():
            if marker in line:
                value = line.split(marker, 1)[1].split(",", 1)[0]
                masses.append(int(value))
        self.assertEqual(masses, [128, 129, 130, 131, 132, 134, 136])
        self.assertIn(
            "Cannot find default matrix which matches input M and Z!",
            source,
        )
        # Xe-124 and Xe-126 are natural isotopes, but have no default
        # AFH v6.0 xenon density-matrix dispatch entries.
        for missing_mass in (124, 126):
            self.assertNotIn(
                f"If[Ziso==54&&Mxx=={missing_mass},",
                source,
            )

    def test_afh_isoscalar_zero_momentum_convention(self):
        W00, _ = afh.package_w00(0.0, self.rows, self.b, self.Tiso)
        Rpackage = 4*math.pi/(2*afh.J_A+1)*W00
        self.assertLess(abs(Rpackage/(131**2/4)-1), 2e-4)

    def test_equal_pn_normalization(self):
        W00, _ = afh.package_w00(0.0, self.rows, self.b, self.Tiso)
        Rpackage = 4*math.pi/(2*afh.J_A+1)*W00
        physical_raw = 4*Rpackage
        self.assertLess(abs(physical_raw/(131**2)-1), 2e-4)
        physical_normalized = 131**2 * physical_raw/physical_raw
        self.assertAlmostEqual(physical_normalized, 131**2, places=10)

    def test_python_and_mma_share_physical_factor4_convention(self):
        normalization_audit = (HERE / "audit" / "AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md").read_text(encoding="utf-8")
        mma_runner = (HERE / "run_afh_default_xe131.wls").read_text(encoding="utf-8")
        mma_verifier = (HERE / "verify_afh_xe131_native.wls").read_text(encoding="utf-8")
        comparator = (HERE / "compare_afh_mathematica_python.py").read_text(encoding="utf-8")

        self.assertIn("16 pi", normalization_audit.lower())
        self.assertIn("factor of four", normalization_audit.lower())

        self.assertIn("rEqualRaw = 4.0*rAFH;", mma_runner)
        self.assertIn("rEqualFormula = 16.0 Pi/(2.0 JA + 1.0)*wm;", mma_runner)
        self.assertIn("factor4Residual > 10^-12", mma_runner)
        self.assertIn("rRaw[q_?NumericQ] := 16 Pi/(2 jA + 1) wm[q];", mma_verifier)
        self.assertIn('"R_equal_pn_raw"', comparator)
        self.assertIn('"raw_AFH_W_M00"', comparator)

    def test_native_comparator_schema_and_no_interpolation_guard(self):
        comparator = HERE / "compare_afh_mathematica_python.py"
        python_fields = [
            "q_GeV", "W_M00_AFH_package",
            "R_AFH_package_4pi_over_2Jplus1",
            "R_equal_pn_raw", "R_equal_pn_normalized",
        ]
        wolfram_fields = [
            "q_GeV", "W_M00_AFH_package",
            "R_AFH_4Pi_over_2Jplus1",
            "R_equal_pn_raw", "R_equal_pn_normalized",
        ]
        base_rows = [
            {"q_GeV": 0.0, "W_M00_AFH_package": 1.0,
             "R_AFH_package_4pi_over_2Jplus1": 1.0,
             "R_AFH_4Pi_over_2Jplus1": 1.0,
             "R_equal_pn_raw": 4.0, "R_equal_pn_normalized": 131**2},
            {"q_GeV": 0.00025, "W_M00_AFH_package": 0.5,
             "R_AFH_package_4pi_over_2Jplus1": 0.5,
             "R_AFH_4Pi_over_2Jplus1": 0.5,
             "R_equal_pn_raw": 2.0, "R_equal_pn_normalized": 131**2/2},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            py_csv = tmpdir / "python.csv"
            wl_csv = tmpdir / "mathematica.csv"
            summary = tmpdir / "comparison.json"

            with py_csv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=python_fields)
                writer.writeheader()
                writer.writerows([{k: row[k] for k in python_fields} for row in base_rows])
            with wl_csv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=wolfram_fields)
                writer.writeheader()
                writer.writerows([{k: row[k] for k in wolfram_fields} for row in base_rows])

            passed = subprocess.run(
                [sys.executable, str(comparator), "--python-csv", str(py_csv),
                 "--mathematica-csv", str(wl_csv), "--output", str(summary)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(passed.returncode, 0, msg=passed.stdout + passed.stderr)
            result = json.loads(summary.read_text(encoding="utf-8"))
            self.assertTrue(result["passed"])
            self.assertEqual(result["points"], 2)
            self.assertEqual(len(result["python_csv_sha256"]), 64)
            self.assertEqual(len(result["mathematica_csv_sha256"]), 64)

            # A changed q node must fail; the comparator is not allowed to interpolate.
            bad_rows = [dict(row) for row in base_rows]
            bad_rows[1]["q_GeV"] = 0.000251
            with wl_csv.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=wolfram_fields)
                writer.writeheader()
                writer.writerows([{k: row[k] for k in wolfram_fields} for row in bad_rows])
            failed = subprocess.run(
                [sys.executable, str(comparator), "--python-csv", str(py_csv),
                 "--mathematica-csv", str(wl_csv), "--output", str(summary)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("q grids differ", failed.stderr)

    def test_native_runner_pins_official_source_and_matrix_hashes(self):
        runner = (HERE / "run_native_afh_audit.ps1").read_text(encoding="utf-8")
        verifier = (HERE / "verify_afh_xe131_native.wls").read_text(encoding="utf-8")
        mma_runner = (HERE / "run_afh_default_xe131.wls").read_text(encoding="utf-8")
        self.assertIn("4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727", runner)
        self.assertIn("dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372", runner)
        self.assertIn("f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45", runner)
        self.assertIn('Join-Path (Join-Path $scriptDir "input") "afh_default_xe131_density_matrix.csv"', runner)
        self.assertIn("afh_native_audit_manifest.json", runner)
        self.assertIn('Join-Path (Join-Path $outputDir "native_exports") "afh_default_xe131_WM00_mathematica.csv"', runner)
        self.assertIn('nativeOutputDir = FileNameJoin[{scriptDir, "output", "native_exports"}]', mma_runner)
        self.assertIn("Compress-Archive", runner)
        self.assertIn("afh-native-audit-results.zip", runner)
        self.assertIn("WolframVersion = ", verifier)
        self.assertIn("NativeGridCSV_SHA256 = ", verifier)

    def test_independent_high_precision_kernel_check_points(self):
        # Reference values independently checked with 60-digit mpmath evaluation
        # of the finite sums in AFH BesselElement.
        expected = {
            (0.157, 0): 0.16587194445197020453,
            (0.157, 2): 0.26402074701536012526,
            (0.25625, 0): -0.00073663417732777932351,
            (0.25625, 2): -0.01861327862684671077,
            (0.365, 0): -0.00042424625191455005691,
            (0.365, 2): 0.029211388204593898543,
        }
        for (q, rank), target in expected.items():
            value = afh.compute_amplitude(q, rank, self.rows, self.b, self.Tiso)
            self.assertAlmostEqual(value, target, delta=2e-11)

    def test_minima_locations(self):
        with (HERE / "output" / "minima.csv").open(newline="", encoding="utf-8") as f:
            minima = list(csv.DictReader(f))
        expected = [157.93578, 256.27187, 365.06657, 499.37189]
        self.assertEqual(len(minima), 4)
        for got, want in zip(minima, expected):
            self.assertAlmostEqual(float(got["q_min_MeV"]), want, delta=0.01)


if __name__ == "__main__":
    unittest.main()

