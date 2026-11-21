"""Independent data, integration, normalization and phase-space checks for the halo spectra."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import pandas as pd
import scipy
from scipy.integrate import quad
from scipy.interpolate import make_interp_spline
from scipy.optimize import brentq

import run_fold as fold
from three_body_tensor import integrated, fixed

ENERGIES = [101, 200, 267, 269, 300, 542]
REFERENCE_DIR = fold.RESEARCH / "afh_default_density_natural_xenon_halo"
OUTPUT = fold.OUT


def rel(a, b):
    return np.abs(np.asarray(a)/np.asarray(b) - 1)


def check_native(archive):
    gate = json.loads((archive/"native-comparison.json").read_text())
    if not (gate["status"] == "PASS" and gate["native_afh_validated"] and gate["rows_compared"]==16807):
        raise ValueError("unexpected native reference")
    expected = {name.replace(chr(92),"/"):checksum for checksum,name in
                (line.split(maxsplit=1) for line in (archive/"SHA256SUMS.txt").read_text().splitlines() if line.strip())}
    if fixed.hash_file(archive/"native-comparison.json") != expected["native-comparison.json"]:
        raise ValueError("invalid native reference checksum")
    direct = fold.inputs()[-1]
    channels = list(fixed.CHANNELS)
    result = {}
    for a in fold.SPIN:
        name = f"native/afh_v6_xe{a}_eight_response_native.csv"
        path = archive/name
        if fixed.hash_file(path) != expected[name]:
            raise ValueError(f"invalid reference input {path.name}")
        original = pd.read_csv(path)
        independent = make_interp_spline(original.q_GeV, original[["W_"+s+"00_AFH" for s in channels]], k=5)
        values = direct.loc[a]
        model = independent(values.Q_A_GeV)
        diff = np.abs(values[channels].to_numpy()-model)
        np.testing.assert_allclose(values[channels], model, atol=2e-11, rtol=1e-7)
        result[str(a)] = dict(source_sha256=expected[name], max_abs_vs_reference_interpolant=float(diff.max()),
                              common_C0=fold.isotope_input(a)[3])
    return result


def check_quadrature(iso, workers):
    fine = (22, 20, 8, 8)
    speed_only = (22, *fold.ORDER[1:])
    tasks = [(n,a,ENERGIES,order,False) for order in [fine,speed_only]
             for n in fold.BENCHMARKS for a in fold.SPIN]
    checks = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for task, (frame, _) in zip(tasks, pool.map(fold.one_isotope, tasks)):
            frame["check"] = "all_axes" if task[3] == fine else "speed_only"
            checks.append(frame)
    checks = pd.concat(checks, ignore_index=True)
    result = []
    keys = [*fold.KEYS,"A"]
    for kind, frame in checks.groupby("check"):
        matched = iso.merge(frame, on=keys, suffixes=("_base","_fine"))
        matched = matched[matched.is_open_base]
        for k in ["B_time","C_time","D","space_delta"]:
            residual = rel(matched[k+"_base"],matched[k+"_fine"])
            worst = matched.iloc[np.argmax(residual)]
            result.append(dict(check=kind,quantity=k,max_relative_difference=residual.max(),
                               compared_open_isotope_rows=len(residual),worst_benchmark=worst.benchmark,
                               worst_A=int(worst.A),worst_ER_keV=int(worst.ER_keV)))
            if residual.max() > 2e-6:
                raise ArithmeticError((kind, k, residual.max()))
    pd.DataFrame(result).to_csv(OUTPUT/"quadrature_checks.csv",index=False)
    return dict(base=fold.ORDER, refined_all=fine, refined_speed=speed_only, checks=result)


def check_tensors():
    res = []
    for name, (ms, gap) in fold.BENCHMARKS.items():
        mass = fixed.MA
        reference = fixed.integrate(267., ms*1e-6, gap*1e-3, (16,8,8), validate=True)
        calc = integrated(mass,267.,ms*1e-6,gap*1e-3,[800.],(16,8,8),check=True)
        res.append(max(float(rel(calc[i][0], reference[key])) for i,key in enumerate(["L00","deltaLC","LT"])))
    traces = []
    for a, e, speed, ms in [(129,200.,750.,200.),(136,267.,773.,360.)]:
        m = fold.isotope_input(a)[0]
        l00 = integrated(m,e,ms*1e-6,.001,[speed],(12,4,4),w_map="linear_w2",check=True)[0][0]
        ref = fixed.eq6.reduced_kernel(fixed.MCHI, ms*1e-6,.001,m,e*1e-6,speed,
                                       nw=12,nz=4,nphi=4,width_scheme="pole",g2=1.)
        traces.append(float(rel(l00,ref)))
    if max(res)>2e-12 or max(traces)>3e-7:
        raise ArithmeticError((res,traces))
    return dict(fixed_spinor_L00_deltaLC_LT_max_relative=max(res), independent_gamma0_trace_max_relative=max(traces))


def archive_comparison(iso):
    old = pd.read_csv(REFERENCE_DIR/"output/ame2020_direct_exactq_fold/seven_isotope_contributions.csv")
    old = old[(old.mass_scheme=="ame2020_nuclear") & (old.halo_model=="shm_cutoff") &
              (old.response_method=="direct_exact_q") & (old.nv==64)].copy()
    old["benchmark"] = old.benchmark.str.split("_").str[0]
    joined = iso.merge(old,on=[*fold.KEYS,"A"],suffixes=("","_archive"))
    result = []
    for row in joined.itertuples():
        if not row.is_open:
            if row.rate_contribution_events_kg_day_keV != 0:
                raise ArithmeticError("archive support mismatch")
            continue
        ms, gap = fold.BENCHMARKS[row.benchmark]
        ms, gap, er = ms*1e-6, gap*1e-3, row.ER_keV*1e-6
        # Replay the archive's linear W² and v Gauss nodes with its exact nuclear response.
        x,w = fixed.eq6._cached_leggauss(64)
        v = row.vmin_km_s + (fold.VMAX-row.vmin_km_s)*(x+1)/2
        pdf = np.array([fold.shm_truncated_pdf(x,fold.V0,fold.VEARTH,fold.VESC) for x in v])
        l00, _, _, p2 = integrated(row.mass_GeV,row.ER_keV,ms,gap,v,(8,8,4),w_map="linear_w2")
        pref = row.mass_GeV*fixed.GPROD2*fixed.CONVERT/(256*np.pi**3*(fixed.MV**2+2*row.mass_GeV*er)**2)
        flux = fold.inputs()[3] * row.atom_fraction*(fold.RHO/fixed.MCHI)*1e5*86400
        replay = flux*pref*row.R_A*(fold.VMAX-row.vmin_km_s)/2 * (w@(v*pdf*l00/p2))
        ref = row.rate_contribution_events_kg_day_keV
        result.append(dict(benchmark=row.benchmark,A=row.A,ER_keV=row.ER_keV,
                           archived_M_only=ref,matched_archive_replay=replay,
                           archive_order_replay_over_archive_minus1=replay/ref-1,
                           threshold_map_over_archive_minus1=row.M0_time*row.R_A/row.R_M/ref-1))
    checks = pd.DataFrame(result)
    checks.to_csv(OUTPUT/"archived_M_only_crosscheck.csv",index=False)
    max_rel = checks.archive_order_replay_over_archive_minus1.abs().max()
    if max_rel > 3e-5:
        raise ArithmeticError(("archived leading density replay", max_rel))
    return dict(open_anchor_rows=len(checks), max_rel_at_archived_quadrature=float(max_rel),
                max_rel_refined_vs_old_order=float(checks.threshold_map_over_archive_minus1.abs().max()))


def check_saved(iso, total):
    micro = pd.read_csv(OUTPUT/"microscopic_cross_sections.csv.gz")
    _, _, _, nt, _ = fold.inputs()
    atom = fold.inputs()[1].reindex(micro.A).to_numpy()
    flux = (nt*fold.RHO/fixed.MCHI*86400*1e5*atom*micro.speed_km_s*
            micro.f_speed_per_km_s*micro.dv_km_s)
    np.testing.assert_allclose(flux,micro.fold_weight,rtol=5e-13,atol=0.)
    keys = [*fold.KEYS,"A"]
    np.testing.assert_allclose(micro[[x+"_cm2_keV" for x in fold.COMPONENTS]].sum(axis=1),
                               micro.D_cm2_keV,rtol=2e-13,atol=0.)
    for name in ("B_time","C_time","D",*fold.COMPONENTS):
        rebuilt = (flux*micro[name+"_cm2_keV"]).groupby([micro[k] for k in keys]).sum()
        expected = iso[iso.is_open].set_index(keys)[name].sort_index()
        if not rebuilt.index.equals(expected.index):
            raise ArithmeticError("saved microscopic grid differs")
        np.testing.assert_allclose(rebuilt,expected,rtol=6e-13,atol=0.)
    for frame in (iso,total):
        np.testing.assert_allclose(frame[list(fold.COMPONENTS)].sum(axis=1),frame.D,rtol=2e-13,atol=0.)
        np.testing.assert_allclose(frame.C_time+frame.space_delta,frame.D,rtol=2e-13,atol=0.)
    if not ((total.D>0)==(total.open_isotopes>0)).all() or not total.loc[total.D==0,"D_over_B_time"].isna().all():
        raise ArithmeticError("invalid zero-rate ratios")
    bounds=[]
    for name,(ms,_) in fold.BENCHMARKS.items():
        for a in fold.SPIN:
            m=fold.isotope_input(a)[0]
            def dist(e):
                return fold.vmin_three_body_km_s(fixed.MCHI,ms*1e-6,m,e*1e-6)-fold.VMAX
            grid=np.linspace(0,1200,601)
            d=np.array([dist(e) for e in grid])
            roots=[brentq(dist,grid[i],grid[i+1]) for i in np.flatnonzero(d[:-1]*d[1:]<0)]
            if len(roots) not in (0,2):
                raise ArithmeticError("unexpected kinematic endpoints")
            bounds.append(dict(benchmark=name,A=a,ER_low_keV=roots[0] if roots else None,
                               ER_high_keV=roots[-1] if roots else None))
    pd.DataFrame(bounds).to_csv(OUTPUT/"kinematic_endpoints.csv",index=False)
    return dict(microscopic_rows=len(micro),isotope_rows=len(iso),natural_sum_rows=len(total),
                open_rows=int(iso.is_open.sum()),phase_space_closed_isotope_rows=int((~iso.is_open).sum()))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--native-archive",type=Path,default=fold.HERE.parents[3]/"P0-native-AFH-acceptance-2026-11-18")
    ap.add_argument("--workers",type=int,default=4)
    args=ap.parse_args()
    iso=pd.read_csv(OUTPUT/"isotope_contributions.csv.gz")
    total=pd.read_csv(OUTPUT/"halo_spectra.csv")
    audit=dict(native_reference=check_native(args.native_archive),tensor=check_tensors(),
               stored_rates=check_saved(iso,total), archive=archive_comparison(iso),
               quadrature=check_quadrature(iso,args.workers))
    masses, abund, molar, nt, _ = fold.inputs()
    audit.update(computed_locally=True, one_body_matching="leading-static conditional candidate",
                 source_revision_qN="c9cf4b86babd3b29fbe6a80a2b2a7be647677e9c",
                 native_AFH_source_revision="dcefbeb7ad705b6c03f2b4689200eb1d9252e67b",
                 local_repository_base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=fold.HERE,text=True).strip(),
                 runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,pandas=pd.__version__),
                 molar_mass_g_mol=molar,targets_kg=nt,atom_coverage=float(abund.loc[list(fold.SPIN)].sum()),
                 halo=dict(v0=fold.V0,vE=fold.VEARTH,vesc=fold.VESC,rho=fold.RHO,
                           integral=quad(lambda v:fold.shm_truncated_pdf(v,fold.V0,fold.VEARTH,fold.VESC),
                                         0,fold.VMAX,points=[fold.VESC-fold.VEARTH])[0]),
                 widths_keV={n:1e6*fixed.eq6.chi2_width_dirac_scalar(fixed.MCHI,ms*1e-6,gap*1e-3,fixed.G2)
                             for n,(ms,gap) in fold.BENCHMARKS.items()})
    inputs=[fold.MASSES,fold.ABUNDANCES,fold.RESEARCH.parent/"v6/dmformfactor-V6.m",Path(fixed.__file__),
            Path(fixed.eq6.__file__),Path(fixed.ff.__file__),Path(sys.modules["rate_kinematics"].__file__),
            Path(sys.modules["run_natural_xenon_halo_fold"].__file__),
            REFERENCE_DIR/"output/ame2020_direct_exactq_fold/seven_isotope_contributions.csv"]
    numeric_outputs=[p for p in OUTPUT.glob("*.csv*") if p.name!="benchmark_summary.csv"]
    files=[*inputs,*fold.HERE.glob("*.py"),fold.HERE/"native_recoil_responses.wls",*numeric_outputs]
    audit["sha256"]={str(p.relative_to(fold.RESEARCH.parent).as_posix()):fixed.hash_file(p) for p in files}
    (OUTPUT/"validation.json").write_text(json.dumps(audit,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({k:audit[k] for k in ("tensor","stored_rates","archive","quadrature")},indent=2))


if __name__=="__main__":
    main()
