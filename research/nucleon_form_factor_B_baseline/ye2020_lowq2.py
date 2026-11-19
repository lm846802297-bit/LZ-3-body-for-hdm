#!/usr/bin/env python3
"""Ye et al. low-Q2 electromagnetic proton/neutron form factors.

The central values and covariance matrix are pinned from the Ye et al.
supplemental material as redistributed in GENIE-MC/Generator.  The four
unconstrained coefficients for each Sachs form factor are completed with
G(0) normalization and the four Q^4 asymptotic sum rules, matching GENIE's
Q4limit implementation.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data" / "ye2020"
PARAMS = json.loads((DATA / "parameters.json").read_text(encoding="utf-8"))
COV_FULL = np.loadtxt(DATA / "ELZExpFF.dat", comments="%")

MP_GEV = 0.9382720813
MN_GEV = 0.9395654133
MAVG_GEV = 0.5 * (MP_GEV + MN_GEV)
HBARC_GEV_FM = 0.1973269804
FM2_TO_GEVM2 = 1.0 / HBARC_GEV_FM**2

ZCFG = PARAMS["z_expansion"]
TCUT = float(ZCFG["t_cut_GeV2"])
T0 = float(ZCFG["t0_GeV2"])
Z0 = (math.sqrt(TCUT) - math.sqrt(TCUT - T0)) / (
    math.sqrt(TCUT) + math.sqrt(TCUT - T0)
)
G0 = ZCFG["normalizations"]
FREE = PARAMS["free_coefficients"]

AP = np.asarray(FREE["A_P"], dtype=float)
BP = np.asarray(FREE["B_P_tilde"], dtype=float)
AN = np.asarray(FREE["A_N"], dtype=float)
BN = np.asarray(FREE["B_N_tilde"], dtype=float)

COV_P = COV_FULL[:8, :8]
COV_NE = COV_FULL[8:12, 8:12]
COV_NM = COV_FULL[12:16, 12:16]


def z_of_q2(q2_GeV2):
    q2 = np.asarray(q2_GeV2, dtype=float)
    if np.any(q2 < 0.0):
        raise ValueError("spacelike Q^2 must be non-negative")
    a = np.sqrt(TCUT + q2)
    b = math.sqrt(TCUT - T0)
    return (a - b) / (a + b)


def _constraint_matrix() -> np.ndarray:
    """Map unknown coefficients (c0,c5,c6,c7,c8) to five constraints."""
    unknown = (0, 5, 6, 7, 8)
    rows = []
    # G(0) normalization at z=z(0).
    rows.append([Z0**k for k in unknown])
    # Q^4 asymptotic constraints: derivatives n=0,1,2,3 vanish at z=1.
    for n in range(4):
        rows.append([
            math.factorial(k) / math.factorial(k-n) if k >= n else 0.0
            for k in unknown
        ])
    return np.asarray(rows, dtype=float)


CONSTRAINT_MATRIX = _constraint_matrix()
UNKNOWN_INDICES = np.asarray([0, 5, 6, 7, 8], dtype=int)
KNOWN_INDICES = np.asarray([1, 2, 3, 4], dtype=int)


def complete_coefficients(free_coefficients, normalization: float) -> np.ndarray:
    """Complete c_1..c_4 into c_0..c_8 using exact linear constraints."""
    free = np.asarray(free_coefficients, dtype=float)
    if free.shape[-1] != 4:
        raise ValueError("expected four free z-expansion coefficients")
    lead = free.shape[:-1]
    flat = free.reshape((-1, 4))
    rhs = np.empty((flat.shape[0], 5), dtype=float)
    rhs[:, 0] = normalization - flat @ (Z0 ** KNOWN_INDICES)
    for n in range(4):
        factors = np.asarray([
            math.factorial(k) / math.factorial(k-n) if k >= n else 0.0
            for k in KNOWN_INDICES
        ])
        rhs[:, n+1] = -(flat @ factors)
    solved = np.linalg.solve(CONSTRAINT_MATRIX, rhs.T).T
    out = np.zeros((flat.shape[0], 9), dtype=float)
    out[:, KNOWN_INDICES] = flat
    out[:, UNKNOWN_INDICES] = solved
    return out.reshape(lead + (9,))


COEFF_GEP = complete_coefficients(AP, float(G0["GEp_0"]))
COEFF_GMP = complete_coefficients(BP, float(G0["GMp_0"]))
COEFF_GEN = complete_coefficients(AN, float(G0["GEn_0"]))
COEFF_GMN = complete_coefficients(BN, float(G0["GMn_0"]))


def _poly(coefficients: np.ndarray, z):
    powers = np.asarray(z)[..., None] ** np.arange(9, dtype=float)
    return np.sum(powers * coefficients, axis=-1)


def sachs_form_factors(q2_GeV2) -> dict[str, np.ndarray]:
    """Return G_E and G_M for p and n at spacelike Q^2."""
    z = z_of_q2(q2_GeV2)
    return {
        "GEp": _poly(COEFF_GEP, z),
        "GMp": _poly(COEFF_GMP, z),
        "GEn": _poly(COEFF_GEN, z),
        "GMn": _poly(COEFF_GMN, z),
    }


def dirac_pauli_form_factors(q2_GeV2) -> dict[str, np.ndarray]:
    """Convert Sachs to Dirac-Pauli using the physical p and n masses."""
    q2 = np.asarray(q2_GeV2, dtype=float)
    sachs = sachs_form_factors(q2)
    taup = q2 / (4.0 * MP_GEV**2)
    taun = q2 / (4.0 * MN_GEV**2)
    out = {}
    for nucleon, tau in (("p", taup), ("n", taun)):
        ge = sachs[f"GE{nucleon}"]
        gm = sachs[f"GM{nucleon}"]
        out[f"F1{nucleon}"] = (ge + tau*gm) / (1.0+tau)
        out[f"F2{nucleon}"] = (gm-ge) / (1.0+tau)
    return out


def _strange_sachs(q2_GeV2, model: str) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return unit-current strange (GE,GM), with explicit current convention."""
    q2 = np.asarray(q2_GeV2, dtype=float)
    if model == "sufian2017_unit_current":
        # Sufian et al. calculate <N| s-bar gamma_mu s |N>; no e_s factor
        # multiplies the quoted unit-current form factors.
        mu_s = -0.064
        rE2_fm2 = -0.0043
        ge = -(rE2_fm2 * FM2_TO_GEVM2) * q2 / 6.0
        gm = np.full_like(q2, mu_s, dtype=float)
        return ge, gm, {
            "model": model,
            "current": "unit strange current sbar gamma_mu s",
            "mu_s_unit": mu_s,
            "rE2_unit_fm2": rE2_fm2,
            "GM_s_Q2_dependence": "constant frozen-moment benchmark; magnetic radius not supplied by this fit",
        }

    if model == "alexandrou2020_charge_weighted_converted":
        # Alexandrou et al. explicitly use j_s^mu=e_s*sbar gamma^mu s,
        # e_s=-1/3, and state that this charge factor is included in G_E,M^s.
        # Divide the reported charge-weighted Sachs functions by e_s before
        # using them as matrix elements of the unit strange current.
        e_s = -1.0/3.0
        mu_weighted = -0.017
        rE2_weighted_fm2 = -0.0048
        rM2_weighted_fm2 = -0.015
        ge_weighted = -(rE2_weighted_fm2 * FM2_TO_GEVM2) * q2 / 6.0
        gm_weighted = mu_weighted - (rM2_weighted_fm2 * FM2_TO_GEVM2) * q2 / 6.0
        return ge_weighted/e_s, gm_weighted/e_s, {
            "model": model,
            "source_current": "e_s*sbar gamma_mu s with e_s=-1/3",
            "conversion_to_unit_current": "divide G_E^s and G_M^s by e_s=-1/3",
            "mu_s_charge_weighted": mu_weighted,
            "rE2_charge_weighted_fm2": rE2_weighted_fm2,
            "rM2_charge_weighted_fm2": rM2_weighted_fm2,
            "GM_s_Q2_dependence": "linear low-Q2 expansion from the published magnetic radius",
        }

    raise ValueError(f"unknown strange form-factor model: {model}")


def flavor_sum_form_factors(q2_GeV2, strange_model: str = "sufian2017_unit_current"):
    """Return F1,2^(u+d+s) for universal unit quark coupling.

    Isospin reconstruction:
      F_i^(uds,N) = 3 [ F_i^(EM,p) + F_i^(EM,n) + F_i^(s,unit) ].
    The strange input must be for the unit current sbar gamma_mu s.
    """
    q2 = np.asarray(q2_GeV2, dtype=float)
    em = dirac_pauli_form_factors(q2)
    ge_s, gm_s, strange_meta = _strange_sachs(q2, strange_model)
    tau_s = q2/(4.0*MAVG_GEV**2)
    f1s = (ge_s + tau_s*gm_s)/(1.0+tau_s)
    f2s = (gm_s-ge_s)/(1.0+tau_s)
    f1uds = 3.0*(em["F1p"]+em["F1n"]+f1s)
    f2uds = 3.0*(em["F2p"]+em["F2n"]+f2s)
    return {
        "F1uds": f1uds,
        "F2uds": f2uds,
        "F1p_EM": em["F1p"],
        "F2p_EM": em["F2p"],
        "F1n_EM": em["F1n"],
        "F2n_EM": em["F2n"],
        "F1s_unit": f1s,
        "F2s_unit": f2s,
        "GE_s_unit": ge_s,
        "GM_s_unit": gm_s,
        "strange_metadata": strange_meta,
    }


def cM_and_factor(q2_GeV2, strange_model: str = "sufian2017_unit_current"):
    """Return c_M(t_N), F_M=c_M/3, and its rate multiplier |F_M|^2.

    t_N=-Q_A^2=-Q^2 and c_M=F1+t_N/(8 m_N^2)*(F1+2F2).
    """
    q2 = np.asarray(q2_GeV2, dtype=float)
    f = flavor_sum_form_factors(q2, strange_model)
    tN = -q2
    cM = f["F1uds"] + tN/(8.0*MAVG_GEV**2)*(f["F1uds"]+2.0*f["F2uds"])
    fm = cM/3.0
    return {
        **f,
        "Q2_GeV2": q2,
        "tN_GeV2": tN,
        "cM": cM,
        "F_M": fm,
        "rate_multiplier": fm*fm,
    }


def sample_cM_factors(q2_GeV2, n_draws: int = 5000, seed: int = 20261119,
                      strange_model: str = "sufian2017_unit_current"):
    """Monte-Carlo propagate Ye2020 free-coefficient covariance to F_M.

    Strange inputs are held at their scenario central values here; their
    separate lattice uncertainties are reported as a distinct model band.
    """
    if n_draws < 2:
        raise ValueError("n_draws must be at least 2")
    q2 = np.atleast_1d(np.asarray(q2_GeV2, dtype=float))
    rng = np.random.default_rng(seed)
    pmean = np.concatenate([AP, BP])
    pdraw = rng.multivariate_normal(pmean, COV_P, size=n_draws)
    nedraw = rng.multivariate_normal(AN, COV_NE, size=n_draws)
    nmdraw = rng.multivariate_normal(BN, COV_NM, size=n_draws)
    cg_ep = complete_coefficients(pdraw[:, :4], float(G0["GEp_0"]))
    cg_mp = complete_coefficients(pdraw[:, 4:], float(G0["GMp_0"]))
    cg_en = complete_coefficients(nedraw, float(G0["GEn_0"]))
    cg_mn = complete_coefficients(nmdraw, float(G0["GMn_0"]))
    z = z_of_q2(q2)
    powers = z[:, None] ** np.arange(9, dtype=float)[None, :]
    gep = cg_ep @ powers.T
    gmp = cg_mp @ powers.T
    gen = cg_en @ powers.T
    gmn = cg_mn @ powers.T
    taup = q2/(4.0*MP_GEV**2)
    taun = q2/(4.0*MN_GEV**2)
    f1p = (gep+taup[None,:]*gmp)/(1.0+taup[None,:])
    f2p = (gmp-gep)/(1.0+taup[None,:])
    f1n = (gen+taun[None,:]*gmn)/(1.0+taun[None,:])
    f2n = (gmn-gen)/(1.0+taun[None,:])
    ges, gms, _ = _strange_sachs(q2, strange_model)
    taus = q2/(4.0*MAVG_GEV**2)
    f1s = (ges+taus*gms)/(1.0+taus)
    f2s = (gms-ges)/(1.0+taus)
    f1uds = 3.0*(f1p+f1n+f1s[None,:])
    f2uds = 3.0*(f2p+f2n+f2s[None,:])
    cM = f1uds - q2[None,:]/(8.0*MAVG_GEV**2)*(f1uds+2.0*f2uds)
    fm = cM/3.0
    return {
        "F_M_median": np.median(fm, axis=0),
        "F_M_p16": np.percentile(fm, 16, axis=0),
        "F_M_p84": np.percentile(fm, 84, axis=0),
        "rate_multiplier_median": np.median(fm*fm, axis=0),
        "rate_multiplier_p16": np.percentile(fm*fm, 16, axis=0),
        "rate_multiplier_p84": np.percentile(fm*fm, 84, axis=0),
        "n_draws": n_draws,
        "seed": seed,
        "strange_model": strange_model,
    }


def covariance_diagnostics() -> dict:
    return {
        "proton_min_eigenvalue": float(np.linalg.eigvalsh(COV_P).min()),
        "neutron_GE_min_eigenvalue": float(np.linalg.eigvalsh(COV_NE).min()),
        "neutron_GM_min_eigenvalue": float(np.linalg.eigvalsh(COV_NM).min()),
        "proton_covariance_symmetric": bool(np.allclose(COV_P, COV_P.T, atol=1e-12)),
        "neutron_GE_covariance_symmetric": bool(np.allclose(COV_NE, COV_NE.T, atol=1e-12)),
        "neutron_GM_covariance_symmetric": bool(np.allclose(COV_NM, COV_NM.T, atol=1e-12)),
    }
