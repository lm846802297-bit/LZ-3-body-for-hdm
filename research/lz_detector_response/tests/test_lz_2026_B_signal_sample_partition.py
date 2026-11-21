from __future__ import annotations

import csv
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lz_2026_extended_nr"))

from partition_lz_2026_signal_samples import (
    DELAYED_FRACTION,
    MODEL_NAMES,
    PROMPT_FRACTION,
    SCIENCE_FRACTION,
    partition_rows,
    write_outputs,
)


def source_row(**overrides):
    row = {
        "strange_model": MODEL_NAMES[0],
        "benchmark": "red_ms200_dm1",
        "scenario": "AFH-7",
        "ms_MeV": "0.2",
        "delta_m_MeV": "1.0",
        "exposure_tonne_year": "2.84",
        "exposure_kg_day": "1037310.0",
        "expected_events_in_high_efficiency_window": "0.2662628",
        "expected_events_in_candidate_statistical_slice": "0.2475",
        "detector_efficiency_applied": "True",
        "energy_resolution_smearing_applied": "False",
        "two_dimensional_signal_pdf_applied": "False",
        "background_likelihood_applied": "False",
    }
    row.update(overrides)
    return row


class SignalSamplePartitionTests(unittest.TestCase):
    def test_published_exclusive_fractions_sum_to_one(self):
        self.assertAlmostEqual(SCIENCE_FRACTION + PROMPT_FRACTION + DELAYED_FRACTION, 1.0, places=15)
        self.assertAlmostEqual(SCIENCE_FRACTION, 0.9713, places=15)
        self.assertAlmostEqual(PROMPT_FRACTION, 1.0e-4, places=15)
        self.assertAlmostEqual(DELAYED_FRACTION, 2.86e-2, places=15)

    def test_partition_closes_and_keeps_three_samples_separate(self):
        result = partition_rows([source_row()])[0]
        total = result["expected_events_after_FigS2_before_veto"]
        parts = (
            result["expected_events_science"],
            result["expected_events_prompt_veto"],
            result["expected_events_delayed_veto"],
        )
        self.assertAlmostEqual(sum(parts), total, places=15)
        self.assertAlmostEqual(result["sample_sum_closure_abs"], 0.0, places=15)
        self.assertAlmostEqual(result["expected_events_science"], total * 0.9713, places=15)
        self.assertAlmostEqual(result["expected_events_prompt_veto"], total * 1.0e-4, places=15)
        self.assertAlmostEqual(result["expected_events_delayed_veto"], total * 0.0286, places=15)

    def test_rejects_missing_fig_s2_efficiency(self):
        with self.assertRaisesRegex(ValueError, "Fig. S2"):
            partition_rows([source_row(detector_efficiency_applied="False")])

    def test_rejects_double_claimed_two_dimensional_pdf(self):
        with self.assertRaisesRegex(ValueError, "rate-level"):
            partition_rows([source_row(two_dimensional_signal_pdf_applied="True")])

    def test_candidate_slice_is_partitioned_with_same_sample_fractions(self):
        result = partition_rows([source_row()])[0]
        candidate = result["candidate_slice_events_after_FigS2_before_veto"]
        self.assertAlmostEqual(
            result["candidate_slice_events_science"]
            + result["candidate_slice_events_prompt_veto"]
            + result["candidate_slice_events_delayed_veto"],
            candidate,
            places=15,
        )

    def test_write_outputs_marks_result_as_diagnostic_not_exclusion(self):
        rows = partition_rows([source_row()])
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            write_outputs(rows, out)
            with (out / "lz_2026_B_signal_three_sample_partition.csv").open(newline="") as f:
                saved = list(csv.DictReader(f))
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]["is_exclusion_limit"], "False")
            self.assertEqual(saved[0]["background_likelihood_applied"], "False")
            self.assertTrue((out / "metadata.json").is_file())


if __name__ == "__main__":
    unittest.main()
