# Three-body nucleon-current matching to AFH: charge sector and remaining spatial currents

**Status:** the \(M+\Phi''\) vector-charge sector has been matched and
numerically evaluated using the explicitly provisional zero-momentum
form-factor anchors. The full finite-\(t\), all-current three-body prediction
is not yet complete.

## 1. Existing evidence that must be reused, not recalculated

This work connects the existing three-body current and AFH nuclear-response
audits:

- **PR #53** (research/vector_current_response_audit/): exact four-component
  \(L^{\mu\nu}\), both scalar-emission orderings, their interference, and
  zero/pole/running width comparisons. The reference spatial-to-temporal
  integrated current norm is \(r_\chi\simeq2.47\times10^{-3}\).
- **PR #54** (research/afh_vv_phi_xe131/): AFH v6.0 Xe-131
  \(W_M^{00}\), \(W_{\Phi''}^{00}\), and \(W_{M\Phi''}^{00}\) on 2401
  momentum-transfer points. At \(q_A=256.271867617\) MeV,
  \(W_{\Phi''}/W_M=115.8894642\) and
  \(W_{M\Phi''}/W_M=-1.46248999\). These are nuclear responses, not rate
  multipliers.
- **This stacked PR #57** (research/three_body_spin_resolved_current/):
  spin-resolved \(2\times2\) matrices for all four \(\mathcal T_3^\mu\)
  components, finite-width Ward identity, fixed-speed point-nucleus
  recoil-kernel scan, and the natural-xenon \(W_M\)-only halo-fold width
  crosscheck.

The independent native Mathematica export in PR #54 remains pending; its
Python/AFH response audit must not be described as a completed native
Mathematica comparison.

## 2. Matched \(M+\Phi''\) vector-charge sector

Use the momentum delivered to the target nucleon,
\[
q_A^\mu=k'^\mu-k^\mu,\qquad t_A=q_A^2=-|\boldsymbol q_A|^2,
\]
and the Dirac--Pauli convention
\[
J_N^\mu(q_A)=
\bar u_N(k')
\left[
F_1^{V,N}(t_A)\gamma^\mu+
\frac{iF_2^{V,N}(t_A)}{2m_N}
\sigma^{\mu\nu}q_{A,\nu}
\right]u_N(k).
\]
The plus sign is tied to \(q_A=k'-k\). Hoferichter--Menéndez--Schwenk
use \(q=k-k'=-q_A\) and the equivalent vertex with
\(-iF_2\sigma^{\mu\nu}q_\nu/(2m_N)\).

For the AFH nuclear Fourier operators, the elastic-reference convention is
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\). In the radiative process,
\[
\boldsymbol p_\chi'-\boldsymbol p_\chi
=-\boldsymbol q_A-\boldsymbol k_s.
\]
Do not identify the AFH nuclear Fourier momentum with the full DM momentum
change. The nuclear multipoles are evaluated at the momentum flowing through
the nucleon current, \(|\boldsymbol q_{\rm AFH}|=|\boldsymbol q_A|\);
the emitted scalar momentum remains inside the three-body DM current.

Hoferichter, Menéndez, and Schwenk, PRD 102, 074018 (2020), Eq. (41),
give the nonrelativistic vector charge
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
\(\boldsymbol S_N=\boldsymbol\sigma_N/2\). They state immediately below
Eq. (41) that the spacelike components do not contribute to their \(M\)
and spin-orbit \(\Phi^{00}\) responses. The latter is the vector-charge
spin-orbit response represented by AFH \(\Phi''\), whose operator is
defined in Anand--Fitzpatrick--Haxton, PRC 89, 065501 (2014), Eq. (51).

Matching the charge expansion gives
\[
\boxed{
c_M(t_A)=F_1^V(t_A)
+\frac{t_A}{8m_N^2}
 \left[F_1^V(t_A)+2F_2^V(t_A)\right],
}
\]
\[
\boxed{
c_{\Phi''}(t_A)=
\frac{q_A^2}{4m_N^2}
\left[F_1^V(t_A)+2F_2^V(t_A)\right].
}
\]
The signs correspond to the current and AFH momentum conventions above.

For
\[
\chi_1(p)+N(k)\to\chi_1(p')+N(k')+s(k_s),
\qquad q_A=k'-k=p-p'-k_s,
\]
the charge part of the exact radiative amplitude is
\[
\boxed{
\mathcal M_{M+\Phi''}^{(3)}
=\mathcal T_3^0(p,p',k_s)
\left[c_M(t_A)M+c_{\Phi''}(t_A)\Phi''\right].
}
\]
Both operators multiply the same exact two-diagram, finite-width
\(\mathcal T_3^0\). Consequently the common spin-averaged three-body factor
\[
I_{00}^{(3)}(E_R)=
\int d\Phi_3\,
\frac12\operatorname{Tr}
\left[\mathcal T_3^0\mathcal T_3^{0\dagger}\right]
\]
cancels from the *relative* \(M+\Phi''\) charge-sector correction at fixed
\(E_R\), when the same isoscalar form factors are used for both responses.

With
\[
\eta(q_A)=\frac{c_{\Phi''}(t_A)}{c_M(t_A)},
\]
the ratio is
\[
\boxed{
Q_{\Phi''}(q_A)=
1+2\eta\frac{W_{M\Phi''}}{W_M}
+\eta^2\frac{W_{\Phi''}}{W_M}.
}
\]
This is already a genuine three-body charge-sector result. It does not
require a second three-body phase-space integration for the relative
correction. It does not, however, replace the phase-space integral needed
for the absolute rate.

### 2.1 Zero-momentum form-factor diagnostic

For the universal light-flavour current, use the existing zero-momentum
anchors
\[
F_1^V(0)=3,\qquad F_2^V(0)=-0.552,
\qquad F_1^V(0)+2F_2^V(0)=1.896,
\]
with \(m_N=0.938918\) GeV. These are diagnostic anchors only; they are not
finite-\(t_A\) form factors.

At the second AFH \(W_M\) minimum,
\[
q_A=256.271867617\ {\rm MeV},\qquad
E_R=269.103897622\ {\rm keV},
\]
the coefficients are
\[
c_M=2.98234390,\qquad
c_{\Phi''}=0.03531221,\qquad
\eta=0.01184042.
\]
The exact selected-point AFH responses give
\[
W_{\Phi''}/W_M=115.8894642,\qquad
W_{M\Phi''}/W_M=-1.46248999,
\]
and hence
\[
\boxed{Q_{\Phi''}=0.9816142.}
\]
This is a \(-1.839\%\) correction relative to the same relativistically
corrected \(M\)-only charge response. Including the \(t_A/(8m_N^2)\)
correction to \(c_M\), the combined change relative to
\(F_1^V(0)^2W_M\) is \(-2.991\%\) at this point.

Across the 2401-node Xe-131 grid, the sampled \(Q_{\Phi''}-1\) varies
locally from \(-13.61\%\) at \(q_A=255.75\) MeV to \(+11.50\%\) at
\(q_A=256.75\) MeV. These are local ratios to a very small \(W_M\)
denominator around its deep cancellation, not global event-rate changes.
The signed interference changes rapidly across the minimum; the matched
charge response remains nonnegative.

The numerical implementation and output are in PR #54:
- research/afh_vv_phi_xe131/phi_charge_response_match.py
- research/afh_vv_phi_xe131/output/phi_charge_match_full_grid.csv
- research/afh_vv_phi_xe131/output/phi_charge_match_selected_points.csv
- research/afh_vv_phi_xe131/output/phi_charge_match_summary.json

## 3. Remaining spatial-current matching

The factorization above applies only to the vector-charge \(M+\Phi''\)
sector. The spatial contraction
\[
-\mathcal T_3^i J_{N,i}
\]
must still be reduced. Its nucleon convection and magnetization pieces can
generate orbital/convection and spin responses, including AFH
\(\Delta\), \(\Sigma'\), and \(\Sigma''\), with possible interference terms.

The next calculation is therefore not to recompute the already matched
charge sector. It is to use the exact spin-resolved matrices for all four
\(\mathcal T_3^\mu\) components from PR #53/#57 and the finite-\(t_A\)
Dirac--Pauli current to derive the spatial-current coefficients. Keep the
two scalar-emission orderings coherent and retain the same width prescription
as the existing recoil calculation.

The small integrated ratio \(r_\chi\) is useful for power counting the
spatial-current terms, but it is not a substitute for the coefficient-level
projection onto \(\Delta\), \(\Sigma'\), and \(\Sigma''\). Nor should
\(W_{\Phi''}/W_M\) be multiplied by \(r_\chi\): \(\Phi''\) belongs to the
vector-charge spin-orbit sector just matched above.

## 4. Mandatory validation sequence for the remaining spatial current

1. **Elastic charge regression.** Reproduce the vector-charge expansion
   above, including the \(F_1+2F_2\) combination, the \(t_A/(8m_N^2)\)
   term, and the AFH \(\Phi''\) sign.
2. **Nucleon-current checks.** Verify the Dirac and Pauli pieces separately,
   \(q_{A\mu}J_N^\mu=0\) for on-shell equal-mass nucleons, and the
   spin-resolved result against an independent Dirac trace.
3. **Three-body current checks.** Retain both scalar-emission diagrams and
   their interference; verify the finite-width Ward identity and
   conserved-target contraction at every sampled phase-space point.
4. **Spatial-current projection.** Derive the coefficients of the
   convection/orbital and magnetization/spin operators. Project them onto
   AFH \(\Delta\), \(\Sigma'\), and \(\Sigma''\), and calculate their
   interference terms where allowed by parity and time-reversal symmetry.
5. **Width comparison.** Keep zero width as a diagnostic and compare the
   manuscript pole width with the running scalar-channel diagnostic.
   Keep \(g_2\) explicit because the coupling product does not fix
   \(\Gamma_{\chi_2}\).
6. **AFH normalization.** Apply the equal-\(p=n\) factor of four exactly
   once. It cancels in response ratios but remains explicit in absolute
   rates.
7. **Quadrature convergence.** Converge the \(W^2,z,\phi\) integration
   independently for each spatial response and interference. Near-pole
   points require endpoint-adapted mappings.
8. **Natural xenon.** Repeat the AFH spatial-response calculation for the
   other naturally abundant isotopes. Do not use Xe-131 responses as a
   proxy for other isotopes.

## 5. Existing \(W_M\)-only natural-xenon baseline

The workflow natural-xenon-width-comparison passed on commit
2575be4d72348dfa5789c6436e6a0a7b1a41c738 (run 44189329275).
It used the existing GCN/JJ55 \(W_M\) grids, seven isotopes
\(\{128,129,130,131,132,134,136\}\), and 99.8158% of natural abundance.
It is a pre-detector truncated-SHM fold with
\(v_0=220\), \(v_E=232\), \(v_{\rm esc}=544\) km/s, \(m_\chi=1\) TeV,
\(m_s=300\) keV, \(\Delta m=1\) MeV, and \(g_2=1\).

| \(E_R\) (keV) | GCN pole/zero | JJ55 pole/zero |
|---:|---:|---:|
| 101 | 0.989799 | 0.989799 |
| 200 | 0.989267 | 0.989267 |
| 267 | 0.989067 | 0.989070 |
| 542 | 0.989332 | 0.989357 |

This table isolates the width effect **within the old \(W_M\)-only
construction**. It does not measure the change caused by adding
\(\Phi''\), \(M\Phi''\), \(\Sigma'\), \(\Sigma''\), or \(\Delta\).

## 6. What can and cannot be concluded now

- The \(W_M\)-only natural-xenon spectrum remains a reproducible baseline.
- The \(M+\Phi''\) charge-sector correction is now matched. With the
  zero-momentum form-factor benchmark, it is \(-1.839\%\) relative to
  corrected \(M\)-only at the second \(W_M\) minimum.
- The \(W_{\Phi''}/W_M=115.89\) nuclear ratio is not a 115.89-fold rate
  enhancement; the small coefficient and negative mixed response must be
  included.
- The numerical charge-sector correction is not yet a finite-\(t\)
  prediction because the model-specific \(F_1^{V,N}(t_A)\) and
  \(F_2^{V,N}(t_A)\) are still needed.
- The spatial-current \(\Delta\), \(\Sigma'\), and \(\Sigma''\) coefficients
  and the other xenon isotope responses remain pending. Therefore the
  percentage change in the complete natural-xenon recoil spectrum is not
  yet known.
- Do not estimate the complete correction by multiplying
  \(W_{\Phi''}/W_M\) by \(r_\chi\), \(F_2/F_1\), or a point-nucleon
  kinematic factor. The charge-sector coefficient has its own derivation,
  and the spatial-current coefficients require a separate projection.
