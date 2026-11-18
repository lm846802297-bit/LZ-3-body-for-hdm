# P3-A: pointwise covariant and q-frame contraction check

**Status:** implementation and tests added; awaiting the current PR workflow.  
**Scope:** pointwise spinor-level check using the actual three-body DM current and
an exact free on-shell one-nucleon Dirac--Pauli current. This is **P3-A only**;
it is not the full nuclear OBDME contraction.

## 1. Purpose

P0 phase-space integration and convergence are complete. P1 has decomposed the
free on-shell one-body Dirac--Pauli current, and P2 has independently fixed the
particle-side AFH Eq. (107) coefficients and the signed
\(\Sigma'\)-\(\Delta\) coefficient.

P3 must now connect these layers without conflating a free one-nucleon
spinor test with a bound-nucleus calculation. The first executable slice
(P3-A) tests the same phase-space point in three representations:

1. direct covariant \(4\times4\) spin operator
   \[
   {\cal A}_{\rm cov}=
   {\cal T}_3^0\otimes J_N^0
   -\sum_{i=1}^3{\cal T}_3^i\otimes J_N^i;
   \]
2. the same operator after a proper SO(3) rotation that sends
   \(\boldsymbol q_A\) to the local \(+\hat z\) axis;
3. AFH Eq. (107) spatial particle-side coefficients evaluated directly
   on the actual complex spin channels and independently from the
   spin-averaged Lorentz tensor.

## 2. Inputs and conventions

The test uses the repository's reference three-body phase-space point and
coherent two-diagram DM current. The nucleon current is computed from the
exact Dirac--Pauli spinors with
\[
q_N^\mu=k_N'^\mu-k_N^\mu,\qquad
\Gamma_N^\mu=F_1^V\gamma^\mu+
\frac{iF_2^V}{2m_N}\sigma^{\mu\nu}q_{N,\nu},
\]
and is converted to the AFH nonrelativistic state normalization by
\(1/(2\sqrt{E_NE_N'})\). The diagnostic uses \(F_1^V=1\),
\(F_2^V=-0.184\), and \(v_N=0.10\) with internal momentum perpendicular
to \(\boldsymbol q_A\). These are matching diagnostics, not finite-\(t_N\)
form factors or a bound-nucleon momentum distribution.

The AFH Fourier convention remains
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\), while the nucleon vertex uses
\(\boldsymbol q_N=+\boldsymbol q_A\). The spatial metric sign is retained.

## 3. Acceptance tests

The new test module checks:

- exact covariant \(4\times4\) amplitude and Pauli-product reconstruction;
- free on-shell nucleon Ward identity using \(q_N\);
- direct covariant contraction invariance under the q-alignment rotation;
- direct complex-spin-channel evaluation of AFH Eq. (107) against the
  independent \(L_{ij}\) tensor extractor in both lab and q-aligned frames;
- invariance of \(C_\Delta\), \(C_{\Sigma'}\), and signed
  \(C_{\Sigma'\Delta}\) under the frame rotation;
- nonzero coherent interference between the before- and after-emission
  scalar-radiation diagrams.

The rotation acts on the spatial Lorentz indices of both currents with the
same proper SO(3) matrix. It does not change the Lorentz metric or the
spin-average convention.

## 4. What this does not prove

Passing P3-A does not validate the many-body nuclear multipole contraction.
In particular it does not supply:
- AFH Xe isotope OBDMEs or their phase conventions;
- bound-nucleon energy sharing or an off-shell current prescription;
- exchange/interaction currents required by the nuclear continuity equation;
- the contraction of the exact finite-\(t_N\) current with native AFH nuclear
  matrix elements.

The full P3-B gate remains:
\[
{\cal A}_{\rm cov}^{\rm nuclear}
\stackrel{?}{=}
{\cal A}_{q\text{-frame}}^{\rm nuclear}
\stackrel{?}{=}
{\cal A}_{\rm AFH\ multipoles}^{\rm nuclear}
\]
at selected isotope/recoil points, using the same OBDMEs, normalization,
Fourier convention, and current truncation. A response-function table alone
does not expose all OBDME phase information needed for this amplitude-level
comparison.

## 5. Promotion policy

The test result may be labelled **P3-A pointwise spinor/frame consistency**.
It must not be labelled full P3 PASS, full-current natural-xenon rate, or
validated bound-nucleus current. P3-B and the finite-\(t_N\) natural-xenon
halo fold remain separate gates.
