# Adopted B baseline: nucleon form factors × finite-size AFH response

**Project:** LZ-3-body-for-hdm  
**Decision date:** 2026-11-19  
**Status:** B is the adopted primary baseline. The finite-size AFH nuclear response is mandatory; the low-momentum flavor-resolved nucleon current is also included. No additional AFH response is included in B.  
**Nuclear input:** AFH v6.0 only  
**Form-factor baseline:** Bishara et al., arXiv:1707.06998, Appendix A.1, first-order Dirac slopes and leading Pauli values  
**Formal width:** asymmetric Pole width only

## 1. Adopted calculation hierarchy

The baseline is **B**, not A:

| Version | Single-nucleon current | Whole-nucleus response | Role |
|---|---|---|---|
| A | zero-transfer effective current, \(\widehat F_1(0)=1\) | finite-size \(W_M(y_A)\) | historical AFH reference |
| **B** | **finite-\(t_N\) Dirac–Pauli current \(\widehat F_1(t_N),\widehat F_2(t_N)\)** | **finite-size \(W_M(y_A)\)** | **adopted primary baseline** |
| C | same finite-\(t_N\) current as B | \(W_M,W_{\Phi''},W_{M\Phi''}\) | additional charge-response correction |
| D | same finite-\(t_N\) current as B | all allowed AFH responses and interference terms | full one-body nuclear-current extension; P3-C/native gates required |

The B baseline is
\[
\boxed{
\frac{d\sigma_B}{dE_R}
=\mathcal P_3(E_R)\,
L_C^{(3)}\,
\widehat c_M(t_N)^2\,
W_M^{\rm phys}(y_A).
}
\]
Here \(\mathcal P_3\) contains the common three-body phase-space, flux, mediator-propagator, and coupling prefactors. The primary nuclear response is **only** \(W_M\). No \(W_{\Phi''}\), \(W_\Delta\), \(W_{\Sigma'}\), \(W_{\Sigma''}\), or response interference is added to B.

The three useful comparisons are
\[
\boxed{B/A-1}
\quad\text{(finite-\(t_N\) nucleon-current correction),}
\]
\[
\boxed{C/B-1}
\quad\text{(additional charge multipoles at fixed nucleon current),}
\]
\[
\boxed{C/A-1}
\quad\text{(total change relative to the historical AFH reference).}
\]
B is the reference for subsequent C and D response studies.

## 2. Two different finite-size effects

The nucleon form factors and the AFH nuclear responses describe different physical scales.

**Inside one nucleon:** the quark vector current is matched onto a proton or neutron matrix element,
\[
\langle N'|J_q^\mu|N\rangle
=\bar u_N'
\left[
F_1^{q/N}(t_N)\gamma^\mu
+\frac{iF_2^{q/N}(t_N)}{2m_N}\sigma^{\mu\nu}q_{N,\nu}
\right]u_N.
\]
The flavor-summed form factors describe the finite-momentum structure of the quark current inside an individual nucleon.

**Inside the whole nucleus:** the nucleons occupy a finite spatial distribution and form nuclear multipoles. AFH describes this with
\[
W_M(y_A),\quad W_{\Phi''}(y_A),\quad W_\Delta(y_A),\quad
W_{\Sigma'}(y_A),\ldots
\]
The \(W_M\) response is already a finite-size nuclear response. It must not be replaced by a point-nucleus constant or multiplied by an additional Helm/nuclear form factor.

For the original AFH M-only reference,
\[
R_{A,M}\propto
\widehat F_1(0)^2 L_C^{(3)}W_M^{\rm phys}(y_A)
=L_C^{(3)}W_M^{\rm phys}(y_A).
\]
For B,
\[
R_{B,M}\propto
\widehat c_M(t_N)^2L_C^{(3)}W_M^{\rm phys}(y_A).
\]
The same finite-size AFH \(W_M\) occurs in both.

## 3. Coupling normalization: do not count the factor three twice

The external rate convention uses
\[
g_{VN}=3g_{Vq},\qquad
\mathcal P_3\propto(g_1g_2g_{VN})^2.
\]
For the universal light-quark current \(u+d+s\), the raw flavor-summed values at zero transfer are
\[
F_1^{uds}(0)=3,\qquad F_2^{uds}(0)=-0.552.
\]
Therefore the nucleon-current coefficients in this external-\(g_{VN}\) convention must use
\[
\boxed{
\widehat F_i(t_N)=\frac{F_i^{uds}(t_N)}{3},
\qquad
\widehat F_1(0)=1,\quad
\widehat F_2(0)=-0.184.
}
\]
The external prefactor already contains \(g_{VN}\); using the raw \(F_i^{uds}\) in the current coefficients would count the factor three twice and produce a factor-nine error in the rate.

The equivalent convention is to use \(g_{Vq}=g_{VN}/3\) externally with the unnormalized \(F_i^{uds}\). Both conventions must agree pointwise. **All formal B production modules use the first convention.** Legacy A-reference runners and the archived Mathematica engine are deliberately retained as historical calculations; they do not include the finite-\(t_N\) Dirac--Pauli insertion and must not be described as B or used to generate new B results.

## 4. Adopted low-momentum flavor-separated prescription

B uses the flavor-separated first-order Dirac slopes and leading Pauli inputs from Bishara et al., Appendix A.1:
\[
\begin{aligned}
F_1^{u/p}(t_N)&=2+5.57t_N,\\
F_1^{d/p}(t_N)&=1+2.84t_N,\\
F_1^{s/p}(t_N)&=-0.018t_N,
\end{aligned}
\]
with slopes in \({\rm GeV}^{-2}\). Summing the universal \(u+d+s\) current gives
\[
\boxed{
F_1^{uds,N}(t_N)=3+8.392t_N+\mathcal O(t_N^2).
}
\]
Equivalently, for \(Q_N^2=-t_N\),
\[
F_1^{uds,N}(Q_N^2)=3-8.392Q_N^2+\mathcal O(Q_N^4).
\]
The flavor-separated Pauli inputs are
\[
F_2^{u/p}(0)=1.609,\qquad
F_2^{d/p}(0)=-2.097,\qquad
F_2^{s/p}(0)=-0.064,
\]
so
\[
F_2^{uds,N}(t_N)=-0.552+\mathcal O(t_N).
\]
The available input does **not** provide a validated Pauli slope. B therefore uses the leading constant Pauli term; it does not invent an \(F_2'\).

In the external-\(g_{VN}\) convention,
\[
\boxed{
\widehat F_1(t_N)=1+\frac{8.392}{3}t_N+\mathcal O(t_N^2),
\qquad
\widehat F_2(t_N)=-0.184+\mathcal O(t_N).
}
\]
This is the adopted low-momentum truncation for B, not an all-orders nucleon form-factor fit. The alternative isoscalar_zexp model is retained only as a sensitivity comparison; it is not the default baseline.

## 5. Transfer variables

For an initially resting on-shell nucleus,
\[
q_A^\mu=P_A'^\mu-P_A^\mu=(E_R,\boldsymbol q_A).
\]
The exact invariant and spatial momentum are different:
\[
\boxed{t_A=q_A^2=-2m_AE_R,}
\qquad
\boxed{Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2.}
\]
The mediator propagator uses
\[
(m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2.
\]
The AFH oscillator variable uses
\[
y_A=\frac{b_A^2Q_A^2}{4}.
\]

For the formal one-body impulse prescription,
\[
q_N^\mu=q_A^\mu,\qquad
\boxed{t_N=t_A=-2m_AE_R.}
\]
Thus \(-t_N=2m_AE_R\), whereas the AFH and spatial NR coefficients retain the exact \(Q_A^2=2m_AE_R+E_R^2\). The static diagnostic \(q_N^0=0\), \(t_N=-Q_A^2\), is a different approximation and is not the B production convention.

## 6. B current coefficient and C extension

The effective one-nucleon Dirac–Pauli current is
\[
J_N^\mu=\bar u_N'
\left[
\widehat F_1(t_N)\gamma^\mu+
\frac{i\widehat F_2(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N.
\]
The charge coefficient used by the B M-only kernel is
\[
\boxed{
\widehat c_M(t_N)=
\widehat F_1(t_N)+
\frac{t_N}{8m_N^2}
\left[\widehat F_1(t_N)+2\widehat F_2(t_N)\right].
}
\]
Therefore B is \(\widehat c_M^2L_C^{(3)}W_M\), with no additional response.

For C, the spin-orbit charge multipole is added:
\[
\widehat c_{\Phi''}=
\frac{Q_A^2}{4m_N^2}
\left[\widehat F_1(t_N)+2\widehat F_2(t_N)\right],
\]
\[
R_C\propto L_C^{(3)}
\left[
\widehat c_M^2W_M+
\widehat c_{\Phi''}^2W_{\Phi''}+
2\widehat c_M\widehat c_{\Phi''}W_{M\Phi''}
\right].
\]
The signed interference must be retained. C is a separate extension, not the baseline.

## 7. Xe-131 selected-point comparison

The current fixed-speed native-AFH diagnostics give the following dimensionless ratios. The absolute coefficients are in the external-\(g_{VN}\) convention; the ratios are unchanged by a common factor-three conversion.

| \(E_R\) | Prescription | \(B/A\) | \(C/B\) | \(C/A\) |
|---:|---|---:|---:|---:|
| 200 keV | bishara_linear | 0.739883 | 0.996955 | 0.737630 |
| 200 keV | isoscalar_zexp | 0.780997 | 0.996558 | 0.778309 |
| 267 keV | bishara_linear | 0.662175 | 0.914637 | 0.605649 |
| 267 keV | isoscalar_zexp | 0.721663 | 0.899610 | 0.649216 |

The finite-\(t_N\) nucleon-current correction reduces the M-only kernel by roughly 22–34% at these points. The additional \(\Phi''\) plus signed \(M-\Phi''\) correction is small at 200 keV but larger near the \(W_M\) diffraction minimum around 267 keV. These are fixed-speed Xe-131 charge-sector results, not a natural-xenon halo spectrum.

## 8. Historical provenance and validation boundary

The archived Mathematica notebook explicitly evaluates the AFH finite-q nuclear response through \(W_M(y_A)\). Its recorded rate-engine path uses a constant effective nucleon coupling and does not, by itself, show an explicit finite-\(t_N\), flavor-resolved Dirac–Pauli insertion. If a different earlier local calculation included another low-order quark-shape prescription, its exact source and coefficients still need to be recovered. This provenance question does not block the adopted B baseline: B is now the declared primary prescription for subsequent calculations.

The formal B implementation is present in the current research branch. The initial post-rename CI failures were caused by stale A/B/C field names, a q=0 test fixture that still supplied finite-tN inputs, and a raw-versus-effective form-factor mismatch in the P3-C workflow. These have been corrected rather than waived. The full-current workflow 44465719660 passed, including all regression tests, native charge-sector unit tests, phase-space tensor generation, AFH Eq. (107) extraction, response contraction, and the normalized P3-C spatial helicity subgate. The fixed-speed charge-sector workflow 44464849221 also passed. The dedicated B absolute-spectrum workflow is still required before its curve is promoted, and the natural-xenon halo fold still requires a native seven-isotope/eight-response provenance PASS. P3-C remains a spatial subgate PASS, not a full covariant nuclear-amplitude PASS; the spatial D candidate is provisional.

### 8.1 Executable pipeline inventory

| Path | Classification | Form-factor treatment | Use |
|---|---|---|---|
| `research/three_body_full_current_nucleon_match/xe131_fixed_benchmark_absolute_dsigma.py` | Formal B/C | `Fhat_i=F_i^{uds}/3` | Fixed-benchmark absolute Xe-131 spectrum |
| `research/three_body_full_current_nucleon_match/native_charge_sector_halo_fold.py` | Formal B/C; optional D candidate | `Fhat_i=F_i^{uds}/3` | Seven-isotope natural-xenon halo fold; B is emitted separately from C |
| `research/three_body_full_current_nucleon_match/xe131_fixed_speed_charge_dsigma.py` | Formal finite-`t_N` diagnostic | `Fhat_i=F_i^{uds}/3` | Fixed-speed charge-sector kernels and ratios |
| `research/three_body_full_current_nucleon_match/xe131_full_afh_fixed_speed_recoil_scan.py` | Provisional full-current diagnostic | `Fhat_i=F_i^{uds}/3` | Six-channel matching; not yet a promoted D prediction |
| `research/afh_default_density_xe131/run_python_full_dsigma_xe131.py` | Legacy A reference | Constant effective coupling; no explicit finite-`t_N` Dirac--Pauli insertion | Historical Xe-131 absolute-spectrum comparison only |
| `research/afh_default_density_xe131/compute_four_benchmark_dsigma.py` | Legacy A reference | Constant effective coupling; no finite-`t_N` form-factor insertion | Historical four-benchmark Xe-131 comparison only |
| `research/three_body_calculation_and_validation/run_natural_xenon_joint.py` | Legacy A reference | Constant effective coupling; no finite-`t_N` Dirac--Pauli insertion | Historical natural-xenon isotope-sum comparison only |
| `research/afh_default_density_natural_xenon_halo/run_ame2020_natural_xenon_halo_fold.py` | Legacy A reference | Constant effective coupling; no finite-`t_N` Dirac--Pauli insertion | Historical AME2020 halo-fold comparison only |
| `research/afh_default_density_natural_xenon_halo/run_ame2020_direct_exactq_natural_xenon_halo_fold.py` | Legacy A reference | Constant effective coupling; no finite-`t_N` Dirac--Pauli insertion | Historical exact-q AME2020 halo-fold comparison only |
| `research/three_body_calculation_and_validation/run_natural_xenon_halo_fold.py` | Legacy A reference | AFH finite-size response with constant effective nucleon coupling | Historical halo-fold comparison only |
| `research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py` | Legacy A reference | AFH finite-size response with constant effective nucleon coupling | Historical halo-fold comparison only |
| `research/three_body_calculation_and_validation/mathematica_halo_notebook/three_body_rate_engine.wl` | Legacy A reference | Constant effective nucleon coupling; no explicit `F_1(t_N),F_2(t_N)` | Mathematica historical cross-check |
| `research/historical_three_body_calculations/mathematica_rate_calculation_archive/three_body_rate_engine.wl` | Archived A reference | Constant effective nucleon coupling; no explicit `F_1(t_N),F_2(t_N)` | Immutable Mathematica provenance archive |

The legacy A entries are intentionally preserved rather than silently rewritten: they document the calculation that generated the old reference results. Their output is not the adopted B prediction. The formal B production path is the first four rows, and every new absolute B result must record the external-`g_{VN}` coupling basis, the `Fhat_i` normalization, the one-body transfer convention, and the AFH factor-four ledger.

## 9. Reporting requirements

Every new result must report:
1. the B absolute spectrum or rate, using \(\widehat F_1(t_N),\widehat F_2(t_N)\) and finite-size AFH \(W_M(y_A)\) only;
2. B/A, which isolates the nucleon-current finite-\(t_N\) correction;
3. C/B, which isolates the additional charge multipoles;
4. C/A, which gives the total change relative to the historical AFH M-only reference;
5. the form-factor prescription, transfer convention, coupling basis, AFH normalization, interpolation provenance, and quadrature convergence.

Never call B a point-nucleus calculation. Never replace AFH \(W_M(y_A)\) with a constant. Never multiply a second whole-nucleus form factor onto AFH. Never use raw \(F_i^{uds}\) with an external \(g_{VN}\) prefactor; use \(\widehat F_i=F_i^{uds}/3\).
