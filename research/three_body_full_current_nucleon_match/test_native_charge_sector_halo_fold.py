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

    def test_mediator_denominator_uses_invariant_tA_not_spatial_QA(self):
        mA, mV, ER_keV = 121.9, 10.0, 200.0
        ER = ER_keV * 1.0e-6
        tA = -2.0 * mA * ER
        actual = fold.mediator_denominator_squared_GeV4(mV, mA, ER_keV)
        self.assertAlmostEqual(actual, (mV*mV - tA)**2, places=13)
        spatial_QA2 = 2.0*mA*ER + ER*ER
        self.assertNotAlmostEqual(actual, (mV*mV + spatial_QA2)**2, places=12)

    def test_q0_anchor_is_effective_gVN_normalized_form_factor(self):
        f1, f2 = fold.form_factor_values(0.22, "q0_anchor", tN_GeV2=-0.01)
        self.assertAlmostEqual(f1, 1.0, places=14)
        self.assertAlmostEqual(f2, -0.184, places=14)

    def test_bishara_form_factors_follow_formal_tN_and_effective_basis(self):
        mA = 121.90971983538435
        ER_keV = 200.0
        qA = fold.exact_qA_GeV(mA, ER_keV)
        tN = -2.0 * mA * ER_keV * 1.0e-6
        f1hat, f2hat = fold.form_factor_values(
            qA, "bishara_linear", tN_GeV2=tN
        )
        raw_f1, raw_f2 = fold.bishara_linear(-tN)
        self.assertAlmostEqual(f1hat, raw_f1 / 3.0, places=14)
        self.assertAlmostEqual(f2hat, raw_f2 / 3.0, places=14)
        self.assertNotAlmostEqual(tN, -(qA * qA), places=10)

        transfer = fold.recoil_transfer_kinematics(mA, ER_keV)
        self.assertEqual(transfer["qA_four_vector_GeV"], transfer["qN_four_vector_GeV"])
        self.assertAlmostEqual(transfer["tA_GeV2"], transfer["tN_GeV2"], places=16)
        self.assertAlmostEqual(transfer["Q_A2_GeV2"], qA*qA, places=16)

        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.5, qA, responses, "bishara_linear", tN_GeV2=tN
        )
        expected_cM = f1hat + tN * (f1hat + 2.0 * f2hat) / (
            8.0 * fold.DEFAULT_MN_GEV**2
        )
        self.assertAlmostEqual(result["cM"], expected_cM, places=14)
        self.assertAlmostEqual(result["tN_GeV2"], tN, places=15)

    def test_charge_kernel_decomposes_exactly(self):
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.5, 0.22, responses, "q0_anchor", tN_GeV2=-0.22**2
        )
        expected = sum(result["terms"].values())
        self.assertAlmostEqual(result["extension_C_MplusPhiPP"], expected, places=14)
        self.assertAlmostEqual(
            result["baseline_A_original_AFH_M"], 2.5 * responses["M"], places=14
        )

    def test_charge_kernel_uses_continuity_reduced_weight(self):
        responses = {"M": 4.0, "PhiPP": 0.2, "MPhiPP": -0.3}
        result = fold.charge_kernel_from_coulomb_weight(
            2.4, 0.22, responses, "q0_anchor", tN_GeV2=-0.22**2
        )
        self.assertAlmostEqual(result["L_C"], 2.4)
        self.assertAlmostEqual(result["baseline_A_original_AFH_M"], 2.4 * 4.0)
        self.assertAlmostEqual(
            result["extension_C_MplusPhiPP"],
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

    def test_provisional_response_interpolation_uses_common_linear_psd_preserving_path(self):
        q = np.asarray([0.0, 1.0, 2.0])
        entry = {
            "q": q,
            "interpolation_mode": "linear_psd_preserving",
            "physical": {
                name: np.asarray([1.0, 2.0, 1.0])
                for name in fold.FULL_VECTOR_RESPONSE_NAMES
            },
        }
        out = fold.interpolate_native_response(
            entry, 0.5, response_names=fold.FULL_VECTOR_RESPONSE_NAMES
        )
        self.assertEqual(out["interpolation_used"], "linear_psd_preserving")
        for name in fold.FULL_VECTOR_RESPONSE_NAMES:
            self.assertAlmostEqual(out["physical_equal_pn"][name], 1.5)
            self.assertAlmostEqual(out["linear_physical_equal_pn"][name], 1.5)
            self.assertGreater(out["pchip_linear_relative_difference"][name], 0.1)

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
            result["leading_static_vector_current_candidate"],
            result["charge_sector"] + result["spatial_sector"],
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
        f1, f2 = fold.form_factor_values(0.0, "isoscalar_zexp", tN_GeV2=0.0)
        self.assertAlmostEqual(f1, 1.0, places=10)
        self.assertAlmostEqual(f2, -0.184, places=10)

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
                    for name, column in fold.NATIVE_RESPONSE_W_COLUMNS.items():
                        row[column] = 1.0
                        row[f"Im_{column}"] = 0.0
                    if i == 0:
                        conversion = 4.0 * math.pi / (2.0 * fold.J_BY_A[A] + 1.0)
                        # Deliberately offset the raw package normalization so
                        # the loader must derive and apply C0(A)=0.999.
                        row[fold.NATIVE_RESPONSE_W_COLUMNS["M"]] = (
                            A * A / (4.0 * 0.999 * conversion)
                        )
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
                bundle[131]["common_matrix_normalization_C0"],
                0.999,
                places=12,
            )
            self.assertAlmostEqual(
                bundle[131]["physical"]["M"][0], 131.0**2, places=10
            )
            self.assertEqual(
                gate["provenance"]["physical_zero_momentum_M_anchor"],
                "M(q_A=0)=A^2",
            )
            for A in fold.ISOTOPES:
                self.assertAlmostEqual(
                    bundle[A]["physical"]["M"][0], float(A * A), places=10
                )
                c0 = bundle[A]["common_matrix_normalization_C0"]
                conversion = 4.0 * math.pi / (2.0 * fold.J_BY_A[A] + 1.0)
                expected_nonzero_q = 4.0 * c0 * conversion
                for name in fold.NATIVE_RESPONSE_W_COLUMNS:
                    self.assertAlmostEqual(
                        bundle[A]["physical"][name][1],
                        expected_nonzero_q,
                        places=10,
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
            self.assertGreater(mb["rate_A_original_AFH_M_events_kg_day_keV"], 0.0)
            self.assertGreater(mb["rate_B_baseline_M_events_kg_day_keV"], 0.0)
            self.assertGreater(mb["rate_C_charge_extension_events_kg_day_keV"], 0.0)
            self.assertIn("W_M(y_A)", result["primary_baseline"])
            self.assertIn("t_A=-2*m_A*E_R", result["mediator_denominator"])
            self.assertEqual(result["nucleon_transfer_scheme"],
                "one-body impulse-current external-transfer assignment q_N^mu=q_A^mu; t_N=t_A=-2*m_A*E_R")
            xe131 = next(item for item in mb["isotope_rows"] if item["A"] == 131)
            self.assertEqual(xe131["qA_four_vector_GeV"], xe131["qN_four_vector_GeV"])
            self.assertAlmostEqual(xe131["tA_GeV2"], xe131["tN_GeV2"], places=16)
            self.assertEqual(xe131["metric_signature"], "+---")
            self.assertGreater(
                mb["rate_leading_static_vector_candidate_events_kg_day_keV"], 0.0
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
