#!/usr/bin/env python3
"""Natural-xenon three-body halo fold using full AFH default-density q grids."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import PchipInterpolator

import run_afh_natural_xenon_halo_fold as selected
from isotope_mass_schemes import isotope_mass_GeV
import eq6_kernel

HERE = Path(__file__).resolve().parent
BENCHMARKS = {
    "red_ms200_dm1": (200e-6, 1e-3),
    "green_ms300_dm1": (300e-6, 1e-3),
    "black_ms360_dm1": (360e-6, 1e-3),
    "blue_ms300_dm10": (300e-6, 10e-3),
}
CASES = [(name, 101.0) for name in BENCHMARKS] + [
    ("green_ms300_dm1", er) for er in (200.0, 267.0, 542.0)
]
C_KM_S = 299792.458
C_CM_S = 2.99792458e10
GEV2_TO_CM2 = 0.3893793721e-27
AVOGADRO = 6.02214076e23


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_full_response_grid(path: Path) -> tuple[dict[int, PchipInterpolator], dict]:
    rows = read_csv(path)
    grouped = {}
    for row in rows:
        grouped.setdefault(int(row["A"]), []).append(row)
    interpolators = {}
    for A, isotope_rows in grouped.items():
        isotope_rows.sort(key=lambda r: float(r["q_GeV"]))
        q = np.array([float(r["q_GeV"]) for r in isotope_rows])
        R = np.array([float(r["R_A_equal_pn"]) for r in isotope_rows])
        if len(q) != 2401 or q[0] != 0.0 or not np.all(np.diff(q) > 0.0):
            raise ValueError(f"incomplete or non-monotone AFH q grid for Xe-{A}")
        if np.any(R < 0.0) or not np.all(np.isfinite(R)):
            raise ValueError(f"invalid AFH response values for Xe-{A}")
        if not math.isclose(float(R[0]), A*A, rel_tol=0.0, abs_tol=1e-9*A*A):
            raise ValueError(f"R_A(0) != A^2 for Xe-{A}")
        interpolators[A] = PchipInterpolator(q, R, extrapolate=False)
    metadata_path = path.parent/"metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return interpolators, metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response-grid", type=Path, required=True)
    parser.add_argument("--isotope-weights", type=Path,
                        default=HERE/"input"/"natural_xenon_isotope_weights.csv")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mass-scheme", choices=("nist_nuclear", "ame2020_nuclear"),
                        default="ame2020_nuclear")
    parser.add_argument("--response-q-convention", choices=("exact_spatial", "nr_approx"),
                        default="exact_spatial")
    parser.add_argument("--mchi-GeV", type=float, default=1000.0)
    parser.add_argument("--mV-GeV", type=float, default=10.0)
    parser.add_argument("--coupling-product-squared", type=float, default=1e-8)
    parser.add_argument("--g2", type=float, default=1.0)
    parser.add_argument("--rho-GeV-cm3", type=float, default=0.3)
    parser.add_argument("--nv", type=int, default=32)
    parser.add_argument("--nw", type=int, default=8)
    parser.add_argument("--nz", type=int, default=8)
    parser.add_argument("--nphi", type=int, default=4)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    response, response_metadata = load_full_response_grid(args.response_grid)
    isotope_rows = read_csv(args.isotope_weights)
    available = [
        row for row in isotope_rows
        if row["AFH_default_density_available"].lower() == "true"
    ]
    abundance = {
        int(row["A"]): float(row["natural_atom_fraction"])
        for row in available
    }
    missing = sorted(set(abundance) - set(response))
    if missing:
        raise ValueError(f"full AFH response grid missing isotopes {missing}")
    extra = sorted(set(response) - set(abundance))
    if extra:
        raise ValueError(f"unexpected isotope response grids {extra}")

    mean_atomic_weight = sum(
        float(row["atomic_mass_u"])*float(row["natural_atom_fraction"])
        for row in isotope_rows
    )
    nuclear_mass = {
        A: isotope_mass_GeV(A, args.mass_scheme)
        for A in abundance
    }

    rate_factor = (
        args.rho_GeV_cm3/args.mchi_GeV
    )*C_CM_S*(AVOGADRO*1000.0/mean_atomic_weight)*GEV2_TO_CM2*1e-6*86400.0

    speed_nodes, speed_weights = leggauss(args.nv)
    isotope_results = []
    total_results = []
    for benchmark, er_keV in CASES:
        ms, delta_m = BENCHMARKS[benchmark]
        ER = er_keV*1e-6
        for halo in ("shm_cutoff", "mb_untruncated"):
            vmax = 776.0 if halo == "shm_cutoff" else 1600.0
            pdf = selected.shm_truncated_pdf if halo == "shm_cutoff" else selected.mb_untruncated_pdf
            partials = []
            for A, fraction in abundance.items():
                mA = nuclear_mass[A]
                q_exact = selected.q_kinematic_exact(mA, ER)
                q_NR = selected.q_response_nr_approx(mA, ER)
                q_response = q_exact if args.response_q_convention == "exact_spatial" else q_NR
                interpolator = response[A]
                if q_response < 0.0 or q_response > 0.6:
                    raise ValueError(
                        f"q={q_response:.12g} GeV outside AFH grid for Xe-{A}, ER={er_keV} keV"
                    )
                RA = float(interpolator(q_response))
                if not math.isfinite(RA) or RA < 0.0:
                    raise ArithmeticError(f"invalid interpolated R_A for Xe-{A}, q={q_response}")

                vmin = selected.vmin_three_body_km_s(args.mchi_GeV, ms, mA, ER)
                integral = 0.0
                if vmin < vmax:
                    vs = 0.5*(vmax+vmin)+0.5*(vmax-vmin)*speed_nodes
                    ws = 0.5*(vmax-vmin)*speed_weights
                    for v, w in zip(vs, ws):
                        fv = pdf(float(v))
                        if fv == 0.0:
                            continue
                        beta = float(v)/C_KM_S
                        pchi = args.mchi_GeV*beta/math.sqrt(1.0-beta*beta)
                        I6 = eq6_kernel.reduced_kernel(
                            args.mchi_GeV, ms, delta_m, mA, ER, float(v),
                            nw=args.nw, nz=args.nz, nphi=args.nphi,
                            width_scheme="pole", g2=args.g2
                        )
                        prefactor = mA*args.coupling_product_squared*RA*I6/(
                            256.0*math.pi**3*pchi**2
                        )
                        integral += float(w)*fv*beta*prefactor

                denominator = (args.mV_GeV**2+2.0*mA*ER)**2
                contribution = rate_factor*fraction*integral/denominator
                partial = {
                    "benchmark": benchmark,
                    "ER_keV": er_keV,
                    "halo_model": halo,
                    "mass_scheme": args.mass_scheme,
                    "response_q_convention": args.response_q_convention,
                    "A": A,
                    "abundance": fraction,
                    "mA_GeV": mA,
                    "q_response_GeV": q_response,
                    "q_exact_GeV": q_exact,
                    "q_NR_GeV": q_NR,
                    "R_A": RA,
                    "vmin_km_s": vmin,
                    "vmax_km_s": vmax,
                    "open": vmin < vmax,
                    "J_A_GeV": integral,
                    "rate_contribution_events_kg_day_keV": contribution,
                    "nv": args.nv,
                    "kernel_quadrature": f"{args.nw}x{args.nz}x{args.nphi}",
                    "width_scheme": "pole",
                    "g2": args.g2,
                }
                partials.append(partial)
            total = sum(row["rate_contribution_events_kg_day_keV"] for row in partials)
            open_isotopes = [row["A"] for row in partials if row["open"]]
            open_fraction = sum(row["abundance"] for row in partials if row["open"])
            for row in partials:
                row["natural_rate_events_kg_day_keV"] = total
            isotope_results.extend(partials)
            total_results.append({
                "benchmark": benchmark,
                "ER_keV": er_keV,
                "halo_model": halo,
                "mass_scheme": args.mass_scheme,
                "response_q_convention": args.response_q_convention,
                "rate_events_kg_day_keV": total,
                "open_isotopes": ";".join(map(str, open_isotopes)),
                "open_abundance_fraction": open_fraction,
                "available_abundance_fraction": sum(abundance.values()),
            })
            print(
                f"{benchmark:18s} ER={er_keV:6.1f} {halo:14s} "
                f"rate={total:.8e} open={';'.join(map(str,open_isotopes)) or 'none'}",
                flush=True,
            )

    write_csv(args.out_dir/"isotope_halo_contributions.csv", isotope_results)
    write_csv(args.out_dir/"natural_xenon_halo_rates.csv", total_results)
    metadata = {
        "calculation": "full AFH-default natural-xenon isotope-specific halo-folded three-body rate",
        "mass_scheme": args.mass_scheme,
        "mass_scheme_formula": {
            "nist_nuclear": "NIST neutral-atom mass - 54 electron masses; historical CODATA-2018; no electron binding correction",
            "ame2020_nuclear": "unrounded AME2020 neutral-atom mass - 54 electron masses + B_e(54); CODATA-2022",
        }[args.mass_scheme],
        "response_q_convention": args.response_q_convention,
        "response_q_formula": (
            "sqrt(2*m_A*E_R+E_R^2), exact spatial momentum transfer"
            if args.response_q_convention == "exact_spatial"
            else "sqrt(2*m_A*E_R), NR approximation; exact q retained in kinematics"
        ),
        "kinematic_q_formula": "sqrt(2*m_A*E_R+E_R^2)",
        "response_grid": str(args.response_grid),
        "response_grid_sha256": sha256(args.response_grid),
        "response_grid_source_metadata": response_metadata,
        "available_isotopes": list(abundance),
        "available_natural_atom_fraction": sum(abundance.values()),
        "omitted_isotopes": [124, 126],
        "omitted_natural_atom_fraction": 1.0-sum(abundance.values()),
        "abundance_convention": "NIST natural atom fractions; no renormalization",
        "mean_atomic_weight_g_mol": mean_atomic_weight,
        "mchi1_GeV": args.mchi_GeV,
        "mV_GeV": args.mV_GeV,
        "coupling_product_squared": args.coupling_product_squared,
        "g2": args.g2,
        "rho_chi_GeV_cm3": args.rho_GeV_cm3,
        "benchmarks": {
            "red_ms200_dm1": {"ms_keV": 200.0, "Delta_m_MeV": 1.0},
            "green_ms300_dm1": {"ms_keV": 300.0, "Delta_m_MeV": 1.0},
            "black_ms360_dm1": {"ms_keV": 360.0, "Delta_m_MeV": 1.0},
            "blue_ms300_dm10": {"ms_keV": 300.0, "Delta_m_MeV": 10.0},
        },
        "halo": {
            "baseline": {"model": "truncated SHM", "v0_km_s": 220.0, "vE_km_s": 232.0,
                         "vesc_km_s": 544.0, "vmax_lab_km_s": 776.0},
            "diagnostic": {"model": "untruncated boosted Maxwell-Boltzmann", "vmax_km_s": 1600.0},
        },
        "quadrature": {
            "speed_nodes": args.nv,
            "kernel": [args.nw, args.nz, args.nphi],
        },
        "width_scheme": "pole chi2 -> chi1 s; conditional Dirac/real-scalar/pure-scalar/single-channel",
        "rate_units": "events/(kg day keV)",
        "detector_response": "not applied",
        "not_included": [
            "Xe-124 and Xe-126: no AFH v6.0 default-density response matrices in the available target set",
            "detector efficiency, resolution, exposure, cuts, backgrounds, and likelihood",
            "native Mathematica re-execution",
        ],
    }
    (args.out_dir/"metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
