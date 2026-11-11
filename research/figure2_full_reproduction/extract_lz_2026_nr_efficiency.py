#!/usr/bin/env python3
"""Extract the final LZ 2026 NR WS-ROI efficiency curve from Fig. S2 PDF vectors.

The official HEPData download endpoint is Cloudflare-blocked in the current
runner, so this script digitizes the black final-ROI vector path from the
public arXiv PDF. The PDF SHA256 is recorded in the output metadata.
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

# Local SVG coordinates calibrated to the 0--300 keV and 0--1 efficiency axes
# in the Fig. S2 plotting frame (page 14 of arXiv:2609.02823v1).
X_0 = 51.087864
X_300 = 497.850350
Y_0 = 62.457768
Y_1 = 349.147721


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def extract_curve(svg_path: Path) -> list[tuple[float, float]]:
    root = ET.parse(svg_path).getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    candidates = []
    for element in root.iter(f"{SVG_NS}path"):
        if element.attrib.get("stroke") != "rgb(0%, 0%, 0%)":
            continue
        if element.attrib.get("fill") != "none":
            continue
        d = element.attrib.get("d", "")
        if len(d) < 1000:
            continue
        parent = parents.get(element)
        in_main_plot = False
        while parent is not None:
            if parent.attrib.get("clip-path") == "url(#clip-16)":
                in_main_plot = True
                break
            parent = parents.get(parent)
        if in_main_plot:
            candidates.append((len(d), element, d))

    if not candidates:
        raise RuntimeError("Could not identify the black final-ROI path in Fig. S2")
    _, element, d = max(candidates, key=lambda item: item[0])
    transform = element.attrib.get("transform", "")
    if "0.49133" not in transform:
        raise RuntimeError(f"Unexpected Fig. S2 path transform: {transform}")

    raw = [(float(x), float(y)) for x, y in PATH_RE.findall(d)]
    points = sorted(
        (
            (300.0 * (x - X_0) / (X_300 - X_0),
             (y - Y_0) / (Y_1 - Y_0))
            for x, y in raw
        ),
        key=lambda p: p[0],
    )
    # Remove duplicate x values while retaining the final vector point.
    deduplicated: list[tuple[float, float]] = []
    for point in points:
        if deduplicated and abs(point[0] - deduplicated[-1][0]) < 1e-12:
            deduplicated[-1] = point
        else:
            deduplicated.append(point)
    if len(deduplicated) < 50:
        raise RuntimeError(f"Only {len(deduplicated)} vector points were extracted")
    return deduplicated


def interpolate(points: list[tuple[float, float]], energy: float) -> float:
    if energy <= points[0][0]:
        return points[0][1]
    if energy >= points[-1][0]:
        return points[-1][1]
    lo, hi = 0, len(points) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if points[mid][0] <= energy:
            lo = mid
        else:
            hi = mid
    x0, y0 = points[lo]
    x1, y1 = points[hi]
    return y0 + (y1 - y0) * (energy - x0) / (x1 - x0)


def integrate_mean(points: list[tuple[float, float]], lo: float, hi: float) -> float:
    n = 20000
    step = (hi - lo) / n
    values = [interpolate(points, lo + i * step) for i in range(n + 1)]
    area = step * (
        0.5 * values[0] + math.fsum(values[1:-1]) + 0.5 * values[-1]
    )
    return area / (hi - lo)


def crossings(points: list[tuple[float, float]], level: float) -> list[float]:
    result = []
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if (y0 - level) * (y1 - level) <= 0 and y1 != y0:
            result.append(x0 + (level - y0) * (x1 - x0) / (y1 - y0))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    svg_prefix = args.out_dir / "lz_2026_figS2"
    subprocess.run(
        [
            "pdftocairo", "-svg", "-f", "14", "-l", "14",
            str(args.pdf), str(svg_prefix),
        ],
        check=True,
    )
    svg_path = args.out_dir / "lz_2026_figS2.svg"
    points = extract_curve(svg_path)

    energies = sorted(set(float(i) for i in range(301)) | {5.4, 269.9})
    csv_path = args.out_dir / "lz_2026_nr_efficiency_digitized.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ER_keV", "efficiency_final_WS_ROI", "source_curve"])
        for energy in energies:
            writer.writerow(
                [
                    f"{energy:.1f}",
                    f"{interpolate(points, energy):.8f}",
                    "FigS2_black_final_ROI_vector_path",
                ]
            )

    mean_14_250 = integrate_mean(points, 14.0, 250.0)
    crossing_50 = crossings(points, 0.5)
    metadata = {
        "source": "LZ Collaboration, arXiv:2609.02823v1 (2026), Fig. S2, PDF page 14",
        "data_release_doi": "10.17182/hepdata.182472.v1",
        "pdf_sha256": sha256(args.pdf),
        "extraction_method": "vector-path extraction from the black final WIMP-search ROI curve",
        "svg_path_selector": {
            "stroke": "rgb(0%, 0%, 0%)",
            "parent_clip_path": "url(#clip-16)",
            "minimum_path_data_length": 1000,
        },
        "axis_calibration_local_svg_units": {
            "x_0keV": X_0,
            "x_300keV": X_300,
            "y_efficiency_0": Y_0,
            "y_efficiency_1": Y_1,
        },
        "raw_vector_point_count": len(points),
        "sampled_csv_point_count": len(energies),
        "mean_final_roi_efficiency_14_250": mean_14_250,
        "published_text_mean_efficiency_14_250": 0.96,
        "crossings_at_50_percent_keV": crossing_50,
        "published_low_energy_50_percent_anchor_keV": 5.4,
        "published_high_energy_50_percent_anchor_keV": 269.9,
        "digitization_note": (
            "The vector curve gives a low-energy 50% crossing near 5.09 keV, "
            "whereas the paper text/caption quotes 5.4 keV from Ref. [5]. "
            "The high-energy crossing near 269.87 keV agrees with 269.9 keV. "
            "The mean final-ROI efficiency over 14--250 keV is expected to "
            "round to the published 96%."
        ),
        "not_included": [
            "efficiency uncertainty band",
            "S1c/log10(S2c) two-dimensional signal PDFs",
            "NEST nuisance-parameter covariance",
            "background likelihood",
        ],
    }
    metadata_path = args.out_dir / "lz_2026_nr_efficiency_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
