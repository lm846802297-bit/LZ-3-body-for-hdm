from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from compare_phase_space_archive import compare_rows


def make_row(i6: float, mass_scheme: str = "historical_A_times_u_approx") -> dict[str, str]:
    archived = 1433678.0722868
    high_order = 1431577.6869309
    return {
        "case": "green_ER200_v800",
        "mass_scheme": mass_scheme,
        "mchi_GeV": "1000",
        "ms_keV": "300",
        "Delta_m_MeV": "1",
        "mA_GeV": "122",
        "ER_keV": "200",
        "speed_km_s": "800",
        "implementation": "independent_linear_W2",
        "mapping": "linear_w2",
        "nW": "16",
        "nz": "16",
        "nphi": "8",
        "I6_GeV2": f"{i6:.14g}",
        "archived_I6_GeV2": f"{archived:.14g}",
        "relative_to_archived": f"{i6 / archived - 1.0:.12e}",
        "reference_I6_GeV2": f"{high_order:.14g}",
        "relative_to_high_order_reference": f"{i6 / high_order - 1.0:.12e}",
    }


class PhaseSpaceArchiveComparisonTests(unittest.TestCase):
    def test_derived_columns_are_checked_per_run_not_cross_compared(self) -> None:
        old = make_row(1431622.8698121)
        # This shift is within the 5e-8 relative tolerance for the primary I6.
        # Its relative_to_archived diagnostic consequently shifts by ~1.3e-8.
        new = make_row(1431622.8881)
        self.assertEqual(compare_rows("anchor.csv", [old], [new]), [])

    def test_primary_i6_outside_tolerance_still_fails(self) -> None:
        old = make_row(1431622.8698121)
        new = make_row(1431622.8698121 * (1.0 + 1e-6))
        failures = compare_rows("anchor.csv", [old], [new])
        self.assertTrue(any(":I6_GeV2:" in failure for failure in failures))

    def test_internally_inconsistent_derived_column_fails(self) -> None:
        old = make_row(1431622.8698121)
        new = make_row(1431622.8698121)
        new["relative_to_archived"] = str(float(new["relative_to_archived"]) + 1e-6)
        failures = compare_rows("anchor.csv", [old], [new])
        self.assertTrue(any("relative_to_archived" in failure for failure in failures))

    def test_historical_mass_alias_is_only_allowed_at_122_gev(self) -> None:
        old = make_row(1431622.8698121, "historical_A_times_u_approx")
        new = make_row(1431622.8698121, "coarse_mA_122_GeV_approx")
        self.assertEqual(compare_rows("anchor.csv", [old], [new]), [])
        new["mA_GeV"] = "122.1"
        failures = compare_rows("anchor.csv", [old], [new])
        self.assertTrue(any(":mass_scheme:" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
