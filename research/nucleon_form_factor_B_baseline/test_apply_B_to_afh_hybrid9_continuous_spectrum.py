import csv
import json
import math
import tempfile
import unittest
from pathlib import Path

from apply_B_to_afh_hybrid9_continuous_spectrum import rate_prefactor, run


class ApplyBToAbsoluteAFHSpectrumTests(unittest.TestCase):
    def _write_csv(self, path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_exact_P0_closure_and_isotope_level_B_resummation(self):
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
                "recoil_grid_keV": {"points": 2, "minimum": 100.0, "maximum": 200.0},
                "response_convention": "AFH direct finite-sum at exact spatial q",
                "afh_source_file": "v6/dmformfactor-V6.m",
                "afh_source_sha256": "test-source-sha",
                "natural_atom_fraction_AFH7": 0.998158,
                "natural_atom_fraction_missing": 0.001842,
                "A2_weighted_AFH_coverage_at_q0": 0.998334,
                "nuclear_mass_scheme": "NIST nuclear masses",
            }
            (source / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")

            isotope_rows = []
            spectrum_rows = []
            prefactor = rate_prefactor(metadata)
            mV = 10.0
            isotope_specs = [
                (124, 115.39, 0.000952, None, 1.30),
                (129, 120.046, 0.264006, 0.80, 0.90),
                (131, 121.910, 0.212324, 0.75, 0.85),
            ]
            for ER in (100.0, 200.0):
                grouped = []
                for A, mA, abundance, r_afh, r_helm in isotope_specs:
                    ER_GeV = ER * 1.0e-6
                    q = math.sqrt(2.0*mA*ER_GeV + ER_GeV**2)
                    kernel = 1.0e-12 * (1.0 + A/100.0) * (1.0 + ER/100.0)
                    isotope = {
                        "benchmark": "test_benchmark",
                        "A": A,
                        "ER_keV": ER,
                        "mA_GeV": mA,
                        "q_exact_spatial_GeV": q,
                        "natural_atom_fraction": abundance,
                        "kernel_halo_integral_GeV": kernel,
                        "R_AFH_direct_exact_q": "" if r_afh is None else r_afh,
                        "R_Helm": r_helm,
                    }
                    isotope_rows.append(isotope)
                    grouped.append((isotope, r_afh, r_helm))

                for scenario in ("AFH-7", "Hybrid-9 (AFH-7 + Helm-2)"):
                    total = 0.0
                    for isotope, r_afh, r_helm in grouped:
                        if scenario == "AFH-7":
                            response = 0.0 if r_afh is None else r_afh
                        else:
                            response = r_helm if r_afh is None else r_afh
                        if response == 0.0:
                            continue
                        ER_GeV = ER * 1.0e-6
                        denominator = (
                            mV*mV + 2.0*isotope["mA_GeV"]*ER_GeV
                        )**2
                        total += (
                            prefactor * isotope["natural_atom_fraction"]
                            * isotope["kernel_halo_integral_GeV"]
                            * response / denominator
                        )
                    spectrum_rows.append({
                        "benchmark": "test_benchmark",
                        "scenario": scenario,
                        "ER_keV": ER,
                        "rate_events_kg_day_keV": total,
                    })

            self._write_csv(source / "afh_hybrid9_isotope_kernel_integrals.csv", isotope_rows)
            self._write_csv(source / "afh_hybrid9_natural_xenon_spectrum.csv", spectrum_rows)

            result = run(
                source, out, "sufian2017_unit_current",
                n_draws=64, seed=7, closure_tolerance=2.0e-11,
            )
            self.assertEqual(result["status"], "PASS")
            self.assertLessEqual(
                result["validation"]["maximum_P0_reconstruction_relative_difference"],
                2.0e-11,
            )

            with (out / "afh_hybrid9_B_natural_xenon_spectrum.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                rates = list(csv.DictReader(handle))
            with (out / "afh_hybrid9_B_isotope_contributions.csv").open(
                newline="", encoding="utf-8"
            ) as handle:
                isotope_rates = list(csv.DictReader(handle))

            self.assertEqual(len(rates), 4)
            self.assertEqual(len(isotope_rates), 10)
            self.assertTrue(all(0.0 < float(row["B_over_P0_rate"]) < 1.0 for row in rates))
            self.assertTrue(all("c_M_raw" in row and "c_M_hat" in row for row in isotope_rates))
            self.assertAlmostEqual(
                float(isotope_rates[0]["c_M_hat"]),
                float(isotope_rates[0]["c_M_raw"])/3.0,
                places=12,
            )
            self.assertAlmostEqual(
                float(isotope_rates[0]["F_M"]),
                float(isotope_rates[0]["c_M_hat"]),
                places=12,
            )
            self.assertTrue(all(float(row["nucleon_FF_rate_multiplier"]) > 0.0
                                for row in isotope_rates))
            transfer_row = isotope_rates[0]
            q2_ff = 2.0 * float(transfer_row["mA_GeV"]) * float(transfer_row["ER_keV"]) * 1.0e-6
            qA2 = q2_ff + (float(transfer_row["ER_keV"]) * 1.0e-6) ** 2
            self.assertAlmostEqual(float(transfer_row["Q2_form_factor_GeV2"]), q2_ff, places=16)
            self.assertAlmostEqual(float(transfer_row["Q_A2_GeV2"]), qA2, places=16)
            self.assertAlmostEqual(float(transfer_row["t_N_GeV2"]), -q2_ff, places=16)
            self.assertAlmostEqual(float(transfer_row["t_A_GeV2"]), -q2_ff, places=16)
            hybrid_100 = next(
                row for row in isotope_rates
                if row["scenario"] == "Hybrid-9 (AFH-7 + Helm-2)"
                and int(row["A"]) == 124 and float(row["ER_keV"]) == 100.0
            )
            self.assertGreater(float(hybrid_100["rate_B_contribution_events_kg_day_keV"]), 0.0)
            self.assertIn('"detector_response_applied": false', (out / "metadata.json").read_text())


if __name__ == "__main__":
    unittest.main()
