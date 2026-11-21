# P3-A: direct full-current contraction and q-frame covariance

**Status:** direct lab-frame and q-aligned-frame full spin-amplitude contractions agree at the reference three-body phase-space point. This is the first P3 tensor-level gate; the AFH nuclear OBDME contraction is not yet included.

## 1. Construction

The exact spin-resolved three-body DM transition current is taken from
build_reference_inputs. The nucleon current is the exact Dirac--Pauli
spinor matrix element with
\[
q_N^\mu=q_A^\mu,\qquad
p_N=\ell-\frac{\boldsymbol q_A}{2},\qquad
p_N'=\ell+\frac{\boldsymbol q_A}{2},
\]
and the energy-transfer-matched free on-shell value of \(\ell_\parallel\).
The amplitude operator is
\[
\mathcal A=
\mathcal T_3^0\otimes J_N^0
-\sum_{i=1}^3\mathcal T_3^i\otimes J_N^i.
\]
A right-handed orthogonal matrix \(R\) is built with rows
\((\boldsymbol e_1,\boldsymbol e_2,\widehat{\boldsymbol q}_A)\). Both
spatial currents are transformed as
\[
\boldsymbol{\mathcal T}_{3,q}=R\boldsymbol{\mathcal T}_{3,\rm lab},
\qquad
\boldsymbol J_{N,q}=R\boldsymbol J_{N,\rm lab}.
\]
The same contraction is then evaluated in both frames.

## 2. What the test checks

The regression checks:
- \(R R^T=1\) and \(\det R=+1\);
- \(R\boldsymbol q_A=(0,0,Q_A)\);
- the DM Lorentz tensor transforms as
  \(L_q=\Lambda_R L_{\rm lab}\Lambda_R^T\);
- the exact nucleon current rotates with the same \(R\);
- the full \(4\times4\) DM-spin \(\otimes\) nucleon-spin amplitude,
  its charge part, and its spatial part are invariant;
- the spin-summed amplitude norm is invariant;
- the free on-shell nucleon Ward identity holds with \(q_N=q_A\).

This closes the direct-covariant versus q-frame part of P3 at one
representative phase-space point. It does not test the nuclear multipole
expansion or any AFH OBDME.

## 3. Actual three-body Eq. (107) bridge

The test also takes the actual spin-resolved \(\mathcal T_3^i\) matrices,
rotates them to the q-aligned frame, and flattens the four DM spin
transitions into complex spatial amplitudes. It evaluates AFH Eq. (107)
before spin averaging, using the correct initial-DM-spin average factor
(two), and compares the result with the independent 4x4 Lorentz-tensor
extractor. The three coefficients \(C_\Delta\), \(C_{\Sigma'}\), and
\(C_{\Sigma'\Delta}\) must agree, with the signed mixed coefficient
negative for the current benchmark.

This is a direct check of the actual three-body particle-side tensor
against the AFH Eq. (107) coefficient algebra. It still does not replace
the nuclear OBDME contraction:
\[
\mathcal R_{\alpha\beta}^{(3)}W_{\alpha\beta}
\]
must be computed with the native AFH multipole matrix elements and
compared to the direct covariant one-body-current contraction before a
full nuclear-current result is claimed.

## 4. Reproduction

Run the full-current test suite:
~~~bash
python -m unittest research.three_body_full_current_nucleon_match.test_three_body_qframe_full_current_projection -v
~~~



## 5. Updated P3-A acceptance record

Workflow [44295391452](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44295391452):
the full-current job passed with 92 tests, including:
- direct covariant versus q-aligned full \(4\times4\) amplitude;
- lab-frame versus q-frame AFH Eq. (107) coefficients using the
  frame-independent transverse projector;
- signed \(C_{\Sigma'\Delta}\) consistency;
- coherent addition of the two scalar-emission amplitudes and a nonzero
  squared-amplitude interference cross term.

The separate quadrature-convergence job was still running at the time of
this update. This record is **P3-A PASS**, not full P3 PASS. The many-body
AFH OBDME/multipole comparison remains P3-B.
