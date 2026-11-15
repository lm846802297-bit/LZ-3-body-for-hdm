#!/usr/bin/env python3
"""Digitize the four cumulative LZ 2026 NR efficiency curves in Supplemental Fig. S2.

The figure labels the cumulative stages: Trigger; Trigger + S1 Threshold;
Trigger + S1 Threshold + SS & Data Analysis Cuts; and + ROI. This script
extracts all four vector paths and also reports conditional stage ratios.
The ratios are diagnostic decompositions of cumulative efficiencies, not
independent detector efficiencies.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"
PATH_RE = re.compile(r"[ML]\s*([-+0-9.]+)\s+([-+0-9.]+)")
X_0 = 51.087864
X_300 = 497.850350
Y_0 = 62.457768
Y_1 = 349.147721

CURVES = {
    "trigger": {"stroke": "rgb(0%, 0%, 100%)", "clip": "url(#clip-15)", "min_path": 100},
    "trigger_plus_s1_threshold": {
        "stroke": "rgb(100%, 64.704895%, 0%)", "clip": "url(#clip-15)", "min_path": 100
    },
    "trigger_plus_s1_ss_analysis": {
        "stroke": "rgb(0%, 50.195312%, 0%)", "clip": "url(#clip-16)", "min_path": 1000
    },
    "final_plus_roi": {
        "stroke": "rgb(0%, 0%, 0%)", "clip": "url(#clip-16)", "min_path": 1000
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def interpolate(points: list[tuple[float, float]], x: float) -> float:
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    lo, hi = 0, len(points) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if points[mid][0] <= x:
            lo = mid
        else:
            hi = mid
    x0, y0 = points[lo]
    x1, y1 = points[hi]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def extract_curve(svg_path: Path, stroke: str, clip: str, min_path: int) -> list[tuple[float, float]]:
    root = ET.parse(svg_path).getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    candidates = []
    for element in root.iter(f"{SVG_NS}path"):
        if element.attrib.get("stroke") != stroke or element.attrib.get("fill") != "none":
            continue
        d = element.attrib.get("d", "")
        if len(d) < min_path:
            continue
        parent = parents.get(element)
        in_expected_clip = False
        while parent is not None:
            if parent.attrib.get("clip-path") == clip:
                in_expected_clip = True
                break
            parent = parents.get(parent)
        if in_expected_clip:
            candidates.append((len(d), d, element.attrib.get("transform", "")))
    if not candidates:
        raise RuntimeError(f"could not identify vector path for {stroke} under {clip}")
    _, d, transform = max(candidates, key=lambda x: x[0])
    if "matrix(0.49133, 0, 0, -0.49133, 181.024, 234.203)" not in transform:
        raise RuntimeError(f"unexpected Fig. S2 path transform: {transform}")
    raw = [(float(x), float(y)) for x, y in PATH_RE.findall(d)]
    points = sorted(
        (
            (300.0 * (x - X_0) / (X_300 - X_0), (y - Y_0) / (Y_1 - Y_0))
            for x, y in raw
        ),
        key=lambda p: p[0],
    )
    deduplicated: list[tuple[float, float]] = []
    for point in points:
        if deduplicated and abs(point[0] - deduplicated[-1][0]) < 1e-12:
            deduplicated[-1] = point
        else:
            deduplicated.append(point)
    if len(deduplicated) < 5:
        raise RuntimeError(f"too few vector points extracted for {stroke}")
    return deduplicated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = args.out_dir / "lz_2026_figS2_efficiency_components.svg"
    subprocess.run(
        ["pdftocairo", "-svg", "-f", "14", "-l", "14", str(args.pdf), str(svg_path)],
        check=True,
    )
    curves = {
        name: extract_curve(svg_path, spec["stroke"], spec["clip"], spec["min_path"])
        for name, spec in CURVES.items()
    }
    energies = sorted(set(float(i) for i in range(301)) | {5.4, 248.0, 269.9})
    rows = []
    for energy in energies:
        vals = {name: interpolate(points, energy) for name, points in curves.items()}
        trigger = vals["trigger"]
        plus_s1 = vals["trigger_plus_s1_threshold"]
        plus_ss = vals["trigger_plus_s1_ss_analysis"]
        final = vals["final_plus_roi"]
        if not (-0.002 <= final <= plus_ss + 0.002 <= plus_s1 + 0.004 <= trigger + 0.006):
            raise RuntimeError(
                f"cumulative efficiency ordering failed at {energy:.1f} keV: {vals}"
            )
        rows.append({
            "ER_keV": energy,
            "trigger_cumulative": trigger,
            "trigger_plus_s1_threshold_cumulative": plus_s1,
            "trigger_plus_s1_ss_analysis_cumulative": plus_ss,
            "final_plus_roi_cumulative": final,
            "trigger_incremental": trigger,
            "s1_threshold_conditional": plus_s1 / trigger if trigger > 0 else 0.0,
            "ss_analysis_conditional": plus_ss / plus_s1 if plus_s1 > 0 else 0.0,
            "roi_conditional": final / plus_ss if plus_ss > 0 else 0.0,
        })
    out_csv = args.out_dir / "lz_2026_nr_selection_efficiency_components.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    def at(energy: float) -> dict:
        row = min(rows, key=lambda r: abs(r["ER_keV"] - energy))
        if abs(row["ER_keV"] - energy) < 1e-12:
            return row
        return {
            key: (energy if key == "ER_keV" else
                  row[key])
            for key in rows[0]
        }

    metadata = {
        "source": "LZ Collaboration, arXiv:2609.02823v1, Supplemental Fig. S2, PDF page 14",
        "pdf_sha256": sha256(args.pdf),
        "method": "SVG vector-path extraction using published axis calibration; no rescaling",
        "cumulative_curves": {
            "blue": "Trigger",
            "orange": "Trigger + S1 Threshold",
            "green": "Trigger + S1 Threshold + SS & Data Analysis Cuts",
            "black": "Trigger + S1 Threshold + SS & Data Analysis Cuts + WS ROI",
        },
        "conditional_ratios": "Orange/blue, green/orange, and black/green are ratios of cumulative curves; they are conditional stage factors only if the published stages are nested.",
        "not_included": [
            "The extracted efficiency curves do not specify a two-dimensional selected S1c/log10(S2c) migration kernel.",
            "They do not supply the exact NEST production configuration, calibration-source spatial distribution, or nuisance covariance.",
        ],
        "values_at_5p4_keV": next(r for r in rows if r["ER_keV"] == 5.4),
        "values_at_248_keV": next(r for r in rows if r["ER_keV"] == 248.0),
        "values_at_269p9_keV": next(r for r in rows if r["ER_keV"] == 269.9),
        "csv": out_csv.name,
    }
    (args.out_dir / "lz_2026_nr_selection_efficiency_components_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
