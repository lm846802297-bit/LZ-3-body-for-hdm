"""Independent upstream tensor check and integrity/physics checks of saved curves."""
import json
from pathlib import Path
import sys
import numpy as np
import compare_responses as c


def main():
    from three_body_phase_space_tensor import integrate_spin_resolved_tensor
    from three_body_multipole_leptonic_weights import complex_from_pairs, extract_afh_vector_coefficients
    checks=[]
    for name,ms_keV,gap_MeV in c.BENCHMARKS:
        er=267.
        ref=integrate_spin_resolved_tensor(mchi=c.MCHI,ms=ms_keV*1e-6,delta_m=gap_MeV*1e-3,
            mA=c.MA,ER=er*1e-6,speed_kms=c.SPEED,g2=c.G2,width_scheme='pole',
            mapping='threshold_u2',nw=16,nz=8,nphi=12,crosscheck_dirac_trace=False)
        L=complex_from_pairs(ref['L_q_aligned_real_imag'])
        tensor=c.integrate(er,ms_keV*1e-6,gap_MeV*1e-3)
        qr=np.sqrt(er*1e-6*(2*c.MA+er*1e-6))
        f1,f2=c.ff.isoscalar_zexp(qr*qr)
        coeff=extract_afh_vector_coefficients(L,qr,f1=f1/3,f2=f2/3,mN_GeV=c.ff.M_N_GEV,omega_GeV=er*1e-6)
        refs={'L00':L[0,0].real,'ReL0L':L[0,3].real,'LLL':L[3,3].real,
              'LC':coeff['L_C_continuity_adjusted_charge_weight'],'LT':(L[1,1]+L[2,2]).real}
        errs={k:abs(tensor[k]/v-1) for k,v in refs.items()}
        if max(errs.values())>2e-6:
            raise ArithmeticError(f'Independent integrated current tensor mismatch: {errs}')
        _,_,response,_=c.load_nuclear()
        nuclear=response(qr)
        reference_kernel=sum(coeff[key]*nuclear[index] for key,index in
            [('C_M',0),('C_PhiPP',3),('C_MPhiPP',6),('C_Delta',5),('C_SigmaPrime',2),('C_SigmaPrimeDelta',7)])
        assembled=c.assemble(er,tensor,nuclear,name,ms_keV,gap_MeV,'PCHIP_anchor')
        new_kernel=tensor['LC']*assembled['R_charge']+tensor['LT']*assembled['R_transverse']
        contraction_error=abs(new_kernel/reference_kernel-1)
        if contraction_error>2e-6: raise ArithmeticError('Six-channel coefficient contraction mismatch')
        checks.append({'benchmark':name,'ER_keV':er,'upstream_order':[16,8,12],
                       'new_periodic_order':list(c.ORDER),'relative_errors':errs,
                       'six_channel_contraction_relative_error':contraction_error})
    rows=c.csv_read(c.OUT/'differential_cross_sections.csv')
    groups={name:[r for r in rows if r['benchmark']==name] for name,_,_ in c.BENCHMARKS}
    ratio_error=0.
    for name,group in groups.items():
        er=np.array([float(r['ER_keV']) for r in group])
        if not np.all(np.diff(er)>0): raise ValueError('Nonmonotonic recoil grid')
        if sum(r['phase_space_open']=='False' for r in group)!=2:
            raise ValueError('Expected two zero-cross-section endpoints')
        for r in group:
            paper=float(r['paper_cm2_per_keV']);time=float(r['time_only_cm2_per_keV']);full=float(r['full_candidate_cm2_per_keV'])
            if r['phase_space_open']=='False':
                if (paper,time,full)!=(0,0,0) or r['full_over_paper'] or r['full_over_time']:
                    raise ValueError('Invalid closed-phase-space treatment')
            else:
                if min(paper,time,full)<=0: raise ValueError('Nonpositive cross section')
                ratio_error=max(ratio_error,abs(float(r['full_over_paper'])-full/paper),
                    abs(float(r['time_over_paper'])-time/paper),
                    abs(float(r['full_over_time_minus_1_ppm'])*1e-6-(full/time-1)))
    if ratio_error>2e-14: raise ArithmeticError('Saved ratios not consistent with saved cross sections')
    q,physical,_,c0=c.load_nuclear()
    for a,b,mix in [(0,3,6),(2,5,7)]:
        if np.any(physical[:,mix]**2>physical[:,a]*physical[:,b]+1e-11*np.maximum(physical[:,a]*physical[:,b],1e-25)):
            raise ArithmeticError('Native response violates Cauchy-Schwarz')
    result={'status':'PASS_FOR_DECLARED_ONE_BODY_CANDIDATE_SCOPE','points':len(rows),
            'independent_upstream_tensor_checks':checks,'max_saved_ratio_identity_residual':ratio_error,
            'zero_recoil_normalization_residual':float(abs(physical[0,0]-131**2)),
            'full_bound_nuclear_current_validated':False}
    (c.OUT/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
