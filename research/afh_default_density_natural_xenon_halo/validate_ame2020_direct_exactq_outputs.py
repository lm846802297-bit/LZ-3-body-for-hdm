#!/usr/bin/env python3
"""Local acceptance checks for the AME2020 direct exact-q selected-point fold."""
from __future__ import annotations
import argparse, csv, hashlib, math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

def rows(path):
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, required=True)
    ap.add_argument("--response-csv", type=Path,
                    default=HERE / "input" / "afh_selected_exact_q_responses.csv")
    args = ap.parse_args()
    d = args.results_dir

    response = rows(args.response_csv)
    integrals = rows(d / "base_kernel_halo_integrals.csv")
    contributions = rows(d / "seven_isotope_contributions.csv")
    rates = rows(d / "seven_isotope_halo_rates.csv")
    repro = rows(d / "nist_mainline_reproduction.csv")
    speed = rows(d / "speed_quadrature_convergence.csv")
    isotope_speed = rows(d / "isotope_speed_quadrature_convergence.csv")
    kernel = rows(d / "kernel_quadrature_convergence.csv")
    hybrid = rows(d / "xe131_only_ame2020_hybrid_direct_exactq.csv")

    expected_isotopes = {128, 129, 130, 131, 132, 134, 136}
    expected_schemes = {"nist_nuclear", "ame2020_nuclear"}
    expected_energies = {101.0, 200.0, 267.0, 542.0}
    response_keys = {(r["mass_scheme"], int(r["A"]), float(r["ER_keV"])) for r in response}
    expected_response_keys = {
        (scheme, A, ER) for scheme in expected_schemes
        for A in expected_isotopes for ER in expected_energies
    }
    assert len(response) == 56 and response_keys == expected_response_keys
    for r in response:
        q = float(r["q_exact_spatial_GeV"])
        exact = float(r["R_A_exact_q_mpmath"])
        pchip = float(r["R_A_PCHIP_2401_grid"])
        assert q > 0 and math.isfinite(q)
        assert math.isfinite(exact) and exact >= 0
        assert math.isfinite(pchip) and pchip >= 0

    assert len(integrals) == 392, len(integrals)
    assert len(contributions) == 784, len(contributions)
    assert len(rates) == 112, len(rates)
    assert len(repro) == 14, len(repro)
    assert len(speed) == 56, len(speed)
    assert len(isotope_speed) == 392, len(isotope_speed)
    assert len(kernel) == 21, len(kernel)
    assert len(hybrid) == 14, len(hybrid)

    integral_keys = {
        (int(r["A"]), r["mass_scheme"], r["benchmark"], float(r["ER_keV"]),
         r["halo_model"], int(r["nv"])) for r in integrals
    }
    assert len(integral_keys) == 392
    for r in integrals:
        value = float(r["speed_integral_dsigma_GeVminus3"])
        assert math.isfinite(value) and value >= 0

    contribution_keys = {
        (int(r["A"]), r["mass_scheme"], r["benchmark"], float(r["ER_keV"]),
         r["halo_model"], int(r["nv"]), r["response_method"]) for r in contributions
    }
    assert len(contribution_keys) == 784
    assert {int(r["A"]) for r in contributions} == expected_isotopes
    assert {r["mass_scheme"] for r in contributions} == expected_schemes
    assert {r["response_method"] for r in contributions} == {
        "direct_exact_q", "historical_2401_PCHIP"
    }
    for r in contributions:
        value = float(r["rate_contribution_events_kg_day_keV"])
        assert math.isfinite(value) and value >= 0

    # Independent closure: sum all seven isotope terms and compare with each stored total.
    key_fields = ("mass_scheme", "benchmark", "ER_keV", "halo_model", "nv", "response_method")
    isotope_sums = defaultdict(list)
    for r in contributions:
        key = tuple(r[k] for k in key_fields)
        isotope_sums[key].append(float(r["rate_contribution_events_kg_day_keV"]))
    rate_keys = set()
    max_rate_sum_relative = 0.0
    for r in rates:
        key = tuple(r[k] for k in key_fields)
        assert key not in rate_keys
        rate_keys.add(key)
        stored = float(r["AFH_7_isotope_rate_events_kg_day_keV"])
        calculated = math.fsum(isotope_sums[key])
        assert math.isfinite(stored) and stored >= 0
        relative = abs(calculated - stored) / max(abs(stored), 1e-300)
        max_rate_sum_relative = max(max_rate_sum_relative, relative)
    assert set(isotope_sums) == rate_keys and len(rate_keys) == 112
    assert max_rate_sum_relative < 1e-12, max_rate_sum_relative

    assert max(float(r["relative_difference"]) for r in repro) < 5e-8
    assert max(float(r["relative_difference_32_to_64"]) for r in speed) < 5e-3
    assert max(float(r["relative_difference_32_to_64"]) for r in isotope_speed) < 5e-3
    assert max(float(r["relative_difference"]) for r in kernel) < 5e-3

    # Verify the output manifest against every listed native output file.
    manifest = (d / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    assert len(manifest) == 12
    for line in manifest:
        digest, name = line.split("  ", 1)
        assert sha256(d / name) == digest, name

    print("PASS: 56 direct exact-q response inputs")
    print("PASS: 392 kernel/halo integrals; 784 isotope contributions; 112 rate summaries")
    print("PASS: seven-isotope contribution sums close to stored totals")
    print("PASS: NIST baseline reproduction, speed convergence, kernel convergence and SHA-256 manifest")
    print(f"max NIST reproduction={max(float(r['relative_difference']) for r in repro):.3e}")
    print(f"max speed convergence={max(float(r['relative_difference_32_to_64']) for r in speed):.3e}")
    print(f"max kernel convergence={max(float(r['relative_difference']) for r in kernel):.3e}")
    print(f"max isotope-sum closure={max_rate_sum_relative:.3e}")

if __name__ == "__main__":
    main()
