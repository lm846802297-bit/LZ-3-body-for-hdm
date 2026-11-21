"""Vectorized event-weighted NEST fold for repeated formal-B spectra."""
from __future__ import annotations

import math
import numpy as np

import converge_lz_2026_three_body_energy_grid as grid

MODES = ("nest", "ws_roi")


def prepare_event_sample(events: dict) -> dict:
    """Flatten one NEST response family once for reuse across all B spectra."""
    bins = sorted({ibin for ibin, _ in events})
    bin_position = {ibin: i for i, ibin in enumerate(bins)}
    energy_parts = []
    bin_parts = []
    replica_parts = []
    s1_parts = []
    log_parts = []
    nest_parts = []
    roi_parts = []
    lows = []
    highs = []
    for ibin in bins:
        for replica in (0, 1):
            rec = events.get((ibin, replica))
            if rec is None or len(rec["energy"]) == 0:
                raise ValueError(f"missing or empty response bin/replica {ibin}/{replica}")
            if replica == 0:
                lows.append(float(rec["lo"]))
                highs.append(float(rec["hi"]))
            elif abs(float(rec["lo"]) - lows[-1]) > 1e-10 or abs(float(rec["hi"]) - highs[-1]) > 1e-10:
                raise ValueError(f"replica energy-bin mismatch in bin {ibin}")
            n = len(rec["energy"])
            energy_parts.append(np.frombuffer(rec["energy"], dtype=np.float64))
            bin_parts.append(np.full(n, bin_position[ibin], dtype=np.int32))
            replica_parts.append(np.full(n, replica, dtype=np.int8))
            s1_parts.append(np.frombuffer(rec["s1_bin"], dtype=np.int32))
            log_parts.append(np.frombuffer(rec["log_s2_bin"], dtype=np.int32))
            nest_parts.append(np.frombuffer(rec["nest_pass"], dtype=np.uint8).astype(bool))
            roi_parts.append(np.frombuffer(rec["roi_pass"], dtype=np.uint8).astype(bool))
    return {
        "prepared": True,
        "bins": bins,
        "lo": np.asarray(lows, dtype=float),
        "hi": np.asarray(highs, dtype=float),
        "energy": np.concatenate(energy_parts),
        "bin_pos": np.concatenate(bin_parts),
        "replica": np.concatenate(replica_parts),
        "s1_bin": np.concatenate(s1_parts),
        "log_s2_bin": np.concatenate(log_parts),
        "nest_pass": np.concatenate(nest_parts),
        "roi_pass": np.concatenate(roi_parts),
    }


def _cell_map(s1_bin: np.ndarray, log_bin: np.ndarray, weights: np.ndarray, mask: np.ndarray) -> dict:
    if not np.any(mask):
        return {}
    s1 = s1_bin[mask].astype(np.int64, copy=False)
    log_s2 = log_bin[mask].astype(np.int64, copy=False)
    if np.any(s1 < 0) or np.any(s1 >= 128) or np.any(log_s2 < 0) or np.any(log_s2 >= 512):
        raise ValueError("observable bin index outside the validated compact NEST map")
    # S1 has at most 60 ten-phd bins and log10(S2c) has fewer than 512 bins.
    codes = s1 * 512 + log_s2
    sums = np.bincount(codes, weights=weights[mask], minlength=65536)
    occupied = np.flatnonzero(sums)
    return {
        (int(code // 512), int(code % 512)): float(sums[code])
        for code in occupied
    }


def weighted_fold_all_replicas(events: dict, xs: list[float], ys: list[float]) -> dict:
    """Vectorized exact-bin event weighting for both replicas and their pool."""
    ev = events if events.get("prepared") else prepare_event_sample(events)
    nbin = len(ev["bins"])
    density = np.interp(
        ev["energy"], np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)
    )
    stratum = 2 * ev["bin_pos"] + ev["replica"].astype(np.int32)
    nstrata = 2 * nbin
    sums = np.bincount(stratum, weights=density, minlength=nstrata)
    counts = np.bincount(stratum, minlength=nstrata)
    exact = np.asarray([
        grid.integrate_linear(xs, ys, float(lo), float(hi))
        for lo, hi in zip(ev["lo"], ev["hi"])
    ], dtype=float)
    bad = (np.repeat(exact, 2) > 0.0) & (sums <= 0.0)
    if np.any(bad):
        i = int(np.flatnonzero(bad)[0])
        raise ValueError(
            f"zero sampled spectrum weight in bin {ev['bins'][i // 2]}, replica {i % 2}"
        )
    bin_rate = exact[ev["bin_pos"]]
    rep_denom = sums[stratum]
    rep_weights = np.divide(
        density * bin_rate, rep_denom,
        out=np.zeros_like(density), where=rep_denom > 0.0
    )
    pooled_denom_by_bin = sums[0::2] + sums[1::2]
    pooled_denom = pooled_denom_by_bin[ev["bin_pos"]]
    pooled_weights = np.divide(
        density * bin_rate, pooled_denom,
        out=np.zeros_like(density), where=pooled_denom > 0.0
    )

    nest_weight = np.bincount(
        stratum[ev["nest_pass"]],
        weights=density[ev["nest_pass"]],
        minlength=nstrata
    )
    roi_weight = np.bincount(
        stratum[ev["roi_pass"]],
        weights=density[ev["roi_pass"]],
        minlength=nstrata
    )
    output = {}
    for rep in (0, 1, None):
        rep_mask = np.ones(len(density), dtype=bool) if rep is None else (ev["replica"] == rep)
        weights = pooled_weights if rep is None else rep_weights
        output[rep] = {
            "raw_rate": float(np.sum(exact)),
            "intensity": {},
            "accepted_rate": {},
            "bin_rows": [],
        }
        for mode, pass_mask in (("nest", ev["nest_pass"]), ("ws_roi", ev["roi_pass"])):
            mask = rep_mask & pass_mask
            cells = _cell_map(ev["s1_bin"], ev["log_s2_bin"], weights, mask)
            output[rep]["intensity"][mode] = cells
            output[rep]["accepted_rate"][mode] = float(np.sum(weights[mask]))

    for i, ibin in enumerate(ev["bins"]):
        s0, s1 = sums[2 * i], sums[2 * i + 1]
        output[None]["bin_rows"].append({
            "energy_bin_index": int(ibin),
            "energy_low_keV": float(ev["lo"][i]),
            "energy_high_keV": float(ev["hi"][i]),
            "exact_raw_rate_integral_events_kg_day": float(exact[i]),
            "n_generated_replica0": int(counts[2 * i]),
            "n_generated_replica1": int(counts[2 * i + 1]),
            "nest_acceptance_weighted_replica0": float(nest_weight[2 * i] / s0) if s0 > 0 else 0.0,
            "nest_acceptance_weighted_replica1": float(nest_weight[2 * i + 1] / s1) if s1 > 0 else 0.0,
            "ws_roi_acceptance_weighted_replica0": float(roi_weight[2 * i] / s0) if s0 > 0 else 0.0,
            "ws_roi_acceptance_weighted_replica1": float(roi_weight[2 * i + 1] / s1) if s1 > 0 else 0.0,
        })
    return output
