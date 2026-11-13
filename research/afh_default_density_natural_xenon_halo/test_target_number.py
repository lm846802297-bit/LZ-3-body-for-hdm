from __future__ import annotations

import csv
import json
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
INPUT = HERE / "input" / "natural_xenon_isotope_weights.csv"
ACTIVE_METADATA = HERE / "results" / "metadata.json"
LEGACY_METADATA = (
    REPO / "afh_default_density_xe131" / "output"
    / "natural_xenon_halo_metadata_nist_mass.json"
)

AVOGADRO = 6.02214076e23


class NaturalXenonTargetNumberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with INPUT.open(newline="", encoding="utf-8") as handle:
            cls.rows = list(csv.DictReader(handle))
        cls.mean_atomic_weight = sum(
            float(row["atomic_mass_u"]) * float(row["natural_atom_fraction"])
            for row in cls.rows
        )
        cls.target_nuclei_per_kg = AVOGADRO * 1000.0 / cls.mean_atomic_weight
        cls.active = json.loads(ACTIVE_METADATA.read_text(encoding="utf-8"))
        cls.legacy = json.loads(LEGACY_METADATA.read_text(encoding="utf-8"))

    def test_all_nine_natural_isotopes_define_target_mass_average(self):
        self.assertEqual(len(self.rows), 9)
        self.assertAlmostEqual(
            sum(float(row["natural_atom_fraction"]) for row in self.rows),
            1.0,
            places=14,
        )
        self.assertAlmostEqual(
            self.mean_atomic_weight, 131.29276144779053, places=12
        )

    def test_active_metadata_matches_input_weighted_average_and_target_count(self):
        self.assertAlmostEqual(
            self.active["mean_atomic_weight_for_target_number_g_mol"],
            self.mean_atomic_weight,
            places=12,
        )
        self.assertTrue(
            math.isclose(
                self.active["target_nuclei_per_kg"],
                self.target_nuclei_per_kg,
                rel_tol=2e-15,
            )
        )

    def test_legacy_metadata_is_aligned_without_renormalizing_afh_isotopes(self):
        self.assertAlmostEqual(
            self.legacy["mean_xenon_atomic_weight_g_mol"],
            self.mean_atomic_weight,
            places=12,
        )
        self.assertTrue(
            math.isclose(
                self.legacy["target_nuclei_per_kg"],
                self.target_nuclei_per_kg,
                rel_tol=2e-15,
            )
        )
        available_fraction = sum(
            float(row["natural_atom_fraction"])
            for row in self.rows
            if row["AFH_default_density_available"].lower() == "true"
        )
        self.assertAlmostEqual(available_fraction, 0.998158, places=12)
        self.assertEqual(self.active["omitted_isotopes"], [124, 126])


if __name__ == "__main__":
    unittest.main()
