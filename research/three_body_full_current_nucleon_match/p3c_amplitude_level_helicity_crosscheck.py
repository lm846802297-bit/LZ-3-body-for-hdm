#!/usr/bin/env python3
"""P3-C Xe-131 spatial amplitude-level Cartesian/helicity cross-check.

The full complex three-body Gram tensor is contracted with signed AFH
Delta_J/Sigma'_J reduced amplitudes before summing over helicity/rank.
This is a spatial-sector subgate, not a full bound-nucleus covariant PASS.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator

AFH_SHA = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
RANKS = (1, 2, 3)

def pairs(x):
    a=np.asarray(x,dtype=float)
    if a.shape[-1] != 2: raise ValueError("complex pair array must end in [real,imag]")
    z=a[...,0]+1j*a[...,1]
    if not np.all(np.isfinite(z)): raise ValueError("non-finite complex tensor")
    return z

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def read_csv(path):
    with path.open(newline="",encoding="utf-8-sig") as f: return list(csv.DictReader(f))

def basis():
    # Right-handed AFH frame: q_AFH=-q_A; G is stored with q_A along +z.
    e1=np.array([1.,0.,0.]); e2=np.array([0.,-1.,0.])
    if not np.allclose(np.cross(e1,e2),[0,0,-1],atol=1e-15,rtol=0):
        raise ArithmeticError("AFH helicity basis orientation error")
    return {1:-(e1+1j*e2)/math.sqrt(2),-1:(e1-1j*e2)/math.sqrt(2)}

def eq107(L,Q,f1,f2,mN):
    LT=float(np.real(L[1,1]+L[2,2]))
    if LT < -1e-10*max(np.linalg.norm(L),1.): raise ValueError("negative transverse trace")
    LT=max(0.,LT)
    return {"C_Delta":f1*f1*Q*Q*LT/(2*mN*mN),
            "C_SigmaPrime":(f1+f2)**2*Q*Q*LT/(8*mN*mN),
            "C_SigmaPrimeDelta":-f1*(f1+f2)*Q*Q*LT/(2*mN*mN)}

def helicity_coeffs(G,Q,f1,f2,mN,phase=1.):
    if G.shape!=(4,4,4,4): raise ValueError("G must have shape 4x4x4x4")
    Gf=G.reshape(16,16)
    herm=float(np.linalg.norm(Gf-Gf.conj().T)/max(np.linalg.norm(Gf),1e-300))
    if herm>1e-10: raise ValueError("G is not Hermitian")
    mineig=float(np.min(np.linalg.eigvalsh((Gf+Gf.conj().T)/2)))
    if mineig < -1e-10*max(np.linalg.norm(Gf),1.): raise ValueError("G is not PSD")
    L=np.einsum("mana->mn",G)
    eps=np.zeros((3,3,3)); eps[0,1,2]=eps[1,2,0]=eps[2,0,1]=1; eps[0,2,1]=eps[2,1,0]=eps[1,0,2]=-1
    q=np.array([0.,0.,-Q]); alpha=(f1+f2)/(2*mN)
    curl=1j*alpha*np.einsum("ijk,j->ik",eps,q)
    total={"dd":0j,"ss":0j,"ds":0j}; per={}
    for lam,e in basis().items():
        ddv=Q/(math.sqrt(2)*mN)*(-f1)*np.conjugate(e)
        ssv=phase*lam/math.sqrt(2)*(np.conjugate(e)@curl)
        v={"dd":0j,"ss":0j,"ds":0j}
        for a in range(4):
            block=G[1:,a,1:,a]
            v["dd"]+=ddv@block@np.conjugate(ddv)
            v["ss"]+=ssv@block@np.conjugate(ssv)
            v["ds"]+=ddv@block@np.conjugate(ssv)
        for k in total: total[k]+=v[k]
        per[str(lam)]={"C_Delta":float(v["dd"].real),
                       "C_SigmaPrime":float(v["ss"].real),
                       "C_SigmaPrimeDelta":float(2*v["ds"].real)}
    return ({"C_Delta":float(total["dd"].real),
             "C_SigmaPrime":float(total["ss"].real),
             "C_SigmaPrimeDelta":float(2*total["ds"].real),
             "G_hermiticity_relative_residual":herm,
             "G_minimum_eigenvalue":mineig,
             "helicity_components":per},L)

def kernel(coeff,amps,C0,JA,by_helicity=None):
    factor=4*C0*(4*math.pi/(2*JA+1))*.25
    out={}
    for J,(d,s) in amps.items():
        if by_helicity is None:
            c=coeff
            value=c["C_Delta"]*abs(d)**2+c["C_SigmaPrime"]*abs(s)**2+c["C_SigmaPrimeDelta"]*(s*d.conjugate()).real
        else:
            value=0.
            for c in by_helicity.values():
                value+=c["C_Delta"]*abs(d)**2+c["C_SigmaPrime"]*abs(s)**2+c["C_SigmaPrimeDelta"]*(s*d.conjugate()).real
        out[int(J)]=factor*float(value)
    return sum(out.values()),out

def run(tensor_path,spatial_dir,contraction_path,weights_path):
    phase=json.loads(tensor_path.read_text()); contraction=json.loads(contraction_path.read_text()); weights=json.loads(weights_path.read_text())
    if phase.get("status")!="PASS_SPIN_RESOLVED_DM_TENSOR" or phase.get("width_schemes")!=["pole"]: raise ValueError("formal three-body tensor must be pole-only and accepted")
    if contraction.get("status")!="PROVISIONAL_AFH_CONTRACTION_PASS": raise ValueError("unexpected response-contraction status")
    meta=json.loads((spatial_dir/"metadata.json").read_text())
    if meta.get("source_file_sha256")!=AFH_SHA or meta.get("native_mathematica_spatial_crosscheck") is not False: raise ValueError("AFH source/native state mismatch")
    mp=spatial_dir/meta["multipole_file"]; rp=spatial_dir/meta["response_file"]
    if sha(mp)!=meta["multipole_file_sha256"] or sha(rp)!=meta["response_file_sha256"]: raise ValueError("AFH spatial CSV hash mismatch")
    rows=[r for r in read_csv(mp) if int(r["A"])==131]
    interp={}
    for J in RANKS:
        rr=sorted((r for r in rows if int(r["multipole_J"])==J),key=lambda r:float(r["q_GeV"]))
        if len(rr)!=2401: raise ValueError(f"Xe-131 J={J} grid is incomplete")
        q=np.array([float(r["q_GeV"]) for r in rr])
        d=np.array([float(r["M_Delta_J"]) for r in rr]); s=np.array([float(r["M_SigmaPrime_J"]) for r in rr])
        interp[J]=(q,d,s,PchipInterpolator(q,d),PchipInterpolator(q,s))
    iso=next(x for x in meta["isotope_metadata"] if int(x["A"])==131)
    C0=float(iso["common_matrix_normalization"]); JA=float(iso["J_A"])
    f1=float(weights["form_factor_input"]["F1V"]); f2=float(weights["form_factor_input"]["F2V"]); mN=float(weights["form_factor_input"]["mN_GeV"])
    targets={(x["benchmark"],int(x["A"])):x for x in contraction["benchmarks"]}
    out=[]
    for b in phase["benchmarks"]:
        if b.get("width_scheme")!="pole": raise ValueError("non-pole benchmark")
        Q=float(b["qA_magnitude_GeV"]); G=pairs(b["G_q_aligned_real_imag"]); Lstored=pairs(b["L_q_aligned_real_imag"])
        hc,L=helicity_coeffs(G,Q,f1,f2,mN); direct=eq107(L,Q,f1,f2,mN)
        trace=float(np.linalg.norm(L-Lstored)/max(np.linalg.norm(Lstored),1e-300))
        cres={k:abs(hc[k]-direct[k])/max(abs(direct[k]),1e-300) for k in direct}
        if trace>2e-12 or max(cres.values())>2e-12: raise ValueError("G/L or Eq107/helicity coefficient mismatch")
        amps_p={J:(complex(float(e[3](Q))),complex(float(e[4](Q)))) for J,e in interp.items()}
        amps_l={J:(complex(float(np.interp(Q,e[0],e[1]))),complex(float(np.interp(Q,e[0],e[2])))) for J,e in interp.items()}
        kp,rp=kernel(direct,amps_p,C0,JA); kh,rh=kernel(hc,amps_p,C0,JA,hc["helicity_components"])
        kl,rl=kernel(direct,amps_l,C0,JA); khl,rhl=kernel(hc,amps_l,C0,JA,hc["helicity_components"])
        if abs(kp-kh)/max(abs(kp),1e-300)>2e-12 or abs(kl-khl)/max(abs(kl),1e-300)>2e-12: raise ValueError("amplitude and Cartesian kernels disagree")
        target=targets[(b["benchmark"],131)]; response=target["responses_physical_equal_pn_C0_corrected"]
        kresp=direct["C_Delta"]*response["Delta"]+direct["C_SigmaPrime"]*response["SigmaPrime"]+direct["C_SigmaPrimeDelta"]*response["SigmaPrimeDelta"]
        if abs(kresp-target["spatial_sector"])>5e-12*max(abs(kresp),1.): raise ValueError("response interpolation differs from archived P3-C kernel")
        out.append({"benchmark":b["benchmark"],"ER_keV":b["ER_keV"],"qA_GeV":Q,"width_scheme":"pole",
          "G_to_L_relative_residual":trace,"G_hermiticity_relative_residual":hc["G_hermiticity_relative_residual"],"G_minimum_eigenvalue":hc["G_minimum_eigenvalue"],
          "Eq107_vs_helicity_coefficient_relative_residuals":cres,
          "K_cartesian_Eq107_PCHIP":kp,"K_helicity_amplitude_PCHIP":kh,"PCHIP_amplitude_vs_cartesian_relative_residual":abs(kp-kh)/max(abs(kp),1e-300),
          "K_cartesian_Eq107_linear_amplitude":kl,"K_helicity_amplitude_linear":khl,"linear_amplitude_vs_cartesian_relative_residual":abs(kl-khl)/max(abs(kl),1e-300),
          "K_existing_linear_response_interpolation":kresp,"K_existing_P3C_stored":target["spatial_sector"],
          "PCHIP_amplitude_vs_linear_response_relative_difference":abs(kh-kresp)/max(abs(kresp),1e-300),
          "linear_amplitude_vs_linear_response_relative_difference":abs(khl-kresp)/max(abs(kresp),1e-300),
          "PCHIP_vs_linear_amplitude_kernel_relative_difference":abs(kh-khl)/max(abs(kh),1e-300),
          "rank_amplitudes_PCHIP":{str(J):{"M_Delta_J":amps_p[J][0].real,"M_SigmaPrime_J":amps_p[J][1].real} for J in amps_p},
          "rank_contributions_PCHIP":{str(J):rh[J] for J in rh},"rank_contributions_linear":{str(J):rhl[J] for J in rhl}})
    return {"status":"PASS_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RECONSTRUCTION",
      "P3C_overall_status":"OPEN_FULL_COVARIANT_NUCLEAR_AMPLITUDE_NOT_YET_VALIDATED",
      "scope":"Xe-131 leading-static spatial sector; full complex three-body G^(3) contracted through signed AFH Delta_J/SigmaPrime_J amplitudes and compared with direct Cartesian Eq.(107)",
      "native_afh_validated":False,"full_covariant_nuclear_amplitude_validated":False,"formal_width_scheme":"pole",
      "AFH_source_sha256":AFH_SHA,"AFH_native_status":meta["status"],"spatial_source_run_id":contraction.get("spatial_afh_source",{}).get("artifact_run_id"),
      "spatial_source_artifact_id":contraction.get("spatial_afh_source",{}).get("artifact_id"),
      "form_factor_status":"constant q=0 anchors; finite-t_N dependence not included","benchmark_count":len(out),
      "max_amplitude_vs_cartesian_relative_residual":max(x["PCHIP_amplitude_vs_cartesian_relative_residual"] for x in out),
      "max_Eq107_vs_helicity_coefficient_relative_residual":max(max(x["Eq107_vs_helicity_coefficient_relative_residuals"].values()) for x in out),
      "results":out,"limitations":[
       "Spatial AFH amplitudes are still source-translated Python; native Wolfram P3-B validation is pending.",
       "Charge multipoles M and Phi'' are not rank-resolved in this archive, so the complete charge-plus-spatial nuclear amplitude is not validated at amplitude level.",
       "The independent direct bound-nucleus coordinate-space current matrix element has not yet been implemented; the direct side is the Cartesian three-body tensor with AFH Eq.(107) coefficients.",
       "Finite-t_N form factors and higher-order/two-body nuclear currents are not included."]}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase-space-tensor",type=Path,required=True); p.add_argument("--spatial-dir",type=Path,required=True)
    p.add_argument("--response-contraction",type=Path,required=True); p.add_argument("--leptonic-weights",type=Path,required=True); p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args(); r=run(a.phase_space_tensor,a.spatial_dir,a.response_contraction,a.leptonic_weights)
    a.out_json.parent.mkdir(parents=True,exist_ok=True); a.out_json.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({"status":r["status"],"P3C_overall_status":r["P3C_overall_status"],"benchmark_count":r["benchmark_count"],
      "max_amplitude_vs_cartesian_relative_residual":r["max_amplitude_vs_cartesian_relative_residual"],
      "max_Eq107_vs_helicity_coefficient_relative_residual":r["max_Eq107_vs_helicity_coefficient_relative_residual"]},indent=2))
    if r["status"]!="PASS_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RECONSTRUCTION": raise SystemExit(1)
if __name__=="__main__": main()
