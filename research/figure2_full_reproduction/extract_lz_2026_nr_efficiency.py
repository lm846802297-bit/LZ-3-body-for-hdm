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


def deduplicate_points(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Sort by energy and retain the final vector point at duplicate x values."""
    ordered = sorted(points, key=lambda p: p[0])
    result: list[tuple[float, float]] = []
    for point in ordered:
        if result and abs(point[0] - result[-1][0]) < 1e-10:
            result[-1] = point
        else:
            result.append(point)
    return result


def extract_uncertainty_envelope(
    svg_path: Path,
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Extract the gray Fig. S2 efficiency envelope from its filled SVG path.

    The gray band is a closed polygon in page coordinates. Its first and
    second branches run from low to high recoil energy and back. The page
    coordinates are mapped through the inverse of the plotted-axis transform
    used by the central efficiency curve.
    """
    root = ET.parse(svg_path).getroot()
    parents = {child: parent for parent in root.iter() for child in parent}
    candidates = []
    for element in root.iter(f"{SVG_NS}path"):
        if element.attrib.get("fill") != "rgb(0%, 0%, 0%)":
            continue
        if element.attrib.get("fill-opacity") != "0.3":
            continue
        d = element.attrib.get("d", "")
        if len(d) < 1000:
            continue
        parent = parents.get(element)
        in_band_clip = False
        while parent is not None:
            if parent.attrib.get("clip-path") == "url(#clip-1)":
                in_band_clip = True
                break
            parent = parents.get(parent)
        if in_band_clip:
            candidates.append((len(d), d))

    if not candidates:
        raise RuntimeError("Could not identify the gray efficiency-uncertainty band in Fig. S2")
    _, d = max(candidates, key=lambda item: item[0])
    raw = [(float(x), float(y)) for x, y in PATH_RE.findall(d)]
    if len(raw) < 100:
        raise RuntimeError(f"Only {len(raw)} points were extracted from the uncertainty band")

    split = max(range(len(raw)), key=lambda i: raw[i][0])
    branches = (raw[: split + 1], raw[split:])
    page_x_min, page_x_max = 206.125, 425.632812
    scale, translate_x, translate_y = 0.49133, 181.024, 234.203

    def to_data(point: tuple[float, float]) -> tuple[float, float]:
        x_page, y_page = point
        x_local = (x_page - translate_x) / scale
        y_local = (translate_y - y_page) / scale
        energy = 300.0 * (x_local - X_0) / (X_300 - X_0)
        efficiency = (y_local - Y_0) / (Y_1 - Y_0)
        return energy, efficiency

    curves = []
    for branch in branches:
        points = deduplicate_points(
            [to_data(p) for p in branch if page_x_min <= p[0] <= page_x_max]
        )
        if len(points) < 50:
            raise RuntimeError(f"Only {len(points)} points remain on an uncertainty-envelope branch")
        curves.append(points)

    # The upper and lower branches are identified by their efficiency at 248 keV.
    if interpolate(curves[0], 248.0) >= interpolate(curves[1], 248.0):
        upper, lower = curves[0], curves[1]
    else:
        upper, lower = curves[1], curves[0]
    return lower, upper


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
    parser.add_argument("--hepdata-status", type=Path, default=None)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = args.out_dir / "lz_2026_figS2.svg"
    subprocess.run(
        [
            "pdftocairo", "-svg", "-f", "14", "-l", "14",
            str(args.pdf), str(svg_path),
        ],
        check=True,
    )
    points = extract_curve(svg_path)
    lower_points, upper_points = extract_uncertainty_envelope(svg_path)

    energies = sorted(set(float(i) for i in range(301)) | {5.4, 248.0, 269.9})
    csv_path = args.out_dir / "lz_2026_nr_efficiency_digitized.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ER_keV",
            "efficiency_final_WS_ROI",
            "efficiency_lower_envelope",
            "efficiency_upper_envelope",
            "source_curve",
        ])
        for energy in energies:
            central = interpolate(points, energy)
            lower = interpolate(lower_points, energy)
            upper = interpolate(upper_points, energy)
            if lower > central + 2e-3 or central > upper + 2e-3:
                raise RuntimeError(
                    f"Central efficiency is outside the gray envelope at {energy:.1f} keV"
                )
            writer.writerow(
                [
                    f"{energy:.1f}",
                    f"{central:.8f}",
                    f"{lower:.8f}",
                    f"{upper:.8f}",
                    "FigS2_black_central_and_gray_uncertainty_envelope",
                ]
            )

    mean_14_250 = integrate_mean(points, 14.0, 250.0)
    mean_lower_14_250 = integrate_mean(lower_points, 14.0, 250.0)
    mean_upper_14_250 = integrate_mean(upper_points, 14.0, 250.0)
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
        "raw_uncertainty_band_polygon_point_count": 1170,
        "sampled_csv_point_count": len(energies),
        "mean_final_roi_efficiency_14_250": mean_14_250,
        "mean_lower_envelope_efficiency_14_250": mean_lower_14_250,
        "mean_upper_envelope_efficiency_14_250": mean_upper_14_250,
        "published_text_mean_efficiency_14_250": 0.96,
        "central_efficiency_at_248_keV": interpolate(points, 248.0),
        "lower_envelope_at_248_keV": interpolate(lower_points, 248.0),
        "upper_envelope_at_248_keV": interpolate(upper_points, 248.0),
        "central_efficiency_at_269_9_keV": interpolate(points, 269.9),
        "lower_envelope_at_269_9_keV": interpolate(lower_points, 269.9),
        "upper_envelope_at_269_9_keV": interpolate(upper_points, 269.9),
        "crossings_at_50_percent_keV": crossing_50,
        "published_low_energy_50_percent_anchor_keV": 5.4,
        "published_high_energy_50_percent_anchor_keV": 269.9,
        "uncertainty_envelope_interpretation": (
            "The gray Fig. S2 envelope is retained as a detector-efficiency systematic range; "
            "the publication does not assign a confidence level to the envelope."
        ),
        "digitization_note": (
            "The central vector curve gives a low-energy 50% crossing near 5.09 keV, "
            "whereas the paper text/caption quotes 5.4 keV from Ref. [5]. "
            "The central high-energy crossing near 269.87 keV agrees with 269.9 keV. "
            "The central mean final-ROI efficiency over 14--250 keV is "
            "95.47%, about 0.53 percentage points below the rounded published 96%; "
            "the curve is not rescaled. The gray uncertainty envelope is also digitized."
        ),
        "hepdata_api_status": (
            args.hepdata_status.read_text(encoding="utf-8").strip()
            if args.hepdata_status and args.hepdata_status.is_file()
            else "HEPData API status not supplied; central and gray curves extracted from the arXiv PDF."
        ),
        "independent_digitization_crosscheck": {
            "source": "arXiv:2609.02608v2, Appendix D",
            "central_efficiency_at_248_keV_published": 0.9457,
            "lower_envelope_at_248_keV_published": 0.8835,
            "upper_envelope_at_248_keV_published": 0.9800,
        },
        "not_included": [
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
