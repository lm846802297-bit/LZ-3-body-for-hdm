"""Compute absolute event spectra at the manuscript benchmark and recover its plotted red curve."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from scipy.interpolate import PchipInterpolator
from scipy.special import exprel

import integrate_event_counts as counts

fold = counts.fold
OUT = counts.HERE / "output" / "recoil_curves"
METHODS = ("M_paper", "M0_time", "A_time", "B_time", "C_time", "D")
ENERGY = np.arange(0., 1000.5, .5)
FIGURE_PDF = fold.RESEARCH.parent / "paper-source/figures/DM_signal_v2.pdf"
FOUR_FIGURE_PDF = FIGURE_PDF.with_name("DM_signal.pdf")


def manuscript_isotope(a):
    if (fold.fixed.MV, fold.fixed.G2, fold.fixed.GPROD2) != (
            counts.FIGURE_MV, counts.FIGURE_G2, counts.FIGURE_PRODUCT2):
        raise ValueError("unexpected manuscript couplings or mediator mass")
    frame, _ = fold.one_isotope((counts.spectrum_benchmark(counts.FIGURE), a, None, fold.ORDER, False))
    frame["benchmark"] = counts.FIGURE
    return frame


def manuscript_red_curve():
    """Read the continuous red stroke (distinct from the red legend swatch)."""
    with pymupdf.open(FIGURE_PDF) as doc:
        page = doc[0]
        paths = page.get_drawings()
        horizontal = [p["rect"] for p in paths if p["color"] == (0.,0.,0.)
                      and p["rect"].width > .66*page.rect.width and p["rect"].height < .001]
    top, bottom, _, _ = sorted(horizontal, key=lambda r: r.y0)
    stroke, = [p for p in paths if p["color"] == (1.,0.,0.) and len(p["items"]) > 2]
    if any(item[0] != "l" for item in stroke["items"]):
        raise ValueError("unexpected red path geometry")
    xy = np.array([[tuple(s[1]),tuple(s[2])] for s in stroke["items"]])
    np.testing.assert_allclose(xy[:-1,1],xy[1:,0],atol=1e-6,rtol=0)
    x, y = np.vstack((xy[0,0], xy[:,1])).T
    # Tick labels on the supplied upper panel: x=0..800 keV, y=10^4..10^-12 events/keV.
    recoil = (x-top.x0)*800/top.width
    number = 10**(4-16*(y-top.y0)/(bottom.y0-top.y0))
    if np.any(np.diff(recoil) <= 0):
        raise ValueError("nonmonotone red path")
    return pd.DataFrame({"ER_keV":recoil,"paper_events_per_keV":number})


def red_integral(red, points):
    """Integral from the first displayed vertex, linear in log(count density) on each segment."""
    x = red.ER_keV.to_numpy()
    n = red.paper_events_per_keV.to_numpy()
    dx, dl = np.diff(x), np.diff(np.log(n))
    area = np.r_[0., np.cumsum(n[:-1]*dx*exprel(dl))]
    points = np.asarray(points)
    if np.any(points < x[0]) or np.any(points > x[-1]):
        raise ValueError("requested paper integral outside the displayed red curve")
    k = np.clip(np.searchsorted(x,points,side="right")-1,0,len(x)-2)
    part = points-x[k]
    return area[k]+n[k]*part*exprel(part*dl[k]/dx[k])


def archived_figure_curves():
    """Digitize only the visible segments of the four-rate figure from the supplied ZIP."""
    colors = {"red": (1.,0.,0.), "green": (0.,.5,0.), "black": (0.,0.,0.), "blue": (0.,0.,1.)}
    with pymupdf.open(FOUR_FIGURE_PDF) as doc:
        page = doc[0]
        paths = page.get_drawings()
        horizontal = [p["rect"] for p in paths if p["color"] == colors["black"]
                      and p["rect"].width > .66*page.rect.width and p["rect"].height < .001]
    top, bottom = sorted(horizontal, key=lambda r: r.y0)
    # The x-axis ticks run 0..800 keV. Major y ticks 10^2, 1, 10^-2, 10^-4
    # place the lower frame at 10^-5 events/(tonne year keV).
    y_ticks = sorted({p["rect"].y0 for p in paths if p["color"] == colors["black"]
                     and abs(p["rect"].width-8)<.001 and p["rect"].height<.001})
    np.testing.assert_allclose(2-7*(np.array(y_ticks)-top.y0)/(bottom.y0-top.y0),[2,0,-2,-4],atol=2e-6)
    pieces = []
    for name, color in colors.items():
        stroke, = [p for p in paths if p["color"] == color and len(p["items"]) > 15]
        xy = np.array([[tuple(s[1]),tuple(s[2])] for s in stroke["items"] if s[0] == "l"])
        if len(xy) != len(stroke["items"]):
            raise ValueError("unexpected line geometry in four-benchmark figure")
        breaks = np.flatnonzero(np.max(np.abs(xy[1:,0] - xy[:-1,1]),axis=1)>1e-6)+1
        panel_segment = 0
        for part in np.split(xy,breaks):
            px, py = np.vstack([part[0,0],part[:,1]]).T
            x = (px-top.x0)*800/top.width
            log_rate = 2 - 7*(py-top.y0)/(bottom.y0-top.y0)
            if np.any(np.diff(x)<=0):
                raise ValueError("unordered recoil coordinates")
            knots = [x, np.array([0.,800.])]
            for level in (-5.,2.):
                k = np.flatnonzero((log_rate[1:]-level)*(log_rate[:-1]-level)<0)
                knots.append(x[k]+(level-log_rate[k])*np.diff(x)[k]/np.diff(log_rate)[k])
            x_new = np.unique(np.concatenate(knots))
            x_new = x_new[(x_new>=max(0.,x[0]))&(x_new<=min(800.,x[-1]))]
            mid = np.interp((x_new[1:]+x_new[:-1])/2,x,log_rate)
            visible = np.flatnonzero((mid>=-5.)&(mid<=2.))
            if not len(visible):
                continue
            for run in np.split(visible,np.flatnonzero(np.diff(visible)>1)+1):
                er = x_new[run[0]:run[-1]+2]
                rate = 10**np.interp(er,x,log_rate)
                pieces.append(pd.DataFrame(dict(benchmark=name,segment=panel_segment,ER_keV=er,
                    paper_events_per_tonne_year_keV=rate,paper_events_per_keV=rate*counts.EXPOSURE_TONNE_YR)))
                panel_segment += 1
    return pd.concat(pieces,ignore_index=True)


def add_paper_charge(frame, archive):
    # The supplemental charge response uses q_p^2=2m_A E_R. The dark tensor,
    # flux, pole width, mediator denominator and normalization stay common.
    for a, group in frame.groupby("A"):
        er = group.ER_keV.to_numpy()*1e-6
        mass = group.mass_GeV.to_numpy()
        response = counts.nuclear_response(archive,a)
        wm = group.R_M.to_numpy()
        if np.any(wm<=0):
            raise ArithmeticError("M-node zero requires an independent L00 evaluation")
        exact = response(np.sqrt(er*(2*mass+er)))[:,0]
        np.testing.assert_allclose(exact,wm,rtol=2e-7,atol=6e-11)
        paper = response(np.sqrt(2*mass*er))[:,0]
        frame.loc[group.index,"M_paper"] = group.M0_time.to_numpy()*(paper/wm)


def direct_static_charge(task):
    """Check the paper-prescription curve with independent energy nodes and an explicit L00 contraction."""
    name, a, low, high, archive = task
    value = dict.fromkeys(counts.WINDOWS,0.)
    if pd.isna(low):
        return value
    mass, abundance, nt, _, _ = fold.isotope_input(a)
    ms_kev, gap_mev = fold.BENCHMARKS[counts.spectrum_benchmark(name)]
    ms, gap = ms_kev*1e-6, gap_mev*1e-3
    energy, dE = counts.energy_nodes(low,high,counts.FINE_ORDER)
    er = energy*1e-6
    wm = counts.nuclear_response(archive,a)(np.sqrt(2*mass*er))[:,0]
    flux = nt*abundance*(fold.RHO/fold.fixed.MCHI)*86400*1e5
    kinematic = mass*fold.fixed.GPROD2*fold.fixed.CONVERT/(256*np.pi**3)
    velocity_integrals = np.empty(len(er))
    for i,e in enumerate(energy):
        minimum = fold.vmin_three_body_km_s(fold.fixed.MCHI,ms,mass,er[i])
        speed, dv = fold.halo_nodes(minimum,fold.ORDER[0])
        density = np.array([fold.shm_truncated_pdf(v,fold.V0,fold.VEARTH,fold.VESC) for v in speed])
        l00, _, _, p2 = fold.integrated(mass,e,ms,gap,speed,fold.ORDER[1:])
        velocity_integrals[i] = np.dot(dv*speed*density,l00/p2)
    integrand = counts.EXPOSURE_KG_DAY*flux*kinematic*wm*velocity_integrals/(fold.fixed.MV**2+2*mass*er)**2
    for window,(left,right) in counts.WINDOWS.items():
        inside = (energy>left)&(energy<right)
        value[window] = dE[inside]@integrand[inside]
    return value


def energy_curve(isotopes, bounds):
    density = np.zeros((len(ENERGY),len(METHODS)))
    cumulative = np.zeros_like(density)
    for a, group in isotopes.groupby("A"):
        low, high = bounds.loc[a,["ER_low_keV","ER_high_keV"]]
        if pd.isna(low):
            continue
        g = group[(group.ER_keV>low)&(group.ER_keV<high)].sort_values("ER_keV")
        x = np.r_[low,g.ER_keV,high]
        zero = np.zeros(len(METHODS))
        y = np.vstack([zero,g[list(METHODS)].to_numpy(),zero])*counts.EXPOSURE_KG_DAY
        interp = PchipInterpolator(x,y,extrapolate=False)
        inside = (low<ENERGY)&(ENERGY<high)
        density[inside] += interp(ENERGY[inside])
        primitive = interp.antiderivative()
        cumulative += primitive(np.clip(ENERGY,low,high))-primitive(low)
    if np.any(density < 0) or np.any(np.diff(cumulative,axis=0)<-1e-13*cumulative[-1]):
        raise ArithmeticError("event count curve violates positivity")
    data = {"ER_keV":ENERGY}
    for j, key in enumerate(METHODS):
        data[key+"_events_per_keV"] = density[:,j]
        data[key+"_events_below_ER"] = cumulative[:,j]
    return pd.DataFrame(data)


def run(archive, workers):
    OUT.mkdir(parents=True,exist_ok=True)
    validation = json.loads((counts.HERE/"count_validation.json").read_text(encoding="utf-8"))
    for path in (counts.SPECTRUM,counts.SUPPORT,FIGURE_PDF,counts.HERE/"event_counts.csv",
                 counts.HERE/"manuscript_figure_comparison.csv"):
        key = path.relative_to(fold.RESEARCH.parent).as_posix()
        if counts.sha256(path)!=validation["sha256"][key]:
            raise ValueError("source checksum mismatch: "+key)
    bounds = pd.read_csv(counts.SUPPORT).set_index(["benchmark","A"])
    static_jobs = []
    for name in (counts.FIGURE,*fold.BENCHMARKS):
        for a in fold.SPIN:
            b = bounds.loc[(counts.spectrum_benchmark(name),a)]
            static_jobs.append((name,a,b.ER_low_keV,b.ER_high_keV,archive))
    paper_jobs = [job for job in static_jobs if job[0] == counts.FIGURE]
    other_jobs = [job for job in static_jobs if job[0] != counts.FIGURE]
    with ProcessPoolExecutor(max_workers=workers,initializer=counts.figure_worker) as pool:
        paper_frames = list(pool.map(manuscript_isotope,fold.SPIN))
        static_counts = list(pool.map(direct_static_charge,paper_jobs))
    jobs = [(name, a, None, fold.ORDER, False) for name in fold.BENCHMARKS for a in fold.SPIN]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        standard = pd.concat([frame for frame,_ in pool.map(fold.one_isotope,jobs)],ignore_index=True)
        static_counts.extend(pool.map(direct_static_charge,other_jobs))
    join_keys = ["benchmark","A","ER_keV"]
    stored = pd.read_csv(counts.SPECTRUM).set_index(join_keys).sort_index()
    fresh = standard.set_index(join_keys).sort_index()
    pd.testing.assert_index_equal(stored.index,fresh.index)
    np.testing.assert_allclose(fresh[list(METHODS[1:])],stored[list(METHODS[1:])],rtol=2e-12,atol=0)
    all_iso = pd.concat([*paper_frames,standard],ignore_index=True)
    add_paper_charge(all_iso, archive)
    reference = pd.read_csv(counts.HERE/"event_counts.csv").set_index(["benchmark","window"])
    direct = pd.DataFrame(static_counts,index=[job[0] for job in paper_jobs+other_jobs]).groupby(level=0).sum()
    curves, checks = [], []
    for name, group in all_iso.groupby("benchmark",sort=False):
        curve = energy_curve(group, bounds.loc[counts.spectrum_benchmark(name)])
        curve.insert(0,"benchmark",name)
        curves.append(curve)
        indexed = curve.set_index("ER_keV")
        for window,(lo,hi) in counts.WINDOWS.items():
            for key in METHODS:
                col = key+"_events_below_ER"
                area = indexed.at[hi,col]-indexed.at[lo,col]
                ref = direct.at[name,window] if key=="M_paper" else reference.at[(name,window),key]
                np.testing.assert_allclose(area,ref,rtol=2e-5,atol=0.)
                checks.append(dict(benchmark=name,window=window,method=key,curve_integral_events=area,
                                   independent_counts=ref,relative_difference=area/ref-1 if ref>0 else np.nan))
    red = manuscript_red_curve()
    measured = pd.read_csv(counts.HERE/"manuscript_figure_comparison.csv").set_index("window")
    displayed = red.ER_keV.iloc[[0,-1]].to_numpy()
    support = bounds.loc[counts.spectrum_benchmark(counts.FIGURE)]
    if displayed[0] > support.ER_low_keV.min() or displayed[1] < support.ER_high_keV.max():
        raise ValueError("the displayed red-curve interval no longer covers the recomputed spectrum")
    manuscript_checks = []
    for window in ("lower","candidate","displayed_red_interval"):
        plotted_range = counts.WINDOWS[window] if window in measured.index else displayed
        area = np.diff(red_integral(red,plotted_range))[0]
        if window in measured.index:
            np.testing.assert_allclose(area,measured.at[window,"paper_red_curve_events"],rtol=1e-12)
        tally_window = window if window in counts.WINDOWS else "all_recoils"
        row = reference.loc[(counts.FIGURE,tally_window)]
        manuscript_checks.append(dict(window=window,ER_min_keV=plotted_range[0],ER_max_keV=plotted_range[1],
            paper_red_curve_events=area,M_paper=direct.at[counts.FIGURE,tally_window],
            **row[list(METHODS[1:])].to_dict(),D_over_paper=row.D/area,
            D_vs_B_percent=row.D_vs_B_percent,D_vs_C_ppm=row.D_vs_C_ppm))
    pd.DataFrame(manuscript_checks).to_csv(OUT/"manuscript_window_comparison.csv",index=False)
    pd.concat(curves,ignore_index=True).to_csv(OUT/"recoil_event_spectra.csv",index=False)
    red.to_csv(OUT/"manuscript_red_curve.csv",index=False)
    archive_curves = archived_figure_curves()
    archive_curves.to_csv(OUT/"four_figure_reference_curves.csv",index=False)
    archive_checks = []
    for name, group in archive_curves.groupby("benchmark",sort=False):
        lo, hi = counts.WINDOWS["candidate"]
        segment, = [s for _,s in group.groupby("segment") if s.ER_keV.min() <= lo and s.ER_keV.max() >= hi]
        area = np.diff(red_integral(segment,[lo,hi]))[0]
        row = reference.loc[(name,"candidate")]
        archive_checks.append(dict(benchmark=name,ms_keV=row.ms_keV,delta_m_MeV=row.delta_m_MeV,
            ER_min_keV=lo,ER_max_keV=hi,attachment_curve_events=area,B_events=row.B_time,D_events=row.D))
    pd.DataFrame(archive_checks).to_csv(OUT/"four_figure_window_comparison.csv",index=False)
    checks = pd.DataFrame(checks)
    checks.to_csv(OUT/"window_integral_checks.csv",index=False)
    print(f"Recomputed {len(paper_frames)} isotope spectra at the main figure point and {len(jobs)} for the four-point comparison.")
    print(f"Main figure: {len(red)} vertices. Four-point figure: {len(archive_curves)} displayed points.")
    print("Largest relative count discrepancy:", checks.relative_difference.abs().max())


if __name__=="__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--native-archive",type=Path,
                    default=fold.HERE.parents[3]/"P0-native-AFH-acceptance-2026-11-18")
    ap.add_argument("--workers",type=int,default=6)
    args=ap.parse_args()
    run(args.native_archive.resolve(),args.workers)
