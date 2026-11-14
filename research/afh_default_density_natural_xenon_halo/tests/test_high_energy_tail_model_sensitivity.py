from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "tail_audit", HERE / "audit" / "audit_high_energy_tail_model_sensitivity.py"
)
tail = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(tail)


class HighEnergyTailAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.metadata = tail.build_results()
        cls.lookup = {(r["benchmark"], r["model"]): r for r in cls.rows}

    def test_piecewise_linear_product_integral_is_analytic(self):
        raw, weighted = tail.integrate_piecewise_linear_product(
            [0.0, 2.0], [2.0, 4.0],
            [0.0, 2.0], [0.5, 0.7],
            0.0, 2.0,
        )
        self.assertAlmostEqual(raw, 6.0, places=13)
        self.assertAlmostEqual(weighted, 11.0 / 3.0, places=13)

    def test_all_four_benchmarks_and_six_model_scenarios_are_present(self):
        self.assertEqual(len(self.rows), 24)
        self.assertEqual(
            {r["benchmark"] for r in self.rows},
            set(tail.BENCHMARKS),
        )
        for benchmark in tail.BENCHMARKS:
            self.assertEqual(
                {r["model"] for r in self.rows if r["benchmark"] == benchmark},
                set(tail.AFH_SCENARIOS) | {"GCN", "JJ55"},
            )

    def test_red_benchmark_reference_tail_counts(self):
        expected = {
            "AFH-7": 0.006731044831060337,
            "Hybrid-9 (AFH-7 + Helm-2)": 0.006809174231040555,
            "Helm-9": 0.030009015013988897,
            "GCN": 0.007606828199442187,
            "JJ55": 0.008015058034335323,
        }
        for model, value in expected.items():
            got = self.lookup[("red_ms200_dm1", model)]["tail_expected_events_central"]
            self.assertAlmostEqual(got, value, delta=max(1.0e-13, value * 2.0e-8))

    def test_gray_efficiency_envelope_brackets_central_count(self):
        for row in self.rows:
            self.assertLessEqual(
                row["tail_expected_events_efficiency_lower"],
                row["tail_expected_events_central"] + 1.0e-14,
            )
            self.assertGreaterEqual(
                row["tail_expected_events_efficiency_upper"] + 1.0e-14,
                row["tail_expected_events_central"],
            )

    def test_helm9_is_separate_large_response_sensitivity_not_hybrid9(self):
        for benchmark in tail.BENCHMARKS:
            afh = self.lookup[(benchmark, "AFH-7")]["tail_expected_events_central"]
            hybrid = self.lookup[(benchmark, "Hybrid-9 (AFH-7 + Helm-2)")]["tail_expected_events_central"]
            helm = self.lookup[(benchmark, "Helm-9")]["tail_expected_events_central"]
            self.assertGreater(helm / afh, 3.0)
            self.assertLess(abs(hybrid / afh - 1.0), 0.02)

    def test_high_tail_fraction_can_coexist_with_negligible_absolute_yield(self):
        row = self.lookup[("black_ms360_dm1", "AFH-7")]
        self.assertGreater(row["tail_fraction_of_full_roi_central"], 0.90)
        self.assertLess(row["tail_expected_events_central"], 1.0e-8)

    def test_model_scope_and_metadata_keep_likelihood_boundary_explicit(self):
        self.assertEqual(self.metadata["status"], "PASS")
        self.assertIn("profile likelihood", " ".join(self.metadata["limitations"]))
        self.assertEqual(self.metadata["integrated_tail_interval_keV"], [225.0, 269.9])
        self.assertAlmostEqual(self.metadata["exposure_kg_day"], 1037310.0, places=8)
        ceiling = self.lookup[("red_ms200_dm1", "AFH-7 + A2-2 ceiling")]
        self.assertIn("diagnostic", ceiling["model_family"])


if __name__ == "__main__":
    unittest.main()
