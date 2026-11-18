# P3-C: C0-consistent rank-resolved three-body AFH response contraction

**Status: PROVISIONAL_AFH_CONTRACTION_PASS.** This is a fixed-speed benchmark
contraction of the leading static three-body vector-current coefficients with
the AFH response basis. It is not the final P3-C covariant-current versus
AFH-multipole equivalence test, and it is not a halo-folded prediction.

Date: 2026-11-18

## 1. Inputs and provenance

| Input | Workflow / artifact |
|---|---|
| AFH-8 Python charge-sector response archive | run 44222087512, artifact 14391456283 |
| P3-B seven-isotope rank-resolved spatial archive | run 44305980766, artifact 14428386181 |
| P3-C fixed-speed coefficient and contraction output | run 44305980766, artifact 14428247140 |
| P3-B spatial-response CSV SHA-256 | 4e0a23c18d29df3af04a2531e75b7bffeaa3251d0efe97674b2287cf3c25e7e3 |
| P3-B rank-multipole CSV SHA-256 | e83f7499cd0af4ec8c1974238f09daf4899ca1b87205ec837ae0964a2e8532c6 |
| AFH v6.0 source SHA-256 | dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372 |

The P3-B archive contains 16,807 total-response rows and 9,604
rank-resolved multipole rows. Its archive validator passed. The independent
Python-to-Python response comparison also passed all 16,807 isotope/q rows.

Both nuclear inputs remain explicitly provisional Python translations:
native_afh_validated=false.

## 2. Normalization rule

The AFH-8 physical equal-p/n columns already contain the isospin factor four:
\[
R_{X,\mathrm{AFH8}}^{\mathrm{physical}}
=4\,\frac{4\pi}{2J_A+1}W_X.
\]

P3-B applies the common finite-decimal OBDME correction \(C_0(A)\) to the
spatial channels:
\[
R_{X,\mathrm{P3B}}^{\mathrm{physical}}
=4C_0(A)\,\frac{4\pi}{2J_A+1}W_X.
\]

The charge and spatial channels must use the same OBDME normalization.
Therefore, the contraction uses
\[
\boxed{
R_{\mathrm{charge}}^{\mathrm{consistent}}
=C_0(A)R_{\mathrm{charge,AFH8}}^{\mathrm{physical}}
}
\]
while it uses the P3-B spatial response columns directly. It does not multiply
the P3-B spatial columns by \(C_0\) again. The factor four is already present
once in both sets of physical equal-p/n columns.

The recorded C0 values are:

| Isotope | C0 |
|---|---:|
| Xe-128 | 1.0000924953327093 |
| Xe-129 | 1.0001103230777202 |
| Xe-130 | 1.0001260610682259 |
| Xe-131 | 1.0000825298069376 |
| Xe-132 | 1.0000445028489864 |
| Xe-134 | 1.0002068258192740 |
| Xe-136 | 1.0000015063597723 |

## 3. Response-basis contraction

For each fixed-speed benchmark, the particle-side three-body coefficients
are contracted with the physical AFH responses:
\[
\begin{aligned}
\mathcal K^{(3)}_{\mathrm{AFH}}
={}&C_M R_M+C_{\Phi''}R_{\Phi''}
+C_{M\Phi''}R_{M\Phi''}\\
&+C_\Delta R_\Delta
+C_{\Sigma'}R_{\Sigma'}
+C_{\Sigma'\Delta}R_{\Sigma'\Delta}.
\end{aligned}
\]

The spatial contribution is therefore
\[
\mathcal K_{\mathrm{spatial}}^{(3)}
=C_\Delta R_\Delta
+C_{\Sigma'}R_{\Sigma'}
+C_{\Sigma'\Delta}R_{\Sigma'\Delta}.
\]

The P3-B rank archive also allows the spatial sector to be reconstructed
multipole by multipole:
\[
\mathcal K_{\mathrm{spatial}}^{(3)}
=\sum_J\left[
C_\Delta R_{\Delta,J}
+C_{\Sigma'}R_{\Sigma',J}
+C_{\Sigma'\Delta}R_{\Sigma'\Delta,J}
\right].
\]

The code compares this rank sum with the total-response contraction at every
benchmark/isotope point.

## 4. Numerical acceptance

The contraction contains 12 fixed-speed benchmark/width combinations and
seven xenon isotopes, for 84 rows.

| Check | Result |
|---|---:|
| Total contracted rows | 84 |
| Positive total kernels | 84 / 84 |
| Maximum absolute spatial/charge ratio | \(7.0959581690\times10^{-9}\) |
| Maximum rank-sum reconstruction residual | \(1.1102230246\times10^{-16}\) |
| Minimum common C0 | 1.00000150636 |
| Maximum common C0 | 1.00020682582 |
| Failure count | 0 |

The largest spatial-to-charge ratio occurs for Xe-131 at
\(E_R=267\) keV and \(v_\chi=776\) km/s, in the
near_pole_362keV_g2_1 running-width benchmark:
\[
\left|\frac{\mathcal K_{\mathrm{spatial}}^{(3)}}
{\mathcal K_{\mathrm{charge}}^{(3)}}\right|
=7.0959581690\times10^{-9}.
\]

At this point the rankwise spatial contributions are:

| Multipole J | Spatial contribution |
|---:|---:|
| 1 | 0.11180846057 |
| 2 | 0 |
| 3 | 0.04211950933 |
| Sum | 0.15392796990 |

For Xe-129, the largest ratio in this benchmark set is
\(3.0993606832\times10^{-11}\). The five even-even isotopes
Xe-128, Xe-130, Xe-132, Xe-134 and Xe-136 have zero spatial response,
consistent with \(J_A=0\).

## 5. Interpretation

Within this fixed-speed, leading-static-current benchmark set, the spatial
AFH sector is extremely small relative to the charge sector. This is a
numerical statement about these 84 contractions, not yet a universal
statement about the natural-xenon event rate.

The result does not yet include:

- finite-\(t_N\) Dirac-Pauli form factors \(F_1^V(t_N)\) and \(F_2^V(t_N)\);
- a full recoil-energy and halo-velocity fold;
- natural-xenon isotope abundance weighting in the final rate;
- detector response, efficiency, resolution, or likelihood;
- native Wolfram validation of the P3-B spatial responses and amplitudes;
- the final direct covariant-current versus AFH multipole equivalence test.

The current result is therefore a useful provisional bound on the size of
the spatial-current contribution in the selected benchmarks. It must not be
promoted to a final P3-C PASS or used to remove spatial channels from the
paper before the native AFH gate and the full halo-folded comparison pass.

## 6. Reproduction and next gate

The full-current workflow now downloads the P3-B artifact from its preceding
job and invokes the C0-consistent contraction. Reproduce it with:

~~~bash
python research/three_body_full_current_nucleon_match/contract_three_body_afh_responses.py \
  --afh-dir /path/to/afh-eight-response \
  --spatial-dir /path/to/p3-spatial-response \
  --weights-json /path/to/three-body-multipole-leptonic-weights.json \
  --out /path/to/three-body-afh-response-contraction.json
~~~

The next mandatory gate is the private native Wolfram workflow. It must first
pass the seven-isotope ResponseNuclear comparison, then the separate
Xe-129/Xe-131 rank-amplitude comparison in
compare_p3_multipoles_vs_native.py. Only after those pass should the
covariant-current versus AFH multipole comparison be promoted.
