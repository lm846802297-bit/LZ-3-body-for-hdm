import unittest

from research.afh_default_density_xe131.audit_xe131_only_ame2020_hybrid import build_hybrid_rows


class Xe131OnlyAME2020HybridTests(unittest.TestCase):
    def setUp(self):
        self.keys = [
            ("red_ms200_dm1", 101.0, "shm_cutoff"),
            ("green_ms300_dm1", 267.0, "shm_cutoff"),
        ]
        self.baseline_isotopes = [
            {
                "benchmark": k[0], "ER_keV": str(k[1]), "halo_model": k[2],
                "A": "131", "rate_contribution_events_kg_day_keV": str(rate),
            }
            for k, rate in zip(self.keys, (2.0, 0.5))
        ]
        self.baseline_totals = [
            {
                "benchmark": k[0], "ER_keV": str(k[1]), "halo_model": k[2],
                "rate_events_kg_day_keV": str(total),
                "open_isotopes": "128;129;130;131;132;134;136",
                "open_abundance_fraction": "0.998158",
            }
            for k, total in zip(self.keys, (10.0, 5.0))
        ]
        self.partials = []
        for k, nist, ame in zip(self.keys, (2.0, 0.5), (1.98, 0.51)):
            for scheme, rate in (("nist_nuclear", nist), ("ame2020_nuclear", ame)):
                self.partials.append({
                    "benchmark": k[0], "ER_keV": str(k[1]), "halo_model": k[2],
                    "mass_scheme": scheme, "response_q_convention": "exact_spatial",
                    "nv": "32", "Xe131_partial_rate_events_kg_day_keV": str(rate),
                })

    def test_hybrid_replaces_only_xe131_term(self):
        rows, metadata = build_hybrid_rows(
            self.baseline_isotopes, self.baseline_totals, self.partials
        )
        self.assertEqual(len(rows), 2)
        by_benchmark = {row["benchmark"]: row for row in rows}
        self.assertAlmostEqual(
            by_benchmark["red_ms200_dm1"]["hybrid_total_Xe131_only_AME2020"], 9.98
        )
        self.assertAlmostEqual(
            by_benchmark["green_ms300_dm1"]["hybrid_total_Xe131_only_AME2020"], 5.01
        )
        self.assertAlmostEqual(
            by_benchmark["red_ms200_dm1"]["hybrid_total_relative_shift"], -0.002
        )
        self.assertAlmostEqual(
            by_benchmark["green_ms300_dm1"]["hybrid_total_relative_shift"], 0.002
        )
        self.assertEqual(metadata["scope"], "hybrid diagnostic only; not a full AME2020 natural-xenon prediction")

    def test_nist_baseline_mismatch_is_rejected(self):
        bad = [dict(r) for r in self.partials]
        for row in bad:
            if row["mass_scheme"] == "nist_nuclear" and row["benchmark"] == "red_ms200_dm1":
                row["Xe131_partial_rate_events_kg_day_keV"] = "2.1"
        with self.assertRaises(ArithmeticError):
            build_hybrid_rows(self.baseline_isotopes, self.baseline_totals, bad)

    def test_missing_isotope_term_is_rejected(self):
        with self.assertRaises(ValueError):
            build_hybrid_rows(
                self.baseline_isotopes[:1], self.baseline_totals, self.partials
            )


if __name__ == "__main__":
    unittest.main()
