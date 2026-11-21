"""Disentangle the AFH recoil-mass and the halo, and compare the two manuscript formulas."""
import json
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.special import erf

import paper_kernels as k
import reproduce as r

REF_EARTH=r.EXTERNAL["modern_mean"].lab
PUBLISHED=k.Halo("galactic",238.,254.,798.)


def direct_fixed_cross_section(a,energy,v,mass_set):
    """Evaluate the fixed-speed pole-width cross section without interpolation."""
    mass=k.masses(mass_set)[k.ISOTOPES.index(a)]
    er=energy*1e-6
    response=k.phys.charge_response(a)(np.sqrt(2*mass*er))
    pref=(k.TO_CM2_KEV*(k.phys.G1*k.phys.G2*k.phys.GN)**2*response /
          (k.phys.MV**2+2*mass*er)**2)
    if v<=k.minimum_speed(mass,er):
        return 0.
    return pref*k.phys.lab_integral(v,mass,er,18,(8,8))


def independent_id_point(e,halo,mass_label,contact):
    """Direct adaptive velocity fold and closed I(D); angular halo integral in the tail."""
    # At the tested energies and speeds all open isotopes probe the upper SHM branch.
    assert not halo.annual and halo.cut=="galactic"
    v0,lab=halo.v0,halo.lab
    esc=halo.endpoint-lab
    c=k.phys.C_KMS
    za=esc/v0
    norm=np.pi**1.5*v0**3*(erf(za)-2*za*np.exp(-za**2)/np.sqrt(np.pi))
    er=e*1e-6
    total=0.
    for a,m in zip(k.ISOTOPES,k.masses(mass_label)):
        if a not in k.AFH:
            continue
        q=np.sqrt(2*m*er)
        threshold=c*(k.phys.MS/q+q*(1/m+1/k.phys.MCHI)/2)
        if threshold>=halo.maximum:
            continue
        assert threshold>esc-lab
        response=k.phys.charge_response(a)(q)
        denom=k.phys.MV**4 if contact else (k.phys.MV**2+q*q)**2
        pref=k.TO_CM2_KEV*(k.phys.G1*k.phys.G2*k.phys.GN)**2*m*response/(2*np.pi**3*k.phys.GAP**2*denom)
        def integrand(v):
            ceiling=(esc**2-v*v-lab*lab)/(2*v*lab)
            directional=quad(lambda z:np.exp(-(v*v+lab*lab+2*v*lab*z)/v0**2),-1,ceiling,
                             epsabs=1e-17,epsrel=1e-9)[0]
            density=2*np.pi*v*v*directional/norm
            d=q*(v-threshold)/c
            ms=k.phys.MS
            # asinh(sqrt(x)*(sqrt(2+x))) avoids acosh(1+x) cancellation.
            x=d/ms
            y=np.sqrt(x*(x+2))
            phase=.5*ms*ms*((1+x)*y-np.arcsinh(y))
            return density*v*phase/(v/c)**2
        average=quad(integrand,threshold,halo.maximum,epsabs=1e-35,epsrel=1e-8)[0]
        total+=k.EXPOSURE_FLUX*k.TABLE.at[a,"natural_atom_fraction"]*pref*average
    return total


def main():
    obs=k.reference()
    e=np.unique(np.r_[np.arange(85.,805.01,.5),obs["red"][0,[0,-1]]])
    grid=pd.read_csv(k.OUT/"exact_kernel_grid.csv.gz")
    red={label:k.Red(grid,label) for label in ("AME","A_mp")}
    blue=k.read_curve(obs["blue"],r.FIT_E)
    controls=[
        ("paper_AME",r.EXTERNAL["paper_example"],"AME","AME","figure-paper example"),
        ("paper_AFHmass",r.EXTERNAL["paper_example"],"A_mp","A_mp","figure-paper example"),
        ("mean_AFHmass",r.EXTERNAL["modern_mean"],"A_mp","A_mp","external fixed mean"),
        ("annual_AFHmass",r.EXTERNAL["modern_annual"],"A_mp","A_mp","external uniform year"),
        ("published_AME",PUBLISHED,"AME","AME","external fixed 254"),
        ("published_AFHmass",PUBLISHED,"A_mp","A_mp","external fixed 254"),
    ]
    for name,kin,qmass,lab in [
        ("blue_mean_AME","AME","AME",REF_EARTH),
        ("blue_mean_AFHmass","A_mp","A_mp",REF_EARTH),
        ("blue_254_AFHmass","A_mp","A_mp",254.),
        ("blue_AME_Ampq","AME","A_mp",REF_EARTH),
        ("blue_Amp_AMEq","A_mp","AME",REF_EARTH),
    ]:
        h,_=r.blue_fit(blue,"galactic","AFH7",kin,lab,qmass)
        controls.append((name,h,kin,qmass,"blue shape only"))
    scores=[]; curves=[]; by_isotope=[]; points=[]; id_checks=[]
    for name,h,kin,qmass,origin in controls:
        blue_raw=k.Blue(r.FIT_E,"AFH7",kin,qmass).evaluate(h)
        # Some predefined input sets have an endpoint below the last blue datum.
        valid=(blue_raw>0)
        scale=np.exp(np.mean(np.log(blue[r.FIT_TRAIN & valid]/blue_raw[r.FIT_TRAIN & valid])))
        residual=np.log(np.maximum(blue_raw,1e-100)*scale/blue)
        validation=(~r.FIT_TRAIN)&valid
        blue_rms=np.sqrt(np.mean(residual[validation]**2))
        models={"pole":red[kin].fold(e,h,"AFH7",q_mass_label=qmass)}
        if name in ("paper_AME","mean_AFHmass","published_AFHmass","blue_mean_AFHmass","blue_254_AFHmass"):
            models["ID_finite"]=k.leading_rate(e,h,kin,qmass,False)
            models["ID_contact"]=k.leading_rate(e,h,kin,qmass,True)
        for formula,contrib in models.items():
            y=contrib.sum(axis=0)
            score=r.red_scores(e,y,obs["red"])
            full_id=name+"_"+formula
            blue_shape=scale*k.Blue(e,"AFH7",kin,qmass).evaluate(h)
            scores.append(dict(model=full_id,formula=formula,origin=origin,kinematic_mass=kin,response_q_mass=qmass,
                         v0=h.v0,vesc=h.endpoint-h.lab,vlab=h.lab,annual_amp=h.annual,vmax=h.maximum,
                         blue_holdout_log_rms_on_open_points=blue_rms,blue_open_fraction=float(valid.mean()),**score))
            curves.append(pd.DataFrame(dict(model=full_id,ER_keV=e,red_prediction_events_keV=y,
                            red_pdf_events_keV=k.read_curve(obs["red"],e),blue_scaled=blue_shape,
                            blue_pdf_events_keV=k.read_curve(obs["blue"],e))))
            ix=np.flatnonzero(e==248.)[0]
            for i,a in enumerate(k.ISOTOPES):
                x=k.TABLE.at[a,"natural_atom_fraction"]
                ni=k.NUCLEI_KG*x
                count=contrib[i,ix]
                by_isotope.append(dict(model=full_id,A=a,ER_keV=248.,nuclei_per_kg=ni,
                                 weighted_events_keV=count,rate_kg_day_keV=count/k.phys.EXPOSURE,
                                 mean_v_sigma_cm3_s_keV=count/(k.phys.EXPOSURE*ni*(k.phys.RHO/k.phys.MCHI)*86400)))
            ref=k.read_curve(obs["red"],np.array([100.,120.,180.,248.,265.,350.,528.,650.,750.,795.]))
            for energy,pdf_value in zip([100.,120.,180.,248.,265.,350.,528.,650.,750.,795.],ref):
                predicted=float(np.interp(energy,e,y))
                points.append(dict(model=full_id,ER_keV=energy,predicted_events_keV=predicted,
                                   pdf_events_keV=pdf_value,predicted_over_pdf=predicted/pdf_value))
            if formula!="pole" and name in ("blue_mean_AFHmass","published_AFHmass"):
                for energy in [180.,248.,350.,750.]:
                    direct=independent_id_point(energy,h,kin,formula=="ID_contact")
                    fast=float(np.interp(energy,e,y))
                    id_checks.append(dict(model=full_id,ER_keV=energy,adaptive_events_keV=direct,
                                      quadrature_events_keV=fast,relative=fast/direct-1))
    score=pd.DataFrame(scores)
    r.write(score,"matched_comparisons.csv")
    r.write(pd.concat(curves,ignore_index=True),"matched_spectra.csv.gz")
    r.write(pd.DataFrame(by_isotope),"matched_isotopes_248keV.csv")
    r.write(pd.DataFrame(points),"matched_selected_energies.csv")
    check=pd.DataFrame(id_checks);r.write(check,"independent_ID_checks.csv")
    assert check.relative.abs().max()<1e-6
    fixed=[]
    for mset in ("AME","A_mp"):
        m=k.masses(mset)[k.ISOTOPES.index(131)]
        q=np.sqrt(2*m*248e-6)
        for v in [700.,720.,750.,776.,800.]:
            val=direct_fixed_cross_section(131,248.,v,mset)
            new=float(red[mset].dsigma(131,np.array(248.),np.array(v),k.phys.charge_response(131)(q)))
            assert val==new==0 or abs(new/val-1)<.001
            fixed.append(dict(A=131,ER_keV=248.,mass_set=mset,mass_GeV=m,
                              vmin_km_s=k.minimum_speed(m,248e-6),speed_km_s=v,
                              absolute_dsigma_cm2_keV=val,spline_dsigma_cm2_keV=new))
    r.write(pd.DataFrame(fixed),"xe131_fixed_248keV.csv")
    files=["matched_comparisons.csv","matched_spectra.csv.gz","matched_isotopes_248keV.csv",
           "matched_selected_energies.csv","independent_ID_checks.csv","xe131_fixed_248keV.csv"]
    record=dict(baseline_commit="b9c9a3dcd702b28017cd6266153e9a218058a4c6",
                supplied_figure_sha256="ab3e375a2803db8860b9de46fa9a1d66b53bcc1d0e8f00a0a78ab10e1aa0d984",
                comparison_inputs={str(p.relative_to(k.phys.RESEARCH.parent)).replace("\\","/"):r.digest(p)
                    for p in [k.phys.MASS_INPUT,k.phys.RESEARCH/"three_body_natural_xenon/dmformfactor-V6.m",
                         *sorted((k.phys.HALO/"inputs/afh_v6/native").glob("*.csv"))]},
                red_fit_parameters=0,halo_density_GeV_cm3=k.phys.RHO,gVN=k.phys.GN,g1=k.phys.G1,g2=k.phys.G2,
                exposure_kg_day=k.phys.EXPOSURE,efficiency=1,target_nuclei_per_kg=k.NUCLEI_KG,
                direct_ID_max_relative=float(check.relative.abs().max()),sha256={n:r.digest(k.OUT/n) for n in files})
    (k.OUT/"matched_run.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf8",newline="\n")
    print(score[["model","low_events","candidate_events","integrated_abs_rel","p90_point_rel","density_750","blue_holdout_log_rms_on_open_points","red_targets_pass"]].to_string(index=False))


if __name__=="__main__":
    main()
