#!/usr/bin/env python3
"""Halo-folded full three-body L00 vs I(D) comparison for seven AFH Xe isotopes.

The calculation uses the repository's canonical Eq. (6) full kernel and AFH
v6.0 default-density matrices. Xe-124 and Xe-126 are excluded from the AFH
central result because AFH v6.0 has no default density matrices for them.
Natural abundances are not renormalized.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HALO_DIR = ROOT / "research" / "afh_default_density_natural_xenon_halo"
CALC_DIR = ROOT / "research" / "three_body_calculation_and_validation"
sys.path.insert(0, str(HALO_DIR))
sys.path.insert(0, str(CALC_DIR))

import eq6_kernel as eq6
from generate_afh_default_xenon_response_grid import (
    ISOTOPES, compute_isotope_grid, parse_density_matrix,
    parse_isotopic_spins, read_natural_xenon_masses,
)

C_KM_S = 299792.458
V0 = 220.0
VE = 232.0
VESC = 544.0
VMAX = VESC + VE
SHM_KINK = VESC - VE
ISOTOPE_WEIGHTS = HALO_DIR / "input" / "natural_xenon_isotope_weights.csv"
AFH_PACKAGE = ROOT / "v6" / "dmformfactor-V6.m"


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
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def shm_speed_pdf(v: float) -> float:
    """Normalized lab-frame truncated Standard Halo Model speed PDF."""
    if v < 0.0 or v > VMAX:
        return 0.0
    z = VESC / V0
    norm = math.erf(z) - 2.0 * z * math.exp(-z*z) / math.sqrt(math.pi)
    if v < SHM_KINK:
        bracket = math.exp(-((v-VE)/V0)**2) - math.exp(-((v+VE)/V0)**2)
    else:
        bracket = math.exp(-((v-VE)/V0)**2) - math.exp(-z*z)
    return v * bracket / (math.sqrt(math.pi) * V0 * VE * norm)


def speed_quadrature(vmin: float, vmax: float, order: int):
    """Split at the SHM analytic kink and apply GL quadrature per segment."""
    if vmax <= vmin:
        return []
    bounds = [vmin]
    if vmin < SHM_KINK < vmax:
        bounds.append(SHM_KINK)
    bounds.append(vmax)
    x, w = leggauss(order)
    out = []
    for lo, hi in zip(bounds[:-1], bounds[1:]):
        vv = 0.5*(hi+lo) + 0.5*(hi-lo)*x
        ww = 0.5*(hi-lo)*w
        out.extend(zip(vv, ww))
    return out


def i_of_d(D: float, ms: float) -> float:
    if D <= 0.0:
        return 0.0
    root = math.sqrt(D*(D+2.0*ms))
    return 0.5*((D+ms)*root - ms*ms*math.acosh(1.0+D/ms))


def d_nr(ER: float, speed_kms: float, mchi: float, ms: float, mA: float) -> float:
    qnr = math.sqrt(2.0*mA*ER)
    mu = mchi*mA/(mchi+mA)
    beta = speed_kms/C_KM_S
    return beta*qnr - qnr*qnr/(2.0*mu) - ms


def exact_speed_threshold(ER: float, mchi: float, ms: float, mA: float) -> float:
    """Solve Wmax^2(v)=Wmin^2 by bisection; return km/s."""
    wmin2 = (mchi+ms)**2
    lo, hi = 0.0, VMAX
    if eq6.limits(mchi, ms, mA, ER, hi)[1] <= wmin2:
        return math.inf
    for _ in range(64):
        mid = 0.5*(lo+hi)
        if eq6.limits(mchi, ms, mA, ER, mid)[1] > wmin2:
            hi = mid
        else:
            lo = mid
    return hi


def nr_speed_threshold(ER: float, mchi: float, ms: float, mA: float) -> float:
    qnr = math.sqrt(2.0*mA*ER)
    mu = mchi*mA/(mchi+mA)
    return C_KM_S*(qnr/(2.0*mu) + ms/qnr)


def threshold_l00(ER: float, speed_kms: float, mchi: float, ms: float,
                  delta_m: float, mA: float) -> float:
    wmin2 = (mchi+ms)**2
    point = eq6.build_point(mchi, ms, mA, ER, speed_kms, wmin2, 0.0, 0.0)
    return eq6.spin_trace(point, mchi, mchi+delta_m, width=0.0)["total"]


def velocity_weighted_kernels(ER: float, mA: float, mchi: float, ms: float,
                              delta_m: float, speed_order: int,
                              nw: int, nz: int, nphi: int) -> tuple[float, float, float, float]:
    """Return halo integrals of full and I(D_NR) kernels and threshold diagnostics.

    The common rate factors beta/p_chi^2 are included. Couplings, mediator
    denominator and nuclear response are applied outside this function.
    """
    vmin_full = exact_speed_threshold(ER, mchi, ms, mA)
    vmin_nr = nr_speed_threshold(ER, mchi, ms, mA)
    full = approx = 0.0
    amp_num = amp_den = 0.0
    if math.isfinite(vmin_full) and vmin_full < VMAX:
        for v, wv in speed_quadrature(vmin_full, VMAX, speed_order):
            beta = v/C_KM_S
            pchi = mchi*beta/math.sqrt(1.0-beta*beta)
            common = wv*shm_speed_pdf(float(v))*beta/(pchi*pchi)
            if common == 0.0:
                continue
            Jfull = eq6.reduced_kernel(
                mchi, ms, delta_m, mA, ER, float(v),
                nw=nw, nz=nz, nphi=nphi, width_scheme="zero"
            )
            full += common*Jfull
            L0 = threshold_l00(ER, float(v), mchi, ms, delta_m, mA)
            # Compare both approximations on the same full-kinematic speed
            # domain; I(D_NR)=0 whenever its own NR threshold is not open.
            Dnr = d_nr(ER, float(v), mchi, ms, mA)
            Japprox = 8.0*L0*i_of_d(Dnr, ms)
            approx += common*Japprox
            Jphase = 8.0*L0*i_of_d(
                math.sqrt(max(0.0, eq6.limits(mchi,ms,mA,ER,float(v))[1]))
                -(mchi+ms), ms
            )
            amp_num += common*Jfull
            amp_den += common*Jphase
    # The NR approximation can open slightly below the exact threshold due
    # to recoil-energy convention differences. Integrate that sliver too.
    if vmin_nr < min(vmin_full, VMAX):
        for v, wv in speed_quadrature(vmin_nr, min(vmin_full, VMAX), speed_order):
            beta = v/C_KM_S
            pchi = mchi*beta/math.sqrt(1.0-beta*beta)
            common = wv*shm_speed_pdf(float(v))*beta/(pchi*pchi)
            if common == 0.0:
                continue
            L0 = threshold_l00(ER, float(v), mchi, ms, delta_m, mA)
            approx += common*8.0*L0*i_of_d(d_nr(ER,float(v),mchi,ms,mA),ms)
    return full, approx, amp_num/amp_den-1.0 if amp_den else math.nan, vmin_full


def load_afh_responses(energies_keV: list[float], masses: dict[int, dict]):
    source_text = AFH_PACKAGE.read_text(encoding="utf-8")
    spins = parse_isotopic_spins(source_text)
    response = {}
    summaries = {}
    for A in ISOTOPES:
        q_values = [
            math.sqrt(2.0*masses[A]["nuclear_mass_GeV"]*E*1e-6+(E*1e-6)**2)
            for E in energies_keV
        ]
        q_grid = np.asarray([0.0, *q_values], dtype=float)
        matrix = parse_density_matrix(source_text, A)
        records, summary = compute_isotope_grid(
            A=A, rows=matrix, J_A=spins[A],
            mass_GeV=masses[A]["nuclear_mass_GeV"], q_grid=q_grid
        )
        summaries[A] = summary
        for E, row in zip(energies_keV, records[1:]):
            response[(A,E)] = float(row["R_equal_pn_normalized"])
    return response, summaries


def run(args):
    mchi = args.mchi_GeV
    ms = args.ms_keV*1e-6
    delta_m = args.delta_m_MeV*1e-3
    mV = args.mV_GeV
    energies = sorted(set(
        [float(x) for x in np.arange(args.er_min_keV, args.er_max_keV+0.5*args.er_step_keV, args.er_step_keV)]
        + [248.0, 267.0]
    ))
    isotope_rows = read_csv(ISOTOPE_WEIGHTS)
    all_masses = read_natural_xenon_masses(ISOTOPE_WEIGHTS)
    afhs = [r for r in isotope_rows if r["AFH_default_density_available"].lower()=="true"]
    abundance = {int(r["A"]): float(r["natural_atom_fraction"]) for r in afhs}
    coverage = sum(abundance.values())
    response, response_summaries = load_afh_responses(energies, all_masses)

    isotope_results = []
    total_results = []
    for E_keV in energies:
        ER = E_keV*1e-6
        total_full = total_approx = 0.0
        for A in ISOTOPES:
            mA = all_masses[A]["nuclear_mass_GeV"]
            Jfull, Japprox, amp_corr, vmin = velocity_weighted_kernels(
                ER, mA, mchi, ms, delta_m, args.speed_order,
                args.nw, args.nz, args.nphi
            )
            RA = response[(A,E_keV)]
            abundance_A = abundance[A]
            # Common isotope-dependent factors from Eq. (6). Absolute global
            # constants cancel in the ratio but the mediator and AFH factors
            # must remain inside the isotope sum.
            mediator = (mV*mV+2.0*mA*ER)**2
            isotope_factor = abundance_A*mA*RA/mediator
            full_contribution = isotope_factor*Jfull
            approx_contribution = isotope_factor*Japprox
            total_full += full_contribution
            total_approx += approx_contribution
            isotope_results.append({
                "ER_keV": E_keV, "A": A,
                "natural_atom_fraction": abundance_A,
                "mA_GeV": mA, "R_A_AFH_direct_exact_q": RA,
                "vmin_exact_km_s": vmin,
                "halo_kernel_full": Jfull,
                "halo_kernel_I_D": Japprox,
                "full_contribution_relative_units": full_contribution,
                "I_D_contribution_relative_units": approx_contribution,
                "isotope_relative_error_pct": (Jfull/Japprox-1.0)*100.0 if Japprox else "",
                "amplitude_correction_after_halo_pct": amp_corr*100.0 if math.isfinite(amp_corr) else "",
            })
        total_results.append({
            "ER_keV": E_keV,
            "natural_xenon_full_relative_rate": total_full,
            "natural_xenon_I_D_relative_rate": total_approx,
            "relative_error_pct": (total_full/total_approx-1.0)*100.0 if total_approx else "",
        })

    out = args.outdir
    write_csv(out/"seven_isotope_halo_comparison.csv", isotope_results)
    write_csv(out/"natural_xenon_halo_comparison.csv", total_results)
    metadata = {
        "status": "COMPUTED",
        "calculation": "Halo-folded full three-body L00 vs I(D_NR), AFH seven-isotope natural xenon",
        "benchmark": {
            "mchi1_GeV": mchi, "ms_keV": args.ms_keV,
            "Delta_m_MeV": args.delta_m_MeV, "mV_GeV": mV,
            "v0_km_s": V0, "vE_km_s": VE, "vesc_km_s": VESC,
            "speed_order_per_smooth_segment": args.speed_order,
            "internal_quadrature_nw_nz_nphi": [args.nw,args.nz,args.nphi],
        },
        "isotopes": list(ISOTOPES),
        "natural_atom_fraction_AFH_coverage": coverage,
        "abundances_not_renormalized": True,
        "missing_AFH_default_density_isotopes": [124,126],
        "AFH_source_sha256": sha256(AFH_PACKAGE),
        "outputs": ["seven_isotope_halo_comparison.csv","natural_xenon_halo_comparison.csv"],
        "scope": "Rate ratios only; detector response, exposure, efficiency and likelihood are not applied.",
    }
    (out/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status": metadata["status"],
        "isotopes": list(ISOTOPES),
        "abundance_coverage": coverage,
        "recoil_points": len(energies),
        "max_abs_natural_rate_difference_pct": max(abs(float(r["relative_error_pct"])) for r in total_results if r["relative_error_pct"]!=""),
        "output_dir": str(out),
    },indent=2))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mchi-GeV",type=float,default=1000.0)
    p.add_argument("--ms-keV",type=float,default=300.0)
    p.add_argument("--delta-m-MeV",type=float,default=10.0)
    p.add_argument("--mV-GeV",type=float,default=5.0)
    p.add_argument("--er-min-keV",type=float,default=180.0)
    p.add_argument("--er-max-keV",type=float,default=320.0)
    p.add_argument("--er-step-keV",type=float,default=10.0)
    p.add_argument("--speed-order",type=int,default=32)
    p.add_argument("--nw",type=int,default=8)
    p.add_argument("--nz",type=int,default=8)
    p.add_argument("--nphi",type=int,default=4)
    p.add_argument("--outdir",type=Path,default=HERE/"halo_seven_isotope_results")
    args=p.parse_args()
    run(args)


if __name__=="__main__":
    main()
