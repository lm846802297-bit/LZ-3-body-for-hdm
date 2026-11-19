import csv
import tempfile
import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from fold_lz_2026_afh_hybrid9_rate_level import (  # noqa: E402
    SCENARIOS,
    fold_one_group,
    read_selected_spectrum_groups,
)


class AFHHybrid9RateLevelFoldTests(unittest.TestCase):
    def _row(self, energy, rate, scenario="AFH-7"):
        return {
            "benchmark": "red_ms200_dm1",
            "scenario": scenario,
            "ER_keV": str(energy),
            "rate_events_kg_day_keV": str(rate),
            "coupling_product_sq": "1e-8",
            "mchi_GeV": "1000",
            "mV_GeV": "10",
            "g2_for_pole_width": "1",
            "rhoDM_GeV_cm3": "0.3",
            "vmax_km_s": "776",
            "available_atom_fraction": "0.998158",
            "missing_atom_fraction": "0.001842",
            "A2_weighted_AFH_coverage_at_q0": "0.998334",
            "mass_scheme": "NIST nuclear masses",
            "response_q_convention": "exact spatial q",
            "width_scheme": "conditional pole width",
            "detector_response_applied": "False",
        }

    def _write_rows(self, path, rows):
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_only_afh7_and_hybrid9_are_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spectrum.csv"
            rows = [
                self._row(0, 1, "AFH-7"),
                self._row(1, 2, "AFH-7"),
                self._row(0, 1, SCENARIOS[1]),
                self._row(1, 2, SCENARIOS[1]),
                self._row(0, 9, "Helm-9"),
                self._row(1, 9, "Helm-9"),
            ]
            self._write_rows(path, rows)
            groups = read_selected_spectrum_groups(path)
        self.assertEqual(
            set(groups),
            {("red_ms200_dm1", SCENARIOS[0]), ("red_ms200_dm1", SCENARIOS[1])},
        )
        self.assertEqual(len(groups[("red_ms200_dm1", SCENARIOS[0])]), 2)

    def test_duplicate_recoil_energies_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spectrum.csv"
            self._write_rows(path, [self._row(10, 1), self._row(10, 2)])
            with self.assertRaisesRegex(ValueError, "strictly increasing"):
                read_selected_spectrum_groups(path)

    def test_detector_efficiency_cannot_be_applied_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spectrum.csv"
            rows = [self._row(0, 1), self._row(1, 2)]
            for row in rows:
                row["detector_response_applied"] = "True"
            self._write_rows(path, rows)
            with self.assertRaisesRegex(ValueError, "already contains detector efficiency"):
                read_selected_spectrum_groups(path)

    def test_analytic_fold_propagates_central_and_gray_envelope(self):
        rows = [self._row(0.0, 1.0), self._row(2.0, 3.0)]
        result, dense_error, refinement = fold_one_group(
            benchmark="red_ms200_dm1",
            scenario="AFH-7",
            rows=rows,
            efficiency_x=[0.0, 2.0],
            efficiency_central=[0.2, 0.4],
            efficiency_lower=[0.1, 0.3],
            efficiency_upper=[0.3, 0.5],
            benchmark_parameters={"ms_MeV": 0.2, "delta_m_MeV": 1.0},
            roi_min_keV=0.0,
            roi_max_keV=2.0,
            exposure_tonne_year=1.0 / (1000.0 * 365.25),
            integration_steps=2000,
            candidate_interval=(0.5, 1.5),
        )
        self.assertAlmostEqual(result["raw_roi_integral_events_kg_day"], 4.0, places=13)
        self.assertAlmostEqual(
            result["efficiency_weighted_integral_events_kg_day"],
            1.2666666666666666,
            places=13,
        )
        self.assertAlmostEqual(
            result["expected_events_efficiency_lower_envelope"],
            0.8666666666666667,
            places=13,
        )
        self.assertAlmostEqual(
            result["expected_events_efficiency_upper_envelope"],
            1.6666666666666667,
            places=13,
        )
        self.assertFalse(result["is_exclusion_limit"])
        self.assertFalse(result["energy_resolution_smearing_applied"])
        self.assertLess(dense_error, 1e-6)
        self.assertLess(refinement, 1e-6)


if __name__ == "__main__":
    unittest.main()
