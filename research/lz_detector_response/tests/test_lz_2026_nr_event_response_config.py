from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "lz_2026_extended_nr"
CPP = ROOT / "cpp" / "lz_2026_nr_event_response.cpp"


class NRResponseConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yield_json = json.loads(
            (EXT / "lz_2026_nest_nr_mean_yield_parameters.json").read_text(
                encoding="utf-8"
            )
        )
        cls.width_json = json.loads(
            (EXT / "lz_2026_nr_fluctuation_baselines.json").read_text(
                encoding="utf-8"
            )
        )
        cls.cpp = CPP.read_text(encoding="utf-8")

    def test_text_table_s5_vector_matches_archived_json(self):
        values = [
            float(value)
            for value in (
                EXT / "lz_2026_nr_yield_params_s5.txt"
            ).read_text(encoding="utf-8").split()
        ]
        self.assertEqual(len(values), 15)
        self.assertEqual(values, self.yield_json["nest_vector"])

    def test_generic_width_vector_matches_pinned_nest_json(self):
        match = re.search(
            r"kGenericNRERWidths\s*=\s*\{([^}]*)\}", self.cpp, re.S
        )
        self.assertIsNotNone(match)
        values = [
            float(token)
            for token in re.findall(
                r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?",
                match.group(1),
            )
        ]
        expected = self.width_json["candidates"]["generic_nest_default"][
            "full_13_element_NRERWidthsParam"
        ]
        self.assertEqual(values, expected)

    def test_energy_grid_contains_candidate_and_analysis_endpoint(self):
        match = re.search(
            r"kEnergiesKeV\s*=\s*\{([^}]*)\}", self.cpp, re.S
        )
        self.assertIsNotNone(match)
        values = [
            float(token)
            for token in re.findall(
                r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?",
                match.group(1),
            )
        ]
        self.assertIn(248.0, values)
        self.assertIn(269.9, values)
        self.assertEqual(values[0], 5.4)

    def test_driver_uses_nest_detector_response_outputs(self):
        self.assertIn("calculator.FullCalculation(", self.cpp)
        self.assertIn("calculator.GetS1(", self.cpp)
        self.assertIn("calculator.GetS2(", self.cpp)
        self.assertIn("NEST::S1CalculationMode::Full", self.cpp)
        self.assertIn("NEST::S2CalculationMode::Full", self.cpp)
        self.assertIn("const double s1c_signed = s1[5];", self.cpp)
        self.assertIn("const double s2c_signed = s2[7];", self.cpp)
        self.assertIn("s2_threshold_raw_equiv_phd", self.cpp)
        self.assertIn("s2c_threshold_reference_phd", self.cpp)
        self.assertIn("result.quanta.photons", self.cpp)
        self.assertIn("result.quanta.electrons", self.cpp)


if __name__ == "__main__":
    unittest.main()
