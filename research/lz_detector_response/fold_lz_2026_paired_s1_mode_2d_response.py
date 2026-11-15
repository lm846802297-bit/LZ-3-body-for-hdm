#!/usr/bin/env python3
"""Fold paired NEST Parametric/Full S1 samples into event-weighted 2D signal PDFs.

One common S2 response is paired with two S1 response modes generated from the
same intrinsic NR quanta and true position. Outputs compare NEST-only and
NEST+WS-ROI (S1c, log10(S2c)) maps. This remains a detector-response proxy,
not the official LZ waveform/selection likelihood.
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import converge_lz_2026_three_body_energy_grid as grid

BENCHMARKS = grid.BENCHMARKS
NUCLEAR_MODELS = ("GCN", "JJ55")
MODES = ("parametric", "full")
STAGES = ("nest", "ws_roi")
ENERGY_MIN_KEV, ENERGY_MAX_KEV, ENERGY_BIN_WIDTH_KEV = 35.0, 269.9, 1.0

REQUIRED = {
    "event", "replica", "energy_bin_index", "energy_bin_low_keV",
    "energy_bin_high_keV", "energy_keV", "s1_param_signed_phd",
    "s1_param_abs_phd", "s1_param_pass", "s1_full_signed_phd",
    "s1_full_abs_phd", "s1_full_pass", "s2_signed_phd",
    "s2_abs_phd", "s2_raw_phd", "s2_threshold_pass",
}

def empty_bucket():
    out = {"n": 0, "sumw": 0.0, "sumw2": 0.0}
    for mode in MODES:
        for stage in ("coin", "nest", "ws_roi"):
            out[f"{mode}_{stage}_w"] = 0.0
            out[f"{mode}_{stage}_w2"] = 0.0
    out.update({"d_ws_w": 0.0, "d_ws_w2": 0.0, "d_ws2_w2": 0.0})
    return out

def weighted_efficiency(sumw, sumw2, passw, passw2):
    if sumw <= 0.0:
        if passw > 1e-12:
            raise ValueError("positive accepted weight with zero denominator")
        return 0.0, 0.0
    p = min(1.0, max(0.0, passw / sumw))
    failw2 = max(0.0, sumw2 - passw2)
    var = p*p*failw2 + (1.0-p)*(1.0-p)*passw2
    return p, math.sqrt(max(0.0, var)) / sumw

def paired_difference(sumw, sumw2, diffw, diffw2, diff2w2):
    if sumw <= 0.0:
        return 0.0, 0.0
    d = diffw / sumw
    var = max(0.0, diff2w2 - 2.0*d*diffw2 + d*d*sumw2) / (sumw*sumw)
    return d, math.sqrt(var)

def total_variation(map_a: dict, map_b: dict):
    total_a, total_b = math.fsum(map_a.values()), math.fsum(map_b.values())
    if total_a <= 0.0 or total_b <= 0.0:
        return None
    keys = set(map_a) | set(map_b)
    return 0.5 * math.fsum(abs(map_a.get(k, 0.0)/total_a - map_b.get(k, 0.0)/total_b) for k in keys)

def read_spectra(spectrum_dir: Path):
    spectra = {}
    for benchmark in BENCHMARKS:
        path = spectrum_dir / benchmark / "natural_xenon_continuous_spectrum.csv"
        for nuclear in NUCLEAR_MODELS:
            spectra[(benchmark, nuclear)] = grid.read_spectrum(path, nuclear)
    return spectra

def accumulate_events(response_csv: Path, spectra: dict, events_per_bin: int):
    stats = defaultdict(empty_bucket)
    maps = defaultdict(lambda: defaultdict(float))
    edges = {}
    counts = defaultdict(int)
    with response_csv.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{response_csv} missing columns: {sorted(missing)}")
        for row in reader:
            ibin, replica = int(row["energy_bin_index"]), int(row["replica"])
            if ibin < 0 or replica not in (0, 1):
                raise ValueError(f"invalid energy-bin or replica label: {ibin}/{replica}")
            lo, hi, energy = (float(row[k]) for k in (
                "energy_bin_low_keV", "energy_bin_high_keV", "energy_keV"
            ))
            if not (math.isfinite(lo) and math.isfinite(hi) and math.isfinite(energy)
                    and hi > lo and lo - 1e-9 <= energy <= hi + 1e-9):
                raise ValueError(f"invalid energy coordinate in bin {ibin}")
            edge = edges.setdefault(ibin, (lo, hi))
            if abs(edge[0]-lo) > 1e-10 or abs(edge[1]-hi) > 1e-10:
                raise ValueError(f"inconsistent energy edges in bin {ibin}")
            counts[(ibin, replica)] += 1

            p_signed, p_s1 = float(row["s1_param_signed_phd"]), float(row["s1_param_abs_phd"])
            f_signed, f_s1 = float(row["s1_full_signed_phd"]), float(row["s1_full_abs_phd"])
            s2_signed, s2c, s2r = (float(row[k]) for k in (
                "s2_signed_phd", "s2_abs_phd", "s2_raw_phd"
            ))
            p_flag, f_flag, s2_flag = (int(row[k]) for k in (
                "s1_param_pass", "s1_full_pass", "s2_threshold_pass"
            ))
            if any(v not in (0, 1) for v in (p_flag, f_flag, s2_flag)):
                raise ValueError(f"non-binary selection flag in bin {ibin}")
            if (p_signed > 0.0) != bool(p_flag) or (f_signed > 0.0) != bool(f_flag):
                raise ValueError(f"S1 sign/pass mismatch in bin {ibin}")
            if (s2_signed > 0.0) != bool(s2_flag):
                raise ValueError(f"S2 sign/pass mismatch in bin {ibin}")
            if not all(math.isfinite(v) for v in (p_s1, f_s1, s2c, s2r)):
                raise ValueError(f"non-finite detector observable in bin {ibin}")

            p_ws_mask = grid.ws_roi_pass(p_s1, s2r, s2c)
            f_ws_mask = grid.ws_roi_pass(f_s1, s2r, s2c)
            if (p_ws_mask or f_ws_mask) and not s2_flag:
                raise ValueError(
                    "WS raw-S2 ROI passed but EFT2024 NEST S2 threshold failed; "
                    "check raw/corrected S2 units and threshold nesting"
                )

            for key, (xs, ys) in spectra.items():
                weight = grid.interpolate(energy, xs, ys)
                if not math.isfinite(weight) or weight < 0.0:
                    raise ValueError(f"invalid spectrum weight for {key}/{ibin}")
                w2 = weight * weight
                bucket = stats[(key, ibin, replica)]
                bucket["n"] += 1
                bucket["sumw"] += weight
                bucket["sumw2"] += w2

                mode_values = {
                    "parametric": (p_flag, p_s1, p_ws_mask),
                    "full": (f_flag, f_s1, f_ws_mask),
                }
                ws_flags = {}
                for mode, (coin_flag, s1c, ws_mask) in mode_values.items():
                    coin_pass = bool(coin_flag)
                    nest_pass = coin_pass and bool(s2_flag) and s1c > 0.0 and s2c > 0.0
                    ws_pass = coin_pass and bool(s2_flag) and ws_mask
                    ws_flags[mode] = int(ws_pass)
                    for stage, passed in (
                        ("coin", coin_pass), ("nest", nest_pass), ("ws_roi", ws_pass)
                    ):
                        if passed:
                            bucket[f"{mode}_{stage}_w"] += weight
                            bucket[f"{mode}_{stage}_w2"] += w2
                            if stage != "coin":
                                cell = grid.cell_key(s1c, s2c)
                                maps[(key, mode, stage, ibin, replica)][cell] += weight

                delta = ws_flags["full"] - ws_flags["parametric"]
                bucket["d_ws_w"] += weight * delta
                bucket["d_ws_w2"] += w2 * delta
                bucket["d_ws2_w2"] += w2 * delta * delta

    expected_edges = grid.make_edges(
        ENERGY_MIN_KEV, ENERGY_MAX_KEV, ENERGY_BIN_WIDTH_KEV
    )
    if sorted(edges) != list(range(len(expected_edges)-1)):
        raise ValueError("paired response does not cover all 1-keV energy strata")
    for ibin, (lo, hi) in enumerate(zip(expected_edges, expected_edges[1:])):
        observed = edges[ibin]
        if abs(observed[0]-lo) > 1e-9 or abs(observed[1]-hi) > 1e-9:
            raise ValueError(f"incorrect response edges in bin {ibin}")
        for replica in (0, 1):
            if counts[(ibin, replica)] != events_per_bin // 2:
                raise ValueError(
                    f"bin {ibin}/replica {replica}: expected {events_per_bin//2}, "
                    f"got {counts[(ibin, replica)]}"
                )
    return stats, maps, edges

def fold(spectra: dict, stats: dict, maps: dict):
    bin_rows, summary_rows, map_rows = [], [], []
    all_map = defaultdict(lambda: defaultdict(float))
    replica_map = defaultdict(lambda: defaultdict(float))
    for key, (xs, ys) in spectra.items():
        benchmark, nuclear = key
        totals = {
            "raw": 0.0, "param_nest": 0.0, "full_nest": 0.0,
            "param_ws": 0.0, "full_ws": 0.0, "delta_ws": 0.0,
            "delta_var": 0.0,
        }
        for ibin in sorted({k[1] for k in stats if k[0] == key}):
            # Edges are fixed by the analysis definition.
            lo = ENERGY_MIN_KEV + ibin * ENERGY_BIN_WIDTH_KEV
            hi = min(ENERGY_MAX_KEV, lo + ENERGY_BIN_WIDTH_KEV)
            raw_rate = grid.integrate_linear(xs, ys, lo, hi)
            buckets = [stats[(key, ibin, rep)] for rep in (0, 1)]
            sumw = math.fsum(b["sumw"] for b in buckets)
            sumw2 = math.fsum(b["sumw2"] for b in buckets)
            if raw_rate > 0.0 and sumw <= 0.0:
                raise ValueError(f"{key}/{ibin}: positive exact spectrum rate but zero sample weight")
            if sumw <= 0.0:
                bin_rows.append({
                    "benchmark": benchmark, "nuclear_model": nuclear,
                    "energy_bin_index": ibin, "energy_low_keV": lo, "energy_high_keV": hi,
                    "exact_raw_rate_events_kg_day": raw_rate, "n_events": sum(b["n"] for b in buckets),
                    "parametric_ws_roi_efficiency": 0.0, "full_ws_roi_efficiency": 0.0,
                    "full_minus_parametric_ws_roi_efficiency": 0.0,
                    "paired_difference_mc_se": 0.0,
                })
                continue

            def pooled(field):
                return math.fsum(b[f"{field}_w"] for b in buckets)
            def pooled2(field):
                return math.fsum(b[f"{field}_w2"] for b in buckets)

            p_coin, _ = weighted_efficiency(sumw, sumw2, pooled("parametric_coin"), pooled2("parametric_coin"))
            f_coin, _ = weighted_efficiency(sumw, sumw2, pooled("full_coin"), pooled2("full_coin"))
            p_nest, _ = weighted_efficiency(sumw, sumw2, pooled("parametric_nest"), pooled2("parametric_nest"))
            f_nest, _ = weighted_efficiency(sumw, sumw2, pooled("full_nest"), pooled2("full_nest"))
            p_ws, p_ws_se = weighted_efficiency(sumw, sumw2, pooled("parametric_ws_roi"), pooled2("parametric_ws_roi"))
            f_ws, f_ws_se = weighted_efficiency(sumw, sumw2, pooled("full_ws_roi"), pooled2("full_ws_roi"))
            d_ws, d_ws_se = paired_difference(
                sumw, sumw2,
                math.fsum(b["d_ws_w"] for b in buckets),
                math.fsum(b["d_ws_w2"] for b in buckets),
                math.fsum(b["d_ws2_w2"] for b in buckets),
            )
            p_ws_rate, f_ws_rate = raw_rate*p_ws, raw_rate*f_ws
            delta_rate = raw_rate*d_ws
            totals["raw"] += raw_rate
            totals["param_nest"] += raw_rate*p_nest
            totals["full_nest"] += raw_rate*f_nest
            totals["param_ws"] += p_ws_rate
            totals["full_ws"] += f_ws_rate
            totals["delta_ws"] += delta_rate
            totals["delta_var"] += (raw_rate*d_ws_se)**2

            bin_rows.append({
                "benchmark": benchmark, "nuclear_model": nuclear,
                "energy_bin_index": ibin, "energy_low_keV": lo, "energy_high_keV": hi,
                "n_events": sum(b["n"] for b in buckets),
                "exact_raw_rate_events_kg_day": raw_rate,
                "parametric_s1_coincidence_efficiency": p_coin,
                "full_s1_coincidence_efficiency": f_coin,
                "parametric_nest_efficiency": p_nest,
                "full_nest_efficiency": f_nest,
                "parametric_ws_roi_efficiency": p_ws,
                "full_ws_roi_efficiency": f_ws,
                "full_minus_parametric_ws_roi_efficiency": d_ws,
                "paired_difference_mc_se": d_ws_se,
                "parametric_ws_roi_rate_events_kg_day": p_ws_rate,
                "full_ws_roi_rate_events_kg_day": f_ws_rate,
                "full_minus_parametric_ws_roi_rate_events_kg_day": delta_rate,
            })

            # Pooled event-weighted 2D cell rates: exact bin rate times sampled
            # cell weight divided by the pooled raw spectrum weight.
            for mode in MODES:
                for stage in STAGES:
                    pooled_cells = defaultdict(float)
                    for rep in (0, 1):
                        for cell, value in maps[(key, mode, stage, ibin, rep)].items():
                            pooled_cells[cell] += value
                    for cell, value in pooled_cells.items():
                        rate = raw_rate * value / sumw
                        all_map[(key, mode, stage)][cell] += rate
                    # Replica-specific maps are kept as stability diagnostics.
                    for rep in (0, 1):
                        denom = buckets[rep]["sumw"]
                        if denom <= 0.0:
                            continue
                        for cell, value in maps[(key, mode, stage, ibin, rep)].items():
                            replica_map[(key, rep, mode, stage)][cell] += raw_rate * value / denom

        for stage in STAGES:
            pmap = all_map[(key, "parametric", stage)]
            fmap = all_map[(key, "full", stage)]
            tv = total_variation(pmap, fmap)
            tv0 = total_variation(
                replica_map[(key, 0, "parametric", stage)],
                replica_map[(key, 0, "full", stage)],
            )
            tv1 = total_variation(
                replica_map[(key, 1, "parametric", stage)],
                replica_map[(key, 1, "full", stage)],
            )
            if stage == "nest":
                p_rate, f_rate = totals["param_nest"], totals["full_nest"]
            else:
                p_rate, f_rate = totals["param_ws"], totals["full_ws"]
            summary_rows.append({
                "benchmark": benchmark, "nuclear_model": nuclear,
                "response_model": "eft2024", "stage": stage,
                "raw_rate_events_kg_day": totals["raw"],
                "parametric_rate_events_kg_day": p_rate,
                "full_rate_events_kg_day": f_rate,
                "full_minus_parametric_rate_events_kg_day": f_rate-p_rate,
                "full_vs_parametric_relative_rate_difference": (
                    (f_rate/p_rate-1.0) if p_rate > 0.0 else None
                ),
                "full_vs_parametric_2d_total_variation": tv,
                "replica0_2d_total_variation": tv0,
                "replica1_2d_total_variation": tv1,
                "map_s1_bin_width_phd": grid.S1_BIN_WIDTH_PHD,
                "map_log10s2_bin_width": grid.LOG10_S2_BIN_WIDTH,
            })
        ws_param = totals["param_ws"]
        ws_full = totals["full_ws"]
        delta_se = math.sqrt(totals["delta_var"])
        # Add the integrated WS-ROI rate difference diagnostic to the WS summary.
        summary_rows[-1]["paired_integrated_rate_difference_mc_se_events_kg_day"] = delta_se
        summary_rows[-1]["integrated_rate_difference_over_mc_se_diagnostic"] = (
            totals["delta_ws"]/delta_se if delta_se > 0.0 else None
        )

    for (key, mode, stage), cells in all_map.items():
        benchmark, nuclear = key
        for (s1_bin, log_bin), rate in cells.items():
            map_rows.append({
                "benchmark": benchmark, "nuclear_model": nuclear,
                "response_model": "eft2024", "s1_mode": mode, "stage": stage,
                "s1_bin_index": s1_bin,
                "s1_bin_low_phd": s1_bin*grid.S1_BIN_WIDTH_PHD,
                "log10s2_bin_index": log_bin,
                "log10s2_bin_low": log_bin*grid.LOG10_S2_BIN_WIDTH,
                "rate_events_kg_day": rate,
            })
    return bin_rows, summary_rows, map_rows

def write_union_schema_csv(path: Path, rows: list[dict]) -> None:
    """Write heterogeneous diagnostic rows using the union of their keys."""
    if not rows:
        raise ValueError(f"cannot write empty diagnostic table: {path}")
    fieldnames = list(dict.fromkeys(field for row in rows for field in row))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-csv", type=Path, required=True)
    ap.add_argument("--spectrum-dir", type=Path, default=Path(
        "research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum"
    ))
    ap.add_argument("--events-per-bin", type=int, default=2000)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    if args.events_per_bin < 2 or args.events_per_bin % 2:
        raise ValueError("events-per-bin must be an even integer >=2")
    spectra = read_spectra(args.spectrum_dir)
    stats, maps, edges = accumulate_events(args.input_csv, spectra, args.events_per_bin)
    bin_rows, summary_rows, map_rows = fold(spectra, stats, maps)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "by_energy_bin": args.out_dir/"paired_s1_mode_2d_response_by_energy_bin.csv",
        "summary": args.out_dir/"paired_s1_mode_2d_response_summary.csv",
        "maps": args.out_dir/"paired_s1_mode_2d_signal_intensity.csv",
        "metadata": args.out_dir/"paired_s1_mode_2d_response_metadata.json",
    }
    for key, rows in (("by_energy_bin", bin_rows), ("summary", summary_rows), ("maps", map_rows)):
        write_union_schema_csv(outputs[key], rows)
    metadata = {
        "study": "paired NEST Parametric/Full S1 mode event-weighted 2D response",
        "status": "PAIRED_2D_RESPONSE_DIAGNOSTIC_ONLY",
        "nest_commit": "541b6430dae6ea289cf110c99f174a9187f7fdee",
        "response_model": "EFT2024",
        "detector_configuration": "LZ_Detector_2024::SetEFT2024Configuration",
        "energy_interval_keV": [ENERGY_MIN_KEV, ENERGY_MAX_KEV],
        "energy_bin_width_keV": ENERGY_BIN_WIDTH_KEV,
        "events_per_energy_bin": args.events_per_bin,
        "events_per_replica_per_bin": args.events_per_bin//2,
        "n_energy_bins": len(edges)-1,
        "n_events": args.events_per_bin*(len(edges)-1),
        "pairing": "Same intrinsic NR quanta and true position; independent Parametric/Full S1 response draws; one common Full S2 draw per event.",
        "fold": "Per true-energy bin, scale sampled event/cell weights by the exact piecewise-linear three-body rate integral; normalize by the pooled raw spectrum weight.",
        "map_binning": {"s1_width_phd": grid.S1_BIN_WIDTH_PHD, "log10s2_width": grid.LOG10_S2_BIN_WIDTH},
        "selection": "NEST S1 coincidence + NEST S2 threshold for nest stage; additionally 3<=S1c<=600 phd, raw S2>645 phd, and 2.75<=log10(S2c)<=4.15 for WS ROI stage.",
        "limitations": [
            "NEST Full S1 PMT/time-window response is not the official LZ waveform-level reconstruction.",
            "The common S2 is NEST integrated Full mode, not the official DAQ waveform trigger.",
            "No DAQ trigger, SS reconstruction, data-analysis cuts, official 4.71-t fiducial-volume map, Skin/OD veto, or live-time migration is included.",
            "Two disjoint halves of one deterministic event design are stability diagnostics, not independent-seed covariance estimates.",
            "The 2D TV is a point estimate on the stated histogram grid; no bootstrap uncertainty is included.",
            "The Fig. S2 residual SS/data-analysis efficiency is deliberately not multiplied into these 2D maps."
        ],
        "n_summary_rows": len(summary_rows),
        "n_energy_bin_rows": len(bin_rows),
        "n_2d_map_rows": len(map_rows),
        "outputs": {k: v.name for k,v in outputs.items()},
    }
    outputs["metadata"].write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({
        "status": metadata["status"], "n_events": metadata["n_events"],
        "n_energy_bins": metadata["n_energy_bins"],
        "n_summary_rows": len(summary_rows), "n_energy_bin_rows": len(bin_rows),
        "n_2d_map_rows": len(map_rows), "outputs": {k:str(v) for k,v in outputs.items()},
    }, indent=2))

if __name__ == "__main__":
    main()
