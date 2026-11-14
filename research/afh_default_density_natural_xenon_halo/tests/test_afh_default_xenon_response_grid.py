from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "afh_default_density_xe131"))

from generate_afh_default_xenon_response_grid import (  # noqa: E402
    EXPECTED_ENTRIES,
    ISOTOPES,
    compute_isotope_grid,
    parse_default_dispatch,
    parse_density_matrix,
    parse_isotopic_spins,
    read_natural_xenon_masses,
)


class AFHDefaultXenonResponseGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_path = ROOT / "v6" / "dmformfactor-V6.m"
        cls.weights_path = HERE / "input" / "natural_xenon_isotope_weights.csv"
        cls.source_text = cls.source_path.read_text(encoding="utf-8")
        cls.spins = parse_isotopic_spins(cls.source_text)
        cls.masses = read_natural_xenon_masses(cls.weights_path)
        cls.matrices = {
            A: parse_density_matrix(cls.source_text, A) for A in ISOTOPES
        }

    def test_official_default_dispatch_is_exactly_seven_isotopes(self):
        self.assertEqual(set(ISOTOPES), {128, 129, 130, 131, 132, 134, 136})
        for A in ISOTOPES:
            self.assertTrue(parse_default_dispatch(self.source_text, A), A)
        self.assertFalse(parse_default_dispatch(self.source_text, 124))
        self.assertFalse(parse_default_dispatch(self.source_text, 126))

    def test_all_density_matrix_entry_counts_and_indices(self):
        for A in ISOTOPES:
            rows = self.matrices[A]
            self.assertEqual(len(rows), EXPECTED_ENTRIES[A], A)
            self.assertEqual(
                [row["index"] for row in rows],
                list(range(1, EXPECTED_ENTRIES[A] + 1)),
                A,
            )

    def test_source_spin_assignments(self):
        expected = {
            124: 0.0, 126: 0.0, 128: 0.0, 129: 0.5,
            130: 0.0, 131: 1.5, 132: 0.0, 134: 0.0, 136: 0.0,
        }
        for A, J in expected.items():
            self.assertEqual(self.spins[A], J, A)

    def test_missing_isotopes_have_real_abundance_but_no_afh_default_matrix(self):
        self.assertAlmostEqual(self.masses[124]["natural_atom_fraction"], 0.000952)
        self.assertAlmostEqual(self.masses[126]["natural_atom_fraction"], 0.000890)
        self.assertFalse(self.masses[124]["AFH_default_density_available"])
        self.assertFalse(self.masses[126]["AFH_default_density_available"])

    def test_isoscalar_multipoles_match_elastic_selection_rules(self):
        rank_counts = {
            A: {
                rank: sum(
                    row["rank"] == rank and row["isospin"] == 0
                    for row in self.matrices[A]
                )
                for rank in range(4)
            }
            for A in ISOTOPES
        }
        for A in (128, 130, 132, 134, 136):
            self.assertEqual(rank_counts[A][0], 16)
            self.assertEqual(rank_counts[A][2], 0)
        self.assertEqual(rank_counts[129][0], 16)
        self.assertEqual(rank_counts[129][2], 0)
        self.assertEqual(rank_counts[131][0], 16)
        self.assertEqual(rank_counts[131][2], 8)

    def test_q_zero_package_and_physical_normalizations_for_all_seven(self):
        for A in ISOTOPES:
            rows, summary = compute_isotope_grid(
                A=A,
                rows=self.matrices[A],
                J_A=self.spins[A],
                mass_GeV=self.masses[A]["nuclear_mass_GeV"],
                q_grid=np.asarray([0.0]),
            )
            self.assertAlmostEqual(
                rows[0]["R_AFH_package_4pi_over_2Jplus1"], A * A / 4.0,
                delta=(A * A / 4.0) * 5.0e-4,
            )
            self.assertAlmostEqual(rows[0]["R_equal_pn_normalized"], A * A, places=9)
            self.assertLess(summary["AFH_R0_relative_error"], 5.0e-4)

    def test_xe131_full_2401_point_grid_matches_archived_python_baseline(self):
        A = 131
        q_grid = np.arange(2401, dtype=float) * 0.00025
        generated, _ = compute_isotope_grid(
            A=A,
            rows=self.matrices[A],
            J_A=self.spins[A],
            mass_GeV=self.masses[A]["nuclear_mass_GeV"],
            q_grid=q_grid,
        )
        baseline_path = (
            ROOT / "research" / "afh_default_density_xe131" /
            "output" / "afh_default_xe131_WM00.csv"
        )
        with baseline_path.open(newline="", encoding="utf-8") as stream:
            baseline = list(csv.DictReader(stream))
        self.assertEqual(len(baseline), 2401)
        for key in (
            "q_GeV", "y", "W_M00_AFH_package",
            "R_AFH_package_4pi_over_2Jplus1",
            "R_equal_pn_raw", "R_equal_pn_normalized",
            "R_equal_J0_normalized", "R_equal_J2_normalized",
            "R_over_A2", "rank0_amplitude", "rank2_amplitude",
        ):
            expected = np.asarray([float(row[key]) for row in baseline])
            actual = np.asarray([row[key] for row in generated])
            np.testing.assert_allclose(actual, expected, rtol=2.0e-8, atol=2.0e-10, err_msg=key)


if __name__ == "__main__":
    unittest.main(verbosity=2)
