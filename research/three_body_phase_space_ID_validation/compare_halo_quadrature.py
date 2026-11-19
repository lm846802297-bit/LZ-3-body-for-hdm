#!/usr/bin/env python3
"""Compare two halo/isotope quadrature runs without third-party dependencies."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path


def read_rows(path: Path, keys: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    result = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        if key in result:
            raise ValueError(f"duplicate key {key} in {path}")
        result[key] = row
    return result


def rel_shift(high: float, low: float) -> float:
    if low == 0.0:
        return 0.0 if high == 0.0 else math.inf
    return (high / low - 1.0) * 100.0


def finite_float(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key}: {value}")
    return value


def compare_table(base_path: Path, high_path: Path, key_fields: tuple[str, ...],
                  full_key: str, approx_key: str, error_key: str,
                  output_path: Path, activity_floor: float) -> dict:
    base = read_rows(base_path, key_fields)
    high = read_rows(high_path, key_fields)
    if base.keys() != high.keys():
        missing_high = sorted(set(base)-set(high))[:10]
        missing_base = sorted(set(high)-set(base))[:10]
        raise ValueError(f"grid mismatch; missing high={missing_high}, missing base={missing_base}")
    peak = max(finite_float(r, full_key) for r in base.values())
    out = []
    full_shifts, approx_shifts, error_shifts = [], [], []
    active_full_shifts, active_approx_shifts, active_error_shifts = [], [], []
    for key in sorted(base, key=lambda k: tuple(float(x) if _is_number(x) else x for x in k)):
        b, h = base[key], high[key]
        bf, hf = finite_float(b, full_key), finite_float(h, full_key)
        ba, ha = finite_float(b, approx_key), finite_float(h, approx_key)
        be, he = finite_float(b, error_key), finite_float(h, error_key)
        sf, sa = rel_shift(hf, bf), rel_shift(ha, ba)
        se = he-be
        active = max(bf, hf) >= activity_floor*peak
        full_shifts.append(abs(sf)); approx_shifts.append(abs(sa)); error_shifts.append(abs(se))
        if active:
            active_full_shifts.append(abs(sf)); active_approx_shifts.append(abs(sa)); active_error_shifts.append(abs(se))
        row = {field: value for field, value in zip(key_fields, key)}
        row.update({
            f"{full_key}_base": bf, f"{full_key}_high": hf,
            "full_rate_quadrature_shift_pct": sf,
            f"{approx_key}_base": ba, f"{approx_key}_high": ha,
            "I_D_rate_quadrature_shift_pct": sa,
            f"{error_key}_base": be, f"{error_key}_high": he,
            "approximation_error_shift_pp": se,
            "active_rate_point": active,
        })
        out.append(row)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader(); w.writerows(out)
    return {
        "point_count": len(out),
        "active_point_count": len(active_full_shifts),
        "max_abs_full_rate_shift_all_pct": max(full_shifts, default=0.0),
        "max_abs_ID_rate_shift_all_pct": max(approx_shifts, default=0.0),
        "max_abs_approximation_error_shift_all_pp": max(error_shifts, default=0.0),
        "max_abs_full_rate_shift_active_pct": max(active_full_shifts, default=0.0),
        "max_abs_ID_rate_shift_active_pct": max(active_approx_shifts, default=0.0),
        "max_abs_approximation_error_shift_active_pp": max(active_error_shifts, default=0.0),
        "activity_floor_relative_to_peak": activity_floor,
    }


def _is_number(value: str) -> bool:
    try:
        float(value); return True
    except (TypeError, ValueError):
        return False


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--baseline-dir", type=Path, required=True)
    p.add_argument("--highorder-dir", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--activity-floor", type=float, default=1e-8)
    a=p.parse_args()
    out=a.out_dir
    natural=compare_table(
        a.baseline_dir/"natural_xenon_halo_comparison.csv",
        a.highorder_dir/"natural_xenon_halo_comparison.csv",
        ("ER_keV",),
        "natural_xenon_full_relative_rate",
        "natural_xenon_I_D_relative_rate",
        "relative_error_pct",
        out/"natural_xenon_quadrature_comparison.csv",
        a.activity_floor,
    )
    isotope=compare_table(
        a.baseline_dir/"seven_isotope_halo_comparison.csv",
        a.highorder_dir/"seven_isotope_halo_comparison.csv",
        ("ER_keV","A"),
        "full_contribution_relative_units",
        "I_D_contribution_relative_units",
        "isotope_relative_error_pct",
        out/"seven_isotope_quadrature_comparison.csv",
        a.activity_floor,
    )
    summary={"status":"COMPUTED","natural_xenon":natural,"seven_isotopes":isotope}
    (out/"quadrature_convergence_summary.json").write_text(
        json.dumps(summary,indent=2,allow_nan=False)+"\n",encoding="utf-8"
    )
    print(json.dumps(summary,indent=2,allow_nan=False))


if __name__=="__main__":
    main()
