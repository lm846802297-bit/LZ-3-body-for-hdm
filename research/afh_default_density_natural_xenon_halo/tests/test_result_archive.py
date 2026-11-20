from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
import unittest
from jsonschema import Draft202012Validator, FormatChecker
from datetime import datetime, timezone
from pathlib import Path

import sys

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research"))

from result_archive import csv_units, write_result_records


class StructuredResultArchiveTests(unittest.TestCase):
    def test_explicit_units_cover_all_current_afh7_output_columns(self):
        cases = {
            "ER_keV": "keV",
            "rate_events_kg_day_keV": "events kg^-1 day^-1 keV^-1",
            "rhoDM_GeV_cm3": "GeV cm^-3",
            "AFH_default_available": "boolean",
            "benchmark": "label",
            "R_AFH_direct_exact_q": "1",
            "weighted_cross_section_integral_GeVminus3": "GeV^-3",
            "Wmin_GeV": "GeV",
            "pole_gap_keV": "keV",
            "v_kms": "km s^-1",
            "dsigma_dER_eq6_GeV_minus3": "GeV^-3",
            "pole_inside_phase_space": "boolean",
            "relative_to_sine2_reference": "1",
            "q_NIST_exact_spatial_GeV": "GeV",
            "q_recomputed_GeV": "GeV",
            "q_abs_difference_GeV": "GeV",
            "b_A_fm_archived": "fm",
            "b_A_fm_recomputed": "fm",
            "PCHIP_vs_direct_relative_difference": "1",
        }
        for column, expected in cases.items():
            with self.subTest(column=column):
                self.assertEqual(csv_units(column), expected)

    def test_unknown_csv_unit_fails_closed(self):
        with self.assertRaises(ValueError):
            csv_units("mystery_column")

    def test_validation_status_never_promotes_partial_checks(self):
        from result_archive import validation_status
        self.assertEqual(validation_status([{"status": "passed"}]), "passed")
        self.assertEqual(validation_status([{"status": "passed"}, {"status": "not_run"}]), "partial")
        self.assertEqual(validation_status([{"status": "failed"}]), "failed")

    def test_writer_packages_existing_afh_response_grid_and_keeps_partial_status(self):
        result_dir = HERE / "output" / "afh_default_xenon_responses"
        metadata_path = result_dir / "afh_xe_isotope_response_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source_output_paths = [
            (result_dir / "afh_xe_isotope_responses.csv", "seven-isotope AFH response grid"),
            (result_dir / "afh_response_selected_sample_regression.csv", "selected-sample regression"),
            (result_dir / "afh_response_selected_sample_regression_diagnostic.json", "interpolation diagnostic"),
            (metadata_path, "original AFH response metadata"),
        ]
        before = {path: path.read_bytes() for path, _ in source_output_paths}
        matrix_dir = HERE / "input" / "afh_default_density_matrices"
        matrix_paths = [matrix_dir / f"afh_default_xe{A}_density_matrix.csv"
                        for A in (128, 129, 130, 131, 132, 134, 136)]
        inputs = [
            (path, f"AFH Xe-{A} density matrix", "AFH v6.0 default-density input")
            for A, path in zip((128, 129, 130, 131, 132, 134, 136), matrix_paths)
        ] + [
            (HERE.parent / "afh_default_density_xe131" / "output" / "afh_default_xe131_WM00.csv",
             "archived Xe-131 reference", "historical full-grid regression reference"),
            (HERE / "input" / "afh_response_samples.csv",
             "archived AFH selected samples", "historical PCHIP regression points"),
        ]
        per_isotope = metadata["isotope_metadata"]
        max_q0 = max(float(item["package_R0_relative_error"]) for item in per_isotope.values())
        reg = metadata["regression"]
        checks = [
            {"check_id": "TEST-XE131-GRID", "name": "Xe-131 grid regression",
             "category": "regression", "status": "passed",
             "method": "Pointwise archived-grid comparison.", "observed": reg["xe131_max_relative_grid_difference"],
             "threshold": 5e-12, "unit": "1", "evidence_path": "afh_xe_isotope_responses.csv"},
            {"check_id": "TEST-PCHIP-ARCHIVE", "name": "Selected PCHIP sample regression",
             "category": "regression", "status": "passed",
             "method": "Pointwise historical PCHIP sample comparison.",
             "observed": reg["selected_sample_max_relative_pchip_vs_archived_difference"],
             "threshold": 5e-7, "unit": "1", "evidence_path": "afh_response_selected_sample_regression.csv"},
            {"check_id": "TEST-Q0-NORMALIZATION", "name": "AFH q=0 normalization",
             "category": "analytic", "status": "passed",
             "method": "Raw package R(0) versus A^2/4.", "observed": max_q0,
             "threshold": 5e-4, "unit": "1", "evidence_path": "afh_xe_isotope_response_metadata.json"},
            {"check_id": "TEST-MATRIX-HASHES", "name": "AFH matrix input hashes",
             "category": "integrity", "status": "passed",
             "method": "Per-isotope matrix SHA-256 comparison.", "observed": "all seven match",
             "threshold": "exact SHA-256 match", "unit": "sha256",
             "evidence_path": "afh_xe_isotope_response_metadata.json"},
            {"check_id": "TEST-PCHIP-DIAGNOSTIC", "name": "PCHIP versus direct exact-q interpolation diagnostic",
             "category": "independent", "status": "inconclusive",
             "method": "Diagnostic only; direct exact-q values remain primary.",
             "observed": reg["selected_sample_max_relative_pchip_vs_direct_difference"],
             "threshold": 5e-4, "unit": "1", "evidence_path": "afh_response_selected_sample_regression_diagnostic.json"},
            {"check_id": "TEST-NATIVE-MMA", "name": "Native Mathematica re-execution",
             "category": "independent", "status": "not_run",
             "method": "Separate independent execution is pending.", "observed": "pending",
             "threshold": "native AFH v6.0 execution", "unit": "status",
             "evidence_path": "afh_xe_isotope_response_metadata.json"},
        ]
        started = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        tick = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="lz-afh-response-archive-", dir=ROOT) as temp:
            out_dir = Path(temp)
            output_paths = []
            for source_path, role in source_output_paths:
                target_path = out_dir / source_path.name
                shutil.copyfile(source_path, target_path)
                output_paths.append((target_path, role))
            archive_metadata = dict(metadata)
            archive_metadata["particle_parameters"] = {"isotopes": metadata["isotopes"]}
            archive_metadata["quadrature"] = metadata["grid"]
            archive_metadata["not_included"] = [
                "native Mathematica re-execution", "non-M nuclear responses",
                "three-body phase-space and halo folding", "detector response",
            ]
            observables = [
                {"name": "AFH_response_rows", "value": metadata["grid"]["total_rows"],
                 "unit": "rows", "status": "computed"},
                {"name": "max_q0_normalization_error", "value": max_q0,
                 "unit": "1", "status": "computed"},
                {"name": "PCHIP_vs_direct_relative_difference",
                 "value": reg["selected_sample_max_relative_pchip_vs_direct_difference"],
                 "unit": "1", "status": "computed"},
            ]
            records = write_result_records(
                repo_root=ROOT, out_dir=out_dir, metadata=archive_metadata,
                source_script=HERE / "run_afh_default_xenon_responses.py",
                started_at=started, started_monotonic=tick,
                input_paths=inputs, output_paths=output_paths, checks=checks,
                observables=observables,
                scope_included=["AFH v6.0 default-density W_M^00 response for seven isotopes"],
                scope_excluded=archive_metadata["not_included"],
                assumptions=[
                    "Raw package q=0 normalization is A^2/4; equal-pn normalization is applied once.",
                    "The Python translation has not been independently re-executed in native Mathematica.",
                ],
                scientific_status="provisional",
                interpretation="AFH nuclear response grid only; not a three-body or detector prediction.",
                extension_name="afh_nuclear_response",
            )
            manifest = json.loads(records["run_manifest"].read_text())
            summary = json.loads(records["result_summary"].read_text())
            report = json.loads(records["validation_report"].read_text())
            self.assertEqual(report["status"], "partial")
            self.assertEqual(manifest["validation"]["status"], "partial")
            self.assertEqual(len(summary["data_files"]), 4)
            schema = json.loads((ROOT / "research/schemas/research-result-record-v1.0.0.schema.json").read_text())
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for record_path in (records["run_manifest"], records["result_summary"], records["validation_report"]):
                record = json.loads(record_path.read_text())
                errors = list(validator.iter_errors(record))
                self.assertFalse(errors, [error.message for error in errors])
            validator_script = ROOT / "research/schemas/validate_result_records.py"
            subprocess.run([
                sys.executable, str(validator_script), "--repo-root", str(ROOT),
                str(records["run_manifest"]), str(records["result_summary"]),
                str(records["validation_report"]),
            ], check=True, cwd=ROOT)
        for path, _ in source_output_paths:
            self.assertEqual(path.read_bytes(), before[path])

    def test_writer_packages_existing_afh_three_body_outputs_without_modifying_them(self):
        result_dir = (
            HERE / "results" / "afh7_hybrid9_continuous_2026-11-14"
        )
        metadata_path = result_dir / "metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        source_output_paths = [
            (result_dir / "afh_hybrid9_response_model_comparison.csv", "AFH response comparison"),
            (result_dir / "afh_hybrid9_isotope_kernel_integrals.csv", "three-body isotope kernel integrals"),
            (result_dir / "afh_hybrid9_natural_xenon_spectrum.csv", "natural-xenon pre-detector spectrum"),
            (result_dir / "afh_hybrid9_quadrature_crosschecks.csv", "quadrature crosschecks"),
            (metadata_path, "original run metadata"),
            (result_dir / "SHA256SUMS.txt", "original output checksums"),
        ]
        before = {path: path.read_bytes() for path, _ in source_output_paths}
        response_inputs = [
            HERE / "results" / "full_afh_v6_default_7_isotope_response"
            / f"afh_default_xe{A}_response_2401.csv"
            for A in (128, 129, 130, 131, 132, 134, 136)
        ]
        inputs = [
            (ROOT / "v6" / "dmformfactor-V6.m", "AFH v6.0 source", "official source package"),
            (HERE / "input" / "natural_xenon_isotope_weights.csv", "natural-xenon isotope weights", "repository input"),
        ] + [(path, f"AFH Xe-{A} response", "AFH response input")
             for A, path in zip((128, 129, 130, 131, 132, 134, 136), response_inputs)]
        checks = [{
            "check_id": "TEST-ARCHIVE", "name": "Archive fixture",
            "category": "integrity", "status": "passed",
            "method": "Synthetic archive writer test.", "observed": 1,
            "threshold": 1, "unit": "1", "evidence_path": "research/result_archive.py",
        }]
        observables = [{
            "name": "spectrum_rows", "value": metadata["row_counts"]["natural_xenon_spectra"],
            "unit": "rows", "status": "computed",
        }]
        started = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        tick = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="lz-result-archive-", dir=ROOT) as temp:
            out_dir = Path(temp)
            output_paths = []
            for source_path, role in source_output_paths:
                target_path = out_dir / source_path.name
                shutil.copyfile(source_path, target_path)
                output_paths.append((target_path, role))
            records = write_result_records(
                repo_root=ROOT, out_dir=out_dir, metadata=metadata,
                source_script=HERE / "run_afh7_hybrid9_continuous_spectrum.py",
                started_at=started, started_monotonic=tick,
                input_paths=inputs, output_paths=output_paths, checks=checks,
                observables=observables,
                scope_included=["three-body Eq. (6) kernel", "direct AFH exact-q response"],
                scope_excluded=metadata["not_included"],
                assumptions=["Seven-isotope AFH coverage is not renormalized."],
                interpretation="Pre-detector theory rate; no likelihood is inferred.",
            )
            manifest = json.loads(records["run_manifest"].read_text())
            summary = json.loads(records["result_summary"].read_text())
            report = json.loads(records["validation_report"].read_text())
            self.assertEqual(manifest["record_type"], "run_manifest")
            self.assertEqual(summary["record_type"], "result_summary")
            self.assertEqual(report["record_type"], "validation_report")
            self.assertEqual(manifest["validation"]["status"], "passed")
            self.assertEqual(report["status"], "passed")
            self.assertEqual(len(manifest["outputs"]), len(output_paths) + 4)
            self.assertEqual(len(summary["data_files"]), 5)
            self.assertEqual(manifest["archive"]["status"], "local_only")
            preserved_checksums = list(out_dir.glob("SHA256SUMS.physics-*.txt"))
            self.assertEqual(len(preserved_checksums), 1)
            original_checksum_path = result_dir / "SHA256SUMS.txt"
            self.assertEqual(preserved_checksums[0].read_bytes(), before[original_checksum_path])
            schema = json.loads((
                ROOT / "research" / "schemas" /
                "research-result-record-v1.0.0.schema.json"
            ).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for record_path in (records["run_manifest"], records["result_summary"], records["validation_report"]):
                record = json.loads(record_path.read_text(encoding="utf-8"))
                errors = list(validator.iter_errors(record))
                self.assertFalse(errors, [error.message for error in errors])
            validator_script = ROOT / "research" / "schemas" / "validate_result_records.py"
            subprocess.run([
                sys.executable, str(validator_script), "--repo-root", str(ROOT),
                str(records["run_manifest"]), str(records["result_summary"]),
                str(records["validation_report"]),
            ], check=True, cwd=ROOT)
        for path, _ in source_output_paths:
            self.assertEqual(path.read_bytes(), before[path])


if __name__ == "__main__":
    unittest.main(verbosity=2)
