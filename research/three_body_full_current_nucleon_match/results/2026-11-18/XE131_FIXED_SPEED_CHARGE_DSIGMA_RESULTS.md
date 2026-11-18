# Xe-131 fixed-speed charge-sector differential cross-section ratio

**Status:** Numerical result obtained for the fixed-speed Xe-131 differential cross-section ratio in the \(M+\Phi''+M\Phi''\) charge-density sector. This is not yet the complete \(L_{\mu\nu}W_A^{\mu\nu}\) result because the native Xe-131 spatial-response set is not part of the validated input.

## 1. Fixed benchmark

| Input | Value |
|---|---:|
| Target | Xe-131, \(J_A=3/2\) |
| Bare nuclear mass | \(m_A=121.9099224472\ \mathrm{GeV}\) |
| Dark-matter mass | \(m_{\chi_1}=1\ \mathrm{TeV}\) |
| Scalar mass | \(m_s=300\ \mathrm{keV}\) |
| Incident speed | \(v=776\ \mathrm{km\,s^{-1}}\) |
| Coupling entering the \(\chi_2\) width | \(g_2=1\) |
| \(E_R=200\ \mathrm{keV}\) | \(\Delta m=450\ \mathrm{keV}\) |
| \(E_R=267\ \mathrm{keV}\) | \(\Delta m=362\ \mathrm{keV}\) |
| Width schemes | pole and running; zero width is not used as the physical result |

The exact nuclear recoil momentum is
\[
q_A=\sqrt{2m_AE_R+E_R^2},
\]
giving
\[
q_A(200\ \mathrm{keV})=0.2208257434695511\ \mathrm{GeV},
\qquad
q_A(267\ \mathrm{keV})=0.2551469574104399\ \mathrm{GeV}.
\]

## 2. Quantity calculated

The comparison is
\[
\mathcal Q_{\sigma,\mathrm{ch}}^{131}(E_R,v)
=
\frac{(d\sigma_{131}^{M+\Phi''}/dE_R)_{\mathrm{finite}\ t_N}}
     {(d\sigma_{131}^{M\text{-only}}/dE_R)_{\mathrm{pointlike}}}.
\]

Within the charge-density factorization,
\[
\frac{d\sigma_{\mathrm{ch}}}{dE_R}
=
\mathcal C(E_R,v,\Delta m,\Gamma_{\chi_2})L_{00}^{(3)}
\left[
c_M^2W_M+
2c_Mc_{\Phi''}W_{M\Phi''}+
c_{\Phi''}^2W_{\Phi''}
\right],
\]
whereas the original pointlike \(M\)-only reference is
\[
\frac{d\sigma_{M,\mathrm{old}}}{dE_R}
=
\mathcal C(E_R,v,\Delta m,\Gamma_{\chi_2})L_{00}^{(3)}\,9W_M.
\]

Thus the common phase-space-integrated \(L_{00}^{(3)}\), propagator, flux, and coupling prefactor cancel:
\[
\boxed{
\mathcal Q_{\sigma,\mathrm{ch}}^{131}
=
\frac{
c_M^2W_M+
2c_Mc_{\Phi''}W_{M\Phi''}+
c_{\Phi''}^2W_{\Phi''}
}{9W_M}.
}
\]

The \(L_{00}^{(3)}\) factor is the same for the numerator and denominator. It contains the two coherent scalar-emission diagrams and the chosen finite-width \(\chi_2\) propagator. Therefore pole and running widths change the absolute differential cross sections, but not this factorized charge-sector ratio.

The finite-\(t_N\) coefficients are
\[
c_M=F_1^V+\frac{t_N(F_1^V+2F_2^V)}{8m_N^2},
\qquad
c_{\Phi''}=\frac{q_A^2(F_1^V+2F_2^V)}{4m_N^2},
\qquad t_N=-q_A^2.
\]
The original denominator is specifically \(F_1^V(0)^2W_M=9W_M\). The numerator therefore uses \(c_M^2\), not \(F_1^2\).

## 3. Native AFH input and interpolation

The nuclear input is the native AFH v6.0 Xe-131 \(M,\Phi'',M\Phi''\) export from PR #51:
- 2,401 points on \(q_A\in[0,0.6]\ \mathrm{GeV}\), with \(\Delta q_A=0.00025\ \mathrm{GeV}\);
- native Wolfram 14.2.0 execution and validated Xe-131 density matrix;
- physical equal-\(p,n\) response columns, with the AFH factor of four applied exactly once;
- interpolation of the absolute response functions with PCHIP; linear interpolation is retained as a cross-check.

The finite-\(Q^2\) form factors use the central isoscalar z-expansion diagnostic in nucleon_vector_form_factors.py. This is not yet a final model-specific \(u+d+s\) form-factor determination, especially for \(F_2^V(Q^2)\).

## 4. Numerical results

### 4.1 \(E_R=200\ \mathrm{keV}\)

Native AFH PCHIP values at the exact recoil momentum:
\[
\frac{W_{\Phi''}}{W_M}=0.03695635,
\qquad
\frac{W_{M\Phi''}}{W_M}=-0.19121037.
\]

Finite-\(t_N\) nucleon-current input:
\[
F_1^V=2.66316290,\qquad F_2^V=-0.46805334,
\]
\[
c_M=2.65122135,\qquad c_{\Phi''}=0.02388309.
\]

The finite-\(t_N\) \(M\)-only factor relative to the old baseline is
\[
\frac{c_M^2}{9}=0.78099718
\quad(-21.9003\%).
\]
The additional \(\Phi''\) correction relative to finite-\(t_N\) \(M\)-only is
\[
Q_{\Phi''}-1=-0.34420\%.
\]

The resulting fixed-speed differential cross-section ratio is
\[
\boxed{
\mathcal Q_{\sigma,\mathrm{ch}}^{131}(200\ \mathrm{keV},776\ \mathrm{km/s})
=0.77830901,
}
\]
or
\[
\boxed{\Delta\sigma_{\mathrm{ch}}=-22.1691\%.}
\]

### 4.2 \(E_R=267\ \mathrm{keV}\)

This point lies in the deep \(W_M\) cancellation region. Native AFH PCHIP values at the exact recoil momentum give
\[
\frac{W_{\Phi''}}{W_M}=19.85124,
\qquad
\frac{W_{M\Phi''}}{W_M}=-4.28355.
\]

Finite-\(t_N\) nucleon-current input:
\[
F_1^V=2.56388562,\qquad F_2^V=-0.44977440,
\]
\[
c_M=2.54852260,\qquad c_{\Phi''}=0.03072605.
\]

The finite-\(t_N\) \(M\)-only factor relative to the old baseline is
\[
\frac{c_M^2}{9}=0.72166305
\quad(-27.8337\%).
\]
The additional \(\Phi''\) correction relative to finite-\(t_N\) \(M\)-only is
\[
Q_{\Phi''}-1=-10.0403\%.
\]

The resulting fixed-speed differential cross-section ratio is
\[
\boxed{
\mathcal Q_{\sigma,\mathrm{ch}}^{131}(267\ \mathrm{keV},776\ \mathrm{km/s})
=0.64920593,
}
\]
or
\[
\boxed{\Delta\sigma_{\mathrm{ch}}=-35.0794\%.}
\]

## 5. Interpolation and normalization audits

| \(E_R\) | PCHIP ratio | Linear-interpolation ratio | PCHIP minus linear |
|---:|---:|---:|---:|
| 200 keV | 0.77830901 | 0.77830906 | \(-4.64\times10^{-8}\) |
| 267 keV | 0.64920593 | 0.64995339 | \(-7.47\times10^{-4}\) |

The 267-keV local response ratios are sensitive to interpolation near the deep \(W_M\) minimum. The corresponding cross-section-ratio shift is \(0.075\) percentage point.

A normalization audit also identifies the source of the earlier quoted \(-21.48\%\) and \(-34.24\%\) values: those values are reproduced approximately by multiplying \(Q_{\Phi''}\) by \(F_1(Q^2)^2/9\). The matched \(M\)-operator coefficient is \(c_M\), so the consistent numerator is \(c_M^2\), not \(F_1^2\). With the PCHIP response interpolation and the consistent \(c_M^2\) coefficient, the corrected values are \(-22.1691\%\) and \(-35.0794\%\). Linear interpolation with the same corrected coefficient gives \(-22.1691\%\) and \(-35.0047\%\).

## 6. Interpretation and limits

These are **fixed-Xe-131, fixed-speed differential cross-section ratios in the charge-density sector**, not pure nuclear-response ratios and not halo-folded recoil-spectrum ratios.

They include:
- the native Xe-131 \(M,\Phi'',M\Phi''\) nuclear responses;
- the finite-\(t_N\) \(F_1^V,F_2^V\) diagnostic;
- the common three-body phase-space factor through \(L_{00}^{(3)}\), which cancels in the ratio;
- the two coherent scalar-emission diagrams and finite-width \(\chi_2\) prescription in that common factor.

They do **not** yet include:
- a native-validated Xe-131 \(\Delta,\Sigma',\Sigma''\) spatial-response contraction;
- a final validated universal finite-\(Q^2\) \(u+d+s\) form-factor set;
- a halo velocity average, natural-xenon isotope sum, or detector response.

Consequently, the ratios above answer the fixed-speed Xe-131 **charge-sector** question. They must not be presented as the final complete-current or natural-xenon recoil-spectrum correction.
