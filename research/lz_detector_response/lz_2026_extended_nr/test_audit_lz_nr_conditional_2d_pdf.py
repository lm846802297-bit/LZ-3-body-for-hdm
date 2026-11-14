from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from audit_lz_nr_conditional_2d_pdf import (
    EXPECTED_FAMILIES,
    EXPECTED_NEST_COMMIT,
    audit_object,
)


def sample_object():
    families = {}
    for name in EXPECTED_FAMILIES:
        families[name] = {
            "n_generated": 100,
            "energy_bins": [
                {
                    "energy_low_keV": 0.0,
                    "energy_high_keV": 10.0,
                    "n_valid": 40,
                    "pdf_sparse": [[10.0, 3.0, 0.25], [20.0, 3.2, 0.75]],
                },
                {
                    "energy_low_keV": 10.0,
                    "energy_high_keV": 20.0,
                    "n_valid": 50,
                    "pdf_sparse": [[30.0, 3.4, 0.5], [40.0, 3.6, 0.5]],
                },
            ],
        }
    return {
        "study": "LZ NR conditional 2D response PDFs",
        "nest_commit": EXPECTED_NEST_COMMIT,
        "energy_prior": "Uniform true NR energy 0.1-330 keV",
        "spatial_prior": "Uniform active-TPC cylinder proxy",
        "binning": {
            "energy_keV": 10.0,
            "S1c_phd": 10.0,
            "log10S2c_dex": 0.02,
        },
        "note": "No separate S1 coincidence flag is stored; conditional on positive observables.",
        "families": families,
    }


class ConditionalPDFAuditTests(unittest.TestCase):
    def test_reports_global_fraction_without_claiming_energy_dependent_efficiency(self):
        report = audit_object(sample_object())
        self.assertEqual(report["audit_status"], "STRUCTURE_VALIDATED")
        self.assertEqual(report["selection_status"], "PRE_SELECTION_ONLY")
        family = report["families"]["eft2024"]
        self.assertAlmostEqual(family["global_positive_observable_fraction"], 0.9)
        self.assertFalse(family["per_bin_generated_count_present"])
        self.assertFalse(family["separate_s1_coincidence_count_present"])
        self.assertTrue(report["missing_information"]["raw_S2_phd_for_S2_gt_645_phd_cut"])
        self.assertFalse(report["likelihood_allowed"])

    def test_rejects_non_normalized_conditional_pdf(self):
        obj = sample_object()
        obj["families"]["eft2024"]["energy_bins"][0]["pdf_sparse"][0][2] = 0.5
        with self.assertRaises(ValueError):
            audit_object(obj)

    def test_rejects_non_contiguous_energy_bins(self):
        obj = sample_object()
        obj["families"]["eft2024"]["energy_bins"][1]["energy_low_keV"] = 11.0
        with self.assertRaises(ValueError):
            audit_object(obj)

    def test_rejects_wrong_nest_commit(self):
        obj = sample_object()
        obj["nest_commit"] = "not-the-audited-commit"
        with self.assertRaises(ValueError):
            audit_object(obj)


if __name__ == "__main__":
    unittest.main()
