"""Check the supplied Fig. 3 against its compiled page and the independent charge calculation."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
import pandas as pd
import pymupdf
import scipy
from PIL import Image, __version__ as pillow_version
from scipy.optimize import brentq
from scipy.special import exprel

import independent_charge as calc

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent / "output/recoil_curves"
WINDOWS = {"lower": (100., 200.), "candidate": (215.5, 280.5)}
SOURCE = {"3body_for_HDM.zip": "658d9a3972e416128d30759d3963efbd417629bb3462092e7ef1c4c06a366f50",
          "3body_for_HDM.pdf": "978c35cf0f8a220ffb6f60a18cf4ccd9f1c52221db3b2ed0c3f66ecec21e83fd",
          "DM_signal_v2.pdf": "ab3e375a2803db8860b9de46fa9a1d66b53bcc1d0e8f00a0a78ab10e1aa0d984"}
OLDER_FIG_SHA = "4f8d91b56dc504ea0d1f32ce4ae617de3d6887add9199f7aa44db91a9ee49c97"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def paths(page):
    draws = page.get_drawings()
    strokes = [d for d in draws if d["type"] == "s" and len(d["items"])>200]
    red, = [d for d in strokes if d["color"] == (1.,0.,0.)]
    blue, = [d for d in strokes if d["color"][2]>.5 and d["color"][0]==0.]
    lower, = [d for d in strokes if d["color"]==(0.,0.,0.) and d["dashes"]=="[] 0"]
    elastic, = [d for d in strokes if d["color"]==(0.,0.,0.) and d["dashes"]!="[] 0"]
    result = {}
    for name, d in (("red",red),("blue",blue),("ratio",lower),("elastic",elastic)):
        lines = d["items"]
        assert all(seg[0]=="l" for seg in lines)
        ends = np.array([[tuple(s[1]),tuple(s[2])] for s in lines])
        np.testing.assert_allclose(ends[:-1,1],ends[1:,0],rtol=0,atol=2e-5)
        result[name] = np.vstack((ends[0,0],ends[:,1]))
    return result


def calibrate(page):
    drawings = page.get_drawings()
    frames = sorted([p["rect"] for p in drawings if p["color"]==(0.,0.,0.)
                     and p["rect"].height<.001 and p["rect"].width>.65*page.rect.width],
                    key=lambda r:r.y0)
    top, bottom, _, lower_bottom = frames
    one, = [p["rect"].y0 for p in drawings if p["dashes"]!="[] 0" and p["color"]
            and .49 < p["color"][0] < .51 and p["rect"].width>.65*page.rect.width]
    curves = {}
    for name, xy in paths(page).items():
        energy = (xy[:,0]-top.x0)*800/top.width
        if name == "ratio":
            values = (lower_bottom.y0-xy[:,1])/(lower_bottom.y0-one)
        else:
            values = 10**(4.-16*(xy[:,1]-top.y0)/(bottom.y0-top.y0))
        # The elastic drawing extends under the clipping rectangle beyond the right frame.
        curves[name] = np.array([energy, values])
    return curves


def value(curve, energy, logarithmic=True):
    x, y = curve
    if np.min(energy)<x[0] or np.max(energy)>x[-1]:
        raise ValueError("requested point outside available vertices")
    if logarithmic:
        return np.exp(np.interp(energy, x, np.log(y)))
    return np.interp(energy,x,y)


def area(curve, lo, hi, log=True):
    x, _ = curve
    e = np.r_[lo, x[(x>lo)&(x<hi)], hi]
    y = value(curve,e,log)
    if log:
        return float(np.sum(np.diff(e)*y[:-1]*exprel(np.diff(np.log(y)))))
    return float(np.trapezoid(y,e))


def raster_check(figure):
    """Integrate median coloured pixels from Poppler. Find the axes from the black frame."""
    with TemporaryDirectory() as tmp:
        prefix = Path(tmp)/"fig3"
        subprocess.run(["pdftoppm","-f","1","-l","1","-singlefile","-r","432","-png",
                        str(figure),str(prefix)],check=True)
        with Image.open(prefix.with_suffix(".png")) as img:
            pix = np.array(img.convert("RGB"))
    black = np.max(pix, axis=2)<64
    long_rows = np.flatnonzero(black.sum(axis=1)>.67*black.shape[1])
    groups = np.split(long_rows,np.flatnonzero(np.diff(long_rows)>1)+1)
    top, bottom = [round(np.mean(g)) for g in groups[:2]]
    # Outside the axis rectangle there are only isolated glyphs/ticks on the top row.
    cols = np.flatnonzero(black[top])
    longest = max(np.split(cols,np.flatnonzero(np.diff(cols)>1)+1),key=len)
    left,right = longest[[0,-1]]
    xs = np.arange(left,right+1)
    energy = 800*(xs-left)/(right-left)
    # Both signal curves lie below one event/keV. Cropping here removes the legend.
    start = round(top+(bottom-top)/4)
    r,g,b = (pix[start:bottom+1,left:right+1,i].astype(np.int16) for i in range(3))
    result = dict(axis_px=[int(i) for i in (left,right,top,bottom)])
    for name,mask in [("red",(r-g>100)&(r-b>100)),
                      ("blue",(g-r>35)&(b-r>85)&(b-g>30))]:
        trace_x,trace_y=[],[]
        for j in np.flatnonzero(mask.any(axis=0)):
            ordinate=start+np.median(np.flatnonzero(mask[:,j]))
            trace_x.append(energy[j])
            trace_y.append(10**(4-16*(ordinate-top)/(bottom-top)))
        e,n = map(np.array,(trace_x,trace_y))
        result[name] = dict(measured_x_columns=len(e),visible_keV=[float(e[0]),float(e[-1])],
                            area=float(np.trapezoid(n,e)))
    result["red_over_blue_area"] = result["red"]["area"]/result["blue"]["area"]
    return result


def inspect_files(source):
    manifest = {}
    for name, expected in SOURCE.items():
        data = (source/name).read_bytes()
        if sha(data)!=expected:
            raise ValueError(f"input changed: {name}")
        manifest[name] = dict(bytes=len(data),sha256=sha(data))
    with ZipFile(source/"3body_for_HDM.zip") as bundle:
        member = bundle.read("figures/DM_signal_v2.pdf")
        assert member == (source/"DM_signal_v2.pdf").read_bytes()
        tex = bundle.read("main.tex")
        assert b"{figures/DM_signal_v2.pdf}" in tex
        manifest["ZIP_members"] = {i.filename:sha(bundle.read(i)) for i in bundle.infolist()}
    with pymupdf.open(source/"DM_signal_v2.pdf") as single, pymupdf.open(source/"3body_for_HDM.pdf") as paper:
        page = paper[3]
        form = [xref for xref,_,_,_ in page.get_xobjects()
                if paper.xref_stream(xref)==single[0].read_contents()]
        assert len(form)==1
        manifest.update(paper_pages=len(paper),fig3_page=4,
                        identical_form_stream_bytes=len(paper.xref_stream(form[0])),
                        identical_form_stream_sha256=sha(paper.xref_stream(form[0])))
        embedded, original = paths(page), paths(single[0])
        x = np.column_stack((original["red"],np.ones(len(original["red"]))))
        transform = np.linalg.lstsq(x,embedded["red"],rcond=None)[0]
        residuals = {k:float(np.max(np.abs(np.c_[v,np.ones(len(v))]@transform-embedded[k])))
                     for k,v in original.items()}
        assert max(residuals.values())<.01
        manifest["embedded_path_residual_pt"] = residuals
        new = calibrate(single[0])
    older = calc.RESEARCH.parent/"paper-source/figures/DM_signal_v2.pdf"
    if sha(older.read_bytes())!=OLDER_FIG_SHA:
        raise ValueError("read the earlier figure from the pinned comparison checkout")
    manifest["earlier_figure_sha256"] = OLDER_FIG_SHA
    with pymupdf.open(older) as old_pdf:
        old = calibrate(old_pdf[0])
    return manifest,new,old


def main(source):
    out = HERE/"output"
    out.mkdir(exist_ok=True)
    manifest,new,old = inspect_files(source)
    curves = pd.concat([pd.DataFrame({"version":version,"curve":name,"ER_keV":x,"value":y})
                        for version,curves in [("supplied",new),("earlier",old)]
                        for name,(x,y) in curves.items() if name!="elastic"],ignore_index=True)
    curves.to_csv(out/"figure_vertices.csv",index=False,lineterminator="\n")
    # The digitizer reads both axes from each PDF, so the changed range of the lower panel is accounted for.
    for version,curves in [("supplied",new),("earlier",old)]:
        r,b,l = (curves[k] for k in ("red","blue","ratio"))
        lo,hi = max(r[0,0],b[0,0]),min(r[0,-1],b[0,-1])
        ratio = value(r,248.)/value(b,248.)
        direct = value(l,248.,False)
        manifest[version] = dict(red_vertices=r.shape[1],blue_vertices=b.shape[1],
             ratio_vertices=l.shape[1],ratio_at_248_from_spectra=ratio,
             ratio_at_248_from_lower_panel=direct,
             visible_red_area=area(r,*r[0,[0,-1]]),visible_blue_area=area(b,*b[0,[0,-1]]),
             common_interval_keV=[lo,hi],red_over_blue_area_on_common_interval=area(r,lo,hi)/area(b,lo,hi))
    assert abs(manifest["supplied"]["ratio_at_248_from_spectra"]-manifest["supplied"]["ratio_at_248_from_lower_panel"])<.05
    manifest["red_vertices_identical"] = bool(np.array_equal(new["red"],old["red"]))
    manifest["elastic_vertices_identical"] = bool(np.array_equal(new["elastic"],old["elastic"]))
    manifest["poppler_raster_check"] = raster_check(source/"DM_signal_v2.pdf")
    for colour in ("red","blue"):
        vector = manifest["supplied"]["visible_"+colour+"_area"]
        assert abs(manifest["poppler_raster_check"][colour]["area"]/vector-1)<.02
    energy = np.linspace(120,700,1161)
    scale = value(new["blue"],energy)/value(old["blue"],energy)
    manifest["new_over_earlier_blue_120_700_keV"] = dict(median=float(np.median(scale)),
                    percentile_1_99=np.percentile(scale,[1,99]).tolist())
    manifest["new_ratio_unity_crossings_keV"] = [brentq(lambda e:value(new["ratio"],e,False)-1,a,b)
                                                 for a,b in [(140,200),(550,650)]]

    masses,_ = calc.isotope_inputs()
    rows = []
    for a,row in masses.iterrows():
        mass=row.mA_AME2020_CODATA2022_GeV
        low,high=calc.support(mass)
        er=750.e-6
        mu=mass*calc.MCHI/(mass+calc.MCHI)
        q=np.sqrt(2*mass*er)
        rows.append(dict(A=a,low_keV=low,high_keV=high,
                         vmin_750_exact_km_s=calc.exact_min_speed(mass,er),
                         vmin_750_NR_km_s=calc.C_KMS*(calc.MS/q+q/(2*mu))))
    threshold=pd.DataFrame(rows)
    threshold.to_csv(out/"all_isotope_thresholds.csv",index=False,lineterminator="\n")
    assert (threshold.vmin_750_NR_km_s-threshold.vmin_750_exact_km_s).abs().max()<.02
    assert threshold.low_keV.max() < threshold.high_keV.min()
    low,high=threshold.low_keV.min(),threshold.high_keV.max()
    red=new["red"]
    manifest["endpoints"] = dict(all_nine_union_keV=[low,high], least_speed_at_750_km_s=threshold.vmin_750_exact_km_s.min(),
        paper_density_at_750_events_per_keV=float(value(red,750.)),
        visible_events_below_support=area(red,red[0,0],low),
        visible_events_above_support=area(red,high,red[0,-1]))
    manifest["endpoints"]["first_last_plotted_red_points"]=[
        dict(ER_keV=e,events_per_keV=n,
             min_required_speed_km_s=min(calc.exact_min_speed(m, e*1e-6) for m in masses.mA_AME2020_CODATA2022_GeV))
        for e,n in red.T[[0,-1]]]
    archived = pd.read_csv(ARCHIVE/"manuscript_window_comparison.csv").set_index("window")
    rows=[]
    for name,(lo,hi) in WINDOWS.items():
        red_n=area(red,lo,hi)
        approx=calc.approximate_window(lo,hi,20)
        row = dict(window=name,low_keV=lo,high_keV=hi,new_red=red_n,old_red=area(old["red"],lo,hi),
                   new_blue=area(new["blue"],lo,hi),old_blue=area(old["blue"],lo,hi),
                   linear_y_vs_log_y_rel=area(red,lo,hi,False)/red_n-1,
                   independent_ID_events=approx,ID_order10_vs20_rel=calc.approximate_window(lo,hi,10)/approx-1)
        for col in ["M_paper","A_time","B_time","C_time","D"]:
            row[col]=archived.at[name,col]
        row["red_over_static"]=red_n/row["M_paper"]
        fine = calc.lab_window(lo,hi,14,10)
        row["lab_trace_events"] = fine
        row["lab_vs_archive_rel"] = fine/row["M_paper"]-1
        row["lab_coarse_vs_fine_rel"] = calc.lab_window(lo,hi,9,6)/fine-1
        rows.append(row)
    window=pd.DataFrame(rows).set_index("window")
    window.to_csv(out/"windows.csv",lineterminator="\n")
    assert window.linear_y_vs_log_y_rel.abs().max()<.01 and window.ID_order10_vs20_rel.abs().max()<.001
    assert window.lab_vs_archive_rel.abs().max()<1e-4 and window.lab_coarse_vs_fine_rel.abs().max()<1e-4
    stored=pd.read_csv(ARCHIVE/"recoil_event_spectra.csv").query("benchmark=='manuscript_figure'").set_index("ER_keV")
    rows=[]
    for energy in [180.,248.,350.]:
        fine=calc.exact_charge_at(energy,20)
        coarse=calc.exact_charge_at(energy,12)
        angular=calc.exact_charge_at(energy,20,(8,12))
        archive=stored.at[energy,"M_paper_events_per_keV"]
        rows.append(dict(ER_keV=energy,red_events_keV=value(red,energy),archive_static_events_keV=archive,
                         lab_trace_events_keV=fine,lab_vs_archive_rel=fine/archive-1,
                         coarse_vs_fine_rel=coarse/fine-1,angular_8x12_vs_4x4_rel=angular/fine-1))
    exact=pd.DataFrame(rows)
    exact.to_csv(out/"independent_absolute_points.csv",index=False,lineterminator="\n")
    assert exact.lab_vs_archive_rel.abs().max()<.001 and exact.coarse_vs_fine_rel.abs().max()<.0001
    assert exact.angular_8x12_vs_4x4_rel.abs().max()<.0001
    probability=0.
    for a,b in [(0.,calc.VESC-calc.VLAB),(calc.VESC-calc.VLAB,calc.VMAX)]:
        v,dv=calc.integrate_interval(a,b,48)
        probability+=dv@calc.speed_pdf(v)
    assert abs(probability-1)<1e-11
    manifest.update(halo_pdf_integral=probability,pole_width_MeV=1000*calc.pole_width(),
                    benchmark=dict(mchi_GeV=calc.MCHI,mV_GeV=calc.MV,ms_keV=calc.MS*1e6,
                                   gap_MeV=calc.GAP*1e3,g1=calc.G1,g2=calc.G2,gVN=calc.GN,
                                   rho_GeV_cm3=calc.RHO,exposure_kg_day=calc.EXPOSURE,
                                   v0_vesc_vlab_km_s=[calc.V0,calc.VESC,calc.VLAB],efficiency=1),
                    environment=dict(python=sys.version,platform=platform.platform(),cpu=platform.processor(),
                                     scipy=scipy.__version__,numpy=np.__version__,
                                     pymupdf=pymupdf.__version__,pandas=pd.__version__,pillow=pillow_version,
                                     poppler=subprocess.run(["pdftoppm","-v"],check=True,capture_output=True,text=True).stderr.splitlines()[0]),
                    source_commit="4541f1ab07ec017bd41924e69870a4124b1b0053")
    frozen_files=[calc.MASS_INPUT,ARCHIVE/"manuscript_window_comparison.csv",ARCHIVE/"recoil_event_spectra.csv",
                  *sorted((calc.HALO/"inputs/afh_v6/native").glob("*.csv"))]
    manifest["shared_or_archived_inputs"]={f.relative_to(calc.RESEARCH.parent).as_posix():sha(f.read_bytes()) for f in frozen_files}
    manifest["local_numerical_outputs"]={f.name:sha(f.read_bytes()) for f in sorted(out.glob("*.csv"))}
    (out/"audit.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf8",newline="\n")
    print(window.to_string())
    print(exact.to_string(index=False))
    print(json.dumps({k:manifest[k] for k in ("endpoints","supplied","earlier","new_ratio_unity_crossings_keV")},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_directory",type=Path,help="Directory containing the three supplied files")
    main(parser.parse_args().source_directory)
