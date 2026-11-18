# Xe-131 fixed-benchmark absolute differential cross section

**Scope:** fixed-speed, single-isotope absolute \(d\sigma/dE_R\) in the native-AFH coherent charge sector \(M+\Phi''+M\Phi''\). This is not the complete six-channel nuclear-vector-current result.

## Fixed benchmark

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
| width prescription | zero width |
| target | Xe-131 |

The target mass follows the current repository isotope-mass convention:
\[
m_A=(M_{\rm atom}-54m_e)u
=121.90971983538435~\mathrm{GeV}.
\]
This supersedes the older \(131u=122.02572741702\) GeV approximation used by the 2026-11-13 exploratory curve. The AFH response factor of four is already included once in the physical equal-proton/neutron response; it is not applied again.

## Cross-section formula

The absolute charge-sector differential cross section is obtained by restoring the common three-body phase-space, incident-flux, mediator and coupling factors:
\[
\frac{d\sigma_{\rm ch}}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2(m_V^2+Q_A^2)^2}
L_C^{(3)}
\left[
c_M^2W_M+
2c_Mc_{\Phi''}W_{M\Phi''}
+c_{\Phi''}^2W_{\Phi''}
\right].
\]
Here \(Q_A^2=2m_AE_R+E_R^2\) is the exact nuclear mass-shell transfer and \(p_{\chi_1}=m_{\chi_1}\gamma v/c\). The continuity-reduced weight is
\[
L_C^{(3)}=
L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
\]
This reduction is conditional on continuity of the complete nuclear one-body vector current. The DM transition current is not assumed to be conserved. The charge coefficients use the central finite-\(Q^2\) isoscalar-z-expansion diagnostic:
\[
c_M=F_1^V-\frac{Q_A^2(F_1^V+2F_2^V)}{8m_N^2},
\qquad
c_{\Phi''}=\frac{Q_A^2(F_1^V+2F_2^V)}{4m_N^2}.
\]
The kernel has units GeV\(^2\), the public prefactor GeV\(^{-5}\), and \(d\sigma/dE_R\) GeV\(^{-3}\). Conversion to cm\(^2\)/keV uses \(3.893793721\times10^{-34}\).

## Numerical prescription

- Integrate the coherent two-diagram spin-resolved DM current over the complete \(2\to3\) phase space.
- Use the zero-width prescription of the fixed benchmark; the \(\chi_2\) pole remains closed throughout the fixed-\(\Delta m=450\) keV interval.
- Use the provenance-pinned 2,401-point native AFH v6.0 \(W_M,W_{\Phi''},W_{M\Phi''}\) archive with PCHIP interpolation.
- Use a 2-keV global recoil grid and 0.5-keV refinement around the AFH response minima, including exact kinematic endpoints.
- Compare the curve-order integral with independent higher-order anchors.
- Cross-check the spin-resolved \(L_{00}^{(3)}\) against the legacy Eq. (6) integral.

## Explicit scope limits

This is an absolute **charge-sector** spectrum, not the final complete \(L_{\mu\nu}W_A^{\mu\nu}\) spectrum. Native transverse \(\Delta,\Sigma'\), and \(\Sigma'-\Delta\) response validation and the P3-C bound-nucleus amplitude-level contraction remain separate gates. The finite-\(Q^2\) \(F_1^V,F_2^V\) prescription is diagnostic, especially for \(F_2^V(Q^2)\). No halo average, isotope sum, detector response, exposure, event count or exclusion is included. The absolute normalization is the stated unit reference \((g_1g_2g_{VN})^2=1\); other coupling choices rescale the result linearly.
