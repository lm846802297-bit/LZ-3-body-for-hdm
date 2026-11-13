#!/usr/bin/env python3
"""Create reproducible SVG plots from the archived fixed-speed Xe-131 CSV.

Only the Python standard library is required. The response-ratio plot uses
R_A(GCN)/R_A(JJ55); for the common Eq. (6) kernel this is also the ratio of
the two fixed-speed differential cross sections.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

WIDTH, HEIGHT = 1200, 760
LEFT, RIGHT, TOP, BOTTOM = 145, 65, 100, 130
PLOT_W, PLOT_H = WIDTH - LEFT - RIGHT, HEIGHT - TOP - BOTTOM
BLUE, AMBER = "#24577a", "#c47a23"


def esc(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def xmap(value: float) -> float:
    return LEFT + (value - 130.0) / (650.0 - 130.0) * PLOT_W


def svg_start(title: str, subtitle: str, ylabel: str) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{WIDTH/2}" y="42" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="27" font-weight="700" fill="#17212b">{esc(title)}</text>',
        f'<text x="{WIDTH/2}" y="73" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#536170">{esc(subtitle)}</text>',
        f'<text transform="translate(35 {TOP + PLOT_H/2}) rotate(-90)" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="19" fill="#17212b">{esc(ylabel)}</text>',
    ]


def add_x_axis(parts: list[str]) -> None:
    for x in range(150, 651, 50):
        px = xmap(float(x))
        parts.append(f'<line x1="{px:.2f}" y1="{TOP}" x2="{px:.2f}" y2="{TOP + PLOT_H}" stroke="#e6e9ed" stroke-width="1"/>')
        parts.append(f'<line x1="{px:.2f}" y1="{TOP + PLOT_H}" x2="{px:.2f}" y2="{TOP + PLOT_H + 7}" stroke="#344454" stroke-width="1.5"/>')
        parts.append(f'<text x="{px:.2f}" y="{TOP + PLOT_H + 31}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="15" fill="#344454">{x}</text>')
    parts.append(f'<line x1="{LEFT}" y1="{TOP + PLOT_H}" x2="{LEFT + PLOT_W}" y2="{TOP + PLOT_H}" stroke="#344454" stroke-width="2"/>')
    parts.append(f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{TOP + PLOT_H}" stroke="#344454" stroke-width="2"/>')
    parts.append(f'<text x="{LEFT + PLOT_W/2}" y="{HEIGHT - 45}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="19" fill="#17212b">Nuclear recoil energy E_R [keV]</text>')


def path_for(rows: list[dict[str, str]], yfield: str, ymap) -> str:
    commands = []
    for i, row in enumerate(rows):
        x = xmap(float(row["ER_keV"]))
        y = ymap(float(row[yfield]))
        commands.append(f'{"M" if i == 0 else "L"}{x:.2f},{y:.2f}')
    return " ".join(commands)


def make_cross_section(rows: list[dict[str, str]], minima: list[dict[str, str]]) -> str:
    title_sub = "m_chi1 = 1 TeV, Delta m = 450 keV, m_s = 300 keV, m_V = 10 GeV, v = 776 km/s"
    parts = svg_start(
        "Fixed-speed Xe-131 differential cross section",
        title_sub + "; m_A = 131 u; zero-width prescription",
        "d sigma / d E_R [cm^2 / keV]",
    )
    log_min, log_max = -38.0, math.log10(3.0e-32)

    def ymap(value: float) -> float:
        return TOP + (log_max - math.log10(value)) / (log_max - log_min) * PLOT_H

    for exponent in range(-38, -31):
        py = ymap(10.0 ** exponent)
        parts.append(f'<line x1="{LEFT}" y1="{py:.2f}" x2="{LEFT + PLOT_W}" y2="{py:.2f}" stroke="#e6e9ed" stroke-width="1"/>')
        parts.append(f'<text x="{LEFT - 15}" y="{py + 5:.2f}" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#344454">1e{exponent}</text>')
    add_x_axis(parts)
    parts.append(f'<path d="{path_for(rows, "dsigma_GCN_cm2_per_keV", ymap)}" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    parts.append(f'<path d="{path_for(rows, "dsigma_JJ55_cm2_per_keV", ymap)}" fill="none" stroke="{AMBER}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    for row in minima:
        er = float(row["ER_keV"])
        field = "dsigma_GCN_cm2_per_keV" if er in (269.0, 551.0) else "dsigma_JJ55_cm2_per_keV"
        color = BLUE if field.startswith("dsigma_GCN") else AMBER
        parts.append(f'<circle cx="{xmap(er):.2f}" cy="{ymap(float(row[field])):.2f}" r="5.5" fill="#ffffff" stroke="{color}" stroke-width="2.5"/>')
    parts.extend([
        f'<line x1="830" y1="112" x2="875" y2="112" stroke="{BLUE}" stroke-width="3"/><text x="885" y="117" font-family="Arial,Helvetica,sans-serif" font-size="16" fill="#17212b">GCN</text>',
        f'<line x1="980" y1="112" x2="1025" y2="112" stroke="{AMBER}" stroke-width="3"/><text x="1035" y="117" font-family="Arial,Helvetica,sans-serif" font-size="16" fill="#17212b">JJ55</text>',
        f'<text x="{WIDTH/2}" y="{HEIGHT - 15}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#66727e">Fixed-speed single-isotope diagnostic; 130-650 keV grid. Not a halo-folded or detector-level LZ event spectrum.</text>',
        "</svg>",
    ])
    return "\n".join(parts) + "\n"


def make_response_ratio(rows: list[dict[str, str]]) -> str:
    title_sub = "m_chi1 = 1 TeV, Delta m = 450 keV, m_s = 300 keV, m_V = 10 GeV, v = 776 km/s"
    parts = svg_start(
        "Xe-131 nuclear-response ratio: GCN / JJ55",
        title_sub + "; ratio uses the common Eq. (6) kernel",
        "R_A(GCN) / R_A(JJ55)",
    )

    def ymap(value: float) -> float:
        return TOP + (35.0 - value) / 35.0 * PLOT_H

    for y in range(0, 36, 5):
        py = ymap(float(y))
        parts.append(f'<line x1="{LEFT}" y1="{py:.2f}" x2="{LEFT + PLOT_W}" y2="{py:.2f}" stroke="#e6e9ed" stroke-width="1"/>')
        parts.append(f'<text x="{LEFT - 15}" y="{py + 5:.2f}" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="14" fill="#344454">{y}</text>')
    add_x_axis(parts)
    ratio_rows = [
        {**row, "ratio": float(row["R_A_GCN"]) / float(row["R_A_JJ55"])}
        for row in rows
    ]
    py = ymap(1.0)
    parts.append(f'<line x1="{LEFT}" y1="{py:.2f}" x2="{LEFT + PLOT_W}" y2="{py:.2f}" stroke="#7c8792" stroke-width="1.8" stroke-dasharray="8 6"/>')
    commands = []
    for i, row in enumerate(ratio_rows):
        x = xmap(float(row["ER_keV"]))
        y = ymap(float(row["ratio"]))
        commands.append(f'{"M" if i == 0 else "L"}{x:.2f},{y:.2f}')
    parts.extend([
        f'<path d="{" ".join(commands)}" fill="none" stroke="#3d6d4f" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>',
        f'<text x="{LEFT + PLOT_W - 8}" y="{py - 10:.2f}" text-anchor="end" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#68747f">equal response</text>',
        f'<text x="{WIDTH/2}" y="{HEIGHT - 15}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="13" fill="#66727e">For a common Eq. (6) kernel, this is also the fixed-speed d sigma_GCN / d sigma_JJ55 ratio.</text>',
        "</svg>",
    ])
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    here = Path(__file__).resolve().parent
    parser.add_argument("--csv", type=Path, default=here / "results" / "fixed_speed_xe131_dsigma_450kev.csv")
    parser.add_argument("--minima", type=Path, default=here / "results" / "local_minima_refinement_1keV.csv")
    parser.add_argument("--out-dir", type=Path, default=here / "results" / "plots")
    args = parser.parse_args()
    rows, minima = load_csv(args.csv), load_csv(args.minima)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "fixed_speed_xe131_dsigma_450kev.svg").write_text(make_cross_section(rows, minima), encoding="utf-8")
    (args.out_dir / "xe131_gcn_jj55_response_ratio_450kev.svg").write_text(make_response_ratio(rows), encoding="utf-8")
    print(f"wrote two SVG figures to {args.out_dir}")


if __name__ == "__main__":
    main()
