# Form-factor baseline comparison: A / B / C / D

**Status:** B is the adopted production baseline. The code and regression
repairs are being validated on PR #67; this document defines the comparison
and the provenance rules. Do not promote a result to B until its code path
and run metadata pass the corresponding checks.

## 1. Two different physical layers

The single-nucleon Dirac--Pauli form factors describe the internal structure
of one proton or neutron:

\[
F_1^{V,N}(t_N),\qquad F_2^{V,N}(t_N).
\]

The AFH response describes the finite-size coherent response of the entire
nucleus:

\[
W_M^{\tau\tau'}(y_A),\qquad
y_A=\frac{b_A^2Q_A^2}{4}.
\]

They are not interchangeable. In particular, AFH \(W_M\) is already a
finite-size nuclear response; it is not a point-nucleus response.

## 2. Coupling and normalization convention

The quark interaction is universal over \(u,d,s\), and the external
rate prefactor is written using

\[
g_{VN}=3g_{Vq}.
\]

The raw flavor-summed nucleon form factors have

\[
F_1^{uds,N}(0)=3,\qquad F_2^{uds,N}(0)=-0.552.
\]

Therefore the current coefficients must use

\[
\boxed{
\widehat F_i^N(t_N)=\frac{F_i^{uds,N}(t_N)}{3}
}
\]

with

\[
\widehat F_1^N(0)=1,\qquad
\widehat F_2^N(0)=-0.184.
\]

The factor of three is already in \(g_{VN}\); using the raw form factors
again in the nucleon current double-counts it and multiplies an absolute
rate by nine. This normalization is independent of the AFH factor of four.

For the raw AFH v6.0 isoscalar response,

\[
R_{\rm AFH,raw}(q_A)
=\frac{4\pi}{2J_A+1}W_{M,\rm raw}^{00}(y_A),
\qquad
R_{\rm AFH,raw}(0)\simeq\frac{A^2}{4}.
\]

The physical equal-proton/equal-neutron response is

\[
R_A^{\rm phys}(q_A)
=4C_0(A)R_{\rm AFH,raw}(q_A),
\qquad
R_A^{\rm phys}(0)=A^2.
\]

The factor four and the small \(C_0(A)\) normalization correction are
applied once in the physical AFH response. They must not be folded into
the nucleon form factors or repeated in the cross-section prefactor.

## 3. Exact transfer conventions

For an initially stationary nucleus,

\[
q_A^\mu=P_A'^\mu-P_A^\mu,
\qquad
t_A=q_A^2=-2m_AE_R.
\]

The exact spatial momentum is

\[
Q_A^2=|\boldsymbol q_A|^2
=2m_AE_R+E_R^2.
\]

The adopted one-body impulse prescription for B is

\[
q_N^\mu=q_A^\mu,
\qquad
\boxed{t_N=t_A=-2m_AE_R}.
\]

Consequently:

- \(t_N\) enters the nucleon form factors and \(c_M\);
- \(Q_A^2\) enters the AFH variable \(y_A\) and the spatial-momentum
  coefficient \(c_{\Phi''}\);
- the mediator propagator uses \((m_V^2-t_A)^2
  =(m_V^2+2m_AE_R)^2\).

The separate static diagnostic \(q_N^0=0\), for which
\(t_N=-Q_A^2\), must never be substituted into the formal B production
path.

## 4. The A / B / C / D hierarchy

All four rows below use the same isotope-specific finite-size AFH nuclear
response and exact spatial recoil momentum.

| Label | Single-nucleon current | Nuclear response | Interpretation |
|---|---|---|---|
| **A** | \(\widehat F_1(0)=1,\widehat F_2(0)=-0.184\) | \(W_M^{\rm phys}(y_A)\) | Zero-transfer nucleon-current reference; not a point nucleus |
| **B** | \(\widehat F_{1,2}(t_N)\), with \(t_N=t_A\) | \(W_M^{\rm phys}(y_A)\) | **Adopted production baseline** |
| **C** | Same finite-\(t_N\) current as B | \(W_M,W_{\Phi''},W_{M\Phi''}\) with matched coefficients | Additional charge-multipole extension |
| **D** | Full matched one-body Dirac--Pauli current | All required AFH responses and interference terms | Full one-body-current target, pending P3-C completion |

The B charge coefficient is

\[
\boxed{
\widehat c_M(t_N)
=
\widehat F_1^N(t_N)
+\frac{t_N[\widehat F_1^N(t_N)+2\widehat F_2^N(t_N)]}
{8m_N^2}
}
\]

and its nuclear kernel is

\[
K_B=\widehat c_M(t_N)^2W_M^{\rm phys}(y_A).
\]

For C, add the matched charge terms

\[
K_C=K_B
+2\widehat c_M\widehat c_{\Phi''}W_{M\Phi''}^{\rm phys}
+\widehat c_{\Phi''}^{\,2}W_{\Phi''}^{\rm phys},
\]

where

\[
\widehat c_{\Phi''}
=
\frac{Q_A^2[\widehat F_1^N(t_N)+2\widehat F_2^N(t_N)]}
{4m_N^2}.
\]

Do not add \(W_{\Phi''}\) to B. C is a separate diagnostic extension;
D requires the full three-body particle coefficients and the validated
spatial nuclear multipoles.

## 5. Adopted low-momentum form-factor prescription

The adopted B truncation uses the flavor-separated Dirac slope from
Bishara et al. and the available leading constant Pauli term:

\[
F_1^{uds,N}(t_N)=3+8.392\,t_N+O(t_N^2),
\qquad
F_2^{uds,N}(t_N)=-0.552+O(t_N).
\]

After conversion to the external-\(g_{VN}\) basis,

\[
\widehat F_1^N(t_N)=1+\frac{8.392}{3}t_N+O(t_N^2),
\qquad
\widehat F_2^N(t_N)=-0.184+O(t_N).
\]

No finite-\(t_N\) Pauli slope is invented. The isoscalar electromagnetic
z-expansion remains an alternate sensitivity prescription and is not
the adopted B production input.

## 6. Xe-131 fixed-speed anchor values

At the two established recoil anchors, the adopted Bishara-linear
prescription gives

| \(E_R\) | \(B/A\) | \(C/B\) | \(C/A\) |
|---:|---:|---:|---:|
| 200 keV | 0.7398828761 | 0.9969554024 | 0.7376302305 |
| 267 keV | 0.6621749872 | 0.9146639874 | 0.6056676141 |

The 267 keV row uses the exact native AFH responses at q(267 keV)=0.255146745 GeV. The merged 2,509-point dense-grid PCHIP anchor is C/A=0.6056675913, a 2.3e-8 interpolation residual.

The B/A column isolates the finite single-nucleon form-factor correction.
The C/B column isolates the additional charge-multipole correction at
fixed B nucleon current. C/A is their combined effect. The 267-keV
ratio is near a deep \(W_M\) cancellation and must be interpreted
alongside the absolute response values.

These are fixed-speed Xe-131 charge-sector ratios. They are not a
natural-xenon halo rate, detector prediction, or complete
\(L_{\mu\nu}^{(3)}W_A^{\mu\nu}\) result.

## 7. Historical result classification

The following results remain useful but are not B:

1. **Original Mathematica \(W_M\) rate engine:** A-like constant-current
   reference with finite-size AFH \(W_M\); not B.
2. **Legacy \(9W_M\) curve:** raw \(F_1^{uds}(0)=3\) was combined with
   the external \(g_{VN}\) prefactor. It is a raw-normalization
   historical reference, not a point nucleus and not an absolute
   physical rate.
3. **Static form-factor diagnostics:** use \(t_N=-Q_A^2\); useful for
   testing the \(q_N^0=0\) approximation, not formal B.
4. **Alternate isoscalar-z-expansion results:** sensitivity diagnostics,
   not the adopted Bishara-linear B input.
5. **Raw P3-C coefficient archive:** useful for helicity/Cartesian
   structural checks, but its absolute particle coefficients carry
   the factor-nine normalization warning. The normalized
   \(g_{VN}\)-basis output is the physical coefficient convention.
6. **Historical full-recoil and six-channel scans:** preserve their
   CSVs, plots, workflow IDs, and hashes. Relabel them as historical
   diagnostics; do not silently replace their numerical contents.

The corrected code must write raw and effective form factors to distinct
fields, record \(t_N\), \(Q_A^2\), and \(t_A\) separately, and state
which A/B/C/D level each output represents.

## 8. Required regression gates

Before promoting the current PR #67 branch:

- [ ] effective_nucleon_form_factors(3,-0.552) returns (1,-0.184).
- [ ] charge_coefficients requires an explicit \(t_N\) and uses
      \(Q_A^2\) only for \(c_{\Phi''}\).
- [ ] Formal B tests \(t_N=-2m_AE_R\) and distinguishes it from
      \(-Q_A^2\).
- [ ] P3 defaults and serialized F1N_effective / F2N_effective fields
      use the effective basis.
- [ ] Fixed-speed anchors reproduce B/A, C/B, and C/A above.
- [ ] The absolute spectrum outputs A, B, and C separately, with B
      identified as the production baseline.
- [ ] The native seven-isotope halo fold passes its artifact,
      kinematic, normalization, and numerical-convergence gates.
- [ ] Paper formulas use \(m_N\) for a free nucleon and \(m_A\) for
      the nucleus; \(F_A\) is reserved for the whole-nucleus shape
      function and is not confused with \(W_M\).

