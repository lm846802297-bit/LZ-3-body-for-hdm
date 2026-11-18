# Three-body \(M+\Phi''\) vector-charge matching with AFH Xe-131 responses

**Status:** the vector-charge \(M+\Phi''\) coefficient is derived and
contracted with the existing PR #53 three-body \(I_{00}\) kernels. Numerical
form factors are held at their adopted zero-momentum anchors. This is a
matched charge-sector result, not the complete all-current natural-xenon
prediction.

## 1. What this calculation combines

- PR #53 supplies the exact spin-resolved radiative current and the
  phase-space-integrated \(I_{00}\) kernel, including the two coherent
  scalar-emission diagrams and the selected width prescriptions.
- PR #54 supplies the independent AFH v6.0 Xe-131 responses
  \(W_M\), \(W_{\Phi''}\), and \(W_{M\Phi''}\) on 2401 momentum points, plus
  exact selected points at the \(W_M\) minima.
- This PR combines these inputs only in the vector-charge sector. It does
  not recompute either source dataset and does not add the spatial-current
  \(\Delta\), \(\Sigma'\), or \(\Sigma''\) responses.

## 2. Fixed current and momentum conventions

The momentum delivered to the target nucleon is
\[
q_A^\mu=k'^\mu-k^\mu,\qquad t_A=q_A^2=-|\boldsymbol q_A|^2.
\]
Use
\[
J_N^\mu(q_A)=
\bar u_N(k')
\left[
F_1^{V,N}(t_A)\gamma^\mu+
\frac{iF_2^{V,N}(t_A)}{2m_N}
\sigma^{\mu\nu}q_{A,\nu}
\right]u_N(k).
\]
The plus Pauli sign is tied to \(q_A=k'-k\). Hoferichter--Menéndez--Schwenk
use \(q=k-k'=-q_A\) and the equivalent vertex with a minus sign.

For the AFH Fourier operators the elastic-reference momentum is
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\). In the radiative process,
\[
\boldsymbol p_\chi'-\boldsymbol p_\chi
=-\boldsymbol q_A-\boldsymbol k_s.
\]
The AFH nuclear momentum is the momentum flowing through the nucleon
current, not the full dark-matter momentum change. The scalar momentum
remains inside \(\mathcal T_3^\mu\).

## 3. Derivation of the charge coefficients

Hoferichter, Menéndez, and Schwenk, PRD 102, 074018 (2020), Eq. (41),
give the nonrelativistic one-nucleon vector charge
\[
J_N^0 =
F_1^{V,N}(t_A)
+\frac{t_A}{8m_N^2}
  \left[F_1^{V,N}(t_A)+2F_2^{V,N}(t_A)\right]
-\frac{i}{4m_N^2}
  \left[F_1^{V,N}(t_A)+2F_2^{V,N}(t_A)\right]
  \boldsymbol S_N\cdot
  (\boldsymbol q_{\rm AFH}\times\boldsymbol P_N),
\]
where \(\boldsymbol P_N=\boldsymbol k+\boldsymbol k'\) and
\(\boldsymbol S_N=\boldsymbol\sigma_N/2\).

The spin-orbit term maps to the AFH \(\Phi''\) operator of
Anand--Fitzpatrick--Haxton, PRC 89, 065501 (2014), Eq. (51). Therefore
\[
\boxed{
c_M=F_1^V(t_A)
+\frac{t_A}{8m_N^2}\left[F_1^V(t_A)+2F_2^V(t_A)\right],
}
\]
\[
\boxed{
c_{\Phi''}=
\frac{|\boldsymbol q_A|^2}{4m_N^2}
\left[F_1^V(t_A)+2F_2^V(t_A)\right].
}
\]
The sign corresponds to the conventions in Sec. 2.

An important statement immediately following Eq. (41) of
Hoferichter--Menéndez--Schwenk is that the spacelike components do not
contribute to their \(M\) and spin-orbit \(\Phi^{00}\) responses. The latter
is the same vector-charge spin-orbit response represented by AFH
\(\Phi''\). Thus the \(M+\Phi''\) responses are charge multipoles. The
spatial contraction is required for other nuclear responses; it does not
cancel or modify the charge-sector \(M\)-\(\Phi''\) interference.

## 4. Why the exact three-body factor cancels in this ratio

For
\[
\chi_1(p)+N(k)\to\chi_1(p')+N(k')+s(k_s),
\qquad q_A=k'-k=p-p'-k_s,
\]
the charge part of the exact radiative amplitude is
\[
\mathcal M_{M+\Phi''}^{(3)}
=\mathcal T_3^0(p,p',k_s)
\left[c_M M+c_{\Phi''}\Phi''\right].
\]
Both charge operators multiply the same exact two-diagram, finite-width
\(\mathcal T_3^0\). The common spin-averaged phase-space factor
\[
I_{00}^{(3)}(E_R)=
\int d\Phi_3\,
\frac12\operatorname{Tr}
\left[\mathcal T_3^0\mathcal T_3^{0\dagger}\right]
\]
therefore cancels from the relative charge-sector response at fixed recoil.

Define
\[
\eta=\frac{|\boldsymbol q_A|^2}{4m_N^2}
\left(1+2\frac{F_2^V(t_A)}{F_1^V(t_A)}\right).
\]
Then
\[
\frac{c_M}{F_1^V}=1-\frac{\eta}{2},
\qquad
\frac{c_{\Phi''}}{F_1^V}=\eta.
\]
The charge response relative to the leading \(F_1^2W_M\) baseline is
\[
\boxed{
R_{\rm charge/M}=
\left(1-\frac{\eta}{2}\right)^2
+2\left(1-\frac{\eta}{2}\right)\eta
 \frac{W_{M\Phi''}}{W_M}
+\eta^2\frac{W_{\Phi''}}{W_M}.
}
\]
This is a matched three-body charge-sector result. It is not the full
\(L_{\mu\nu}W_A^{\mu\nu}\) contraction because the spatial-current
\(\Delta,\Sigma',\Sigma''\) sectors are not included.

## 5. Adopted zero-momentum flavour benchmark

For the universal light-flavour current, the adopted inputs are
\[
F_1^V(0)=3,\qquad F_2^V(0)=-0.552,
\qquad \frac{F_2^V(0)}{F_1^V(0)}=-0.184.
\]
They follow from the flavour-separated zero-momentum values
\[
F_2^{u/p}(0)=1.609,\quad
F_2^{d/p}(0)=-2.097,\quad
F_2^{s/p}(0)=-0.064.
\]
Use \(m_N=0.938918\) GeV. These are zero-momentum anchors, not a finite-\(t_A\)
form-factor fit. The HKS 2015 low-\(t\) notation discrepancy recorded in
the main theory archive remains open; this calculation explicitly uses the
adopted Bishara et al. flavour-separated benchmark.

At the exact second AFH \(W_M\) minimum,
\[
q_A=256.271867617\ {\rm MeV},\qquad
E_R=269.103897622\ {\rm keV},
\]
\[
\eta=0.01177073615,\qquad
R_{\rm charge/M}=0.9700938740.
\]
Thus the matched \(M+\Phi''\) charge response changes the leading
\(F_1^V(0)^2W_M\) result by
\[
\boxed{-2.9906\%}
\]
at this selected point. This number includes the \(t_A/(8m_N^2)\) correction
to the \(M\) coefficient, the \(M\)-\(\Phi''\) interference, and the
\(\Phi''\)-squared term. It is not the \(\Phi''\)-only addition relative to
a relativistically corrected \(M\)-only denominator.

For comparison, using the earlier illustrative \(F_2/F_1=-0.15\) gives
\(R_{\rm charge/M}=0.96881984\), or \(-3.1180\%\), at the same exact point.
The adopted model benchmark is \(-0.184\), not \(-0.15\).

## 6. Three-body benchmark integration

The script reads the 2401-point AFH grid and exact selected minima from
PR #54, and the PR #53 three-body \(I_{00}\) table. At each fixed recoil
momentum it multiplies the existing \(I_{00}\) kernel by
\(R_{\rm charge/M}\). Because the ratio depends only on \(q_A\) and the
form-factor scenario, changing the \(\chi_2\) width changes the absolute
\(I_{00}\) kernel but not this relative charge-sector correction at fixed
\(q_A\).

The output includes:
- the 2401-point response correction for \(F_2/F_1=0,-0.14,-0.15,-0.17,-0.184\);
- the PR #53 three-body benchmark kernels with the adopted \(-0.184\)
  zero-momentum ratio;
- the four exact AFH \(W_M\)-minimum points;
- order-6 versus order-8 local interpolation differences;
- Cauchy--Schwarz and positivity checks and SHA-256 provenance.

The PR #53 \(I_{00}\) kernels are phase-space-integrated reference points,
not the full continuous \(dR/dE_R\) spectrum. The output is therefore a
charge-sector correction to those kernels, not a detector-level rate.

## 7. Remaining work and interpretation boundary

- The default \(-0.184\) is a zero-momentum form-factor ratio. Finite-\(t_A\)
  flavour-separated \(F_1^V(t_A)\) and \(F_2^V(t_A)\) are still required.
- Spatial-current terms must be projected onto AFH \(\Delta\), \(\Sigma'\),
  and \(\Sigma''\), with their allowed interference terms.
- The other naturally abundant xenon isotopes need their own AFH response
  calculations; Xe-131 cannot stand in for the isotope sum.
- The native Mathematica cross-check for PR #54 remains pending.
- No complete all-current natural-xenon spectrum, detector convolution,
  likelihood, or manuscript result is claimed.

The \(-2.9906\%\) value at the second \(W_M\) minimum is the first
model-benchmark \(M+\Phi''\) charge-sector correction. It must not be
misreported as the total change to the natural-xenon recoil spectrum.
