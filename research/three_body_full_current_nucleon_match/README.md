# Full three-body current × nucleon Dirac-Pauli matching diagnostic

**Status:** exact one-nucleon spin-matrix contraction at a static reference point; AFH many-body matching remains open.

## Purpose

This study takes the spin-resolved three-body current from PR #57 and
contracts all four Lorentz components with an explicit one-nucleon
Dirac-Pauli vector current:
\[
\mathcal A=\mathcal T_3^0\otimes J_N^0
-\sum_i\mathcal T_3^i\otimes J_N^i.
\]

The 4x4 operator acts in external chi1 spin space tensor nucleon spin space.
It is decomposed into the complete Pauli-product basis
\[
\mathcal A=\sum_{a,b=0}^3 c_{ab}\,
\sigma_\chi^a\otimes\sigma_N^b.
\]

This is the first step that keeps the charge and spatial current terms
together before identifying the spin-orbit coefficient.

## Nucleon convention and static approximation

The nucleon vertex uses
\[
\Gamma_N^\mu=F_1\gamma^\mu+
\frac{iF_2}{2m_N}\sigma^{\mu\nu}q_{N,\nu},
\qquad q_N=P_N'-P_N.
\]
The sign is translated to the project convention q_A=P'-P.

For this first diagnostic, the free nucleon is on shell in a static elastic
impulse-approximation point:
\[
\mathbf p_N=\boldsymbol\ell-\mathbf q_A/2,\qquad
\mathbf p_N'=\boldsymbol\ell+\mathbf q_A/2,\qquad
\boldsymbol\ell\cdot\mathbf q_A=0.
\]
Thus q_N^0=0. The small nuclear recoil energy q_A^0 is neglected in the
one-nucleon current, as in the static AFH operator reduction. This is a
controlled kinematic diagnostic, not a complete bound-nucleon treatment.

## Covariant versus AFH one-body normalization

The Dirac spinors in the exact contraction use covariant normalization.
Before identifying coefficients of AFH one-body operators, the nucleon
matrix element must be converted to nonrelativistic external-state
normalization:
[
J^mu_{N,mathrm{NR}}=
rac{ar u(p_N')Gamma_N^mu u(p_N)}
     {2sqrt{E_NE_N'}}.
]
The diagnostic now reports both the raw covariant projection and this
nonrelativistically normalized projection. The latter is the one to compare
with the AFH operator coefficients. This conversion is especially important
for the spin-independent (M) coefficient; the leading spin-orbit coefficient
is also checked against the exact normalized spinor expression.

The code uses (m_N=0.938918) GeV and the provisional zero-momentum
benchmark (F_2/F_1=-0.184), with (F_1) normalized to one. It does not
pretend that this ratio is a finite-(t_N) form factor.

## Static energy-transfer approximation

The target nucleon is taken on shell with
[
mathbf p_N=oldsymbolell-mathbf q_A/2,qquad
mathbf p_N'=oldsymbolell+mathbf q_A/2,qquad
oldsymbolellcdotmathbf q_A=0,
]
so its free on-shell energy transfer is (q_N^0=0). The nuclear transfer
has (q_A^0=E_R
e0). The code therefore reports the Ward residual both
with (q_N) (which must vanish) and with the physical (q_A) (which
quantifies the static approximation). The latter is not a failure of the
free-nucleon Ward test; it is a reminder that the static impulse point does
not implement the full bound-nucleon continuity equation or the Proca
longitudinal propagator contraction.

## Extracting the spin-orbit component

The coefficient of the nucleon-spin structure odd under
\(\boldsymbol\ell\to-\boldsymbol\ell\) is projected along
\(\mathbf q_A\times\boldsymbol\ell\). The code evaluates the full,
charge-only, and spatial-only contributions separately, reports all 16
Pauli-product coefficients for each piece, and verifies
\[
c_{\rm full}=c_{\rm charge}+c_{\rm spatial}.
\]

The purpose is to determine how the spatial current modifies the
charge-piece spin-orbit term before mapping the complete result to AFH
\(\Phi''\), \(\Sigma'\), \(\Sigma''\), and \(\Delta\).

## Results from the archived reference point

The successful workflow run 44209893848 (commit
\`8a99ef3f0908053d60ae38881543826510c240fe\`) used
\(F_1/F_1(0)=1\), \(F_2/F_1(0)=-0.184\), and \(m_N=0.938918\) GeV.

The free static nucleon-current Ward residual using \(q_N\) is
\(3.84\times10^{-18}\), and the spin-resolved DM-current trace agrees with
the independent PR #53 tensor to \(4.46\times10^{-16}\). The physical
nuclear transfer has \(q_A^0=E_R\ne0\), however, so using it with the
static \(q_N^0=0\) current gives a separate scaled residual
\(5.35\times10^{-4}\). The ratio \(q_A^0/Q_A\) is
\(9.05\times10^{-4}\). This quantifies the static energy-transfer
approximation; it is not to be silently relabelled as exact conservation
with \(q_A\).

At \(v_N=0.10\), the nonrelativistically normalized coefficient of
\(\boldsymbol\sigma_N\cdot(\boldsymbol q_A\times\boldsymbol\ell)\)
for the charge piece is
\[
C_{\rm charge}^{\rm NR}
=-\,8.41409\times10^6\,i
\]
in the code's per-\((q_A\times\ell)\) convention. The full result agrees
with it at the displayed precision, while the spatial-only contribution
to this *same odd spin-orbit projection* is about \(8.35\times10^{-12}i\).
This is a one-point result, not a proof that the spatial current is
irrelevant.

The complete Pauli decomposition shows why that distinction matters. For
the same \(F_2/F_1(0)=-0.184\) point, one spatial-only coefficient with
nucleon spin perpendicular to \(\boldsymbol q_A\) is
\[
c_{0,2}^{\rm spatial}=-3.75817\times10^3\,i.
\]
This is a transverse-spin **candidate** for the AFH \(\Sigma'\) sector,
not yet a computed \(\Sigma'\) Wilson coefficient or nuclear response.
The artifact contains all \(4\times4\) Pauli-product coefficients for
the full, charge-only, and spatial-only amplitudes. Their reconstruction
residuals are below \(1.4\times10^{-16}\).

The correct conclusion is therefore twofold:

- At this reference point, the spatial current does not change the
  selected \(\Phi''\)-type odd-in-\(\ell\) projection at detectable precision.
- The spatial current does generate other nucleon-spin and DM-spin /
  nucleon-spin structures. They must be projected onto AFH multipoles
  before deciding their impact on the recoil rate.

The output is a static one-nucleon matching diagnostic. It is not yet a
phase-space-integrated \(\Sigma'\), \(\Delta\), or full natural-xenon result.

## Reproduction

Python 3.12+ and NumPy are required.

~~~bash
python -m unittest discover \
  -s research/three_body_full_current_nucleon_match \
  -p 'test_*.py' -v

python research/three_body_full_current_nucleon_match/full_current_nucleon_match.py \
  --out /tmp/full-current-nucleon-match.json
~~~

## Limitations

- One three-body phase-space point and one nucleon-momentum orientation are
  used; this is not a phase-space-integrated nuclear response.
- q_N^0=0 is used for the on-shell static nucleon. A complete treatment must
  include the appropriate bound-nucleon/current-conservation framework.
- The finite-t F1 and F2 of the model-specific universal vector current are
  not fixed; the code uses F1=1 and compares F2=0 with -0.15.
- No AFH response coefficient is claimed yet. The complete Pauli-product
  structures still need a multipole projection and nuclear OBDME contraction.
- The spatial-only contribution to the selected spin-orbit projection is
  negligible at the archived reference point; this does not imply that its
  other Pauli structures or AFH responses vanish.
- No absolute cross section, halo fold, isotope sum, detector response, or
  likelihood is included.
