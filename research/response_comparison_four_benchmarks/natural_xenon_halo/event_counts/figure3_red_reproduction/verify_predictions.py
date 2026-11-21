"""Independent whole-window folds and robustness to changing held-out blue blocks."""
import json
import sys

import numpy as np
import pandas as pd
from scipy.optimize import brentq
from scipy.special import erf

import paper_kernels as k
import reproduce as r
import convention_controls as ctrl


def endpoints(a,mass_label,maximum,nonrelativistic=False):
    m=k.masses(mass_label)[k.ISOTOPES.index(a)]
    center=1e6*k.phys.MS*k.phys.MCHI/(k.phys.MCHI+m)
    if nonrelativistic:
        mu=m*k.phys.MCHI/(m+k.phys.MCHI)
        beta=maximum/k.phys.C_KMS
        root=np.sqrt(1-2*k.phys.MS/(mu*beta**2))
        q_lo=2*k.phys.MS/(beta*(1+root))
        q_hi=mu*beta*(1+root)
        return 1e6*q_lo**2/(2*m),1e6*q_hi**2/(2*m)
    def excess(e):
        return k.phys.threshold_excess(m,e*1e-6,maximum)
    return (brentq(excess,1.,center,xtol=2e-11),brentq(excess,center,1200.,xtol=2e-11))


def direct_pair_density(energy,halo,order):
    """Evaluate Eq. (22) with the pair-rest-frame tensor directly at every quadrature node."""
    sys.path.insert(0,str(k.phys.HALO))
    import three_body_tensor as pair
    assert not halo.annual and halo.cut=="galactic"
    er=energy*1e-6
    result=0.
    ve=halo.lab
    z=(halo.endpoint-ve)/halo.v0
    norm=erf(z)-2*z*np.exp(-z*z)/np.sqrt(np.pi)
    # All active velocities for this benchmark are above vesc - vlab.
    u,wu=k.unit_quadrature(order)
    previous=pair.fixed.G2
    pair.fixed.G2=k.phys.G2
    try:
        for a in k.AFH:
            m=a*.938272
            vmin=k.phys.exact_min_speed(m,er)
            if vmin>=halo.maximum:
                continue
            assert vmin>halo.endpoint-2*halo.lab
            # Use a threshold-square speed map independent of the stored spline.
            v=vmin+(halo.maximum-vmin)*u*u
            dv=2*(halo.maximum-vmin)*u*wu
            probability=v*(np.exp(-((v-ve)/halo.v0)**2)-np.exp(-z*z))/(np.sqrt(np.pi)*ve*halo.v0*norm)
            charge=k.phys.charge_response(a)(np.sqrt(2*m*er))
            dark,_,_,p2=pair.integrated(m,energy,k.phys.MS,k.phys.GAP,v,(10,4,4))
            dsigma=(m*(k.phys.G1*k.phys.G2*k.phys.GN)**2*charge*k.TO_CM2_KEV*dark/
                    (256*np.pi**3*p2*(k.phys.MV**2+2*m*er)**2))
            result+=k.EXPOSURE_FLUX*k.TABLE.at[a,"natural_atom_fraction"]*(dv@(v*probability*dsigma))
    finally:
        pair.fixed.G2=previous
    return result


def window(func,lo,hi,vmax,n):
    breaks=list(np.linspace(lo,hi,1+int(np.ceil((hi-lo)/12.))))
    for a in k.AFH:
        breaks.extend(x for x in endpoints(a,"A_mp",vmax) if lo<x<hi)
    breaks=np.unique(breaks)
    x,w=k.unit_quadrature(n)
    total=0.
    for a,b in zip(breaks[:-1],breaks[1:]):
        values=[func(e) for e in a+(b-a)*x]
        total+=(b-a)*(w@values)
    return float(total)


def main():
    scores=pd.read_csv(k.OUT/"matched_comparisons.csv").set_index("model")
    models=["published_AFHmass_pole","blue_mean_AFHmass_ID_contact"]
    rows=[]
    for name in models:
        cfg=scores.loc[name]
        halo=k.Halo("galactic",cfg.v0,cfg.vlab,cfg.vlab+cfg.vesc)
        for label,lo,hi in [("low",100.,200.),("candidate",215.5,280.5)]:
            values=[]
            for n in (6,10):
                if cfg.formula=="pole":
                    fn=lambda e:direct_pair_density(e,halo,14 if n==6 else 22)
                else:
                    fn=lambda e:ctrl.independent_id_point(e,halo,"A_mp",True)
                values.append(window(fn,lo,hi,halo.maximum,n))
            grid=cfg.low_events if label=="low" else cfg.candidate_events
            ratio=grid/values[1]-1
            rows.append(dict(model=name,window=label,grid_events=grid,independent_events=values[1],
                             grid_over_independent_minus_one=ratio,coarse_over_fine_minus_one=values[0]/values[1]-1))
    independent=pd.DataFrame(rows)
    assert independent.grid_over_independent_minus_one.abs().max()<.0003
    assert independent.coarse_over_fine_minus_one.abs().max()<1e-6
    r.write(independent,"independent_window_integrals.csv")

    refs=k.reference()
    x=r.FIT_E
    blue=k.read_curve(refs["blue"],x)
    e=np.unique(np.r_[np.arange(85.,805.01,.5),refs["red"][0,[0,-1]]])
    folds=[]
    for block in (0,1,2):
        train=(np.floor((x-100)/18).astype(int)%3)!=block
        h,fit=r.blue_fit(blue,"galactic","AFH7","A_mp",lab=ctrl.REF_EARTH,train=train)
        pred=k.leading_rate(e,h,"A_mp","A_mp",True).sum(axis=0)
        score=r.red_scores(e,pred,refs["red"])
        folds.append(dict(heldout_block=block,blue_log_rms=fit["heldout_log_rms"],v0=h.v0,
                         vesc=h.endpoint-h.lab,vlab=h.lab,**score))
    r.write(pd.DataFrame(folds),"blue_holdout_rotations.csv")

    src=refs["red"]
    xobs=src[0]
    # The continuous red stroke is polygonal in log ordinate. Check true PDF vertices also.
    curves=pd.read_csv(k.OUT/"matched_spectra.csv.gz")
    feature_rows=[]; tail_rows=[]
    for name in models:
        c=curves[curves.model==name]
        for f,lo,hi,maximum in [("peak_1",140,220,True),("dip_1",235,290,False),
                ("peak_2",300,395,True),("dip_2",495,557,False),("peak_3",565,640,True)]:
            sub=c[c.ER_keV.between(lo,hi)]
            ix=sub.red_prediction_events_keV.idxmax() if maximum else sub.red_prediction_events_keV.idxmin()
            mask=(xobs>=lo)&(xobs<=hi)
            ref=src[:,mask]; j=int(np.argmax(ref[1]) if maximum else np.argmin(ref[1]))
            feature_rows.append(dict(model=name,feature=f,graph_ER_keV=ref[0,j],
                 calculated_ER_keV=c.at[ix,"ER_keV"],graph_events_keV=ref[1,j],
                 calculated_events_keV=c.at[ix,"red_prediction_events_keV"]))
        cfg=scores.loc[name]
        exact_bounds=[endpoints(a,"A_mp",cfg.vmax) for a in k.AFH]
        nr_bounds=[endpoints(a,"A_mp",cfg.vmax,nonrelativistic=True) for a in k.AFH]
        for bounds in (exact_bounds,nr_bounds):
            assert max(low for low,high in bounds)<min(high for low,high in bounds)
        lower=min(low for low,high in exact_bounds)
        upper=max(high for low,high in exact_bounds)
        main=(xobs>=120)&(xobs<=700)&(src[1]>1e-5)
        interpolated=np.interp(xobs,c.ER_keV,c.red_prediction_events_keV)
        tail_rows.append(dict(model=name,exact_union_min_keV=lower,exact_union_max_keV=upper,
                 NR_union_min_keV=min(low for low,high in nr_bounds),NR_union_max_keV=max(high for low,high in nr_bounds),
                 main_PDF_vertex_count=int(main.sum()),main_vertex_p90_abs_rel=np.quantile(abs(interpolated[main]/src[1,main]-1),.9),
                 integrated_graph_interval_events=np.trapezoid(c.loc[c.red_pdf_events_keV.notna(),"red_prediction_events_keV"],
                                                              c.loc[c.red_pdf_events_keV.notna(),"ER_keV"])))
    r.write(pd.DataFrame(feature_rows),"peak_and_dip_positions.csv")
    r.write(pd.DataFrame(tail_rows),"endpoints_and_vertices.csv")
    files=["independent_window_integrals.csv","blue_holdout_rotations.csv","peak_and_dip_positions.csv","endpoints_and_vertices.csv"]
    (k.OUT/"verification.json").write_text(json.dumps({n:r.digest(k.OUT/n) for n in files},indent=2)+"\n",encoding="utf8",newline="\n")
    print(independent.to_string(index=False))
    print(pd.DataFrame(folds)[["heldout_block","blue_log_rms","v0","vesc","low_events","candidate_events","integrated_abs_rel"]].to_string(index=False))


if __name__=="__main__":
    main()
