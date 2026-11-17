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

## Extracting the spin-orbit component

The coefficient of the nucleon-spin structure odd under
\(\boldsymbol\ell\to-\boldsymbol\ell\) is projected along
\(\mathbf q_A\times\boldsymbol\ell\). The code evaluates the full,
charge-only, and spatial-only contributions separately and verifies
\[
c_{\rm full}=c_{\rm charge}+c_{\rm spatial}.
\]

The purpose is to determine how the spatial current modifies the
charge-piece spin-orbit term before mapping the complete result to AFH
\(\Phi''\), \(\Sigma'\), \(\Sigma''\), and \(\Delta\).

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
- No AFH response coefficient is claimed yet. The Pauli-product structures
  still need a complete operator/multipole projection and normalization.
- No absolute cross section, halo fold, isotope sum, detector response, or
  likelihood is included.
