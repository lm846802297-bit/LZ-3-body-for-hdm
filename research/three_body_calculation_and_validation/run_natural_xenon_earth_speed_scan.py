#!/usr/bin/env python3
"""Annual lab-speed sensitivity of the NIST-mass natural-xenon 101 keV rate."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_natural_xenon_halo_fold import (  # noqa: E402
    NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL,
    compute_isotope_halo_integrals,
    rate_conversion_factor,
)
from run_natural_xenon_joint import AVAILABLE, MODELS, NATURAL_ABUNDANCE  # noqa: E402

ER_KEV = 101.0


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-dir", type=Path,
                        default=HERE / "results" / "anand_wm_response")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--ms-MeV", type=float, default=0.3)
    parser.add_argument("--delta-m-MeV", type=float, default=1.0)
    parser.add_argument("--coupling-product-sq", type=float, default=1.0e-8)
    parser.add_argument("--rhoDM-GeV-cm3", type=float, default=0.3)
    parser.add_argument("--mV-GeV", type=float, default=0.1)
    parser.add_argument("--ve-values-km-s", type=float, nargs="+",
                        default=[217.0, 232.0, 247.0])
    parser.add_argument("--v0-km-s", type=float, default=220.0)
    parser.add_argument("--vesc-km-s", type=float, default=544.0)
    parser.add_argument("--nv-orders", type=int, nargs="+", default=[16, 32])
    parser.add_argument("--nw", type=int, default=16)
    parser.add_argument("--nz", type=int, default=16)
    parser.add_argument("--nphi", type=int, default=8)
    parser.add_argument("--max-relative-convergence", type=float, default=5.0e-3)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ms = args.ms_MeV * 1.0e-3
    delta_m = args.delta_m_MeV * 1.0e-3
    rate_factor = rate_conversion_factor(args.rhoDM_GeV_cm3, args.mchi_GeV)

    isotope_rows: list[dict] = []
    natural_rows: list[dict] = []
    for ve in args.ve_values_km_s:
        for nv in args.nv_orders:
            per_isotope = {}
            for A in AVAILABLE:
                rows = compute_isotope_halo_integrals(
                    A=A,
                    ER_keV=ER_KEV,
                    halo_model="shm_cutoff",
                    mass_scheme="nist_nuclear",
                    nv=nv,
                    mchi=args.mchi_GeV,
                    ms=ms,
                    delta_m=delta_m,
                    speed_v0=args.v0_km_s,
                    speed_ve=ve,
                    speed_vesc=args.vesc_km_s,
                    untruncated_vmax=1600.0,
                    coupling_product_sq=args.coupling_product_sq,
                    response_dir=args.response_dir,
                    nw=args.nw,
                    nz=args.nz,
                    nphi=args.nphi,
                )
                for row in rows:
                    row["ve_km_s"] = ve
                    isotope_rows.append(row)
                    per_isotope[(A, row["model"])] = row

            for model in MODELS:
                weighted_sigma_integral = 0.0
                open_isotopes = []
                for A in AVAILABLE:
                    row = per_isotope[(A, model.upper())]
                    if row["speed_phase_space_open"]:
                        open_isotopes.append(A)
                    mA = float(row["mA_GeV"])
                    denominator = (
                        args.mV_GeV**2 + 2.0 * mA * ER_KEV * 1.0e-6
                    ) ** 2
                    weighted_sigma_integral += (
                        NATURAL_ABUNDANCE[A] * float(row["J_A_GeV"]) / denominator
                    )
                natural_rows.append({
                    "mass_scheme": "nist_nuclear",
                    "halo_model": "shm_cutoff",
                    "model": model.upper(),
                    "ER_keV": ER_KEV,
                    "ve_km_s": ve,
                    "vmax_lab_km_s": args.vesc_km_s + ve,
                    "open_available_isotopes": ";".join(map(str, open_isotopes)),
                    "mV_GeV": args.mV_GeV,
                    "nv": nv,
                    "available_abundance_fraction": sum(
                        NATURAL_ABUNDANCE[A] for A in AVAILABLE
                    ),
                    "mean_xenon_atomic_weight_g_mol": NIST_XE_STANDARD_ATOMIC_WEIGHT_G_MOL,
                    "sum_xA_halo_integral_dsigma_GeVminus3": weighted_sigma_integral,
                    "rate_events_kg_day_keV": rate_factor * weighted_sigma_integral,
                })

    convergence_rows = []
    orders = sorted(set(args.nv_orders))
    if len(orders) >= 2:
        lo, hi = orders[-2], orders[-1]
        for ve in args.ve_values_km_s:
            for model in MODELS:
                low = next(r for r in natural_rows if
                           r["ve_km_s"] == ve and r["model"] == model.upper() and r["nv"] == lo)
                high = next(r for r in natural_rows if
                            r["ve_km_s"] == ve and r["model"] == model.upper() and r["nv"] == hi)
                lr, hr = float(low["rate_events_kg_day_keV"]), float(high["rate_events_kg_day_keV"])
                rel = abs(hr / lr - 1.0) if lr > 0.0 else (0.0 if hr == 0.0 else float("inf"))
                convergence_rows.append({
                    "ve_km_s": ve,
                    "model": model.upper(),
                    "nv_low": lo,
                    "nv_high": hi,
                    "rate_low": lr,
                    "rate_high": hr,
                    "relative_difference": rel,
                })
                if rel > args.max_relative_convergence:
                    raise ArithmeticError(
                        f"Earth-speed scan not converged at ve={ve}, model={model}: {rel:.4g}"
                    )

    write_csv(args.out_dir / "isotope_earth_speed_contributions.csv", isotope_rows)
    write_csv(args.out_dir / "natural_xenon_earth_speed_scan.csv", natural_rows)
    if convergence_rows:
        write_csv(args.out_dir / "earth_speed_quadrature_convergence.csv", convergence_rows)

    metadata = {
        "calculation": "Xe-136 and natural-xenon annual lab-speed sensitivity at ER=101 keV",
        "mass_scheme": "NIST nuclear mass: (atomic isotope mass - 54 electron masses)*u",
        "mchi_GeV": args.mchi_GeV,
        "ms_MeV": args.ms_MeV,
        "delta_m_MeV": args.delta_m_MeV,
        "coupling_product_sq": args.coupling_product_sq,
        "rhoDM_GeV_cm3": args.rhoDM_GeV_cm3,
        "ER_keV": ER_KEV,
        "halo_model": "truncated SHM",
        "v0_km_s": args.v0_km_s,
        "vesc_km_s": args.vesc_km_s,
        "ve_scan_km_s": args.ve_values_km_s,
        "vE_interpretation": (
            "fixed-speed sensitivity bracket; not a time-averaged annual modulation calculation"
        ),
        "mV_GeV": args.mV_GeV,
        "width_scheme": "zero",
        "available_isotopes": list(AVAILABLE),
        "available_abundance_fraction": sum(NATURAL_ABUNDANCE[A] for A in AVAILABLE),
        "rate_units": "events/(kg day keV)",
        "not_included": [
            "Xe-124 and Xe-126 nuclear response contributions",
            "exact date-dependent orbital projection and time averaging",
            "detector efficiency, energy resolution and exposure",
        ],
    }
    (args.out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    for row in natural_rows:
        if row["nv"] == max(args.nv_orders):
            print(
                f"ve={row['ve_km_s']:6.1f} vmax={row['vmax_lab_km_s']:6.1f} "
                f"{row['model']:4s} open={row['open_available_isotopes'] or 'none'} "
                f"rate={row['rate_events_kg_day_keV']:.8e}"
            )


if __name__ == "__main__":
    main()
