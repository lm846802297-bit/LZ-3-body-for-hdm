"""Fit the companion blue two-body SHAPE only, then predict the absolute red signal."""
from dataclasses import asdict
import hashlib
import json
import os
import platform
import subprocess
import sys

import numpy as np
import pandas as pd
import scipy
from scipy.integrate import quad
from scipy.optimize import least_squares

import paper_kernels as k
from paper_kernels import Halo

OUT = k.OUT
EXTERNAL = {
    "paper_example":Halo("galactic",220.,232.,776.),
    "modern_mean":Halo("galactic",238.,250.2,794.2),
    "modern_annual":Halo("galactic",238.,250.2,794.2,14.9),
    "galactic_800":Halo("galactic",220.,232.,800.),
    "laboratory_800":Halo("laboratory",220.,232.,800.),
}
# Blue points every 3 keV. Entire 18-keV blocks are held out in each 54-keV interval.
FIT_E=np.arange(100.,789.,3.)
FIT_TRAIN=(np.floor((FIT_E-100)/18).astype(int)%3)!=1


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(data,name):
    compression={"method":"gzip","compresslevel":6,"mtime":0} if name.endswith(".gz") else None
    data.to_csv(OUT/name,index=False,lineterminator="\n",compression=compression)


def blue_fit(observed,cut,nuclear,mass_label,lab=None,q_mass_label=None,train=FIT_TRAIN):
    model=k.Blue(FIT_E,nuclear,mass_label,q_mass_label)
    logs=np.log(observed)
    # Include the full fitted blue energy range in the support of at least one isotope.
    supported=model.weight>0
    needed=np.where(supported,model.vmin,np.inf).min(axis=0).max()+.04
    def make(par):
        if lab is None:
            return Halo(cut,par[0],par[1],par[2])
        return Halo(cut,par[0],lab,par[1])
    def differences(par):
        y=model.evaluate(make(par))
        raw=np.log(np.maximum(y,1e-100))-logs
        return raw-raw[train].mean()
    if lab is None:
        initial=[230.,248.,802.]
        bounds=([150.,180.,needed],[320.,320.,840.])
    else:
        initial=[230.,802.]
        bounds=([150.,needed],[320.,840.])
    fit=least_squares(lambda p:differences(p)[train],initial,bounds=bounds,x_scale="jac",
                      ftol=5e-12,xtol=5e-12,gtol=5e-12,max_nfev=240)
    if not fit.success:
        raise RuntimeError(fit.message)
    h=make(fit.x)
    raw=model.evaluate(h)
    scale=float(np.exp((logs-np.log(raw))[train].mean()))
    err=np.expm1(differences(fit.x))
    return h, dict(cut=cut,nuclear=nuclear,mass_set=mass_label,
                   fixed_lab=lab, v0=h.v0,lab=h.lab,endpoint=h.endpoint,blue_scale=scale,
                   train_log_rms=float(np.sqrt(np.mean(differences(fit.x)[train]**2))),
                   heldout_log_rms=float(np.sqrt(np.mean(differences(fit.x)[~train]**2))),
                   heldout_p90_rel=float(np.quantile(abs(err[~train]),.9)),
                   boundary=bool(fit.active_mask.any()))


def window_integral(e,y,low,high):
    inside=(e>low)&(e<high)
    return float(np.trapezoid(np.r_[np.interp(low,e,y),y[inside],np.interp(high,e,y)],
                              np.r_[low,e[inside],high]))


def red_scores(e,y,source):
    obs=k.read_curve(source,e)
    measured=np.isfinite(obs)
    meaningful=(e>=120)&(e<=700)&(obs>1e-5)
    total=np.trapezoid(obs[measured],e[measured])
    l1=np.trapezoid(abs(y[measured]-obs[measured]),e[measured])/total
    p90=np.quantile(abs(y[meaningful]/obs[meaningful]-1),.9)
    lo=window_integral(e,y,100,200)
    hi=window_integral(e,y,215.5,280.5)
    rlo=k.reference_cumulative(source,100.,200.)[1][-1]
    rhi=k.reference_cumulative(source,215.5,280.5)[1][-1]
    tail=float(np.interp(750.,e,y))
    return dict(low_events=lo,candidate_events=hi,low_ratio=lo/rlo,candidate_ratio=hi/rhi,
        low_over_candidate=lo/hi,integrated_abs_rel=float(l1),p90_point_rel=float(p90),
        density_248=float(np.interp(248.,e,y)),density_750=tail,
        red_targets_pass=bool(abs(lo/rlo-1)<.05 and abs(hi/rhi-1)<.05 and l1<.05 and p90<.10 and tail>0))


def cross_section_checks(red):
    sys.path.insert(0,str(k.phys.HALO))
    import three_body_tensor as pair
    energies=[101.,140.,180.,248.,265.,350.,528.,750.,796.]
    rows=[]
    previous_g2=pair.fixed.G2
    pair.fixed.G2=k.phys.G2
    try:
        for a in k.AFH:
            m=k.TABLE.at[a,"mA_AME2020_CODATA2022_GeV"]
            for e in energies:
                er=e*1e-6
                vmin=k.minimum_speed(m,er)
                threshold_root=k.phys.exact_min_speed(m,er)
                assert abs(vmin-threshold_root)<2e-9
                check=[vmin-.05,vmin+.1,vmin+14.3,vmin+83.5]
                if a==131 and e==248.:
                    check+= [700.,720.,750.,776.,800.]
                r=k.phys.charge_response(a)(np.sqrt(2*m*er))
                for v in sorted(set(check)):
                    candidate=float(red.dsigma(a,np.array(e),np.array(v),r))
                    if v<=vmin:
                        assert candidate==0.
                        rows.append((a,e,v,vmin,0.,0.,0.))
                        continue
                    l00,_,_,p2=pair.integrated(m,e,k.phys.MS,k.phys.GAP,np.array([v]),(12,6,6))
                    factor=k.TO_CM2_KEV*(k.phys.G1*k.phys.G2*k.phys.GN)**2*r/(k.phys.MV**2+2*m*er)**2
                    direct=float((m*l00/(256*np.pi**3*p2))[0])*factor
                    rows.append((a,e,v,vmin,candidate,direct,candidate/direct-1))
    finally:
        pair.fixed.G2=previous_g2
    data=pd.DataFrame(rows,columns=["A","ER_keV","speed_km_s","threshold_km_s","lab_cm2_per_keV",
                                    "independent_pair_cm2_per_keV","relative_difference"])
    if data.relative_difference.abs().max()>.001:
        raise ArithmeticError("independent phase-space cross sections differ by more than 0.1%")
    return data


def normalization(h):
    if h.annual:
        esc=h.endpoint-h.lab
        labs=h.lab+h.annual*k.annual_phases()
        return float(np.mean([normalization(Halo(h.cut,h.v0,lab,lab+esc)) for lab in labs]))
    edges=[0.,h.maximum]
    if h.cut=="galactic":
        mid=h.endpoint-2*h.lab
        edges += [b for b in (mid-h.annual,mid+h.annual,h.endpoint-h.annual) if 0<b<h.maximum]
    edges=sorted(set(edges))
    return sum(quad(lambda v:float(h.pdf(v)),a,b,epsabs=1e-9,limit=160)[0] for a,b in zip(edges[:-1],edges[1:]))


def main():
    OUT.mkdir(exist_ok=True)
    refs=k.reference()
    red_ref,blue_ref=refs["red"],refs["blue"]
    # Use half-keV spacing across both windows and add the red graph endpoints explicitly.
    e=np.unique(np.r_[np.arange(85.,805.01,.5),red_ref[0,[0,-1]]])
    obs=k.read_curve(blue_ref,FIT_E)
    fits=[]
    for nuclear,mass in [("AFH7","AME"),("hybrid9","AME"),("Helm9","AME"),("AFH7","A_u"),("AFH7","A_mp")]:
        for cut in ("galactic","laboratory"):
            h,res=blue_fit(obs,cut,nuclear,mass)
            fits.append(res)
    ranked=sorted(fits,key=lambda r:r["heldout_log_rms"])
    best=ranked[0]
    for lab in (220.,232.,250.2,270.,290.):
        _,r=blue_fit(obs,best["cut"],best["nuclear"],best["mass_set"],lab)
        fits.append(r)
    fit_frame=pd.DataFrame(fits)
    write(fit_frame,"blue_shape_fits.csv")
    cases={name:(h,"AFH7","AME","predefined") for name,h in EXTERNAL.items()}
    # Evaluate all assessed nuclear/halo alternatives; never rank them on the red before prediction.
    for i,r in enumerate(fits):
        name=f"blue_{i+1:02d}"
        h=Halo(r["cut"],r["v0"],r["lab"],r["endpoint"])
        cases[name]=(h,r["nuclear"],r["mass_set"],"blue shape only")
    chosen=f"blue_{fits.index(best)+1:02d}"
    grids={}; red_models={}
    for mass in sorted({case[2] for case in cases.values()}):
        grids[mass]=k.build_kernel_grid(mass)
        red_models[mass]=k.Red(grids[mass],mass)
    write(pd.concat(grids.values(),ignore_index=True),"exact_kernel_grid.csv.gz")
    cross=cross_section_checks(red_models["AME"])
    write(cross,"fixed_speed_cross_sections.csv")
    spectra=[]; summary=[]; iso248=[]; check_folds=[]
    for name,(h,nuclear,mass,origin) in cases.items():
        iso=red_models[mass].fold(e,h,nuclear)
        prediction=iso.sum(axis=0)
        scores=red_scores(e,prediction,red_ref)
        blue=k.Blue(e,nuclear,mass).evaluate(h)
        blue_at_train=k.Blue(FIT_E,nuclear,mass).evaluate(h)
        blue_ok=FIT_TRAIN & (blue_at_train>0)
        scale=float(np.exp(np.mean(np.log(obs[blue_ok]/blue_at_train[blue_ok]))))
        spectra.append(pd.DataFrame(dict(model=name,ER_keV=e,red_prediction_events_keV=prediction,
                         red_pdf_events_keV=k.read_curve(red_ref,e),blue_shape_scaled=scale*blue,
                         blue_pdf_events_keV=k.read_curve(blue_ref,e))))
        summary.append(dict(model=name,origin=origin,nuclear=nuclear,mass_set=mass,**asdict(h),**scores))
        j=int(np.flatnonzero(e==248.)[0])
        for a,contribution in zip(k.ISOTOPES,iso[:,j]):
            x=k.TABLE.at[a,"natural_atom_fraction"]
            iso248.append(dict(model=name,A=a,atom_fraction=x,nuclei_per_kg=k.NUCLEI_KG*x,
                          weighted_dN_dER_events_keV=contribution, rate_per_kg_day_keV=contribution/k.phys.EXPOSURE,
                          mean_v_sigma_cm3_s_keV=contribution/(k.phys.EXPOSURE*k.NUCLEI_KG*x*(k.phys.RHO/k.phys.MCHI)*86400)))
        if name in ("paper_example","modern_mean","modern_annual",chosen):
            test=np.array([140.,180.,248.,350.,528.,650.,750.])
            fine=red_models[mass].fold(test,h,nuclear,order=80).sum(axis=0)
            default=np.interp(test,e,prediction)
            rel=np.divide(default-fine,fine,out=np.zeros_like(fine),where=fine>0)
            check_folds.append(dict(model=name,halo_probability=normalization(h),max_fold_rel=float(abs(rel).max())))
    scores=pd.DataFrame(summary)
    write(scores,"red_prediction_scores.csv")
    write(pd.concat(spectra,ignore_index=True),"spectra.csv.gz")
    write(pd.DataFrame(iso248),"isotope_halo_248keV.csv")
    check=pd.DataFrame(check_folds)
    assert np.max(np.abs(check.halo_probability-1))<2e-7
    assert check.max_fold_rel.max()<.001
    frozen=scores.set_index("model").loc["paper_example"]
    assert abs(frozen.low_events/.8777871586965662-1)<.0005 and abs(frozen.candidate_events/.2025363492833815-1)<.0005
    checkout=subprocess.check_output(["git","-C",str(k.HERE),"rev-parse","HEAD"],text=True).strip()
    manifest=dict(baseline_commit="b9c9a3dcd702b28017cd6266153e9a218058a4c6",execution_checkout=checkout,
                  program_sha256={p.name:digest(p) for p in sorted(k.HERE.glob("*.py"))},
                  selected_by_blue_holdout=chosen,
                  comparisons=check_folds, max_cross_section_relative_difference=float(cross.relative_difference.abs().max()),
                  pole_width_MeV=k.phys.pole_width()*1e3,recoil_grid_step_keV=.5,
                  python=sys.version,numpy=np.__version__,scipy=scipy.__version__,pandas=pd.__version__,
                  platform=platform.platform(),cpu=platform.processor(),logical_cpus=os.cpu_count(),
                  device_used="CPU",blas_threads_env=os.getenv("OPENBLAS_NUM_THREADS"),
                  reference_vertices_sha256=digest(k.HERE.parent/"figure3_source_audit/output/figure_vertices.csv"),
                  output_sha256={name:digest(OUT/name) for name in (
                      "blue_shape_fits.csv","exact_kernel_grid.csv.gz","fixed_speed_cross_sections.csv",
                      "red_prediction_scores.csv","spectra.csv.gz","isotope_halo_248keV.csv")})
    (OUT/"run.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf8",newline="\n")
    print(fit_frame.to_string(index=False))
    print("Selected by held-out blue blocks:",chosen)
    print(scores[["model","low_events","candidate_events","integrated_abs_rel","p90_point_rel","density_750","red_targets_pass"]].to_string(index=False))
    print("Checks",check_folds)


if __name__=="__main__":
    main()
