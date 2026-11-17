# Exploratory Phi'' charge-projection stress test — not a physical VV matching

**Status:** arithmetic and interpolation are reproducible; the coefficient map is a trial ansatz and must not be interpreted as a three-body rate prediction.

## 1. Motivation

PR #54 established that Xe-131 has nonzero AFH spin-orbit response
\(W_{\Phi''}\) and mixed response \(W_{M\Phi''}\), especially near minima of
\(W_M\). It explicitly did not establish the three-body WIMP coefficient
multiplying these responses.

This file tests the numerical sensitivity of the existing AFH responses to
one possible charge-sector coefficient map. It is a diagnostic, not the
physical contraction of the full vector current.

## 2. Exact object that must eventually be matched

The full amplitude is
\[
\mathcal M_3=\mathcal T_3^\mu(p,p',k_s)\,J^N_\mu(q_A),
\]
with
\[
\mathcal T_3^\mu=
\bar u_{\chi_1}(p')
\left[
\gamma^\mu\frac{\slashed r_1+m_{\chi_2}}{D_1}
+\frac{\slashed r_2+m_{\chi_2}}{D_2}\gamma^\mu
\right]u_{\chi_1}(p).
\]
Both scalar-emission orderings must be retained coherently. The nucleon
current has both time and spatial components. A charge-only projection
\(\mathcal T_3^0J_N^0\) is not the full amplitude and is not, by itself, a
physical AFH response coefficient.

The AFH \(W_{\Phi''}\) response is associated with a spin-orbit nuclear
operator. In a full VV reduction, the spin-orbit terms from the charge and
spatial currents must be combined before identifying the coefficient of the
relative-velocity operator and the associated nuclear response. One must
not infer the full \(\Phi''\) coefficient from \(F_2\), from the charge
density alone, or from \(W_{\Phi''}/W_M\).

## 3. Trial coefficient map used only for sensitivity

For an exploratory numerical stress test, the script uses
\[
\eta_{\rm trial}=\frac{q_A^2}{4m_N^2}
\left(1+2\frac{F_2^V}{F_1^V}\right),
\]
\[
C_M^{\rm trial}/F_1^V=1-\eta_{\rm trial}/2,\qquad
C_{\Phi''}^{\rm trial}/F_1^V=\eta_{\rm trial}.
\]
This produces
\[
R_C^{\rm trial}=
(1-\eta_{\rm trial}/2)^2
+2(1-\eta_{\rm trial}/2)\eta_{\rm trial}
 \frac{W_{M\Phi''}}{W_M}
+\eta_{\rm trial}^2\frac{W_{\Phi''}}{W_M}.
\]

The superscript “trial” is essential. The expression is a sensitivity
parameterization, not a derived coefficient map for the complete
\(\mathcal T_3^\mu J^N_\mu\) amplitude.

## 4. Numerical sensitivity results

For the illustrative \(F_2/F_1=-0.15\) case, the trial expression gives:

| Three-body point | \(q_A\) | \(R_C^{\rm trial}\) | Trial change |
|---|---:|---:|---:|
| \(E_R=200\) keV | 220.9306 MeV | 0.98664069 | -1.33593% |
| \(E_R=267\) keV | 255.2681 MeV | 0.87210768 | -12.78923% |

At the exact second AFH \(W_M\) minimum,
\[
q_A=256.271867617\ {\rm MeV},
\]
the exact-point response values give \(R_C^{\rm trial}=0.96881984\), or
-3.11802%.

The strong variation across this diffraction structure shows why a
single response ratio at the exact minimum cannot substitute for evaluating
the actual three-body recoil point. These percentages are **not** the
predicted full VV recoil-rate corrections.

## 5. Why the full current matters

The nucleon vector current is
\[
J_N^\mu=\bar u_N'
\left[F_1^V(t)\gamma^\mu
-\frac{iF_2^V(t)}{2m_N}\sigma^{\mu\nu}q_\nu
\right]u_N,
\]
with the Pauli-term sign translated consistently to the project convention
\(q_A=P'-P\).

The charge and spatial pieces contain different nucleon momentum and spin
structures. In an elastic matching, these pieces are reorganized into the
nonrelativistic operator basis only after contracting both currents. The
three-body current has additional dependence on \(k_s\), the off-shell
\(\chi_2\) propagators, and the mass splitting. Therefore the elastic
operator coefficients cannot simply be copied into the three-body process.

Hoferichter, Klos, and Schwenk give the explicit one-body vector-current
reduction and its form-factor dependence in their Eq. (25). The present
project must perform the corresponding reduction with the actual
\(\mathcal T_3^\mu\), rather than retaining only its time component.

## 6. What the current code validates

The Python tests verify:
- the 2401-point AFH grid identity and Cauchy-Schwarz bound;
- local interpolation at the two PR #53 benchmark momenta;
- arithmetic of the trial response combination;
- invariance under a common AFH response normalization;
- use of exact selected-point AFH values at the nuclear minima;
- cancellation of the common \(I_{00}\) factor inside this trial charge-only
  ratio at fixed \(q_A\).

They do not validate the trial coefficient map as the physical three-body
matching.

## 7. Status and next work

- AFH \(\Phi''\) native Mathematica cross-check in PR #54: pending.
- Trial charge-projection sensitivity calculation: reproducible; CI passed.
- Spin-resolved \(\mathcal T_3^\mu\): not yet implemented in this study.
- Full Dirac-Pauli nucleon-current contraction: not yet implemented.
- Physical AFH coefficients and interferences: not yet established.
- No absolute cross section, halo integral, isotope sum, detector response,
  or likelihood is produced.

The next calculation is to construct the 2x2 spin matrix for every
\(\mathcal T_3^\mu\), reproduce the existing \(L^{\mu\nu}\) trace from it,
derive the nonconservation/Ward identity for \(m_{\chi_2}\ne m_{\chi_1}\),
and then perform the complete nucleon-current Pauli reduction.
