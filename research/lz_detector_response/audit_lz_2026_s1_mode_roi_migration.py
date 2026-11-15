#!/usr/bin/env python3
"""Audit S1c ROI migration between NEST Parametric and Full S1 modes.

The paired source sample shares NR quanta, recoil energy and true position,
but uses separate S1-response random streams. This is a one-dimensional S1
diagnostic only: no S2 is present, so it cannot establish 2D PDF equivalence.
"""
from __future__ import annotations
import argparse, csv, json, math
from collections import Counter
from pathlib import Path
import summarize_lz_2026_s1_coincidence_mode_comparison as base

S1_MIN, S1_MAX, HIST_WIDTH = 3.0, 600.0, 10.0

def selected(pass_flag: int, s1c: float) -> bool:
    return bool(pass_flag) and S1_MIN <= s1c <= S1_MAX

def histogram_tv(a: list[float], b: list[float], width: float = HIST_WIDTH) -> float | None:
    if width <= 0:
        raise ValueError("histogram width must be positive")
    if not a or not b:
        return None
    ca, cb = Counter(math.floor(x / width) for x in a), Counter(math.floor(x / width) for x in b)
    na, nb = len(a), len(b)
    return 0.5 * math.fsum(abs(ca[k] / na - cb[k] / nb) for k in set(ca) | set(cb))

def summarize_bin(ibin: int, rows: list[dict[str, float]]) -> dict:
    if not rows:
        raise ValueError("empty S1 energy bin")
    first = rows[0]
    for row in rows[1:]:
        for key in ("energy_bin_low_keV", "energy_bin_high_keV"):
            if abs(row[key] - first[key]) > 1e-10:
                raise ValueError(f"energy-bin metadata mismatch in bin {ibin}")
    pcoin = [int(r["s1_param_pass"]) for r in rows]
    fcoin = [int(r["s1_full_pass"]) for r in rows]
    proi = [int(selected(p, r["s1_param_abs_phd"])) for p, r in zip(pcoin, rows)]
    froi = [int(selected(f, r["s1_full_abs_phd"])) for f, r in zip(fcoin, rows)]
    n = len(rows)
    npass, fpass = sum(proi), sum(froi)
    ponly = sum(p and not f for p, f in zip(proi, froi))
    fonly = sum(f and not p for p, f in zip(proi, froi))
    diff = (fpass - npass) / n
    discord = (ponly + fonly) / n
    paired_se = math.sqrt(max(0.0, discord - diff * diff) / n)
    ci = base.paired_difference_wilson_interval(fonly, ponly, n)
    pvals = [r["s1_param_abs_phd"] for r, flag in zip(rows, pcoin) if flag]
    fvals = [r["s1_full_abs_phd"] for r, flag in zip(rows, fcoin) if flag]
    pselected = [r["s1_param_abs_phd"] for r, flag in zip(rows, proi) if flag]
    fselected = [r["s1_full_abs_phd"] for r, flag in zip(rows, froi) if flag]
    p_above = sum(flag and r["s1_param_abs_phd"] > S1_MAX for r, flag in zip(rows, pcoin))
    f_above = sum(flag and r["s1_full_abs_phd"] > S1_MAX for r, flag in zip(rows, fcoin))
    return {
        "energy_bin_index": ibin,
        "energy_low_keV": first["energy_bin_low_keV"],
        "energy_high_keV": first["energy_bin_high_keV"],
        "n_generated": n,
        "parametric_s1_coincidence_efficiency": sum(pcoin) / n,
        "full_s1_coincidence_efficiency": sum(fcoin) / n,
        "parametric_s1_roi_efficiency": npass / n,
        "full_s1_roi_efficiency": fpass / n,
        "full_minus_parametric_s1_roi_pp": 100.0 * diff,
        "paired_difference_se_pp": 100.0 * paired_se,
        "paired_difference_95pct_interval_pp": [100.0 * x for x in ci],
        "n_parametric_only_s1_roi": ponly,
        "n_full_only_s1_roi": fonly,
        "paired_s1_roi_discordance_fraction": discord,
        "parametric_s1_roi_given_coincidence": npass / sum(pcoin) if sum(pcoin) else None,
        "full_s1_roi_given_coincidence": fpass / sum(fcoin) if sum(fcoin) else None,
        "parametric_fraction_above_600_given_coincidence": p_above / sum(pcoin) if sum(pcoin) else None,
        "full_fraction_above_600_given_coincidence": f_above / sum(fcoin) if sum(fcoin) else None,
        "s1c_marginal_tv_10phd_given_coincidence": histogram_tv(pvals, fvals),
        "s1c_marginal_tv_10phd_after_s1_roi": histogram_tv(pselected, fselected),
        "parametric_s1c_q10_q50_q90_phd": [base.quantile(pvals, q) for q in (0.1, 0.5, 0.9)],
        "full_s1c_q10_q50_q90_phd": [base.quantile(fvals, q) for q in (0.1, 0.5, 0.9)],
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-csv", type=Path, required=True)
    ap.add_argument("--source-run-id", type=int, default=43658191416)
    ap.add_argument("--source-artifact-id", type=int, default=14138858617)
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args()
    groups = base.read_events(args.input_csv)
    rows = [summarize_bin(i, events) for i, events in sorted(groups.items())]
    if len(rows) != 10 or sum(r["n_generated"] for r in rows) != 100000:
        raise ValueError("unexpected source sample coverage; expected 10 bins and 100,000 events")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "s1_mode_roi_by_energy_bin.csv"
    json_path = args.out_dir / "s1_mode_roi_migration_summary.json"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    summary = {
        "study": "NEST Parametric versus Full S1c ROI migration audit",
        "status": "S1_1D_ROI_MIGRATION_DIAGNOSTIC_ONLY",
        "source_run_id": args.source_run_id,
        "source_artifact_id": args.source_artifact_id,
        "nest_commit": "541b6430dae6ea289cf110c99f174a9187f7fdee",
        "detector_configuration": "LZ_Detector_2024::SetEFT2024Configuration",
        "pairing": "same NR quanta, true recoil energy and true position; independent deterministic S1 response streams",
        "s1_roi_phd": [S1_MIN, S1_MAX],
        "s1_histogram_width_phd": HIST_WIDTH,
        "n_energy_bins": len(rows),
        "n_events": sum(r["n_generated"] for r in rows),
        "max_abs_s1_roi_efficiency_difference_pp": max(abs(r["full_minus_parametric_s1_roi_pp"]) for r in rows),
        "max_s1c_marginal_tv_10phd_given_coincidence": max(r["s1c_marginal_tv_10phd_given_coincidence"] or 0.0 for r in rows),
        "energy_bin_results": rows,
        "interpretation": "Coincidence acceptance agreement does not establish equivalence of the S1c response; the upper S1c ROI can migrate events differently.",
        "limitations": [
            "The source sample contains S1 only; S2 is absent, so no joint 2D (S1c, log10(S2c)) migration or TV is measured.",
            "NEST Full S1 is a PMT/time-window model, not the official LZ waveform-level event reconstruction.",
            "DAQ trigger, SS reconstruction, data-analysis cuts, FV, Skin/OD veto and live-time migration are not included.",
            "Histogram TV is a descriptive point estimate without bootstrap or independent-seed uncertainty.",
            "The 10 energy bins are anchor checks, not a continuous full-spectrum detector-response fold."
        ],
    }
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "n_energy_bins": len(rows), "n_events": summary["n_events"],
        "max_abs_s1_roi_efficiency_difference_pp": summary["max_abs_s1_roi_efficiency_difference_pp"],
        "max_s1c_marginal_tv_10phd_given_coincidence": summary["max_s1c_marginal_tv_10phd_given_coincidence"],
        "outputs": [str(csv_path), str(json_path)]}, indent=2))

if __name__ == "__main__":
    main()
