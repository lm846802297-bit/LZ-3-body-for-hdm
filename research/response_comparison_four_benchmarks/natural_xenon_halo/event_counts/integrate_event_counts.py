"""Radiative signal expectations in true recoil energy for 2.84 tonne-years at unit efficiency."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline, make_interp_spline
from numpy.polynomial.legendre import leggauss

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import run_fold as fold

EXPOSURE_TONNE_YR = 2.84
EXPOSURE_KG_DAY = EXPOSURE_TONNE_YR * 1000 * 365.25
WINDOWS = {"candidate": (215.5, 280.5), "lower": (100., 200.), "all_recoils": (0., 1000.)}
FIGURE = "manuscript_figure"
FIGURE_MV, FIGURE_G1, FIGURE_G2, FIGURE_GVN = 5., .1, 1.725, .04857
FIGURE_PRODUCT2 = (FIGURE_G1*FIGURE_G2*FIGURE_GVN)**2
GROUP_KEYS = ["benchmark", "ms_keV", "delta_m_MeV", "window", "ER_min_keV", "ER_max_keV"]
QUANTITIES = ("M0_time", "A_time", "B_time", "C_time", "D", "space_delta",
              "B_Coul", "B_time_zexp", "C_time_zexp", "D_zexp", *fold.COMPONENTS)
BASE_ORDER, FINE_ORDER, MAX_PANEL_KEV = 6, 10, 30.
SPECTRUM = fold.OUT/"isotope_contributions.csv.gz"
SUPPORT = fold.OUT/"kinematic_endpoints.csv"
PREVIOUS = fold.OUT/"benchmark_summary.csv"
RUN = fold.OUT/"validation.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def figure_worker():
    """The archived kernels read process-wide couplings. This pool exclusively evaluates the paper figure."""
    fold.fixed.MV = FIGURE_MV
    fold.fixed.G2 = FIGURE_G2
    fold.fixed.GPROD2 = FIGURE_PRODUCT2


def spectrum_benchmark(name):
    # The blue reference and the paper figure have exactly the same external dark masses.
    return "blue" if name == FIGURE else name


@lru_cache(None)
def nuclear_response(archive, a):
    path = archive/"native"/f"afh_v6_xe{a}_eight_response_native.csv"
    expected = json.loads(RUN.read_text(encoding="utf-8"))["native_reference"][str(a)]
    if sha256(path) != expected["source_sha256"]:
        raise ValueError(f"native response hash mismatch for Xe-{a}")
    table = pd.read_csv(path)
    q = table.q_GeV.to_numpy()
    raw = table[["W_"+ch+"00_AFH" for ch in fold.CHANNELS]].to_numpy()
    # Same single equal-p/n and OBDME conversion for every channel, fixed by R_M(0)=A^2.
    spline = make_interp_spline(q, raw*(a*a/raw[0,0]), k=5)
    spline.extrapolate = False
    return spline


def energy_nodes(low, high, order):
    boundaries = sorted({low, high, *(edge for w in WINDOWS.values() for edge in w if low < edge < high)})
    x,w = leggauss(order)
    energy, weight = [], []
    for left,right in zip(boundaries[:-1],boundaries[1:]):
        grid=np.linspace(left,right,1+int(np.ceil((right-left)/MAX_PANEL_KEV)))
        half=np.diff(grid)/2
        energy.append((grid[:-1,None]+half[:,None]*(1+x)).ravel())
        weight.append((half[:,None]*w).ravel())
    return np.concatenate(energy), np.concatenate(weight)


def direct(task):
    name, a, low, high, order, archive = task
    zero = np.zeros(len(QUANTITIES))
    if pd.isna(low):
        return {w:zero.copy() for w in WINDOWS}
    mass, fraction, nt, _, _ = fold.isotope_input(a)
    ms, gap = fold.BENCHMARKS[spectrum_benchmark(name)]
    if name == FIGURE and (fold.fixed.MV,fold.fixed.G2,fold.fixed.GPROD2)!=(FIGURE_MV,FIGURE_G2,FIGURE_PRODUCT2):
        raise ArithmeticError("paper-figure model parameters not initialized")
    ms, gap = ms*1e-6, gap*1e-3
    energy, dE = energy_nodes(low, high, order)
    er = energy*1e-6
    responses = nuclear_response(archive,a)(np.sqrt(er*(2*mass+er)))
    if not np.all(np.isfinite(responses)):
        raise ValueError("energy outside the native AFH input")
    common = nt*fraction*fold.RHO/fold.fixed.MCHI*86400*1e5
    common *= mass*fold.fixed.GPROD2*fold.fixed.CONVERT/(256*np.pi**3)
    rates = np.empty((len(energy),len(QUANTITIES)))
    for j,(e,eg,response) in enumerate(zip(energy,er,responses)):
        vmin = fold.vmin_three_body_km_s(fold.fixed.MCHI,ms,mass,eg)
        v,dv = fold.halo_nodes(vmin,fold.ORDER[0])
        pdf = np.array([fold.shm_truncated_pdf(s,fold.V0,fold.VEARTH,fold.VESC) for s in v])
        t,dl,tr,p2 = fold.integrated(mass,e,ms,gap,v,fold.ORDER[1:])
        weight = common*v*pdf*dv/(p2*(fold.fixed.MV**2+2*mass*eg)**2)
        # At fixed (A,E_R), the nuclear coefficients are constant across the speed integral.
        terms = fold.dsigma_terms(mass,eg,response,*[np.array([weight@y]) for y in (t,dl,tr)])
        rates[j] = [terms[k][0] for k in QUANTITIES]
    result = {}
    for w,(left,right) in WINDOWS.items():
        inside = (energy>left)&(energy<right)
        result[w] = EXPOSURE_KG_DAY*(dE[inside]@rates[inside])
    return result


def archived_spectrum_counts(group, low, high):
    """Integrate the prior rate table, with its physical zero and zero slope at both thresholds."""
    zero = np.zeros(len(QUANTITIES))
    if pd.isna(low):
        return {w:zero.copy() for w in WINDOWS}
    g=group[(group.ER_keV>low)&(group.ER_keV<high)].sort_values("ER_keV")
    x=np.r_[low,g.ER_keV,high]
    y=np.vstack([zero,g[list(QUANTITIES)].to_numpy(),zero])
    spline=CubicSpline(x,y,bc_type=((1,zero),(1,zero)),extrapolate=False)
    result={}
    for w,(left,right) in WINDOWS.items():
        left,right=max(left,low),min(right,high)
        result[w]=EXPOSURE_KG_DAY*spline.integrate(left,right) if left<right else zero.copy()
    return result


def figure_on_original_grid(task):
    a,low,high=task
    group,_=fold.one_isotope((spectrum_benchmark(FIGURE),a,None,fold.ORDER,False))
    return archived_spectrum_counts(group,low,high)


def figure_width_and_trace():
    ms, gap=fold.BENCHMARKS[spectrum_benchmark(FIGURE)]
    ms,gap=ms*1e-6,gap*1e-3
    mass=fold.isotope_input(131)[0]
    er, speed=267.,750.
    l00=fold.integrated(mass,er,ms,gap,[speed],(12,4,4),w_map="linear_w2",check=True)[0][0]
    trace=fold.fixed.eq6.reduced_kernel(fold.fixed.MCHI,ms,gap,mass,er*1e-6,speed,
                   nw=12,nz=4,nphi=4,width_scheme="pole",g2=FIGURE_G2)
    width=fold.fixed.eq6.chi2_width_dirac_scalar(fold.fixed.MCHI,ms,gap,fold.fixed.G2)
    if abs(l00/trace-1)>3e-7:
        raise ArithmeticError("paper-width gamma-trace crosscheck")
    return dict(pole_width_MeV=width*1000,independent_L00_trace_relative_difference=l00/trace-1,
                trace_Xe=131,trace_ER_keV=er,trace_speed_km_s=speed)


def displayed_curve_counts(figure_pdf, total):
    """Integrate the published red vector path using the tick labels in its upper panel."""
    import pymupdf
    with pymupdf.open(figure_pdf) as doc:
        paths=doc[0].get_drawings()
    frames=sorted((p["rect"] for p in paths if p["color"]==(0.,0.,0.) and len(p["items"])==1
                   and p["rect"].width>250 and p["rect"].height<1e-4),key=lambda r:r.y0)
    if len(frames)!=4 or not np.allclose([frames[0].x0,frames[0].x1],[frames[1].x0,frames[1].x1]):
        raise ValueError("unexpected plot axes in the paper figure")
    curves=[p for p in paths if p["color"]==(1.,0.,0.) and len(p["items"])>10]
    if len(curves)!=1 or any(s[0]!="l" for s in curves[0]["items"]):
        raise ValueError("cannot identify radiative signal polyline")
    segments=np.array([[tuple(s[1]),tuple(s[2])] for s in curves[0]["items"]])
    np.testing.assert_allclose(segments[:-1,1],segments[1:,0],rtol=0,atol=1e-6)
    points=np.vstack([segments[0,0],segments[:,1]])
    # Axes in this specific figure read 0 to 800 keV and 10^4 to 10^-12 events/keV.
    energy=800*(points[:,0]-frames[0].x0)/frames[0].width
    log_rate=(4-16*(points[:,1]-frames[0].y0)/(frames[1].y0-frames[0].y0))*np.log(10)
    if np.any(np.diff(energy)<=0):
        raise ValueError("red curve is not single-valued in recoil energy")
    figure=total[total.benchmark==FIGURE].set_index("window")
    rows=[]
    for w in ("candidate","lower"):
        lo,hi=WINDOWS[w]
        if not energy[0]<=lo<hi<=energy[-1]:
            raise ValueError("window outside the plotted radiative curve")
        x=np.r_[lo,energy[(energy>lo)&(energy<hi)],hi]
        y=np.interp(x,energy,log_rate)
        dy=np.diff(y)
        # Straight segments on a logarithmic y-axis give an exponential in physical units.
        ratio=np.divide(np.expm1(dy),dy,out=np.ones_like(dy),where=dy!=0)
        shown=float(np.sum(np.diff(x)*np.exp(y[:-1])*ratio))
        rows.append(dict(window=w,ER_min_keV=lo,ER_max_keV=hi,paper_red_curve_events=shown,
                         current_M0=figure.at[w,"M0_time"],current_B=figure.at[w,"B_time"],
                         current_C=figure.at[w,"C_time"],current_D=figure.at[w,"D"]))
    pd.DataFrame(rows).to_csv(HERE/"manuscript_figure_comparison.csv",index=False)
    return dict(segments=len(segments),visible_red_ER_keV=[energy[0],energy[-1]],
                red_curve_events_per_keV_at_750=float(np.exp(np.interp(750.,energy,log_rate))),
                minimum_speed_km_s_at_750=min(fold.vmin_three_body_km_s(
                    fold.fixed.MCHI,300e-6,fold.isotope_input(a)[0],750e-6) for a in fold.SPIN),
                previous_halo_vmax_km_s=fold.VMAX)


def decorate(frame):
    b,c,d=frame.B_time,frame.C_time,frame.D
    def delta_pct(num,den):
        return 100*(num-den)/den.where(den>0)
    frame["D_minus_B_events"]=d-b
    frame["D_vs_B_percent"]=delta_pct(d,b)
    frame["B_vs_M0_percent"]=delta_pct(b,frame.M0_time)
    frame["B_vs_A_percent"]=delta_pct(b,frame.A_time)
    frame["D_vs_C_ppm"]=1e6*frame.space_delta/c.where(c>0)
    return frame


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--native-archive",type=Path,default=fold.HERE.parents[3]/"P0-native-AFH-acceptance-2026-11-18")
    ap.add_argument("--workers",type=int,default=6)
    args=ap.parse_args()
    upstream=json.loads(RUN.read_text(encoding="utf-8"))
    dependencies=[fold.MASSES,fold.ABUNDANCES,fold.NATIVE,Path(fold.__file__),
                  Path(sys.modules["three_body_tensor"].__file__),Path(fold.fixed.__file__),
                  Path(fold.fixed.eq6.__file__),Path(fold.fixed.ff.__file__)]
    for path in [SPECTRUM,SUPPORT,*dependencies]:
        key=path.relative_to(fold.RESEARCH.parent).as_posix()
        if sha256(path)!=upstream["sha256"][key]:
            raise ValueError(f"upstream input hash mismatch for {path.name}")
    if sha256(PREVIOUS)!=upstream["figure_outputs_sha256"][PREVIOUS.name]:
        raise ValueError("previous benchmark summary hash mismatch")
    limits=pd.read_csv(SUPPORT).set_index(["benchmark","A"])
    isotope=pd.read_csv(SPECTRUM).groupby(["benchmark","A"])
    expected={(name,a) for name in fold.BENCHMARKS for a in fold.SPIN}
    if set(limits.index)!=expected or set(isotope.groups)!=expected:
        raise ValueError("incomplete source benchmark/isotope combinations")
    if limits.ER_low_keV.min()<0 or limits.ER_high_keV.max()>WINDOWS["all_recoils"][1]:
        raise ValueError("recoil support extends outside the tabulated spectrum")
    tasks=[]
    reference={}
    for name,a in limits.index:
        low,high=limits.loc[(name,a),["ER_low_keV","ER_high_keV"]]
        reference[name,a]=archived_spectrum_counts(isotope.get_group((name,a)),low,high)
        tasks.extend((name,a,low,high,n,args.native_archive.resolve()) for n in [BASE_ORDER,FINE_ORDER])
    computed={}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for task,values in zip(tasks,pool.map(direct,tasks)):
            name,a,_,_,order,_=task
            computed[name,a,order]=values
    figure_grid=[(a,*limits.loc[("blue",a),["ER_low_keV","ER_high_keV"]]) for a in fold.SPIN]
    figure_tasks=[(FIGURE,a,low,high,n,args.native_archive.resolve())
                  for a,low,high in figure_grid for n in [BASE_ORDER,FINE_ORDER]]
    with ProcessPoolExecutor(max_workers=args.workers,initializer=figure_worker) as pool:
        for task,values in zip(figure_tasks,pool.map(direct,figure_tasks)):
            name,a,_,_,order,_=task
            computed[name,a,order]=values
        for task,values in zip(figure_grid,pool.map(figure_on_original_grid,figure_grid)):
            reference[FIGURE,task[0]]=values
        figure_validation=pool.submit(figure_width_and_trace).result()
    rows,checks=[],[]
    for name,a in reference:
        ms,gap=fold.BENCHMARKS[spectrum_benchmark(name)]
        for window,(left,right) in WINDOWS.items():
            info=dict(benchmark=name,ms_keV=ms,delta_m_MeV=gap,
                      window=window,ER_min_keV=left,ER_max_keV=right)
            full=computed[name,a,FINE_ORDER][window]
            base=computed[name,a,BASE_ORDER][window]
            previous=reference[name,a][window]
            rows.append(dict(**info,A=a,**dict(zip(QUANTITIES,full))))
            for j,k in enumerate(QUANTITIES):
                checks.append(dict(benchmark=name,A=a,window=window,quantity=k,
                                   fine=full[j],coarse=base[j],recoil_grid=previous[j]))
    iso=decorate(pd.DataFrame(rows))
    total=decorate(iso.groupby(GROUP_KEYS,sort=False,as_index=False)[list(QUANTITIES)].sum())
    for frame in (total,iso):
        fig=frame.benchmark==FIGURE
        frame["mV_GeV"]=np.where(fig,FIGURE_MV,fold.fixed.MV)
        frame["g2"]=np.where(fig,FIGURE_G2,fold.fixed.G2)
        frame["coupling_product_squared"]=np.where(fig,FIGURE_PRODUCT2,fold.fixed.GPROD2)
        np.testing.assert_allclose(frame.D,frame[list(fold.COMPONENTS)].sum(axis=1),rtol=1e-13,atol=0)
        np.testing.assert_allclose(frame.D,frame.C_time+frame.space_delta,rtol=1e-13,atol=0)
    if any(total.loc[(total.benchmark=="black")&(total.window=="lower"),k].item()!=0 for k in QUANTITIES):
        raise ArithmeticError("closed black lower window")
    checks=pd.DataFrame(checks).groupby(["benchmark","window","quantity"],as_index=False)[
        ["fine","coarse","recoil_grid"]].sum()
    physical=checks.quantity.isin(["M0_time","A_time","B_time","C_time","D","space_delta"])
    nonzero=checks.fine.ne(0)
    for other in ("coarse","recoil_grid"):
        if (checks.loc[~nonzero,other]!=0).any():
            raise ArithmeticError("closed-window crosscheck failed")
        checks[other+"_over_fine_minus1"]=(checks[other]-checks.fine)/checks.fine.where(nonzero)
    diffs={s:float(checks.loc[physical,s+"_over_fine_minus1"].abs().max()) for s in ("coarse","recoil_grid")}
    if diffs["coarse"]>1e-6 or diffs["recoil_grid"]>1e-4:
        raise ArithmeticError(("energy integration crosscheck",diffs))
    prev=pd.read_csv(PREVIOUS).set_index("benchmark")
    all_counts=total[(total.window=="all_recoils")&(total.benchmark!=FIGURE)].set_index("benchmark")
    old_total_diff=max(float(((all_counts[k]/(EXPOSURE_KG_DAY*prev[k+"_integrated_kg_day"]))-1).abs().max())
                       for k in ("B_time","C_time","D"))
    if old_total_diff>1e-4:
        raise ArithmeticError(("full support vs previous Simpson",old_total_diff))
    total.to_csv(HERE/"event_counts.csv",index=False)
    iso.to_csv(HERE/"isotope_event_counts.csv",index=False)
    checks.to_csv(HERE/"energy_integration_checks.csv",index=False)
    fig_pdf=fold.RESEARCH.parent/"paper-source/figures/DM_signal_v2.pdf"
    displayed=displayed_curve_counts(fig_pdf,total)
    audit=dict(exposure_tonne_years=EXPOSURE_TONNE_YR,exposure_kg_days=EXPOSURE_KG_DAY,
               efficiency=1,energy="true recoil keV",process="radiative tree-level signal only",
               windows_keV=WINDOWS,maximum_energy_panel_keV=MAX_PANEL_KEV,energy_orders=[BASE_ORDER,FINE_ORDER],
               original_halo_phase_orders=fold.ORDER,coverage=upstream["atom_coverage"],four_reference_parameters={
                   "mchi_GeV":fold.fixed.MCHI,"mV_GeV":fold.fixed.MV,"g2":fold.fixed.G2,
                   "coupling_product_squared":fold.fixed.GPROD2,"halo":upstream["halo"]},
               manuscript_figure_parameters=dict(mchi_GeV=fold.fixed.MCHI,ms_keV=300,delta_m_MeV=10,
                   mV_GeV=FIGURE_MV,g1=FIGURE_G1,g2=FIGURE_G2,gVN=FIGURE_GVN,
                   coupling_product_squared=FIGURE_PRODUCT2,**figure_validation),
               independent_published_curve_readout=displayed,
               max_relative_difference_for_summed_rates_and_space_correction=diffs,
               full_support_max_relative_difference_vs_previous_summary=old_total_diff,
               isotope_rows=len(iso),benchmark_window_rows=len(total),
               native_sha256={a:v["source_sha256"] for a,v in upstream["native_reference"].items()})
    files=[RUN,SPECTRUM,SUPPORT,PREVIOUS,fold.RESEARCH.parent/"paper-source/main.tex",
           fig_pdf,Path(__file__).resolve(),
           *(HERE/s for s in ("event_counts.csv","isotope_event_counts.csv","energy_integration_checks.csv",
                              "manuscript_figure_comparison.csv"))]
    audit["sha256"]={p.relative_to(fold.RESEARCH.parent).as_posix():sha256(p) for p in files}
    (HERE/"count_validation.json").write_text(json.dumps(audit,indent=2,allow_nan=False),encoding="utf-8")
    print(total[["benchmark","window","B_time","D","D_vs_B_percent","D_vs_C_ppm"]].to_string(index=False))
    print("Maximum integration differences",diffs, "previous full-support comparison",old_total_diff)


if __name__=="__main__":
    main()
