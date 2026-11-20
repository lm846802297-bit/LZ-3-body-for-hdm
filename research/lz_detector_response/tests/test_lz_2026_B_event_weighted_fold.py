from __future__ import annotations

import array
import json
import tempfile
import unittest
from pathlib import Path

from research.lz_detector_response.fold_lz_2026_three_body_B_event_weighted_response import (
    fold_one_spectrum,
    read_b_spectrum,
    validate_formal_B_metadata,
)


class TestBEventWeightedNESTFold(unittest.TestCase):
    def test_b_spectrum_reader_uses_formal_B_rate_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "spectrum.csv"
            path.write_text(
                "benchmark,scenario,ER_keV,rate_events_kg_day_keV,rate_B_events_kg_day_keV\n"
                "red_ms200_dm1,AFH-7,5.0,99,2\n"
                "red_ms200_dm1,AFH-7,300.0,999,4\n"
                "blue_ms300_dm10,AFH-7,5.0,88,8\n"
                "blue_ms300_dm10,AFH-7,300.0,888,16\n",
                encoding="utf-8",
            )
            xs, ys = read_b_spectrum(path, "red_ms200_dm1", "AFH-7")
            self.assertEqual(xs, [5.0, 300.0])
            self.assertEqual(ys, [2.0, 4.0])

    def test_formal_transfer_metadata_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.json"
            path.write_text(json.dumps({
                "detector_response_applied": False,
                "matching": {"t_N": "-2*m_A*E_R = t_A (formal impulse matching)"},
            }), encoding="utf-8")
            self.assertFalse(validate_formal_B_metadata(path)["detector_response_applied"])
            path.write_text(json.dumps({
                "detector_response_applied": False,
                "matching": {"t_N": "-Q_A^2 (historical static diagnostic)"},
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                validate_formal_B_metadata(path)

    def test_event_weights_close_exact_rate_and_apply_ws_roi_once(self):
        events = {
            (0, 0): {
                "lo": 5.4,
                "hi": 6.4,
                "energy": array.array("d", [5.6, 6.2]),
                "s1_bin": array.array("i", [1, 1]),
                "log_s2_bin": array.array("i", [150, 150]),
                "nest_pass": bytearray([1, 1]),
                "roi_pass": bytearray([1, 1]),
            },
            (0, 1): {
                "lo": 5.4,
                "hi": 6.4,
                "energy": array.array("d", [5.6, 6.2]),
                "s1_bin": array.array("i", [1, 70]),
                "log_s2_bin": array.array("i", [150, 150]),
                "nest_pass": bytearray([1, 1]),
                "roi_pass": bytearray([1, 0]),
            },
        }
        folded = fold_one_spectrum(events, [5.4, 6.4], [2.0, 4.0])
        self.assertAlmostEqual(folded[None]["raw_rate"], 3.0, places=14)
        self.assertAlmostEqual(folded[None]["accepted_rate"]["nest"], 3.0, places=14)
        self.assertAlmostEqual(folded[None]["accepted_rate"]["ws_roi"], 2.1, places=14)
        self.assertAlmostEqual(
            folded[None]["intensity"]["ws_roi"][(1, 150)], 2.1, places=14
        )
        self.assertAlmostEqual(
            folded[None]["intensity"]["nest"][(70, 150)], 0.9, places=14
        )
        self.assertAlmostEqual(
            folded[None]["bin_rows"][0]["ws_roi_acceptance_weighted_replica1"],
            0.4,
            places=14,
        )
        self.assertAlmostEqual(
            folded[None]["bin_rows"][0]["nest_acceptance_weighted_replica0"],
            1.0,
            places=14,
        )


if __name__ == "__main__":
    unittest.main()
