# Three-body nucleon-current matching to AFH: next-stage calculation

**Status:** matching plan and acceptance criteria only. No numerical
\(W_{\Phi''}\)-corrected three-body rate is claimed in this note.

## 1. Existing evidence that must be reused, not recalculated

This work is the physical bridge between the existing stacked three-body
current audit and the independent AFH nuclear-response audit:

- **PR #53** (research/vector_current_response_audit/): exact four-component
  \(L^{\mu\nu}\), both scalar-emission orderings, their interference, and
  zero/pole/running width comparisons. The reference spatial-to-temporal
  integrated current norm is \(r_\chi\simeq2.47\times10^{-3}\).
- **PR #54** (research/afh_vv_phi_xe131/): AFH v6.0 Xe-131
  \(W_M^{00}\), \(W_{\Phi''}^{00}\), and \(W_{M\Phi''}^{00}\) on 2401
  momentum-transfer points. At \(q_A=256.2718676\) MeV,
  \(W_{\Phi''}/W_M=115.8895\) and
  \(W_{M\Phi''}/W_M=-1.46249\). These are nuclear responses, not rate
  multipliers.
- **This stacked PR #57** (research/three_body_spin_resolved_current/):
  spin-resolved \(2\times2\) matrices for all four \(\mathcal T_3^\mu\)
  components, finite-width Ward identity, fixed-speed point-nucleus
  recoil-kernel scan, and the natural-xenon \(W_M\)-only halo-fold width
  crosscheck.

The independent native Mathematica export in PR #54 remains pending; its
Python/AFH response audit must not be described as a completed native
Mathematica comparison.

## 2. Correct elastic benchmark, and why it is not the three-body answer

The standard elastic VV nucleon-current reduction does contain a
spin-orbit term. In Hoferichter--Klos--Schwenk, Eq. (25), the VV
one-body amplitude contains a term proportional to

\[
\frac{F_2^{V,N}(t)}{4m_N^2}
\,\boldsymbol q\cdot(i\boldsymbol\sigma_N\times\boldsymbol P_N),
\qquad \boldsymbol P_N=\boldsymbol p_N+\boldsymbol p_N'.
\]

With elastic two-body kinematics this contributes to the
\(\mathcal O_3\) sector, which maps onto the AFH
\(\Phi''\) and \(M\Phi''\) responses. The older statement that the
subleading VV channel contains only \(\mathcal O_2,\mathcal O_5\) is
therefore withdrawn.

But the elastic coefficient cannot be copied into
\(\chi_1 N\to\chi_1 N s\). In the three-body process,

\[
q_A=p-p'-k_s,\qquad q_\chi=p-p'=q_A+k_s.
\]

For the average velocities

\[
\boldsymbol v_{\rm av}^{(3)}
=\frac{\boldsymbol p+\boldsymbol p'}{2m_\chi}
-\frac{\boldsymbol k+\boldsymbol k'}{2m_N},
\]

nonrelativistic energy-momentum conservation gives

\[
\boldsymbol q_A\cdot\boldsymbol v_{\rm av}^{(3)}
=E_s-\frac{(\boldsymbol p+\boldsymbol p')\cdot\boldsymbol k_s}
{2m_\chi},
\]

not the elastic relation
\(\boldsymbol q\cdot\boldsymbol v^\perp=0\). The scalar momentum changes
the transverse kinematics as well. In addition, the DM current is the
coherent two-diagram \(\mathcal T_3^\mu(p,p',k_s)\), not a single
\(\bar u_\chi'\gamma^\mu u_\chi\) bilinear.

## 3. Required matching object

At each point in the three-body phase space, use the exact finite-width
spin-resolved current

\[
\mathcal T_3^\mu =
\mathcal T_{\rm before}^\mu+\mathcal T_{\rm after}^\mu
\]

with the same width insertion as the manuscript prescription. Contract it
with the one-nucleon Dirac--Pauli current

\[
J_N^\mu(q_A)=
\bar u_N(k')
\left[
F_1^{V,N}(t)\gamma^\mu
-\frac{iF_2^{V,N}(t)}{2m_N}
\sigma^{\mu\nu}q_{A,\nu}
\right]u_N(k),
\qquad t=q_A^2,
\]

using a single consistent sign convention for \(q_A\) and the Pauli term.

The product is a matrix in both DM and nucleon spin spaces. Perform the
nonrelativistic Pauli reduction and project its coefficients onto the
nuclear one-body current multipoles. The first required coefficient
matrices are

\[
C_M^{(3)}(p,p',k_s;q_A),\qquad
C_{\Phi''}^{(3)}(p,p',k_s;q_A),
\]

followed by the associated mixed term. Do not infer
\(C_{\Phi''}^{(3)}\) from \(F_2^V(0)\) alone, and do not replace the
three-body current by its time component before matching.

For each phase-space point, the spin-averaged coefficient products are
formed from the same \(2\times2\) DM matrices, e.g.

\[
\mathcal R_M^{(3)}
=\frac12\operatorname{Tr}
\left[C_M^{(3)}C_M^{(3)\dagger}\right],
\]

\[
\mathcal R_{\Phi''}^{(3)}
=\frac12\operatorname{Tr}
\left[C_{\Phi''}^{(3)}C_{\Phi''}^{(3)\dagger}\right],
\]

\[
\mathcal R_{M\Phi''}^{(3)}
=\operatorname{Re}\frac12\operatorname{Tr}
\left[C_M^{(3)}C_{\Phi''}^{(3)\dagger}\right].
\]

The precise normalization and any explicit powers of \(q_A/m_N\) must be
fixed by matching the operator definitions in the AFH v6.0 convention,
not guessed from the ratios of the tabulated \(W\)'s.

The Xe-131 first-stage recoil kernel is then

\[
I_{\rm Xe131}^{\rm matched}(E_R)
=\int d\Phi_3\left[
\mathcal R_M^{(3)}W_M
+\mathcal R_{\Phi''}^{(3)}W_{\Phi''}
+\mathcal R_{M\Phi''}^{(3)}W_{M\Phi''}
\right],
\]

with all three terms evaluated at the same \(q_A\), scalar momentum,
propagator virtualities, and width prescription.

## 4. Mandatory validation sequence

1. **Elastic limit regression.** Replace the emitted scalar by the elastic
   kinematic limit and reduce \(\mathcal T^\mu\) to the ordinary vector
   WIMP current. Reproduce the published elastic VV Pauli reduction,
   including the \(\mathcal O_3\) coefficient and its sign.
2. **Nucleon-current checks.** Verify the Dirac and Pauli pieces separately,
   \(q_{A\mu}J_N^\mu=0\) for on-shell equal-mass nucleons, and the
   spin-resolved matrix result against an independent Dirac trace.
3. **Three-body current checks.** Retain both scalar-emission diagrams and
   their interference; verify the finite-width Ward identity and the
   conserved-target contraction at every sampled phase-space point.
4. **Width comparison.** Run zero width only as a diagnostic, and compare
   the manuscript pole width with the running scalar-channel diagnostic.
   Keep \(g_2\) explicit because the coupling product does not fix
   \(\Gamma_{\chi_2}\).
5. **AFH normalization.** Apply the equal-\(p=n\) factor of four exactly
   once to the AFH isoscalar responses. The common factor cancels in
   \(M\), \(\Phi''\), and mixed-response ratios, but it must remain explicit
   in absolute rates.
6. **Quadrature convergence.** Converge the \(W^2,z,\phi\) three-body
   integration independently for each response coefficient and for their
   interference. Near-pole points require endpoint-adapted mappings.
7. **Natural xenon.** Only after the Xe-131 matching passes, repeat the
   AFH response calculation for the remaining naturally abundant isotopes.
   Do not use the Xe-131 \(W_{\Phi''}\) curve as a proxy for other isotopes.

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

- The existing \(W_M\)-only natural-xenon spectrum is a reproducible baseline.
- The Xe-131 \(\Phi''\) response is numerically large near the second
  \(W_M\) minimum, so it cannot be discarded on nuclear-structure grounds.
- The exact three-body coefficient multiplying \(\Phi''\) has not yet been
  computed. Consequently, **the percentage change in the natural-xenon
  recoil spectrum is not yet known**.
- A numerical percentage must not be estimated by multiplying
  \(W_{\Phi''}/W_M\) by \(r_\chi\), by \(F_2/F_1\), or by a point-nucleon
  kinematic factor. Those quantities do not constitute the matched
  three-body response coefficient.
