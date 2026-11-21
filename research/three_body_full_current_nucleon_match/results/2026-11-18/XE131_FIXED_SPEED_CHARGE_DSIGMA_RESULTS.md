# Xe-131 fixed-speed native AFH Coulomb-sector differential cross-section ratio

> **SUPERSEDED FOR PRODUCTION NORMALIZATION (2026-11-19):** This archived result used the old (9W_M) M-only normalization label. (W_M(Q_A)) itself is finite-size AFH, not a point nucleus; however, in the adopted external-(g_{VN}) convention the raw (F_1^{uds}(0)=3) must be divided by three before entering the current coefficient. Do not use this artifact's absolute normalization as B. Recompute with (widehat F_i=F_i^{uds}/3), Bishara low-(Q_N^2), and B-only (W_M(y_A)). Its dimensionless old-prescription ratios are historical diagnostics only.

**Status:** \`PASS_XE131_FIXED_SPEED_COULOMB_SECTOR_RATIO\`

**Workflow:** run 44262472992  
**Artifact:** 14408816831  
**Artifact SHA-256:** \`3d63f0d4896946129e1692ee0915da9b6d791323f65da85d0ee242bc1ae498bd\`

## 1. Scope

This calculation compares the fixed-speed Xe-131 differential cross section
from the finite-\(t_N\) Coulomb sector
\[
M+\Phi''+M\Phi''
\]
with the original pointlike \(9W_M\)-only benchmark. It integrates the
complete three-body DM phase space with both scalar-radiation diagrams and
their coherent interference, including pole and running \(\chi_2\) widths.

It is **not** an absolute \(d\sigma/dE_R\), halo average, natural-xenon isotope
sum, detector prediction, or complete vector-current contraction. Native
transverse \(\Delta,\Sigma'\), and \(\Sigma'\)-\(\Delta\) responses are not
included.

## 2. Kinematics and native AFH input

| Quantity | Value |
|---|---:|
| \(m_{\chi_1}\) | 1,000 GeV |
| \(m_s\) | 300 keV |
| \(g_2\) | 1 |
| \(v\) | 776 km/s |
| \(m_V\) (common prefactor only) | 10 GeV |
| Xe-131 atomic mass | 130.90508406 u |
| Xe-131 bare-nucleus mass | 121.90971983538435 GeV |

The mass is taken from the repository's canonical isotope-mass input with
\[
m_A=[M_{\rm atom}-54m_e]u.
\]
For every recoil,
\[
Q_A=q_A=\sqrt{2m_AE_R+E_R^2}.
\]
The nucleon invariant in the static impulse matching is
\(t_N=-Q_A^2\).

The native AFH input is AFH DMFormFactor v6.0 executed with Wolfram 14.2.0.
It contains 2,401 q nodes from 0 to 0.6 GeV in 0.00025 GeV steps and the
physical equal-\(p=n\) response columns \(W_M,W_{\Phi''},W_{M\Phi''}\), with
the factor of four applied once.

Provenance:
- original native export commit:
  \`54e1ff10bba0cbffe7acc6af428014415c708475\`;
- reconciled archive commit:
  \`e6d9dee3527cab200ee6b21198d577b987282fac\`;
- AFH source SHA-256:
  \`dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372\`;
- density-matrix CSV SHA-256:
  \`f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45\`;
- canonical-LF native CSV SHA-256:
  \`b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff\`;
- canonical metadata SHA-256:
  \`ad8231ec92c71faf12631534871e192bc3000601514c2a369fc84d963bfa9887\`;
- canonical validation SHA-256:
  \`6d199ac9fd4d7fdace93292d1dded1c98d9f49c2836244ee9d2e3ddd334e8333\`.

The CSV is checked after UTF-8 CRLF-to-LF canonicalization. Both the raw
checkout hash and canonical hash are recorded; the metadata-to-validation
hash link and the three-file manifest are independently checked.

## 3. Coulomb-sector formula

For a conserved one-body nuclear vector current,
\[
J_A^3=\frac{E_R}{Q_A}J_A^0,
\]
so the effective leptonic Coulomb weight is
\[
L_C^{(3)}
=L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
\]
This is conditional on nuclear-current continuity; it is not a Ward identity
imposed on the inelastic DM transition current.

The finite-\(t_N\) charge coefficients are
\[
c_M=F_1^V+\frac{t_N(F_1^V+2F_2^V)}{8m_N^2},
\qquad
c_{\Phi''}=\frac{Q_A^2(F_1^V+2F_2^V)}{4m_N^2}.
\]
The ratio is
\[
{\cal Q}_{\rm Xe131}
=
\frac{
c_M^2W_M+2c_Mc_{\Phi''}W_{M\Phi''}
+c_{\Phi''}^2W_{\Phi''}
}{
9W_M
}.
\]
The common phase-space-integrated \(L_C^{(3)}\), mediator, flux, and
coupling prefactors cancel between numerator and denominator. Thus this
ratio is independent of the pole/running width, although the absolute
differential cross sections are not.

## 4. Results

| \(E_R\) | \(\Delta m\) | \(Q_A\) (GeV) | finite-\(t_N\) \(M\)-only / pointlike \(9W_M\) | full Coulomb ratio | relative change |
|---:|---:|---:|---:|---:|---:|
| 200 keV | 450 keV | 0.220825560 | 0.780997494 | 0.778309339 | \(-22.1691\%\) |
| 267 keV | 362 keV | 0.255146745 | 0.721663420 | 0.649215911 | \(-35.0784\%\) |

The finite-\(t_N\) form factors and response ratios are:

| \(E_R\) | \(F_1^V\) | \(F_2^V\) | \(c_M\) | \(c_{\Phi''}\) | \(W_{\Phi''}/W_M\) | \(W_{M\Phi''}/W_M\) |
|---:|---:|---:|---:|---:|---:|---:|
| 200 keV | 2.663163406 | -0.468053440 | 2.651221878 | 0.023883057 | 0.036955941 | -0.191209297 |
| 267 keV | 2.563886256 | -0.449774513 | 2.548523254 | 0.030726003 | 19.845062582 | -4.282964386 |

The \(\Phi''\) correction relative to finite-\(t_N\) \(M\)-only is
\[
\frac{{\cal Q}_{\rm Xe131}}{c_M^2/9}-1
=
\begin{cases}
-0.3442\%,&E_R=200~{\rm keV},\\
-10.0390\%,&E_R=267~{\rm keV}.
\end{cases}
\]
The 267 keV point lies near the native \(W_M\) cancellation region, which
explains the large local \(\Phi''\) sensitivity.

For comparison, retaining the older \(F_1^2\) normalization instead of the
matched \(c_M^2\) baseline would give \(-21.4664\%\) and \(-34.2933\%\).
The reported results use the \(c_M^2\) normalization consistently.

## 5. Numerical checks

| Check | 200 keV | 267 keV |
|---|---:|---:|
| \(L_C/L_{00}-1\), pole width | \(-4.35056\times10^{-6}\) | \(-5.03498\times10^{-6}\) |
| \(L_C/L_{00}-1\), running width | \(-4.35098\times10^{-6}\) | \(-5.03395\times10^{-6}\) |
| medium/high \(L_C\) relative difference, worst width | \(1.98\times10^{-10}\) | \(4.73\times10^{-10}\) |
| maximum pole/running ratio spread | \(2.22\times10^{-16}\) | \(1.11\times10^{-16}\) |
| PCHIP minus linear ratio | \(-4.64\times10^{-8}\) | \(-7.47436\times10^{-4}\) |

The 267 keV PCHIP/linear difference corresponds to 0.0747 percentage point
in the ratio. It is retained as an interpolation sensitivity near the deep
\(W_M\) minimum; the PCHIP result is the reported central value.

## 6. Form-factor and interpretation limits

The finite-\(Q^2\) form factors use the current central
\`isoscalar_zexp\` diagnostic from \`nucleon_vector_form_factors.py\`. This is
not yet a final model-specific universal \(u+d+s\) form-factor set,
especially for \(F_2^V(Q^2)\).

The result is Xe-131 only and fixed speed. It does not establish the
seven-isotope natural-xenon rate. The independent seven-isotope/eight-response
native AFH run remains queued on the self-hosted runner. The three-response
Xe-131 archive cannot replace that gate and does not validate the transverse
AFH responses.

The spatial-sector estimate
\(|R_{\rm spatial}/R_{\rm Coulomb}|<7.1\times10^{-9}\) comes from the
provisional 84-row fixed-speed Python contraction only. It is not a global
bound and is not used to discard \(\Delta,\Sigma'\), or
\(\Sigma'\)-\(\Delta\) from the final vector-current kernel.
