#!/usr/bin/env python3
"""Apply finite nucleon form factors to the halo-folded seven-isotope AFH rates.

Input rows already contain the full three-body phase-space and halo integrals,
the isotope abundance, the AFH W_M response, the nuclear mass and mediator
factor.  This postprocessor multiplies each isotope contribution by
|c_M(t_N)/3|^2, with t_N=-Q_A^2 and Q_A^2=2 m_A E_R+E_R^2, then re-sums
natural xenon.  No three-body integral is re-evaluated.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np

from ye2020_lowq2 import cM_and_factor, sample_cM_draws

MODELS = (
    "sufian2017_unit_current",
    "alexandrou2020_charge_weighted_converted",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"empty input CSV: {path}")
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def qA2_from_recoil(mA_GeV: float, ER_keV: float) -> float:
    ER = ER_keV*1e-6
    return 2.0*mA_GeV*ER + ER*ER


def _float(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key}={value}")
    return value


def _quantiles(values: np.ndarray) -> tuple[float, float, float]:
    return tuple(float(x) for x in np.percentile(values, [16, 50, 84]))


def process_one(input_dir: Path, output_dir: Path, model: str,
                n_draws: int, seed: int) -> dict:
    isotope_rows = read_csv(input_dir/"seven_isotope_halo_comparison.csv")
    natural_rows = read_csv(input_dir/"natural_xenon_halo_comparison.csv")

    q2 = np.asarray([
        qA2_from_recoil(_float(r,"mA_GeV"),_float(r,"ER_keV"))
        for r in isotope_rows
    ], dtype=float)
    q2_unique, inverse = np.unique(q2, return_inverse=True)
    central = cM_and_factor(q2, model)
    fm_draws = sample_cM_draws(q2_unique, n_draws=n_draws, seed=seed,
                               strange_model=model)
    multiplier_draws = fm_draws*fm_draws

    enriched = []
    by_energy: dict[float, list[int]] = {}
    for i, row in enumerate(isotope_rows):
        E = _float(row,"ER_keV")
        by_energy.setdefault(E,[]).append(i)
        enriched.append({
            **row,
            "Q_A2_GeV2": q2[i],
            "t_N_GeV2": -q2[i],
            "F1_uds": float(central["F1uds"][i]),
            "F2_uds": float(central["F2uds"][i]),
            "F1s_unit": float(central["F1s_unit"][i]),
            "F2s_unit": float(central["F2s_unit"][i]),
            "c_M": float(central["cM"][i]),
            "F_M_normalized": float(central["F_M"][i]),
            "nucleon_FF_rate_multiplier": float(central["rate_multiplier"][i]),
            "full_contribution_B_relative_units":
                _float(row,"full_contribution_relative_units")*float(central["rate_multiplier"][i]),
            "I_D_contribution_B_relative_units":
                _float(row,"I_D_contribution_relative_units")*float(central["rate_multiplier"][i]),
        })

    natural_by_energy = { _float(r,"ER_keV"):r for r in natural_rows }
    total_rows = []
    for E in sorted(by_energy):
        inds = by_energy[E]
        original = natural_by_energy[E]
        full_A = _float(original,"natural_xenon_full_relative_rate")
        id_A = _float(original,"natural_xenon_I_D_relative_rate")
        full_B = sum(float(enriched[i]["full_contribution_B_relative_units"]) for i in inds)
        id_B = sum(float(enriched[i]["I_D_contribution_B_relative_units"]) for i in inds)
        local_q = inverse[inds]
        local_full = np.asarray([_float(isotope_rows[i],"full_contribution_relative_units") for i in inds])
        local_id = np.asarray([_float(isotope_rows[i],"I_D_contribution_relative_units") for i in inds])
        local_mult_draws = multiplier_draws[:,local_q]
        full_draws = np.sum(local_mult_draws*local_full[None,:],axis=1)
        id_draws = np.sum(local_mult_draws*local_id[None,:],axis=1)
        f16,f50,f84 = _quantiles(full_draws)
        i16,i50,i84 = _quantiles(id_draws)
        valid = id_draws > 0.0
        ratio_draws = full_draws[valid]/id_draws[valid] if np.any(valid) else np.asarray([])
        if ratio_draws.size:
            r16,r50,r84 = _quantiles(ratio_draws)
        else:
            r16=r50=r84=""
        total_rows.append({
            "ER_keV":E,
            "natural_xenon_full_A_relative_rate":full_A,
            "natural_xenon_I_D_A_relative_rate":id_A,
            "natural_xenon_full_B_relative_rate":full_B,
            "natural_xenon_I_D_B_relative_rate":id_B,
            "B_over_A_full_rate_pct":(full_B/full_A-1.0)*100.0 if full_A else "",
            "B_over_A_I_D_rate_pct":(id_B/id_A-1.0)*100.0 if id_A else "",
            "full_vs_I_D_error_B_pct":(full_B/id_B-1.0)*100.0 if id_B else "",
            "full_vs_I_D_error_A_pct":(full_A/id_A-1.0)*100.0 if id_A else "",
            "full_B_p16":f16,"full_B_p50":f50,"full_B_p84":f84,
            "I_D_B_p16":i16,"I_D_B_p50":i50,"I_D_B_p84":i84,
            "full_over_I_D_B_p16":r16,"full_over_I_D_B_p50":r50,"full_over_I_D_B_p84":r84,
            "covariance_draws":n_draws,
        })

    output_dir.mkdir(parents=True,exist_ok=True)
    write_csv(output_dir/"seven_isotope_B_baseline.csv",enriched)
    write_csv(output_dir/"natural_xenon_B_baseline.csv",total_rows)
    errors=[abs(float(r["full_vs_I_D_error_B_pct"])) for r in total_rows if r["full_vs_I_D_error_B_pct"]!=""]
    shifts=[abs(float(r["B_over_A_full_rate_pct"])) for r in total_rows if r["B_over_A_full_rate_pct"]!=""]
    metadata={
        "status":"COMPUTED",
        "baseline":"B = finite nucleon F1(t_N), F2(t_N) times finite-size AFH W_M(y_A)",
        "input_halo_directory":str(input_dir),
        "strange_form_factor_model":model,
        "form_factor_source":"Borah et al., Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640; Ye et al. supplemental coefficients/covariance",
        "strange_input_convention":"model-specific; see strange_current_convention_audit.md",
        "momentum_transfer":{
            "Q_A2_GeV2":"2*m_A*E_R+E_R^2",
            "t_N_GeV2":"-Q_A^2",
            "q_NR_used_for_FF":False,
        },
        "matching":{
            "F_i_uds":"3*(F_i_EM,p+F_i_EM,n+F_i_s,unit)",
            "c_M":"F1_uds+t_N/(8*m_N^2)*(F1_uds+2*F2_uds)",
            "normalized_nucleon_factor":"F_M=c_M/3",
            "rate_multiplier":"|F_M|^2",
            "nuclear_response":"AFH v6.0 finite-size W_M; no point-nucleus replacement",
        },
        "uncertainty":{
            "Ye2020_EM_form_factor_covariance_draws":n_draws,
            "seed":seed,
            "strange_lattice_errors":"not sampled in this first pass; separate strange-current scenarios are both output",
            "detector_response_applied":False,
        },
        "summary":{
            "recoil_points":len(total_rows),
            "max_abs_full_vs_ID_error_B_pct":max(errors,default=0.0),
            "max_abs_B_over_A_full_rate_shift_pct":max(shifts,default=0.0),
        },
    }
    (output_dir/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
    return metadata


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-dir",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    p.add_argument("--draws",type=int,default=3000)
    p.add_argument("--seed",type=int,default=20261119)
    p.add_argument("--models",nargs="+",default=list(MODELS),choices=MODELS)
    a=p.parse_args()
    summaries={}
    for model in a.models:
        summaries[model]=process_one(
            a.input_dir,a.out_dir/model,model,a.draws,a.seed
        )
    print(json.dumps(summaries,indent=2))


if __name__=="__main__":
    main()
