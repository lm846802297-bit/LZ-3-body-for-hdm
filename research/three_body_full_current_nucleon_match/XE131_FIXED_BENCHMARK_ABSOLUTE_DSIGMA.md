# Xe-131 fixed-benchmark absolute differential cross section: adopted B baseline

**Status:** Code and regression tests have been updated to the adopted B
prescription. The new absolute spectrum must be regenerated and pass the
PR #67 workflow before its CSV/PDF/SVG outputs are promoted. Earlier output
and provenance are historical and are not overwritten.

## 1. Fixed benchmark

| Input | Value |
|---|---:|
| \(m_{\chi_1}\) | 1,000 GeV |
| \(m_{\chi_2}\) | 1,000.00045 GeV |
| \(\Delta m\) | 450 keV, fixed at every recoil |
| \(m_s\) | 300 keV |
| \(m_V\) | 10 GeV |
| \(v\) | 776 km/s |
| \(g_2\) (width input) | 1 |
| \((g_1g_2g_{VN})^2\) | 1 |
| width prescription | asymmetric pole-width prescription |
| target | Xe-131 |

The target mass follows the repository's canonical bare-nucleus convention,

\[
m_A=(M_{\rm atom}-54m_e)u
=121.90971983538435~\mathrm{GeV}.
\]

The response input is the provenance-pinned native AFH v6.0 Xe-131
\(W_M,W_{\Phi''},W_{M\Phi''}\) archive. The native export already
contains the equal-proton/equal-neutron factor four, while its metadata
records \(\texttt{shape\_renormalization\_applied=false}\). The loader
therefore derives
\[
C_0(131)=\frac{131^2}{4R_{M,\rm raw}(0)}
=1.0000825298069376
\]
and applies this common OBDME correction exactly once to all three
physical charge responses. Thus \(R_M^{\rm phys}(0)=131^2\).

## 2. Formal B kinematics and form factors

For every recoil,

\[
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2,
\qquad
t_A=q_A^2=-2m_AE_R.
\]

The formal one-body impulse prescription is

\[
q_N^\mu=q_A^\mu,
\qquad
\boxed{t_N=t_A=-2m_AE_R}.
\]

Thus \(t_N\), not \(-Q_A^2\), is passed to the nucleon form factors.
The exact spatial \(Q_A^2\) is used in the AFH variable

\[
y_A=\frac{b_A^2Q_A^2}{4}.
\]

The mediator denominator is Lorentz invariant:

\[
(m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2.
\]

The universal raw flavor-summed form factors satisfy
\(F_1^{uds,N}(0)=3\) and \(F_2^{uds,N}(0)=-0.552\). Since the external
prefactor contains \(g_{VN}=3g_{Vq}\), the effective nucleon form factors
are

\[
\widehat F_i^N(t_N)=F_i^{uds,N}(t_N)/3,
\]

with \(\widehat F_1^N(0)=1\) and \(\widehat F_2^N(0)=-0.184\).

The adopted B truncation uses the Bishara linear Dirac slope and the
available constant Pauli anchor:

\[
F_1^{uds,N}(t_N)=3+8.392t_N+O(t_N^2),
\qquad
F_2^{uds,N}(t_N)=-0.552+O(t_N).
\]

No unsupported finite-\(t_N\) Pauli slope is assumed.

The matched coefficients are

\[
\widehat c_M(t_N)=
\widehat F_1^N(t_N)+
\frac{t_N[\widehat F_1^N(t_N)+2\widehat F_2^N(t_N)]}
{8m_N^2},
\]

\[
\widehat c_{\Phi''}(t_N,Q_A^2)=
\frac{Q_A^2[\widehat F_1^N(t_N)+2\widehat F_2^N(t_N)]}
{4m_N^2}.
\]

## 3. A/B/C differential cross sections

A is the zero-transfer effective-nucleon-current reference:

\[
K_A=L_C^{(3)}W_M^{\rm phys}(y_A).
\]

It is not a point nucleus. The same finite-size AFH \(W_M\) is retained
in all three calculations.

The adopted B production baseline is M-only:

\[
\boxed{
\frac{d\sigma_B}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2(m_V^2-t_A)^2}
\,
\widehat c_M(t_N)^2
W_M^{\rm phys}(y_A)
\,
L_C^{(3)}.
}
\]

C is a separate charge-multipole extension:

\[
K_C=L_C^{(3)}
\left[
\widehat c_M^2W_M^{\rm phys}
+2\widehat c_M\widehat c_{\Phi''}W_{M\Phi''}^{\rm phys}
+\widehat c_{\Phi''}^{\,2}W_{\Phi''}^{\rm phys}
\right].
\]

B is the production baseline. C must not be substituted for B without
explicitly identifying the additional \(\Phi''\) and signed
\(M-\Phi''\) terms. The continuity-reduced weight

\[
L_C^{(3)}=
L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}
\]

is conditional on conservation of the complete nuclear one-body vector
current; it is not a Ward identity imposed on the inelastic DM transition
current.

## 4. Expected fixed-speed A/B/C anchors

The adopted Bishara-linear prescription gives the following nuclear-kernel
ratios, independent of the common three-body phase-space factor:

| \(E_R\) | \(B/A\) | \(C/B\) | \(C/A\) |
|---:|---:|---:|---:|
| 200 keV | 0.7398828761 | 0.9969554024 | 0.7376302305 |
| 267 keV | 0.6621749872 | 0.9146639874 | 0.6056676141 |

The 267 keV row uses the exact native AFH responses at q(267 keV)=0.255146745 GeV. The merged 2,509-point dense-grid PCHIP anchor is C/A=0.6056675913, a 2.3e-8 interpolation residual.

These anchors are regression targets for the absolute-spectrum code.
They are not themselves absolute cross sections or halo-averaged rates.

## 5. Numerical prescription and scope

- Integrate the coherent two-diagram spin-resolved DM current over the
  complete three-body phase space.
- Use the asymmetric pole-width prescription: the first \(p-k\)
  propagator is zero-width and the second \(p'+k\) propagator carries
  the constant pole width.
- Use the native AFH v6.0 response archive and its provenance-pinned
  2,401-point \(q_A\) grid with PCHIP interpolation.
- Use the fixed \(\Delta m=450\) keV benchmark over the entire recoil
  interval.
- Compare medium/high quadrature orders and independently reproduce the
  public Eq. (6) \(L_{00}\) integral.
- Output A, B, and C separately in the CSV, metadata, and publication plot.
  B is the central production curve.

This remains a single-isotope, fixed-speed, coherent charge-sector
calculation. It does not include the native transverse
\(\Delta,\Sigma'\), and \(\Sigma'-\Delta\) sector, halo averaging,
natural-xenon isotope summation, detector response, exposure, event
counts, or an exclusion. It is not the complete
\(L_{\mu\nu}^{(3)}W_A^{\mu\nu}\) prediction.

## 6. Historical outputs

The earlier absolute-spectrum output used the raw \(F_1^{uds}(0)=3\)
normalization together with the external \(g_{VN}\) prefactor, giving
a factor-nine absolute normalization error. Its static
\(t_N=-Q_A^2\) and alternate isoscalar-z-exp form-factor inputs also
differ from formal B. The earlier output is historical and must not be
overwritten or cited as B. The corrected run will use distinct workflow
artifacts and record its own CSV, metadata, SVG, PDF, and SHA-256 values.

