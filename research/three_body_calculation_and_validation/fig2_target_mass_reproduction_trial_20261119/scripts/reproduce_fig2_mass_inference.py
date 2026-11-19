#!/usr/bin/env python3
"""Reproduce the normalized fixed-speed phase-space shape of source-paper Fig. 2."""
import csv, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
MS = 300.0
MCHI = 1000.0
V_KMS = 780.0
V = V_KMS / 299792.458
META = json.loads((ROOT / "inputs/fig2_digitization_metadata.json").read_text())

def trace():
    with (ROOT / "inputs/fig2_red_curve_digitized.csv").open() as f:
        rows = list(csv.DictReader(f))
    e = np.array([float(r["ER_keV"]) for r in rows])
    y = np.array([float(r["normalized_dsigma_dER_1e-3_per_keV"]) for r in rows])
    order = np.argsort(e)
    return e[order], y[order]

def integ(y, x):
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))

def phase_I(d):
    out = np.zeros_like(d)
    ok = d > 0
    x = d[ok]
    root = np.sqrt(x * (x + 2 * MS))
    out[ok] = 0.5 * ((MS + x) * root - MS**2 * np.log((MS + x + root) / MS))
    return out

def spectrum(mt_GeV, n=7001):
    mt, mc = mt_GeV * 1e6, MCHI * 1e6
    mu = mc * mt / (mc + mt)
    disc = V**2 - 2 * MS / mu
    if disc < 0:
        raise ValueError("No phase space at this speed.")
    root = math.sqrt(disc)
    lo = mu**2 / (2 * mt) * (V - root)**2
    hi = mu**2 / (2 * mt) * (V + root)**2
    peak = mu**2 * V**2 / (2 * mt)
    e = np.linspace(0, 700, n)
    q = np.sqrt(2 * mt * e)
    d = V * q - q**2 / (2 * mu) - MS
    raw = phase_I(d)
    y23 = 1e3 * raw / integ(raw, e)
    y22 = np.where((e >= lo) & (e <= hi), 1e3 / (hi - lo), 0.0)
    return e, y22, y23, lo, hi, peak

def invert(lo, hi):
    s, p = lo + hi, math.sqrt(lo * hi)
    mu = MS * (1 + s / (2 * p)) / V**2
    mt = mu * MS / p
    mc = mu * mt / (mt - mu)
    return mu, mt, mc

def main():
    ed, yd = trace()
    lo0, hi0 = META["red_curve_endpoints_keV"]
    mask = (ed > 120) & (ed < 645) & (yd > 0.05)

    def objective(mt):
        e, _, y, *_ = spectrum(float(mt))
        return float(np.mean((np.interp(ed[mask], e, y) - yd[mask])**2))

    fit = minimize_scalar(objective, bounds=(118, 124), method="bounded",
                          options={"xatol": 1e-10})
    mu, mt, mc = invert(lo0, hi0)
    masses = {
        "endpoint_inversion": mt / 1e6,
        "red_shape_fit": float(fit.x),
        "A130_u_approximation": 130.0 * 0.93149410242,
        "mT_122_GeV": 122.0,
    }
    cases = {}
    for label, mass in masses.items():
        _, _, _, lo, hi, peak = spectrum(mass)
        cases[label] = {
            "mT_GeV": float(mass), "ER_minus_keV": lo, "ER_plus_keV": hi,
            "ER_peak_keV": peak,
            "normalized_2to2_plateau_1e_3_per_keV": 1e3 / (hi - lo),
        }

    result = {
        "status": "exploratory_reproduction_diagnostic",
        "source": {"file": META["source_file"], "sha256": META["source_sha256"],
                   "figure": "Fig. 2", "pdf_page": 3,
                   "endpoint_equation": "Eq. (4), PDF p. 2",
                   "phase_space_kernel": "Eq. (6), PDF p. 2"},
        "fixed_inputs": {"mchi_GeV": MCHI, "v_km_per_s": V_KMS, "ms_keV": MS,
                         "delta_iDM_keV": MS, "RA_included": False,
                         "nuclear_response_included": False},
        "digitized_figure": {
            "red_points": len(ed), "red_endpoint_minus_keV": lo0,
            "red_endpoint_plus_keV": hi0,
            "red_peak_ER_keV": META["red_curve_peak"]["ER_keV"],
            "red_peak_height_1e_3_per_keV": META["red_curve_peak"]["height_1e_3_per_keV"],
            "blue_plateau_1e_3_per_keV": META["blue_curve"]["plateau_1e_3_per_keV"],
        },
        "endpoint_inversion": {"mu_GeV": mu / 1e6, "mT_GeV": mt / 1e6,
                               "implied_mchi_GeV": mc / 1e9},
        "red_shape_fit": {"mT_GeV": float(fit.x),
                          "mean_squared_residual": float(fit.fun),
                          "fit_domain_keV": [120, 645],
                          "fit_points": int(mask.sum())},
        "comparisons": cases,
        "interpretation": [
            "Endpoint inversion and red-shape fitting independently indicate an effective target mass near 121.04 GeV.",
            "130u = 121.094233 GeV is numerically consistent with the plotted endpoints at figure-reading precision; the paper does not explicitly state that Fig. 2 uses A=130.",
            "Eq. (107), PDF p. 17, explicitly uses 122 GeV at 770 km/s for a separate illustration; it does not establish the Fig. 2 target mass.",
            "This is a normalized fixed-speed phase-space reproduction without R_A(E_R), nucleon form factors, AFH responses, isotope sum, halo average, or detector response. The adopted B baseline is unchanged."
        ],
    }
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results/fig2_target_mass_inference.json").write_text(json.dumps(result, indent=2))

    e, _, y23, elo, ehi, _ = spectrum(mt / 1e6, 1401)
    e122, _, y122, *_ = spectrum(122.0, 1401)
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    ax.scatter(ed[::3], yd[::3], color="tab:red", s=8, alpha=0.65,
               label="Paper Fig. 2 red trace (digitized)")
    ax.plot(e, y23, color="black", lw=1.6,
            label=fr"Recomputed $2\to3$, $m_T={mt/1e6:.3f}$ GeV")
    ax.plot(e122, y122, color="0.45", ls="--", lw=1.1,
            label=r"$2\to3$ with $m_T=122$ GeV")
    blue = META["blue_curve"]
    ax.hlines(blue["plateau_1e_3_per_keV"], *blue["ER_interval_keV"],
              color="tab:blue", ls="--", label="Paper Fig. 2 blue plateau")
    ax.hlines(1e3 / (ehi - elo), elo, ehi, color="tab:blue", ls=":",
              label=r"Recomputed normalized $2\to2$")
    ax.set(xlim=(0, 700), ylim=(0, 5), xlabel=r"$E_R$ [keV]",
           ylabel=r"$(1/\sigma)\,d\sigma/dE_R$ [$10^{-3}\,\mathrm{keV}^{-1}$]",
           title=r"Fig. 2 reproduction: $v=780$ km/s, $m_s=\delta=300$ keV")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    (ROOT / "figures").mkdir(exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    fig.savefig(ROOT / "figures/fig2_target_mass_inference.svg", format="svg")
    plt.close(fig)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
