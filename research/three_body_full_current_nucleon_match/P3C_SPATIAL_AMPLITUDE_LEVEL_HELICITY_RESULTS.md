# P3-C: Xe-131 spatial amplitude-level helicity reconstruction

**Subgate status:** PASS_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RECONSTRUCTION  
**Overall P3-C status:** OPEN_FULL_COVARIANT_NUCLEAR_AMPLITUDE_NOT_YET_VALIDATED  
**Formal width:** Pole only  
**Date:** 2026-11-19

## 1. Purpose and scope

This calculation moves the spatial AFH check beyond a response-level
contraction. It retains the complex three-body Gram tensor
\[
G_{\mu a,\nu b}^{(3)}
=\int d\Phi_3\,c_a^\mu c_b^{\nu *}
\]
and the signed, rank-resolved Xe-131 reduced amplitudes
\[
\mathcal M_{\Delta,J},\qquad \mathcal M_{\Sigma',J}.
\]
For each transverse helicity and DM Pauli channel, the two AFH amplitudes
are combined coherently before the Gram contraction and before summing
over multipole ranks.

The check compares:
1. the direct Cartesian three-body tensor contracted with the AFH
   Eq. (107) coefficients; and
2. the helicity-amplitude reconstruction, with the signed
   \(\Sigma'\)-\(\Delta\) term retained rank by rank.

This is the spatial-sector amplitude-level subgate. It is not yet the
independent coordinate-space bound-nucleus current comparison required
for the complete P3-C gate.

## 2. Conventions and amplitude reconstruction

The phase-space tensor is stored in a right-handed q_A frame with
\(\boldsymbol q_A\) along \(+z\). The AFH Fourier convention is
\[
\boldsymbol q_{\rm AFH}=-\boldsymbol q_A.
\]
We therefore use the right-handed AFH basis
\((\boldsymbol e_1,\boldsymbol e_2,\hat{\boldsymbol q}_{\rm AFH})
=(\hat x,-\hat y,-\hat z)\).

With
\[
\boldsymbol l_M=-F_1^V\boldsymbol{\mathcal T}_3,\qquad
\boldsymbol l_5=
\frac{i(F_1^V+F_2^V)}{2m_N}
(\boldsymbol q_{\rm AFH}\times\boldsymbol{\mathcal T}_3),
\]
the helicity coefficients are chosen as
\[
d_{\Delta,\lambda}^{a}
=\frac{Q_A}{\sqrt2m_N}\,
\boldsymbol\epsilon_\lambda^*\cdot\boldsymbol l_M^a,
\qquad
d_{\Sigma',\lambda}^{a}
=\frac{\lambda}{\sqrt2}\,
\boldsymbol\epsilon_\lambda^*\cdot\boldsymbol l_5^a,
\quad \lambda=\pm1.
\]
The signed helicity phase is not arbitrary. With this convention,
\[
\begin{aligned}
\sum_{\lambda,a}\langle|d_{\Delta,\lambda}^a|^2\rangle
&=C_\Delta,\\
\sum_{\lambda,a}\langle|d_{\Sigma',\lambda}^a|^2\rangle
&=C_{\Sigma'},\\
2\operatorname{Re}\sum_{\lambda,a}
\langle d_{\Delta,\lambda}^a
d_{\Sigma',\lambda}^{a*}\rangle
&=C_{\Sigma'\Delta},
\end{aligned}
\]
where the right-hand sides are the direct Eq. (107) coefficients
obtained from \(L_{\mu\nu}^{(3)}=\sum_aG_{\mu a,\nu a}^{(3)}\).

For every nuclear multipole rank \(J\), the amplitude is formed as
\[
\mathcal A_{J,\lambda}^{a}
=d_{\Delta,\lambda}^{a}\mathcal M_{\Delta,J}
+d_{\Sigma',\lambda}^{a}\mathcal M_{\Sigma',J}.
\]
The response normalization is applied as
\[
4\,C_0(A)\,\frac{4\pi}{2J_A+1}\,\frac14.
\]
Thus the equal-\(p=n\) factor four and the raw AFH \(1/4\) convention
are each included exactly once.

## 3. Pinned inputs

| Input | Provenance |
|---|---|
| Three-body tensor and response contraction | LZ workflow 44337928314, artifact 14442826214 |
| AFH spatial response and signed multipole amplitudes | LZ workflow 44337928314, artifact 14443055701 |
| AFH v6.0 source SHA-256 | dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372 |
| Isotope | Xe-131, \(J_A=3/2\) |
| \(C_0(131)\) | 1.0000825298069376 |
| Form-factor anchors | \(F_1^V(0)=3,\ F_2^V(0)=-0.552\) |
| Nucleon mass | \(m_N=0.938918\) GeV |
| Width prescription | Pole only |

The AFH amplitudes are still marked
PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES; native Wolfram
validation is pending.

## 4. Numerical results

The full complex Gram tensor is Hermitian. Its minimum eigenvalue over
these benchmarks is \(-3.20\times10^{-14}\), consistent with the
existing PSD tolerance \(-10^{-10}\). The stored \(L_{\mu\nu}\) is
reconstructed from \(G_{\mu a,\nu b}\) with zero residual at the archived
precision.

| Benchmark | \(E_R\) | \(q_A\) (GeV) | \(K_{\rm helicity}\), PCHIP amplitudes | Relative amplitude/Cartesian residual |
|---|---:|---:|---:|---:|
| green_450keV | 200 keV | 0.2209306022 | 0.00835366938272 | \(2.08\times10^{-16}\) |
| green_1MeV | 200 keV | 0.2209306022 | 0.000514111110719 | \(4.22\times10^{-16}\) |
| near_pole_362keV_g2_0p1 | 267 keV | 0.2552681134 | 0.610748897628 | \(5.45\times10^{-16}\) |
| near_pole_362keV_g2_1 | 267 keV | 0.2552681134 | 0.136728078354 | \(6.09\times10^{-16}\) |

The global residuals are
\[
\boxed{
\max\delta_{\rm amp/cart}=6.09\times10^{-16},\qquad
\max\delta_{C_{\rm Eq.(107)}}=8.53\times10^{-16}.
}
\]
The deliberately reversed \(\Sigma'\) helicity phase flips the signed
\(\Sigma'\)-\(\Delta\) coefficient while leaving the two diagonal
coefficients unchanged. This is covered by a unit test.

## 5. Interpolation comparison

The existing P3-C response contraction linearly interpolates the total
\(\Delta,\Sigma',\Sigma'\Delta\) response columns. This calculation
instead interpolates the signed rank amplitudes and reconstructs the
responses. The selected-point differences are:

| Comparison | 200 keV benchmarks | 267 keV benchmarks |
|---|---:|---:|
| PCHIP signed-amplitude kernel vs linear-response kernel | \(5.53\times10^{-6}\) | \(1.14\times10^{-6}\) |
| Linear signed-amplitude kernel vs linear-response kernel | \(1.95\times10^{-6}\) | \(4.97\times10^{-7}\) |
| PCHIP-amplitude vs linear-amplitude kernel | \(3.58\times10^{-6}\) | \(6.42\times10^{-7}\) |

These are few-ppm differences at the selected benchmarks. They are not a
global interpolation bound, particularly near response zeros or
diffraction minima. For the final recoil calculation, the preferred
interpolation variable is the signed reduced multipole amplitude; the
diagonal and interference responses should then be reconstructed from
those interpolated amplitudes.

## 6. Reproduction

The standalone script is
p3c_amplitude_level_helicity_crosscheck.py; its four unit tests are in
test_p3c_amplitude_level_helicity_crosscheck.py.

The full-current workflow now:
1. generates the pole-only three-body tensor;
2. generates the signed AFH spatial multipole archive;
3. computes the C0-consistent response contraction;
4. runs this helicity-amplitude cross-check; and
5. includes the JSON result in the
   full-three-body-current-nucleon-match-and-phase-space-tensor artifact.

## 7. What this does not establish

The result must not be promoted to a full P3-C PASS because:

1. the AFH spatial amplitudes are still source-translated Python outputs;
   the native Wolfram P3-B comparison is queued;
2. the charge multipoles \(M,\Phi''\) are not rank-resolved in this archive,
   so the full charge-plus-spatial nuclear amplitude is not compared at
   amplitude level;
3. an independent direct coordinate-space bound-nucleus current
   calculation using the same OBDMEs and phases is not yet implemented;
4. finite-\(t_N\) \(F_1^V,F_2^V\), higher-order one-body terms, and two-body
   nuclear currents are not included.

Accordingly, the accepted statement is:
\[
\boxed{\text{P3-C spatial helicity-amplitude subgate PASS; full P3-C OPEN.}}
\]
