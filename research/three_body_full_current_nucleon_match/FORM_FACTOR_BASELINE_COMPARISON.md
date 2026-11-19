# Nucleon form-factor baseline and AFH response comparison

**Project:** LZ-3-body-for-hdm  
**Updated:** 2026-11-19  
**Status:** original finite-q AFH nuclear form factor retained; finite-\(t_N\) low-order nucleon-current diagnostics run in parallel; exact legacy flavor-resolved input still to be pinned  
**Formal nuclear input:** AFH v6.0 only  
**Formal width prescription:** asymmetric Pole width only

## 1. Comparison question

The original calculation is not a point-nucleus calculation. The paper source writes the coherent nuclear replacement as
\[
g_N\longrightarrow 3A g_{Vq}F_N(\boldsymbol q),\qquad F_N(\boldsymbol 0)=1,
\]
and the archived Mathematica rate engine implements its finite-momentum nuclear shape through
\[
R_A(Q_A)=A^2\frac{W_M(y_A)}{W_M(0)},\qquad
y_A=\left(\frac{Q_A b_A}{2}\right)^2.
\]
Thus the original AFH \(W_M(Q_A)\) already contains the finite-q nuclear form factor. It must remain in every comparison denominator; do not multiply an additional Helm or AFH nuclear form factor on top of it.

There is a second, distinct layer: the finite-momentum structure of the single-nucleon vector current, described by flavor-resolved \(F_1^{q/N}(t_N)\) and \(F_2^{q/N}(t_N)\). The current work adds this Dirac-Pauli layer while keeping the original AFH nuclear response unchanged.

For a fixed finite-\(t_N\) prescription, define
\[
R_{\mathrm{AFH},M}^{(0)}
\propto F_1^V(0)^2 L_C W_M(Q_A),
\]
\[
R_{t_N,M}\propto c_M(t_N)^2 L_C W_M(Q_A),
\]
and
\[
R_{\mathrm{charge}}\propto L_C\left[
c_M^2 W_M+c_{\Phi''}^2W_{\Phi''}
+2c_Mc_{\Phi''}W_{M\Phi''}\right].
\]
Here \(R_{\mathrm{AFH},M}^{(0)}\) is the original AFH M-only baseline: the nucleon-current normalization is frozen at zero transfer, but the full finite-q AFH nuclear response is retained. It is not a pointlike-nucleus result.

Two ratios must be reported because they answer different questions:
\[
\boxed{\frac{R_{\mathrm{charge}}}{R_{t_N,M}}-1}
\]
isolates the added \(\Phi''\) and signed \(M-\Phi''\) response at fixed nucleon form factors, whereas
\[
\boxed{\frac{R_{\mathrm{charge}}}{R_{\mathrm{AFH},M}^{(0)}}-1}
\]
is the total change relative to the original AFH M-only calculation, including the finite-\(t_N\) nucleon-current correction. The second ratio is the direct legacy comparison; the first is the clean response-only comparison.

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

For the formal one-body impulse current, the nucleon vertex carries the full external four-transfer,
\[
q_N^\mu=q_A^\mu,
\qquad
\boxed{t_N=t_A=-2m_AE_R,\quad -t_N=2m_AE_R.}
\]
Its spatial momentum is still \(\boldsymbol q_N=\boldsymbol q_A\), so the spatial factor in the AFH/NR coefficients is \(Q_A^2=2m_AE_R+E_R^2\).

A distinct static-free-nucleon diagnostic sets \(q_N^0=0\), giving
\[
t_N^{\rm static}=-Q_A^2=t_A-E_R^2.
\]
This is not the same transfer prescription. The formal P4 calculations now use the full external transfer \(q_N^\mu=q_A^\mu\); the static prescription is retained only as an optional diagnostic. Although the numerical difference is tiny at keV recoil energies, metadata must keep \(t_A\), \(t_N\), and \(Q_A^2\) separate.

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
\frac{Q_A^2}{4m_N^2}
\left[F_1^V(t_N)+2F_2^V(t_N)\right].
\]

The signed \(M-\Phi''\) interference must be retained. The spatial-current \(\Delta,\Sigma'\) terms and their signed interference are handled separately by the leading-static candidate and remain subject to the P3-C validation gate.

## 4. Form-factor prescriptions in the current Python engine

The code provides three distinct inputs.

| Prescription | Definition | Interpretation |
|---|---|---|
| original AFH M-only baseline | \(F_1^V(0)=3\) normalization multiplying the finite-q AFH \(W_M(Q_A)\) | Direct comparison with the original nuclear-response calculation; not a point nucleus |
| bishara_linear | \(F_1^V(Q_N^2)=3-(8.392\,{\rm GeV}^{-2})Q_N^2\), \(F_2^V=-0.552\) | First-order low-\(Q_N^2\) diagnostic from the flavor-separated Dirac slopes; \(F_2\) held at its zero-transfer value |
| isoscalar_zexp | Isoscalar electromagnetic Sachs \(z\)-expansion plus the strange-current inputs | Finite-\(Q_N^2\) alternative diagnostic |

The bishara_linear prescription is the explicit first-order flavor-summed low-\(t_N\) expansion from Bishara et al. Appendix A.1, not an all-orders form factor:
\[
F_1^{uds,N}(t_N)=3+8.392t_N+\mathcal O(t_N^2),\qquad
F_2^{uds,N}(0)=-0.552.
\]
The archived matching record warns that this slope is a local \(t_N=0\) check and must not be extrapolated uncritically across the full \(Q_A\) interval; the quoted \(F_2(0)\) does not determine \(F_2(t_N)\). We therefore use bishara_linear as the requested low-order comparison benchmark, but retain its provisional status and show isoscalar_zexp as an alternative sensitivity diagnostic. Neither is silently claimed to be an exact all-orders legacy parameterization.

## 5. Xe-131 selected-point comparison

The following arithmetic uses the archived Xe-131 charge-response ratios at the updated recoil points:

| \(E_R\) | \(W_{\Phi''}/W_M\) | \(W_{M\Phi''}/W_M\) |
|---:|---:|---:|
| 200 keV | 0.03695594 | -0.19120930 |
| 267 keV | 19.84506258 | -4.28296439 |

The corresponding form-factor and charge-sector diagnostics are:

| \(E_R\) | Prescription | \(F_1^V\) | \(F_2^V\) | \(c_M\) | \(c_{\Phi''}\) | \(R_{t_N,M}/R_{\mathrm{AFH},M}^{(0)}\) | \(R_{\rm charge}/R_{t_N,M}\) | \(R_{\rm charge}/R_{\mathrm{AFH},M}^{(0)}\) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 200 keV | bishara_linear | 2.590773 | -0.552000 | 2.580493 | 0.020560 | 0.739883 | 0.996955 | 0.737630 |
| 200 keV | isoscalar_zexp | 2.663163 | -0.468053 | 2.651222 | 0.023883 | 0.780997 | 0.996558 | 0.778309 |
| 267 keV | bishara_linear | 2.453682 | -0.552000 | 2.441223 | 0.024917 | 0.662175 | 0.914637 | 0.605649 |
| 267 keV | isoscalar_zexp | 2.563886 | -0.449775 | 2.548523 | 0.030726 | 0.721663 | 0.899610 | 0.649216 |

All ratios in the table are dimensionless. The first ratio column measures the finite-\(t_N\) single-nucleon normalization relative to the original AFH M-only baseline. The \(R_{\rm charge}/R_{t_N,M}\) column isolates the added \(\Phi''\) and signed \(M-\Phi''\) interference at fixed form-factor prescription. The last column gives the total shift relative to the original calculation while preserving its finite-q AFH nuclear shape.

Two conclusions follow:

1. The finite-\(Q_N^2\) single-nucleon-current normalization can change the \(M\)-only result by tens of percent relative to the original AFH M-only baseline. This is an additional nucleon-current correction; the original finite-q nuclear response remains present in both numerator and denominator.
2. The additional charge-sector correction is small at 200 keV but reaches several-to-ten percent at 267 keV, where the \(W_M\) response is near a diffraction minimum.

These are selected-point charge-sector diagnostics. They are not a natural-xenon halo-integrated result, and they do not include the spatial-current candidate.

## 6. Required reporting convention

Every fixed-speed and halo-fold result must retain, separately:

1. the original AFH M-only baseline, \(F_1^V(0)^2W_M(Q_A)\), which already includes the finite-q nuclear form factor;
2. the finite-\(t_N\) M-only result with the chosen nucleon \(F_1,F_2\);
3. the \(M+\Phi''+M\Phi''\) Coulomb-sector result;
4. the leading-static full one-body candidate, with \(\Delta,\Sigma'\) and signed \(\Sigma'-\Delta\) interference.

Always report both ratios: item 3/item 2 isolates the additional AFH multipoles at fixed nucleon form factors; item 3/item 1 compares with the original AFH calculation. Item 1 is not a point-nucleus baseline: it retains \(W_M(Q_A)\). Never multiply an extra nuclear form factor onto \(W_M\), and never describe the full item 3/item 1 difference as an AFH response correction alone.

The Xe-131 fixed-speed and P4 natural-xenon workflows run bishara_linear and isoscalar_zexp separately. Both use the formal full-transfer prescription \(t_N=t_A=-2m_AE_R\) for the nucleon form-factor argument while retaining \(Q_A^2=2m_AE_R+E_R^2\) in the spatial NR/AFH coefficients. The static \(q_N^0=0\) choice is only an optional diagnostic. The full six-channel fixed-speed recoil scan evaluates both prescriptions after one shared three-body phase-space integration at each recoil point. Each row reports both the finite-\(t_N\) M-only denominator and the original AFH M-only baseline. The spatial candidate remains unpromoted until P3-C passes.

The Xe-131 fixed-speed dual-form-factor workflow passed on 2026-11-19 (run 44443361283, artifact 14491448839; 7/7 regression tests). The measured primary ratios are:

| \(E_R\) | bishara_linear | isoscalar_zexp |
|---:|---:|---:|
| 200 keV | 0.9969554027 (-0.304460%) | 0.9965580497 (-0.344195%) |
| 267 keV | 0.9146368945 (-8.536311%) | 0.8996103903 (-10.038961%) |


A provenance distinction remains important. The archived Mathematica rate engine calls the AFH nuclear response at finite spatial \(Q_A\) and multiplies it by a constant coupling-squared prefactor; its recorded production path does not explicitly evaluate \(F_1^{uds,N}(t_N)\) or \(F_2^{uds,N}(t_N)\). Thus the original calculation did include finite nuclear structure through AFH \(W_M(Q_A)\), but that fact alone does not establish that a finite-\(t_N\) single-nucleon Dirac-Pauli form factor was applied in the rate engine.

The checked paper-source main.tex explicitly contains the finite-q nuclear factor \(F_N(\boldsymbol q)\), and the archived Mathematica notebook realizes it with the AFH \(W_M(Q_A)\) response. That original nuclear shape factor is therefore included in the baseline used here. What is not explicit in the archived rate-engine path is a separate finite-\(t_N\), flavor-resolved single-nucleon \(F_1^{q/N},F_2^{q/N}\) insertion: the notebook uses a constant effective nucleon coupling. The low-order Bishara input supplies the flavor-summed first derivative of \(F_1\) and the zero-transfer \(F_2(0)\), which is the basis of bishara_linear. If a different low-order quark-shape prescription was used in an earlier local calculation, its exact function and coefficients still need to be recovered before we can claim byte-for-byte reproduction of that additional layer.

## 7. Validation boundary and next steps

- P3-C's current spatial helicity-amplitude subgate uses \(q=0\) anchors and passes its internal Cartesian/helicity reconstruction; this does not validate finite-\(t_N\) full nuclear amplitudes.
- P3-B's seven-isotope native Wolfram AFH comparison remains a hard gate. Python-translated AFH data are not a substitute.
- The original low-order quark/nucleon form-factor prescription must be pinned to its exact source and coefficients before either diagnostic is called the legacy input.
- After native AFH validation, run the two finite-\(Q_N^2\) halo folds with the same Pole-width three-body tensor and report convergence separately for speed, three-body phase space, and recoil interpolation.
- Do not promote the spatial-current candidate to a physical full-current result before the independent P3-C covariant-to-AFH nuclear-amplitude comparison passes.
