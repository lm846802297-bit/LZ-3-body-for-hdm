#!/usr/bin/env python3
"""Direct Eq.(6) cross sections for Xe-131: AFH default, GCN and JJ55.

The archived I6(E_R) grid is shared because the nuclear response factorizes
outside the three-body phase-space integral. This script recomputes the full
cross-section prefactor from R_A and I6; it does not compute event rates.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

A, Z, J_A = 131, 54, 1.5
M_A = A * 0.93149410242
M_CHI, M_V, G_PRODUCT_SQ, G2, SPEED = 1000.0, 10.0, 1.0e-8, 1.0, 800.0
C_KM_S = 299792.458
GEV3_TO_CM2_PER_KEV = 0.389379e-33
BENCHMARKS = {
    "red_ms200_dm1": {"m_s_keV": 200, "Delta_m_MeV": 1},
    "green_ms300_dm1": {"m_s_keV": 300, "Delta_m_MeV": 1},
    "black_ms360_dm1": {"m_s_keV": 360, "Delta_m_MeV": 1},
    "blue_ms300_dm10": {"m_s_keV": 300, "Delta_m_MeV": 10},
}

def build(base_csv: Path, afh_csv: Path) -> pd.DataFrame:
    base = pd.read_csv(base_csv)
    required = {"benchmark", "model", "ER_keV", "R_A", "I6_GeV2", "phase_space_open"}
    if required - set(base.columns):
        raise ValueError(f"base CSV missing {sorted(required-set(base.columns))}")
    if set(base.model.unique()) != {"GCN", "JJ55"} or set(base.benchmark.unique()) != set(BENCHMARKS):
        raise ValueError("base CSV must contain the four expected benchmarks and GCN/JJ55")
    afh = pd.read_csv(afh_csv)
    q = afh.q_GeV.to_numpy(float)
    r = afh.R_equal_pn_normalized.to_numpy(float)
    if len(q) != 2401 or not np.all(np.diff(q) > 0) or not np.isclose(r[0], A*A, atol=1e-7, rtol=0):
        raise ValueError("AFH table must be the 2401-point physical response with R_A(0)=A^2")
    interp = PchipInterpolator(q, r, extrapolate=False)
    beta = SPEED / C_KM_S
    pchi = M_CHI * beta / math.sqrt(1-beta*beta)
    rows = []
    for benchmark in BENCHMARKS:
        g = base[(base.benchmark == benchmark) & (base.model == "GCN")].sort_values("ER_keV")
        j = base[(base.benchmark == benchmark) & (base.model == "JJ55")].sort_values("ER_keV")
        if len(g) != 160 or len(j) != 160:
            raise ValueError(f"{benchmark}: expected 160 points per nuclear model")
        if not np.array_equal(g.ER_keV.to_numpy(), j.ER_keV.to_numpy()):
            raise ValueError(f"{benchmark}: GCN/JJ55 recoil grids differ")
        I6 = g.I6_GeV2.to_numpy(float)
        opened = g.phase_space_open.astype(bool).to_numpy()
        if not np.allclose(I6, j.I6_GeV2.to_numpy(float), rtol=1e-12, atol=1e-12):
            raise ValueError(f"{benchmark}: I6 is not common to GCN/JJ55")
        if not np.array_equal(opened, j.phase_space_open.astype(bool).to_numpy()):
            raise ValueError(f"{benchmark}: phase-space masks differ")
        ER = g.ER_keV.to_numpy(float)
        ER_GeV = ER * 1e-6
        q_response = np.sqrt(2*M_A*ER_GeV)
        R_AFH = np.asarray(interp(q_response), float)
        if not np.all(np.isfinite(R_AFH)) or np.any(R_AFH < 0):
            raise ValueError(f"{benchmark}: AFH interpolation invalid or extrapolated")
        denominator = (M_V*M_V + 2*M_A*ER_GeV)**2
        for model, response in (
            ("AFH_default", R_AFH),
            ("GCN", g.R_A.to_numpy(float)),
            ("JJ55", j.R_A.to_numpy(float)),
        ):
            dsigma = M_A*G_PRODUCT_SQ*response*I6/(256*math.pi**3*pchi**2*denominator)
            dsigma = np.where(opened, dsigma, 0.0)
            for i in range(len(ER)):
                rows.append({
                    "benchmark": benchmark, "model": model, "ER_keV": ER[i],
                    "q_response_GeV": q_response[i], "R_A": response[i],
                    "R_A_over_A2": response[i]/(A*A), "I6_GeV2": I6[i],
                    "dsigma_dER_GeVminus3": dsigma[i],
                    "dsigma_dER_cm2_per_keV": dsigma[i]*GEV3_TO_CM2_PER_KEV,
                    "phase_space_open": bool(opened[i]),
                })
    out = pd.DataFrame(rows).sort_values(["benchmark","model","ER_keV"]).reset_index(drop=True)
    validate(out)
    return out

def validate(out: pd.DataFrame) -> None:
    if len(out) != 1920 or out.groupby(["benchmark","model"]).size().ne(160).any():
        raise AssertionError("Expected 4 x 3 x 160 output rows")
    beta = SPEED/C_KM_S
    pchi = M_CHI*beta/math.sqrt(1-beta*beta)
    ER = out.ER_keV.to_numpy(float)*1e-6
    rhs = M_A*G_PRODUCT_SQ*out.R_A.to_numpy(float)*out.I6_GeV2.to_numpy(float)
    rhs /= 256*math.pi**3*pchi**2*(M_V**2+2*M_A*ER)**2
    rhs[~out.phase_space_open.astype(bool).to_numpy()] = 0.0
    if not np.allclose(rhs, out.dsigma_dER_GeVminus3.to_numpy(float), rtol=2e-12, atol=1e-300):
        raise AssertionError("Direct Eq.(6) reconstruction failed")
    for benchmark, group in out.groupby("benchmark"):
        i6s = [group[group.model==m].sort_values("ER_keV").I6_GeV2.to_numpy()
               for m in ["AFH_default","GCN","JJ55"]]
        if not all(np.allclose(i6s[0], x, rtol=1e-12, atol=1e-12) for x in i6s[1:]):
            raise AssertionError(f"{benchmark}: I6 differs across nuclear models")

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--base-csv",type=Path,required=True)
    p.add_argument("--afh-response-csv",type=Path,required=True)
    p.add_argument("--out-csv",type=Path,required=True)
    p.add_argument("--metadata",type=Path,required=True)
    a=p.parse_args()
    out=build(a.base_csv,a.afh_response_csv)
    a.out_csv.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.out_csv,index=False,float_format="%.12g")
    meta={
      "target":{"A":A,"Z":Z,"J_A":J_A,"mA_GeV":M_A},
      "particle_inputs":{"m_chi1_GeV":M_CHI,"m_V_GeV":M_V,"g2":G2,
                         "(g1*g2*gVN)^2":G_PRODUCT_SQ,"speed_km_s":SPEED},
      "benchmarks":BENCHMARKS,
      "AFH":{"source":"DMFormFactor v6.0 built-in sdgXe131","b_A_fm":2.2923417985218975,
             "physical_R_A_zero":"A^2; factor 4 applied once to raw AFH isoscalar response"},
      "I6":{"recomputed":False,"shared_across_nuclear_models":True,
            "reason":"R_A factorizes outside the Eq.(6) W^2,z,phi* integral"},
      "grid_keV":{"start":5,"stop":800,"step":5},
      "units":{"primary":"GeV^-3","converted":"cm^2/keV",
               "conversion":"0.389379e-33 cm^2/keV per GeV^-3"},
      "scope":["Xe-131 only","fixed mono-speed diagnostic","differential cross sections only",
               "no event-rate spectra or halo velocity integration"]
    }
    a.metadata.parent.mkdir(parents=True,exist_ok=True)
    a.metadata.write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")

if __name__ == "__main__":
    main()
