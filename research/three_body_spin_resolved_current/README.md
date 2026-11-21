# Finite-width three-body current and recoil-spectrum audit

**Status:** finite-width Ward identity and fixed-speed coherent point-nucleus recoil-kernel scan are reproduced. The AFH vector-charge (M+Phi'') sector has now been matched using a zero-momentum form-factor benchmark; finite-(t) form factors and the internal spatial-current (Delta), (Sigma'), and (Sigma'') matching remain open.

## 1. Question

Does the non-conservation of the three-body dark-matter current, and the
finite width of the virtual chi2 propagator, change the recoil spectrum?

The answer must distinguish:
1. the longitudinal Ward divergence of the DM current;
2. the transverse current that actually contracts with a conserved nuclear
   vector current;
3. the change of the transverse amplitude caused by the finite-width
   propagator;
4. internal nuclear spin and orbital responses, which are not included in
   the point-nucleus comparison.

## 2. Finite-width Ward identity for the implemented propagator

The current code uses
\[
D_1=r_1^2-m_{\chi_2}^2,\qquad
\widetilde D_2=r_2^2-m_{\chi_2}^2+i a,\qquad
a=m_{\chi_2}\Gamma_{\chi_2},
\]
with
\[
r_1=p-k_s,\qquad r_2=p'+k_s,\qquad q_A=r_1-p'=p-r_2.
\]

Only the second emission ordering has the width inserted, and the numerator
remains \(\slashed r_2+m_{\chi_2}\). Direct use of the external chi1 Dirac
equations gives
\[
\boxed{
q_{A\mu}\mathcal T_3^\mu
=(m_{\chi_2}-m_{\chi_1})\bar u'
\left[
\frac{\slashed r_1+m_{\chi_2}}{D_1}
-\frac{\slashed r_2+m_{\chi_2}}{D_2+i a}
\right]u
+\frac{i a}{D_2+i a}\bar u'u .
}
\]
The last term is required for the denominator-only Breit-Wigner insertion
used in the current code. It disappears only when \(a\to0\).

This is an exact algebraic identity for that phenomenological propagator
prescription. It is not the full Ward-Takahashi identity of a consistently
resummed fermion propagator. A complete resummation requires the Dirac
structure of the self-energy and consistent vertex/counterterm treatment.

## 3. Why the Ward divergence itself does not change the coherent elastic rate

For an elastic nucleus with the same initial and final nuclear mass,
\[
J_A^\mu=(P+P')^\mu F_A(q_A^2),\qquad q_A=P'-P,
\]
and
\[
q_{A\mu}J_A^\mu=(P'^2-P^2)F_A=0.
\]

Therefore
\[
J_{A\mu}\mathcal T_3^\mu
=J_{A\mu}\left[
\mathcal T_3^\mu-q_A^\mu
\frac{q_{A\nu}\mathcal T_3^\nu}{q_A^2}
\right].
\]
The longitudinal part of the non-conserved DM current is annihilated by the
conserved nuclear current. The same statement holds for an on-shell
equal-mass nucleon Dirac-Pauli vector current.

This does **not** mean the width is irrelevant. The finite width changes
the propagator denominators and hence the transverse part of
\(\mathcal T_3^\mu\), which does affect the rate.

## 4. Spectrum calculation

The scan integrates the complete four-component tensor \(L^{\mu\nu}\) over
the same three-body phase space as the existing Eq. (6) kernel, and
contracts it with the coherent point-nucleus current. It compares:
- zero width (diagnostic baseline only);
- pole width (the manuscript's current Breit-Wigner prescription);
- running width (the scalar-channel absorptive-width diagnostic).

The output kernel is
\[
K_{\rm point}(E_R)=
\frac{m_A I_{\rm full}(E_R)}
{[m_V^2+2m_AE_R]^2},
\]
with \(m_V=10\) GeV for the reference plot kernel and the nuclear form
factor factored out. At fixed \(E_R\), ratios between width schemes are
unchanged by multiplying a common nuclear form factor.

Parameters:
\[
m_{\chi_1}=1~{\rm TeV},\quad m_s=300~{\rm keV},\quad
m_A=131u,\quad v=776~{\rm km/s}.
\]
The scan includes the established \(\Delta m=450\) keV and 1 MeV anchors,
plus a deliberately near-pole \(\Delta m=362\) keV case for \(g_2=0.1,1\).
For the near-pole case, only points satisfying \(W_{\max}<m_{\chi_2}\) are
included. The first crossing is at approximately \(E_R=274.788\) keV;
points beyond that are not treated as off-shell three-body benchmarks.

## 5. Reproduction

Python 3.13 and NumPy 2.3.5:

~~~bash
python -m unittest discover \
  -s research/three_body_spin_resolved_current -p 'test_*.py' -v

python research/three_body_spin_resolved_current/recoil_spectrum_width_scan.py \
  --outdir /tmp/finite-width-recoil-spectrum

python research/three_body_spin_resolved_current/spin_resolved_three_body_current.py \
  --out /tmp/finite-width-recoil-spectrum/spin_resolved_ward.json
~~~

The workflow archives the fixed-speed spectrum table, high-order
near-pole convergence checks, and finite-width Ward diagnostics.

## 6. Interpretation limits

- The point-nucleus current includes centre-of-mass convection only.
- Internal nucleon magnetization and convection matrix elements, and AFH
  Sigma', Sigma'', and Delta responses, are not included.
- The scalar-only conditional width assumes Dirac chi fields, a real scalar,
  a pure scalar Yukawa coupling, and no other open chi2 decay channels.
- The running-width prescription uses the scalar-channel absorptive width;
  the complete vector-sector real self-energy is not included.
- The output is a fixed-speed reduced recoil kernel, not a halo-folded
  natural-xenon event rate or detector-level LZ spectrum.
- No absolute experimental normalization, detector response, efficiency,
  exposure, or likelihood is claimed.

## Results

See [results/2026-11-18/RESULTS.md](results/2026-11-18/RESULTS.md) for the finite-width Ward identity checks, recoil-kernel width comparison, near-pole quadrature convergence, and scope limits. The reproducibility bundle is archived as [finite_width_spin_current_recoil_spectrum.zip](results/2026-11-18/finite_width_spin_current_recoil_spectrum.zip).

## AFH matching next stage

See [AFH_MATCHING_NEXT_STAGE.md](AFH_MATCHING_NEXT_STAGE.md) for the matched (M+Phi'') vector-charge sector, the zero-momentum benchmark correction at the Xe-131 second (W_M) minimum, the remaining spatial-current matching plan, and the validated (W_M)-only natural-xenon halo-fold baseline. The complete finite-(t), all-current natural-xenon spectrum remains pending.
