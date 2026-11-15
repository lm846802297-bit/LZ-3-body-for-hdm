import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "audit_lz_2026_conditional_selection_bridge.py"
SPEC = importlib.util.spec_from_file_location("conditional_selection_bridge", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ConditionalSelectionBridgeTests(unittest.TestCase):
    def setUp(self):
        self.event_summary = {
            "comparisons": [
                {
                    "benchmark": "black_ms360_dm1",
                    "nuclear_model": "GCN",
                    "response_family": "eft2024",
                    "acceptance_mode": "nest",
                    "exact_raw_rate_events_kg_day": 10.0,
                    "event_weighted_rate_events_kg_day": 10.0,
                },
                {
                    "benchmark": "black_ms360_dm1",
                    "nuclear_model": "GCN",
                    "response_family": "eft2024",
                    "acceptance_mode": "ws_roi",
                    "exact_raw_rate_events_kg_day": 10.0,
                    "event_weighted_rate_events_kg_day": 8.0,
                },
                {
                    "benchmark": "black_ms360_dm1",
                    "nuclear_model": "GCN",
                    "response_family": "tableS5",
                    "acceptance_mode": "nest",
                    "exact_raw_rate_events_kg_day": 10.0,
                    "event_weighted_rate_events_kg_day": 9.8,
                },
                {
                    "benchmark": "black_ms360_dm1",
                    "nuclear_model": "GCN",
                    "response_family": "tableS5",
                    "acceptance_mode": "ws_roi",
                    "exact_raw_rate_events_kg_day": 10.0,
                    "event_weighted_rate_events_kg_day": 7.5,
                },
            ]
        }
        self.selection_summary = {
            "results": [
                {
                    "benchmark": "black_ms360_dm1",
                    "model": "GCN",
                    "conditional_stage_efficiencies": {
                        "trigger": 1.0,
                        "s1_given_trigger": 1.0,
                        "ss_analysis_given_s1": 0.95,
                        "roi_given_ss_analysis": 0.90,
                        "total_final": 0.855,
                    },
                }
            ]
        }

    def test_factorised_residual_efficiency_is_computed_without_full_curve(self):
        rows = MOD.build_bridge_rows(
            self.event_summary, self.selection_summary, response_family="eft2024"
        )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertAlmostEqual(row["epsilon_nest"], 1.0)
        self.assertAlmostEqual(row["epsilon_ws_roi_given_nest"], 0.8)
        self.assertAlmostEqual(row["epsilon_figs2_ss_da_given_pre_roi"], 0.95)
        self.assertAlmostEqual(row["epsilon_factorized_nest_roi_ss_da"], 0.76)
        self.assertAlmostEqual(row["epsilon_figs2_final"], 0.855)
        self.assertAlmostEqual(row["factorized_to_figs2_final_ratio"], 0.76 / 0.855)

    def test_response_family_filter_selects_tableS5_rows(self):
        rows = MOD.build_bridge_rows(
            self.event_summary, self.selection_summary, response_family="tableS5"
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["response_family"], "tableS5")
        self.assertAlmostEqual(rows[0]["epsilon_nest"], 0.98)
        self.assertAlmostEqual(rows[0]["nest_plus_ws_roi_rate_events_kg_day"], 7.5)

    def test_summary_records_single_response_family(self):
        rows = MOD.build_bridge_rows(
            self.event_summary, self.selection_summary, response_family="tableS5"
        )
        summary = MOD.summarize(rows)
        self.assertEqual(summary["response_family"], "tableS5")
        self.assertEqual(summary["n_rows"], 1)

    def test_summary_rejects_mixed_response_families(self):
        rows = MOD.build_bridge_rows(self.event_summary, self.selection_summary)
        mixed = rows + [{**rows[0], "response_family": "tableS5"}]
        with self.assertRaises(ValueError):
            MOD.summarize(mixed)

    def test_missing_nest_partner_is_rejected(self):
        event = {"comparisons": [self.event_summary["comparisons"][1]]}
        with self.assertRaises(ValueError):
            MOD.build_bridge_rows(event, self.selection_summary)

    def test_invalid_probability_is_rejected(self):
        bad = {
            "results": [{
                "benchmark": "black_ms360_dm1",
                "model": "GCN",
                "conditional_stage_efficiencies": {
                    "trigger": 1.0,
                    "s1_given_trigger": 1.0,
                    "ss_analysis_given_s1": 1.2,
                    "roi_given_ss_analysis": 0.9,
                    "total_final": 0.855,
                },
            }]
        }
        with self.assertRaises(ValueError):
            MOD.build_bridge_rows(self.event_summary, bad)


if __name__ == "__main__":
    unittest.main()
