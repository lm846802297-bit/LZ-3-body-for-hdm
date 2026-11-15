#!/usr/bin/env python3
"""Diagnose the archived Xe-131 green-point I6 difference across W2 mappings.

This is a fixed-speed kernel audit only. It reuses the archived I6 value and
does not recalculate or modify the AFH nuclear-response table.
"""
from __future__ import annotations
import argparse, csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FIGURE2 = REPO / "research" / "figure2_full_reproduction"
sys.path.insert(0, str(FIGURE2))
import eq6_kernel as eq6
import phase_space_convergence as psc

ARCHIVE = FIGURE2 / "results" / "joint_xe131" / "fine" / "xe131_gcn_joint_single_speed.csv"
OUTPUT_NAMES = {
    "csv": "xe131_historical_i6_mapping_comparison.csv",
    "metadata": "xe131_historical_i6_mapping_metadata.json",
}
MCHI, MS, DELTA_M = 1000.0, 300.0e-6, 1.0e-3
M_A = 131.0 * 0.93149410242
SPEED = 776.0
ENERGIES_KEV = (101.0, 200.0, 267.0, 542.0)
HISTORICAL_ORDER = (40, 32, 20)


def rel(value, reference):
    return abs(value - reference) / max(abs(reference), 1.0e-300)


def read_archive(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    selected = {
        float(row["ER_keV"]): row
        for row in rows if row["model"].upper() == "GCN"
    }
    if set(selected) != set(ENERGIES_KEV):
        raise ValueError(f"historical archive must contain {ENERGIES_KEV}; found {sorted(selected)}")
    return selected


def integrate(mapping, energy_kev, order):
    return psc.integrate_i6(
        MCHI, MS, DELTA_M, M_A, energy_kev * 1.0e-6, SPEED,
        nW=order[0], nz=order[1], nphi=order[2],
        mapping=mapping, width_scheme="zero", g2=1.0,
    )


def run(archive_path):
    archived = read_archive(archive_path)
    rows = []
    for energy in ENERGIES_KEV:
        source = archived[energy]
        archived_i6 = float(source["I6_GeV2"])
        archived_open = bool(int(source["phase_space_open"]))
        wmin, wmax = eq6.limits(MCHI, MS, M_A, energy * 1.0e-6, SPEED)
        open_now = wmax > wmin
        if open_now != archived_open:
            raise ValueError(f"{energy:g} keV: archived/current phase-space mask differs")
        record = {
            "ER_keV": energy,
            "archived_phase_space_open": int(archived_open),
            "current_phase_space_open": int(open_now),
            "archived_I6_GeV2": archived_i6,
            "legacy_eq6_linear_w2_40x32x20_GeV2": 0.0,
            "psc_linear_w2_40x32x20_GeV2": 0.0,
            "psc_threshold_u2_40x32x20_GeV2": 0.0,
            "psc_linear_w_40x32x20_GeV2": 0.0,
            "psc_sine2_40x32x20_GeV2": 0.0,
            "psc_linear_w2_48x40x24_GeV2": 0.0,
            "psc_threshold_u2_48x40x24_GeV2": 0.0,
            "psc_threshold_u2_64x48x32_GeV2": 0.0,
            "legacy_vs_archive_relative_difference": 0.0,
            "linear_w2_vs_archive_relative_difference": 0.0,
            "threshold_u2_vs_archive_relative_difference": 0.0,
            "linear_w_vs_archive_relative_difference": 0.0,
            "sine2_vs_archive_relative_difference": 0.0,
            "threshold_u2_48_vs_64_relative_difference": 0.0,
        }
        if open_now:
            legacy = eq6.reduced_kernel(
                MCHI, MS, DELTA_M, M_A, energy * 1.0e-6, SPEED,
                nw=40, nz=32, nphi=20, width_scheme="zero",
            )
            linear = integrate("linear_w2", energy, HISTORICAL_ORDER)
            threshold = integrate("threshold_u2", energy, HISTORICAL_ORDER)
            linear_w = integrate("linear_w", energy, HISTORICAL_ORDER)
            sine2 = integrate("sine2", energy, HISTORICAL_ORDER)
            linear_high = integrate("linear_w2", energy, (48, 40, 24))
            threshold_high = integrate("threshold_u2", energy, (48, 40, 24))
            threshold_higher = integrate("threshold_u2", energy, (64, 48, 32))
            record.update({
                "legacy_eq6_linear_w2_40x32x20_GeV2": legacy,
                "psc_linear_w2_40x32x20_GeV2": linear,
                "psc_threshold_u2_40x32x20_GeV2": threshold,
                "psc_linear_w_40x32x20_GeV2": linear_w,
                "psc_sine2_40x32x20_GeV2": sine2,
                "psc_linear_w2_48x40x24_GeV2": linear_high,
                "psc_threshold_u2_48x40x24_GeV2": threshold_high,
                "psc_threshold_u2_64x48x32_GeV2": threshold_higher,
                "legacy_vs_archive_relative_difference": rel(legacy, archived_i6),
                "linear_w2_vs_archive_relative_difference": rel(linear, archived_i6),
                "threshold_u2_vs_archive_relative_difference": rel(threshold, archived_i6),
                "linear_w_vs_archive_relative_difference": rel(linear_w, archived_i6),
                "sine2_vs_archive_relative_difference": rel(sine2, archived_i6),
                "threshold_u2_48_vs_64_relative_difference": rel(threshold_high, threshold_higher),
            })
        elif archived_i6 != 0.0:
            raise ValueError(f"{energy:g} keV is closed but archived I6 is non-zero")
        rows.append(record)

    open_rows = [row for row in rows if row["current_phase_space_open"]]
    metadata = {
        "status": "DIAGNOSTIC_COMPLETE",
        "scope": "Green Xe-131 fixed-speed I6-only mapping audit at 776 km/s and zero width. AFH response and cross-section normalization are not recalculated.",
        "archive": str(archive_path),
        "inputs": {
            "m_chi1_GeV": MCHI, "m_s_GeV": MS, "Delta_m_GeV": DELTA_M,
            "m_A_GeV": M_A, "speed_km_s": SPEED, "width_scheme": "zero",
            "historical_quadrature": list(HISTORICAL_ORDER),
            "mapping_scan_order": [40, 32, 20],
            "high_order": [48, 40, 24],
            "higher_order": [64, 48, 32],
        },
        "open_energy_points_keV": [row["ER_keV"] for row in open_rows],
        "max_relative_differences": {
            key: max((row[key] for row in open_rows), default=0.0)
            for key in (
                "legacy_vs_archive_relative_difference",
                "linear_w2_vs_archive_relative_difference",
                "threshold_u2_vs_archive_relative_difference",
                "linear_w_vs_archive_relative_difference",
                "sine2_vs_archive_relative_difference",
                "threshold_u2_48_vs_64_relative_difference",
            )
        },
        "rows": rows,
        "interpretation_guard": "Agreement at one quadrature order is not a convergence proof. Use the 48x40x24 and 64x48x32 threshold_u2 comparison to assess stable integration.",
        "outputs": OUTPUT_NAMES,
    }
    return rows, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    rows, metadata = run(args.archive)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / OUTPUT_NAMES["csv"]
    metadata_path = args.out_dir / OUTPUT_NAMES["metadata"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata["output_paths"] = {"csv": str(csv_path), "metadata": str(metadata_path)}
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": metadata["status"],
        "open_points": metadata["open_energy_points_keV"],
        "max_relative_differences": metadata["max_relative_differences"],
        "outputs": OUTPUT_NAMES,
    }, indent=2))


if __name__ == "__main__":
    main()
