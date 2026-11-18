#!/usr/bin/env python3
"""Rebuild Xe-131 full-recoil charge-sector kernels and figures from native AFH.

Run from the repository root:
  python research/three_body_full_current_nucleon_match/build_xe131_full_recoil_charge_scan.py

The kernels omit the common three-body DM-side factor; they are proportional
to, but are not absolute, differential cross sections.
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results" / "2026-11-18"
NATIVE = ROOT / "research" / "afh_default_density_xe131" / "output" / "phi_response_native" / "afh_default_xe131_M_PhiPP_native.csv"
M_A_GEV = 121.90971983538435
M_N_GEV = 0.938918
ER_MIN_KEV, ER_MAX_KEV = 109.382231766, 653.701913810
sys.path.insert(0, str(HERE))
from nucleon_vector_form_factors import isoscalar_zexp, charge_coefficients

native = pd.read_csv(NATIVE)
q_all = native["q_GeV"].to_numpy()
er_all = (np.sqrt(M_A_GEV**2 + q_all**2) - M_A_GEV) * 1.0e6
mask = (er_all >= ER_MIN_KEV) & (er_all <= ER_MAX_KEV)
q, er = q_all[mask], er_all[mask]
wm = native.loc[mask, "R_M_physical_equal_pn"].to_numpy()
wp = native.loc[mask, "R_PhiPP_physical_equal_pn"].to_numpy()
wmp = native.loc[mask, "R_MPhiPP_physical_equal_pn"].to_numpy()

f1, f2, cm, cp = [], [], [], []
for qi in q:
    fi1, fi2 = isoscalar_zexp(float(qi**2))
    ci_m, ci_p = charge_coefficients(float(qi), F1=fi1, F2=fi2, mN_GeV=M_N_GEV)
    f1.append(fi1); f2.append(fi2); cm.append(ci_m); cp.append(ci_p)
f1, f2, cm, cp = map(np.asarray, (f1, f2, cm, cp))
km = cm**2 * wm
kmi = km + 2*cm*cp*wmp
kfull = kmi + cp**2*wp
out = pd.DataFrame({
    "ER_keV":er, "q_GeV":q, "W_M":wm, "W_PhiPP":wp, "W_MPhiPP":wmp,
    "F1V":f1, "F2V":f2, "cM":cm, "cPhiPP":cp,
    "K_M_only":km, "K_M_plus_interference":kmi, "K_full_charge":kfull,
    "ratio_M_plus_int_over_M":kmi/km, "ratio_full_over_M":kfull/km,
})
RESULTS.mkdir(parents=True, exist_ok=True)
out.to_csv(RESULTS / "xe131_charge_kernel_full_recoil_scan.csv", index=False, float_format="%.12g")
scale = km.max()
plt.figure(figsize=(8.6,5.4))
plt.semilogy(er, km/scale, label=r"$M$ only")
plt.semilogy(er, kmi/scale, label=r"$M + M\Phi''$ interference")
plt.semilogy(er, kfull/scale, label=r"$M + M\Phi'' + \Phi''$")
plt.axvline(200,color="0.45",linestyle="--",linewidth=.9)
plt.axvline(267,color="0.45",linestyle=":",linewidth=.9)
plt.xlabel(r"Recoil energy $E_R$ [keV]")
plt.ylabel(r"Normalized charge-sector kernel $K/\max(K_M)$")
plt.title(r"Xe-131 finite-$Q^2$ charge-sector kernels")
plt.legend(frameon=False); plt.tight_layout()
plt.savefig(RESULTS / "xe131_charge_kernel_full_recoil_curves.svg", format="svg"); plt.close()
plt.figure(figsize=(8.6,5.4))
plt.plot(er,kmi/km,label=r"$(M+M\Phi'')/M$")
plt.plot(er,kfull/km,label=r"$(M+M\Phi''+\Phi'')/M$")
plt.axhline(1,color="0.35",linewidth=.9)
plt.axvline(200,color="0.45",linestyle="--",linewidth=.9)
plt.axvline(267,color="0.45",linestyle=":",linewidth=.9)
plt.xlabel(r"Recoil energy $E_R$ [keV]")
plt.ylabel(r"Ratio to finite-$Q^2$ $M$-only kernel")
plt.title(r"Xe-131 charge-sector response correction")
plt.legend(frameon=False); plt.tight_layout()
plt.savefig(RESULTS / "xe131_charge_kernel_full_recoil_ratios.svg", format="svg"); plt.close()
print("Native rows:", len(out), "ER range:", float(er.min()), float(er.max()))
print("Full/M sampled min:", out.loc[out.ratio_full_over_M.idxmin(), ["ER_keV","ratio_full_over_M"]].to_dict())
print("Full/M sampled max:", out.loc[out.ratio_full_over_M.idxmax(), ["ER_keV","ratio_full_over_M"]].to_dict())
