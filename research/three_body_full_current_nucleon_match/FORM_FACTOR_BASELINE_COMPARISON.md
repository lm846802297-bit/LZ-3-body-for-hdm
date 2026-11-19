# Nucleon form-factor baseline and AFH response comparison

**Project:** LZ-3-body-for-hdm  
**Updated:** 2026-11-19  
**Status:** finite-\(Q_N^2\) diagnostics prepared; exact legacy form-factor provenance still to be pinned  
**Formal nuclear input:** AFH v6.0 only  
**Formal width prescription:** asymmetric Pole width only

## 1. Comparison question

The purpose of this comparison is to isolate the change caused by adding AFH nuclear responses without conflating it with the finite-momentum nucleon-current form factors.

For a fixed form-factor prescription, define

\[
R_{q=0,M}\propto F_1^V(0)^2 W_M,
\]

\[
R_{t_N,M}\propto c_M(t_N)^2 W_M,
\]

and

\[
R_{\mathrm{charge}}\propto
c_M^2 W_M+c_{\Phi''}^2W_{\Phi''}
+2c_Mc_{\Phi''}W_{M\Phi''}.
\]

The required comparison is

\[
\boxed{
\frac{R_{\mathrm{charge}}}{R_{t_N,M}}-1
}
\]

because numerator and denominator then use the same \(F_1^V(t_N),F_2^V(t_N)\). The \(q=0\) result is retained as a secondary normalization reference only.

The AFH \(W_M\) response already contains finite nuclear structure. Thus “\(q=0\) nucleon form factors” must not be confused with a point-nucleus approximation.

## 2. Transfer variables: keep the invariants separate

For an initially resting on-shell nucleus,

\[
q_A^\mu=P_A'^\mu-P_A^\mu=(E_R,\boldsymbol q_A).
\]

The exact Lorentz invariant is

\[
\boxed{t_A=q_A^\mu q_{A,\mu}=-2m_AE_R,}
\]

whereas the exact spatial recoil momentum is

\[
\boxed{Q_A^2=|\boldsymbol q_A|^2=E_R(E_R+2m_A).}
\]

These differ by \(E_R^2\). The vector-mediator propagator therefore uses

\[
\boxed{
(m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2,
}
\]

not \((m_V^2+Q_A^2)^2\).

For the nucleon form factor, the current implementation uses the static one-body impulse diagnostic

\[
q_N^0=0,\qquad \boldsymbol q_N=\boldsymbol q_A,
\qquad Q_N^2=-t_N=|\boldsymbol q_N|^2=Q_A^2.
\]

This is a separate approximation at the nucleon vertex. It must not be reused as the mediator's Lorentz-invariant transfer.

## 3. Nucleon-current matching

The Dirac-Pauli nucleon current is

\[
J_N^\mu=
\bar u_N(k_N')
\left[
F_1^V(t_N)\gamma^\mu+
\frac{iF_2^V(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu}
\right]u_N(k_N).
\]

For the static charge-sector reduction used by the diagnostic,

\[
c_M=F_1^V(t_N)
+\frac{t_N}{8m_N^2}
\left[F_1^V(t_N)+2F_2^V(t_N)\right],
\]

\[
c_{\Phi''}=
\frac{Q_N^2}{4m_N^2}
\left[F_1^V(t_N)+2F_2^V(t_N)\right].
\]

The signed \(M-\Phi''\) interference must be retained. The spatial-current \(\Delta,\Sigma'\) terms and their signed interference are handled separately by the leading-static candidate and remain subject to the P3-C validation gate.

## 4. Form-factor prescriptions in the current Python engine

The code provides three distinct inputs.

| Prescription | Definition | Interpretation |
|---|---|---|
| \(q=0\) anchor | \(F_1^V=3,\ F_2^V=-0.552\) | Secondary normalization reference |
| bishara_linear | \(F_1^V(Q_N^2)=3-(8.392\,{\rm GeV}^{-2})Q_N^2\), \(F_2^V=-0.552\) | First-order low-\(Q_N^2\) diagnostic from the flavor-separated Dirac slopes; \(F_2\) held at its zero-transfer value |
| isoscalar_zexp | Isoscalar electromagnetic Sachs \(z\)-expansion plus the strange-current inputs | Finite-\(Q_N^2\) alternative diagnostic |

Neither finite-\(Q_N^2\) prescription is to be silently identified with the exact legacy calculation until its original input file and parameter provenance are pinned. In particular, the first-order Bishara slope is a low-\(Q_N^2\) diagnostic, not a claim that the full quark-current form factor is known to all orders.

## 5. Xe-131 selected-point comparison

The following arithmetic uses the archived Xe-131 charge-response ratios at the updated recoil points:

| \(E_R\) | \(W_{\Phi''}/W_M\) | \(W_{M\Phi''}/W_M\) |
|---:|---:|---:|
| 200 keV | 0.03695594 | -0.19120930 |
| 267 keV | 19.84506258 | -4.28296439 |

The corresponding form-factor and charge-sector diagnostics are:

| \(E_R\) | Prescription | \(F_1^V\) | \(F_2^V\) | \(c_M\) | \(c_{\Phi''}\) | \(R_{t_N,M}/R_{q=0,M}\) | \(R_{\rm charge}/R_{t_N,M}\) | \(R_{\rm charge}/R_{q=0,M}\) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 200 keV | bishara_linear | 2.590773 | -0.552000 | 2.580493 | 0.020560 | 0.739883 | 0.996955 | 0.737630 |
| 200 keV | isoscalar_zexp | 2.663163 | -0.468053 | 2.651222 | 0.023883 | 0.780997 | 0.996558 | 0.778309 |
| 267 keV | bishara_linear | 2.453682 | -0.552000 | 2.441223 | 0.024917 | 0.662175 | 0.914637 | 0.605649 |
| 267 keV | isoscalar_zexp | 2.563886 | -0.449775 | 2.548523 | 0.030726 | 0.721663 | 0.899610 | 0.649216 |

All ratios in the table are dimensionless. The \(R_{\rm charge}/R_{t_N,M}\) column isolates the added \(\Phi''\) and signed \(M-\Phi''\) interference at fixed form-factor prescription.

Two conclusions follow:

1. The finite-\(Q_N^2\) nucleon-current normalization can change the \(M\)-only result by tens of percent relative to the \(q=0\) anchor.
2. The additional charge-sector correction is small at 200 keV but reaches several-to-ten percent at 267 keV, where the \(W_M\) response is near a diffraction minimum.

These are selected-point charge-sector diagnostics. They are not a natural-xenon halo-integrated result, and they do not include the spatial-current candidate.

## 6. Required reporting convention

Every fixed-speed and halo-fold result must retain, separately:

1. the \(q=0\) nucleon-form-factor \(M\) reference;
2. the finite-\(t_N\) \(M\)-only result;
3. the \(M+\Phi''+M\Phi''\) Coulomb-sector result;
4. the leading-static full one-body candidate, with \(\Delta,\Sigma'\) and signed \(\Sigma'-\Delta\) interference.

The primary response correction is always divided by item 2, using the same \(F_1,F_2\) prescription in numerator and denominator. Item 1 is a secondary normalization reference. Never compare a finite-\(t_N\) numerator to a \(q=0\) denominator and describe the whole difference as an AFH response correction.

The Xe-131 fixed-speed charge-sector workflow and the P4 natural-xenon workflow now run bishara_linear and isoscalar_zexp separately. The Xe-131 comparison reports the finite-t_N M-only denominator as its primary ratio; P4 reports both the Coulomb and leading-static candidate outputs. The candidate remains unpromoted until P3-C passes.

The Xe-131 fixed-speed dual-form-factor workflow passed on 2026-11-19 (run 44443361283, artifact 14491448839; 7/7 regression tests). The measured primary ratios are:

| \(E_R\) | bishara_linear | isoscalar_zexp |
|---:|---:|---:|
| 200 keV | 0.9969554027 (-0.304460%) | 0.9965580497 (-0.344195%) |
| 267 keV | 0.9146368945 (-8.536311%) | 0.8996103903 (-10.038961%) |


A provenance distinction remains important. The archived Mathematica rate engine calls the AFH nuclear response at finite spatial \(Q_A\) and multiplies it by a constant coupling-squared prefactor; its recorded production path does not explicitly evaluate \(F_1^{uds,N}(t_N)\) or \(F_2^{uds,N}(t_N)\). Thus the original calculation did include finite nuclear structure through AFH \(W_M(Q_A)\), but that fact alone does not establish that a finite-\(t_N\) single-nucleon Dirac-Pauli form factor was applied in the rate engine.

The checked paper-source main.tex states the universal quark coupling and AFH \(W_M\), but does not itself spell out a finite-\(t_N\) flavor-resolved \(F_1^q/F_2^q\) low-order parameterization. The archived DMFormFactor-v6 file supplies the nuclear-response machinery; it is not, by itself, evidence for a particular quark-level shape-factor input. The longer quark-to-nucleon matching record lists the Bishara \(F_1\) slope as a low-\(Q_N^2\) diagnostic and explicitly marks the finite-\(t_N\) form-factor insertion into the old rate engine as pending. Therefore bishara_linear is treated as a low-\(Q_N^2\) diagnostic until the exact legacy expression and coefficients are identified.

## 7. Validation boundary and next steps

- P3-C's current spatial helicity-amplitude subgate uses \(q=0\) anchors and passes its internal Cartesian/helicity reconstruction; this does not validate finite-\(t_N\) full nuclear amplitudes.
- P3-B's seven-isotope native Wolfram AFH comparison remains a hard gate. Python-translated AFH data are not a substitute.
- The original low-order quark/nucleon form-factor prescription must be pinned to its exact source and coefficients before either diagnostic is called the legacy input.
- After native AFH validation, run the two finite-\(Q_N^2\) halo folds with the same Pole-width three-body tensor and report convergence separately for speed, three-body phase space, and recoil interpolation.
- Do not promote the spatial-current candidate to a physical full-current result before the independent P3-C covariant-to-AFH nuclear-amplitude comparison passes.
