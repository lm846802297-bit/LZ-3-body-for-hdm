import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "aggregate_lz_2026_paired_s1_2d_independent_seeds.py"
)
SPEC = importlib.util.spec_from_file_location("paired_s1_2d_independent_seeds", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def write_seed_fixture(root: Path, seeds: list[int], corrupt_map_closure: bool = False):
    map_fields = [
        "benchmark", "nuclear_model", "response_model", "s1_mode", "stage",
        "s1_bin_index", "s1_bin_low_phd", "log10s2_bin_index",
        "log10s2_bin_low", "rate_events_kg_day",
    ]
    rate_fields = [
        "benchmark", "nuclear_model", "response_model", "stage",
        "parametric_rate_events_kg_day", "full_rate_events_kg_day",
        "full_vs_parametric_relative_rate_difference",
    ]
    noise_fields = [
        "benchmark", "nuclear_model", "stage",
        "mean_within_mode_split_half_tv", "pooled_tv_reproduction_abs_difference",
    ]
    for seed_index, seed in enumerate(seeds):
        fold = root / f"seed-{seed}" / "fold"
        (fold / "sampling-noise").mkdir(parents=True, exist_ok=True)
        map_rows, rate_rows, noise_rows = [], [], []
        for benchmark in MOD.BENCHMARKS:
            for nuclear in MOD.NUCLEAR_MODELS:
                for stage in MOD.STAGES:
                    p_rate = 1.0 + 0.1 * seed_index
                    f_rate = p_rate * (1.0 - 0.001 * (seed_index + 1))
                    p_fractions = (0.70 - 0.01 * seed_index, 0.30 + 0.01 * seed_index)
                    f_fractions = (0.65 - 0.01 * seed_index, 0.35 + 0.01 * seed_index)
                    summary_p_rate = p_rate + (
                        0.5 if corrupt_map_closure and seed_index == 0
                        and benchmark == MOD.BENCHMARKS[0]
                        and nuclear == MOD.NUCLEAR_MODELS[0]
                        and stage == MOD.STAGES[0] else 0.0
                    )
                    rate_rows.append({
                        "benchmark": benchmark,
                        "nuclear_model": nuclear,
                        "response_model": "eft2024",
                        "stage": stage,
                        "parametric_rate_events_kg_day": summary_p_rate,
                        "full_rate_events_kg_day": f_rate,
                        "full_vs_parametric_relative_rate_difference": f_rate / p_rate - 1.0,
                    })
                    noise_rows.append({
                        "benchmark": benchmark,
                        "nuclear_model": nuclear,
                        "stage": stage,
                        "mean_within_mode_split_half_tv": 0.05 + 0.01 * seed_index,
                        "pooled_tv_reproduction_abs_difference": 0.0,
                    })
                    for mode, total, fractions in (
                        ("parametric", p_rate, p_fractions),
                        ("full", f_rate, f_fractions),
                    ):
                        for s1_bin, s2_bin, fraction in (
                            (10, 180, fractions[0]),
                            (11, 181, fractions[1]),
                        ):
                            map_rows.append({
                                "benchmark": benchmark,
                                "nuclear_model": nuclear,
                                "response_model": "eft2024",
                                "s1_mode": mode,
                                "stage": stage,
                                "s1_bin_index": s1_bin,
                                "s1_bin_low_phd": s1_bin * 10.0,
                                "log10s2_bin_index": s2_bin,
                                "log10s2_bin_low": s2_bin * 0.02,
                                "rate_events_kg_day": total * fraction,
                            })
        with (fold / "paired_s1_mode_2d_signal_intensity.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=map_fields)
            writer.writeheader()
            writer.writerows(map_rows)
        with (fold / "paired_s1_mode_2d_response_summary.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=rate_fields)
            writer.writeheader()
            writer.writerows(rate_rows)
        with (fold / "sampling-noise/paired_s1_2d_sampling_noise_summary.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=noise_fields)
            writer.writeheader()
            writer.writerows(noise_rows)


class PairedS1IndependentSeedAggregationTests(unittest.TestCase):
    def test_total_variation_and_mean_map(self):
        self.assertAlmostEqual(
            MOD.total_variation({"a": 0.8, "b": 0.2}, {"a": 0.7, "b": 0.3}),
            0.1,
        )
        mean = MOD.ensemble_mean_map([
            {(0, 0): 1.0, (1, 0): 1.0},
            {(0, 0): 3.0, (1, 0): 1.0},
            {(0, 0): 2.0, (1, 0): 2.0},
        ])
        self.assertAlmostEqual(mean[(0, 0)], 2.0)
        self.assertAlmostEqual(mean[(1, 0)], 4.0 / 3.0)

    def test_three_seed_summary_separates_mode_and_seed_spread(self):
        maps = {
            "seed1": {
                "parametric": {(0, 0): 0.60, (1, 0): 0.40},
                "full": {(0, 0): 0.50, (1, 0): 0.50},
            },
            "seed2": {
                "parametric": {(0, 0): 0.55, (1, 0): 0.45},
                "full": {(0, 0): 0.45, (1, 0): 0.55},
            },
            "seed3": {
                "parametric": {(0, 0): 0.58, (1, 0): 0.42},
                "full": {(0, 0): 0.48, (1, 0): 0.52},
            },
        }
        result = MOD.summarize_seed_maps(maps)
        self.assertEqual(result["n_seeds"], 3)
        self.assertAlmostEqual(result["mean_map_parametric_vs_full_tv"], 0.1)
        self.assertAlmostEqual(result["mean_seed_parametric_vs_full_tv"], 0.1)
        self.assertAlmostEqual(result["mean_within_mode_seed_pairwise_tv"], 1.0 / 30.0)
        self.assertAlmostEqual(
            result["mean_map_tv_over_within_mode_seed_pairwise_tv"], 3.0
        )
        self.assertEqual(set(result["per_seed_parametric_vs_full_tv"]), set(maps))

    def test_aggregate_closes_all_maps_and_includes_split_half_reference(self):
        seeds = [20261117, 40261117, 60261117]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_seed_fixture(root, seeds)
            ensemble, per_seed, extra = MOD.aggregate(root, seeds)
        self.assertEqual(len(ensemble), 16)
        self.assertEqual(len(per_seed), 48)
        self.assertEqual(len(extra["mean_maps"]), 16 * 2 * 2)
        self.assertTrue(all(row["n_seeds"] == 3 for row in ensemble))
        self.assertTrue(all(row["mean_within_stream_split_half_tv"] > 0 for row in ensemble))
        self.assertTrue(all(row["within_stream_split_half_tv"] > 0 for row in per_seed))

    def test_aggregate_rejects_map_rate_nonclosure(self):
        seeds = [20261117, 40261117, 60261117]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_seed_fixture(root, seeds, corrupt_map_closure=True)
            with self.assertRaisesRegex(ValueError, "map/rate closure failed"):
                MOD.aggregate(root, seeds)

    def test_requires_three_distinct_seed_labels(self):
        with self.assertRaisesRegex(ValueError, "at least two independent seeds"):
            MOD.summarize_seed_maps({
                "seed1": {
                    "parametric": {(0, 0): 1.0},
                    "full": {(0, 0): 1.0},
                }
            })


if __name__ == "__main__":
    unittest.main()
