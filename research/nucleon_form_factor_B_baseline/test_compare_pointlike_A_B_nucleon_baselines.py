import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from apply_B_to_afh_hybrid9_continuous_spectrum import rate_prefactor
from compare_pointlike_A_B_nucleon_baselines import (
    MODELS,
    pointlike_dirac_cM_hat,
    q2_form_factor_from_recoil,
    qA2_spatial_from_recoil,
    run,
)


class PointlikeABComparisonTests(unittest.TestCase):
    def _write_csv(self, path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_transfer_definitions_are_separate(self):
        mA = 120.0
        ER = 200.0
        q2_ff = q2_form_factor_from_recoil(mA, ER)
        qA2 = qA2_spatial_from_recoil(mA, ER)
        self.assertAlmostEqual(q2_ff, 2.0 * mA * ER * 1.0e-6, places=16)
        self.assertAlmostEqual(qA2 - q2_ff, (ER * 1.0e-6) ** 2, places=16)
        self.assertEqual(pointlike_dirac_cM_hat(0.0), 1.0)
        self.assertLess(pointlike_dirac_cM_hat(q2_ff), 1.0)

    def test_A_P_B_spectra_and_detector_fold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            out = root / "out"
            source.mkdir()

            metadata = {
                "status": "PASS",
                "detector_response_applied": False,
                "particle_parameters": {
                    "mchi_GeV": 1000.0,
                    "mV_GeV": 10.0,
                    "coupling_product_squared": 1.0e-8,
                    "g2_for_width": 1.0,
                    "rhoDM_GeV_cm3": 0.3,
                    "benchmarks": {
                        "test_benchmark": {"ms_MeV": 0.3, "delta_m_MeV": 1.0}
                    },
                },
                "halo": {"vmax_lab_km_s": 776.0},
                "natural_atom_fraction_AFH7": 0.264,
                "natural_atom_fraction_missing": 0.000952,
                "A2_weighted_AFH_coverage_at_q0": 0.99,
                "nuclear_mass_scheme": "synthetic test masses",
                "response_convention": "synthetic AFH test response",
                "afh_source_file": "synthetic",
                "afh_source_sha256": "synthetic",
            }
            (source / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

            isotope_specs = [
                (129, 120.0, 0.264, 0.8, 0.9),
                (124, 115.39, 0.000952, "", 1.3),
            ]
            isotope_rows = []
            spectrum_rows = []
            prefactor = rate_prefactor(metadata)
            mV = 10.0
            for ER in (5.0, 300.0):
                by_scenario = {"AFH-7": 0.0, "Hybrid-9 (AFH-7 + Helm-2)": 0.0}
                for A, mA, abundance, r_afh, r_helm in isotope_specs:
                    ER_GeV = ER * 1.0e-6
                    q = math.sqrt(2.0 * mA * ER_GeV + ER_GeV**2)
                    kernel = 0.0 if ER == 5.0 else 1.0e-12
                    isotope_rows.append({
                        "benchmark": "test_benchmark",
                        "A": A,
                        "ER_keV": ER,
                        "mA_GeV": mA,
                        "q_exact_spatial_GeV": q,
                        "natural_atom_fraction": abundance,
                        "kernel_halo_integral_GeV": kernel,
                        "R_AFH_direct_exact_q": r_afh,
                        "R_Helm": r_helm,
                    })
                    tA_abs = 2.0 * mA * ER_GeV
                    denominator = (mV * mV + tA_abs) ** 2
                    if kernel == 0.0:
                        contribution = 0.0
                    else:
                        contribution = prefactor * abundance * kernel * r_afh / denominator if r_afh != "" else 0.0
                    by_scenario["AFH-7"] += contribution
                    hybrid_response = r_afh if r_afh != "" else r_helm
                    if kernel == 0.0:
                        hybrid_contribution = 0.0
                    else:
                        hybrid_contribution = prefactor * abundance * kernel * hybrid_response / denominator
                    by_scenario["Hybrid-9 (AFH-7 + Helm-2)"] += hybrid_contribution

                for scenario, rate in by_scenario.items():
                    spectrum_rows.append({
                        "benchmark": "test_benchmark",
                        "scenario": scenario,
                        "ER_keV": ER,
                        "rate_events_kg_day_keV": rate,
                    })

            self._write_csv(source / "afh_hybrid9_isotope_kernel_integrals.csv", isotope_rows)
            self._write_csv(source / "afh_hybrid9_natural_xenon_spectrum.csv", spectrum_rows)

            efficiency_rows = [
                {"ER_keV": 0.0, "efficiency_final_WS_ROI": 0.0,
                 "efficiency_lower_envelope": 0.0, "efficiency_upper_envelope": 0.0},
                {"ER_keV": 5.4, "efficiency_final_WS_ROI": 0.5,
                 "efficiency_lower_envelope": 0.45, "efficiency_upper_envelope": 0.55},
                {"ER_keV": 100.0, "efficiency_final_WS_ROI": 0.8,
                 "efficiency_lower_envelope": 0.75, "efficiency_upper_envelope": 0.85},
                {"ER_keV": 269.9, "efficiency_final_WS_ROI": 0.9,
                 "efficiency_lower_envelope": 0.85, "efficiency_upper_envelope": 0.95},
                {"ER_keV": 300.0, "efficiency_final_WS_ROI": 0.9,
                 "efficiency_lower_envelope": 0.85, "efficiency_upper_envelope": 0.95},
            ]
            efficiency_path = root / "efficiency.csv"
            self._write_csv(efficiency_path, efficiency_rows)

            result = run(
                source_dir=source,
                efficiency_csv=efficiency_path,
                out_dir=out,
                roi_min_keV=5.4,
                roi_max_keV=269.9,
                exposure_tonne_year=2.84,
            )
            self.assertEqual(result["status"], "PASS")
            self.assertLessEqual(
                result["validation"]["maximum_A_reconstruction_relative_difference"],
                2.0e-11,
            )

            with (out / "pointlike_A_B_detector_yields.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                detector_rows = list(csv.DictReader(handle))
            self.assertEqual(len(detector_rows), 2 * len(MODELS))
            self.assertTrue(all(
                float(row["P_expected_events"]) < float(row["A_expected_events"])
                for row in detector_rows
            ))
            self.assertTrue(all(
                float(row["B_expected_events"]) > 0.0
                for row in detector_rows
            ))
            afh = next(row for row in detector_rows
                       if row["scenario"] == "AFH-7"
                       and row["strange_form_factor_model"] == MODELS[0])
            hybrid = next(row for row in detector_rows
                          if row["scenario"] == "Hybrid-9 (AFH-7 + Helm-2)"
                          and row["strange_form_factor_model"] == MODELS[0])
            self.assertGreater(
                float(hybrid["A_expected_events"]),
                float(afh["A_expected_events"]),
            )
            self.assertTrue((out / "SHA256SUMS.txt").is_file())


if __name__ == "__main__":
    unittest.main()
