import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "audit_lz_2026_paired_s1_2d_binning_stability.py"
)
SPEC = importlib.util.spec_from_file_location("paired_s1_2d_binning_stability", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def write_map_fixture(root: Path, seeds: list[int]) -> None:
    fields = [
        "benchmark", "nuclear_model", "response_model", "s1_mode", "stage",
        "s1_bin_index", "s1_bin_low_phd", "log10s2_bin_index",
        "log10s2_bin_low", "rate_events_kg_day",
    ]
    for seed in seeds:
        fold = root / f"seed-{seed}" / "fold"
        fold.mkdir(parents=True, exist_ok=True)
        rows = []
        for benchmark in MOD.BENCHMARKS:
            for nuclear in MOD.NUCLEAR_MODELS:
                for stage in MOD.STAGES:
                    for mode, fractions in (
                        ("parametric", (0.70, 0.30)),
                        ("full", (0.60, 0.40)),
                    ):
                        for (s1_bin, s2_bin), fraction in zip(
                            ((1, 1), (2, 2)), fractions
                        ):
                            rows.append({
                                "benchmark": benchmark,
                                "nuclear_model": nuclear,
                                "response_model": "eft2024",
                                "s1_mode": mode,
                                "stage": stage,
                                "s1_bin_index": s1_bin,
                                "s1_bin_low_phd": s1_bin * 10.0,
                                "log10s2_bin_index": s2_bin,
                                "log10s2_bin_low": s2_bin * 0.02,
                                "rate_events_kg_day": fraction,
                            })
        with (fold / "paired_s1_mode_2d_signal_intensity.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)


class PairedS1TwoDBinningStabilityTests(unittest.TestCase):
    def test_ten_seed_metadata_and_row_coverage_are_dynamic(self):
        seeds = [20261117, 40261117, 60261117, 80261117, 100261117,
                 120261117, 140261117, 160261117, 180261117, 200261117]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_map_fixture(root, seeds)
            summary, per_seed, metadata = MOD.audit(root, seeds)
        self.assertEqual(metadata["n_seeds"], 10)
        self.assertEqual(metadata["seeds"], seeds)
        self.assertEqual(len(summary), 48)
        self.assertEqual(len(per_seed), 480)
        self.assertIn("10 independent pseudorandom seeds", metadata["limitations"][0])
        self.assertNotIn("Three independent pseudorandom seeds only", metadata["limitations"][0])

    def test_rebinning_preserves_integrated_rate(self):
        source = {
            (0, 0): 1.0,
            (1, 1): 2.0,
            (2, 2): 3.0,
            (3, 3): 4.0,
        }
        coarse = MOD.rebin_map(source, 2)
        self.assertEqual(coarse, {(0, 0): 3.0, (1, 1): 7.0})
        self.assertAlmostEqual(sum(source.values()), sum(coarse.values()))

    def test_total_variation_cannot_increase_under_exact_coarsening(self):
        parametric = {(0, 0): 0.5, (1, 1): 0.5}
        full = {(0, 1): 0.5, (1, 0): 0.5}
        fine_tv = MOD.total_variation(parametric, full)
        coarse_tv = MOD.total_variation(
            MOD.rebin_map(parametric, 2),
            MOD.rebin_map(full, 2),
        )
        self.assertAlmostEqual(fine_tv, 1.0)
        self.assertAlmostEqual(coarse_tv, 0.0)
        self.assertLessEqual(coarse_tv, fine_tv)

    def test_marginalization_projects_the_requested_axis(self):
        cells = {
            (0, 0): 1.0,
            (0, 1): 2.0,
            (1, 0): 3.0,
        }
        self.assertEqual(MOD.marginalize_map(cells, 0), {0: 3.0, 1: 3.0})
        self.assertEqual(MOD.marginalize_map(cells, 1), {0: 4.0, 1: 2.0})

    def test_invalid_rebin_factor_and_axis_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "factor must be one of"):
            MOD.rebin_map({(0, 0): 1.0}, 3)
        with self.assertRaisesRegex(ValueError, "axis must be"):
            MOD.marginalize_map({(0, 0): 1.0}, 2)


if __name__ == "__main__":
    unittest.main()
