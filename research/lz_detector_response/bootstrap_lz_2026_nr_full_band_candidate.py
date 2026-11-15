#!/usr/bin/env python3
"""Deterministic finite-MC bootstrap for the LZ NR candidate's S2c band offset."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

OBS_S1 = 540.07916
OBS_S2 = 9267.53
OBS_LOG_S2 = math.log10(OBS_S2)
S1_LOW = 540.0
S1_HIGH = 545.0
SIGMA80_FACTOR = 2.5631031311
BOOTSTRAP_SEED = 20261115
BOOTSTRAP_REPLICATES = 2000


def summarize(path: Path, rng: np.random.Generator) -> dict:
    values = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            s1 = float(row["s1c_phd"])
            s2 = float(row["s2c_phd"])
            if not (math.isfinite(s1) and math.isfinite(s2)):
                raise ValueError(f"non-finite S1c/S2c in {path}")
            if S1_LOW <= s1 < S1_HIGH and s1 > 0.0 and s2 > 0.0:
                values.append(math.log10(s2))

    sample = np.asarray(values, dtype=np.float64)
    if sample.size < 100:
        raise ValueError(f"only {sample.size} events in candidate S1c bin for {path}")

    q10, median, q90 = np.quantile(sample, [0.10, 0.50, 0.90], method="linear")
    sigma_eq = (q90 - q10) / SIGMA80_FACTOR
    z_observed = (OBS_LOG_S2 - median) / sigma_eq

    indices = rng.integers(0, sample.size,
                           size=(BOOTSTRAP_REPLICATES, sample.size))
    replicas = sample[indices]
    q10_b, median_b, q90_b = np.quantile(
        replicas, [0.10, 0.50, 0.90], axis=1, method="linear"
    )
    sigma_b = (q90_b - q10_b) / SIGMA80_FACTOR
    z_b = (OBS_LOG_S2 - median_b) / sigma_b
    ci_low, ci_high = np.quantile(z_b, [0.025, 0.975], method="linear")

    return {
        "file": path.name,
        "n_events_in_540_545_phd_bin": int(sample.size),
        "log10_s2c_p10": float(q10),
        "log10_s2c_median": float(median),
        "log10_s2c_p90": float(q90),
        "sigma80_equivalent": float(sigma_eq),
        "candidate_minus_median_sigma80": float(z_observed),
        "bootstrap_z_standard_error": float(np.std(z_b, ddof=1)),
        "bootstrap_z_95_percentile_interval": [float(ci_low), float(ci_high)],
    }


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: bootstrap_lz_2026_nr_full_band_candidate.py CSV [CSV ...]")
    paths = [Path(x) for x in sys.argv[1:]]
    order = {"uniform_tpc": 0, "candidate": 1}
    paths.sort(key=lambda p: (order.get("uniform_tpc" if "uniform_tpc" in p.name else "candidate", 2), p.name))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    results = [summarize(path, rng) for path in paths]
    print(json.dumps({
        "study": "LZ NR candidate band finite-MC bootstrap",
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "confidence_interval": "central 95% percentile interval from event resampling within the 540 <= S1c < 545 phd bin",
        "band_definition": "positive S1c and S2c events, before NEST pass flags and analysis ROI",
        "sigma_definition": "sigma80 = (q90 - q10) / 2.5631031311; z = (log10(S2c_observed) - median) / sigma80",
        "observed_candidate": {
            "S1c_phd": OBS_S1,
            "S2c_phd": OBS_S2,
            "log10_S2c": OBS_LOG_S2,
        },
        "samples": results,
    }, indent=2))


if __name__ == "__main__":
    main()
