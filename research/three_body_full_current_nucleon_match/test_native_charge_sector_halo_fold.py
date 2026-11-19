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

    def test_mediator_denominator_uses_exact_lorentz_invariant(self):
        mA = 121.90971983538435
        ER_keV = 200.0
        mV = 10.0
        ER = ER_keV * 1.0e-6
        tA = fold.nuclear_transfer_invariant_tA_GeV2(mA, ER_keV)
        self.assertAlmostEqual(tA, -2.0 * mA * ER, places=18)
        expected = (mV * mV + 2.0 * mA * ER) ** 2
        actual = fold.mediator_denominator_squared_GeV4(mV, mA, ER_keV)
        self.assertAlmostEqual(actual, expected, places=12)
        qA2 = fold.exact_qA_GeV(mA, ER_keV) ** 2
        spatial_substitution = (mV * mV + qA2) ** 2
        self.assertNotEqual(actual, spatial_substitution)

    def test_charge_kernel_decomposes_exactly(self):
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.5, 0.22, responses, "q0_anchor"
        )
        expected = sum(result["terms"].values())
        self.assertAlmostEqual(result["charge_M_PhiPP"], expected, places=14)
        self.assertAlmostEqual(
            result["AFH_finite_size_M_baseline"], 2.5 * responses["M"], places=14
        )
        self.assertAlmostEqual(
            result["AFH_finite_size_M_baseline"], result["AFH_finite_size_M_baseline"], places=14
        )

    def test_charge_kernel_uses_continuity_reduced_weight(self):
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.4, 0.22, responses, "q0_anchor"
        )
        self.assertAlmostEqual(result["L_C"], 2.4)
        self.assertAlmostEqual(result["AFH_finite_size_M_baseline"], 2.4 * 4.0)
        self.assertAlmostEqual(result["AFH_finite_size_M_baseline"], result["AFH_finite_size_M_baseline"])
        self.assertAlmostEqual(
            result["charge_M_PhiPP"],
            sum(result["terms"].values()),
            places=14,
        )

    def test_coulomb_weight_is_read_from_continuity_reduced_tensor(self):
        fake = {
            "point_nucleus_contractions": {
                "I00": 100.0,
                "L_C_continuity_adjusted": 99.81,
                "continuity_reduced_relative_residual": 1.0e-16,
            }
        }
        result = fold._coulomb_weights_from_result(fake)
        self.assertEqual(result["L00"], 100.0)
        self.assertAlmostEqual(result["L_C"], 99.81)
        self.assertAlmostEqual(result["charge_continuity_relative_correction"], -0.0019)
        with self.assertRaises(ValueError):
            fold._coulomb_weights_from_result({
                "point_nucleus_contractions": {
                    "I00": 100.0,
                    "L_C_continuity_adjusted": 99.81,
                    "continuity_reduced_relative_residual": 1.0e-3,
                }
            })

    def test_full_vector_response_interpolation_covers_all_eight_channels(self):
        q = np.linspace(0.0, 0.6, 2401)
        entry = {
            "q": q,
            "physical": {name: np.ones_like(q) for name in fold.FULL_VECTOR_RESPONSE_NAMES},
        }
        out = fold.interpolate_native_response(
            entry, 0.2551467453856506,
            response_names=fold.FULL_VECTOR_RESPONSE_NAMES,
        )
        self.assertEqual(
            set(out["physical_equal_pn"]),
            set(fold.FULL_VECTOR_RESPONSE_NAMES),
        )
        self.assertEqual(
            set(out["pchip_linear_relative_difference"]),
            set(fold.FULL_VECTOR_RESPONSE_NAMES),
        )

    def test_leading_static_vector_kernel_reconstructs_charge_and_spatial(self):
        L = np.zeros((4, 4, 2), dtype=float)
        L[0, 0, 0] = 1.0
        L[1, 1, 0] = 0.01
        L[2, 2, 0] = 0.01
        responses = {
            "M": 4.0,
            "SigmaDoublePrime": 0.0,
            "SigmaPrime": 1.0,
            "PhiPP": 0.2,
            "PhiTildePrime": 0.0,
            "Delta": 2.0,
            "MPhiPP": -0.3,
            "SigmaPrimeDelta": -1.0,
        }
        result = fold.leading_static_vector_current_kernel_from_tensor(
            L, 0.22, 200.0e-6, responses, "q0_anchor"
        )
        self.assertAlmostEqual(
            result["full_six_channel_candidate"],
            result["charge_M_PhiPP"] + result["spatial_sector"],
            places=13,
        )
        self.assertGreaterEqual(result["spatial_sector"], 0.0)
        self.assertLess(result["particle_Cauchy_identity_relative_residual"], 1.0e-12)
        self.assertLess(result["charge_reconstruction_relative_residual"], 1.0e-12)

    def test_leading_static_vector_kernel_rejects_bad_charge_cauchy_response(self):
        L = np.zeros((4, 4, 2), dtype=float)
        L[0, 0, 0] = 1.0
        L[1, 1, 0] = 0.01
        L[2, 2, 0] = 0.01
        responses = {
            "M": 1.0,
            "SigmaDoublePrime": 0.0,
            "SigmaPrime": 1.0,
            "PhiPP": 1.0,
            "PhiTildePrime": 0.0,
            "Delta": 1.0,
            "MPhiPP": 10.0,
            "SigmaPrimeDelta": -1.0,
        }
        with self.assertRaisesRegex(ValueError, "M-Phi'' response violates Cauchy-Schwarz"):
            fold.leading_static_vector_current_kernel_from_tensor(
                L, 0.22, 200.0e-6, responses, "q0_anchor"
            )

    def test_leading_static_vector_kernel_rejects_bad_nuclear_cauchy_response(self):
        L = np.zeros((4, 4, 2), dtype=float)
        L[0, 0, 0] = 1.0
        L[1, 1, 0] = 0.01
        L[2, 2, 0] = 0.01
        responses = {
            "M": 4.0,
            "SigmaDoublePrime": 0.0,
            "SigmaPrime": 1.0,
            "PhiPP": 0.2,
            "PhiTildePrime": 0.0,
            "Delta": 2.0,
            "MPhiPP": -0.3,
            "SigmaPrimeDelta": 10.0,
        }
        with self.assertRaisesRegex(ValueError, "Cauchy-Schwarz"):
            fold.leading_static_vector_current_kernel_from_tensor(
                L, 0.22, 200.0e-6, responses, "q0_anchor"
            )

    def test_zero_momentum_form_factor_anchor(self):
        f1q, f2q = fold.quark_form_factor_values(0.0, "isoscalar_zexp")
        f1, f2 = fold.form_factor_values(0.0, "isoscalar_zexp")
        self.assertAlmostEqual(f1q, 3.0, places=10)
        self.assertAlmostEqual(f2q, -0.552, places=10)
        self.assertAlmostEqual(f1, 1.0, places=10)
        self.assertAlmostEqual(f2, -0.184, places=10)

    def test_charge_kernel_uses_full_impulse_tN_when_supplied(self):
        qA = 0.22
        omega = 200.0e-6
        tN = omega * omega - qA * qA
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.5, qA, responses, "bishara_linear", tN_GeV2=tN
        )
        self.assertAlmostEqual(result["F1V_quark_sum"], 3.0 - 8.392 * (-tN), places=13)
        self.assertAlmostEqual(result["F2V_quark_sum"], -0.552, places=13)
        self.assertNotAlmostEqual(-tN, qA * qA, places=12)

    def test_charge_correction_uses_same_finite_t_M_baseline(self):
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.5, 0.22, responses, "bishara_linear"
        )
        self.assertAlmostEqual(
            result["relative_charge_vs_nucleon_finite_t_M_only"],
            result["charge_M_PhiPP"] / result["nucleon_finite_t_M_only"] - 1.0,
            places=14,
        )
        self.assertAlmostEqual(
            result["nucleon_q0_M_only"], result["AFH_finite_size_M_baseline"], places=14
        )
        self.assertAlmostEqual(
            result["AFH_finite_size_M_baseline"], result["AFH_finite_size_M_baseline"], places=14
        )
        self.assertNotEqual(
            result["relative_charge_vs_nucleon_finite_t_M_only"],
            result["relative_charge_vs_AFH_finite_size_M_baseline"],
        )

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

    def test_formal_halo_fold_rejects_non_pole_width_before_loading_inputs(self):
        with self.assertRaisesRegex(ValueError, "pole-only"):
            fold.fold(
                native_dir=Path("does-not-need-to-exist"),
                mchi=1000.0, ms=0.00045, delta_m=0.00045, mV=0.1,
                g2=1.0, coupling_product_squared=1e-8, rho=0.3,
                ER_values_keV=[200.0], nv=2, nw=2, nz=2, nphi=2,
                form_factor_prescription="q0_anchor", width_scheme="running",
            )
        with self.assertRaisesRegex(ValueError, "pole-only"):
            fold.fold(
                native_dir=Path("does-not-need-to-exist"),
                mchi=1000.0, ms=0.00045, delta_m=0.00045, mV=0.1,
                g2=1.0, coupling_product_squared=1e-8, rho=0.3,
                ER_values_keV=[200.0], nv=2, nw=2, nz=2, nphi=2,
                form_factor_prescription="q0_anchor", width_scheme="zero",
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

    def test_gated_leading_static_vector_candidate_fold_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_native_artifact(root)
            result = fold.fold(
                native_dir=root,
                mchi=1000.0,
                ms=300.0e-6,
                delta_m=450.0e-6,
                mV=10.0,
                g2=1.0,
                coupling_product_squared=1.0e-8,
                rho=0.3,
                ER_values_keV=(200.0,),
                nv=2,
                nw=2,
                nz=2,
                nphi=2,
                form_factor_prescription="q0_anchor",
                width_scheme="pole",
                include_leading_static_vector_candidate=True,
            )
            self.assertEqual(
                result["status"],
                "COMPUTED_WITHIN_LEADING_STATIC_VECTOR_CURRENT_CANDIDATE",
            )
            self.assertFalse(result["full_current_complete"])
            self.assertFalse(result["P3_tensor_validation_complete"])
            self.assertTrue(result["leading_static_vector_current_candidate_included"])
            self.assertEqual(len(result["results"]), 2)
            mb = next(row for row in result["results"] if row["halo_model"] == "mb_untruncated")
            self.assertGreater(
                mb["rate_full_six_channel_candidate_events_kg_day_keV"], 0.0
            )
            self.assertGreater(mb["rate_AFH_finite_size_M_baseline_events_kg_day_keV"], 0.0)
            self.assertIn("relative_full_candidate_vs_AFH_finite_size_M_baseline", mb)
            self.assertEqual(
                result["nuclear_response_baseline"],
                "finite-size native AFH W_M(y_A) at each recoil; no point-nucleus substitution",
            )
            self.assertEqual(
                result["AFH_response_normalization"],
                "physical equal-p=n; raw-to-physical factor four applied exactly once",
            )
            self.assertEqual(
                result["coupling_normalization"],
                "coupling_product_squared=(g1*g2*gVN)^2; use Fhat_i=F_i^(u+d+s)/3 in all nucleon-current coefficients",
            )
            self.assertIsNotNone(mb["minimum_spatial_candidate_kernel"])
            self.assertGreaterEqual(mb["minimum_spatial_candidate_kernel"], -1.0e-12)
            self.assertLess(mb["max_native_response_Cauchy_excess"], 1.0e-12)
            self.assertLess(mb["max_native_charge_response_Cauchy_excess"], 1.0e-12)
            self.assertLess(mb["max_native_spatial_response_Cauchy_excess"], 1.0e-12)
            self.assertLess(mb["max_particle_Cauchy_identity_residual"], 1.0e-12)
            self.assertLess(mb["max_charge_reconstruction_residual"], 1.0e-12)

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
