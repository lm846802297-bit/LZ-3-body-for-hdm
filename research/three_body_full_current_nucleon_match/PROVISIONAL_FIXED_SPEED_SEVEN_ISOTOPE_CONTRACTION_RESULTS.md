# Provisional fixed-speed seven-isotope AFH contraction results

> **Adopted-baseline notice (2026-11-19):** This remains a provisional fixed-speed response contraction with zero-momentum nucleon-current anchors. It is not the adopted B rate, which requires finite-(t_N) Bishara (widehat F_1,widehat F_2) and AFH (W_M(y_A)) only. Do not promote these kernel numbers as B; recompute B separately and keep this file as a P3-D/current-matching diagnostic.

> **Superseded normalization record (2026-11-18).** The contraction below predates the common-\(C_0(A)\) correction to the charge sector. Its qualitative benchmark conclusion is retained as historical context, but its charge-kernel numbers must not be used as the current result. The canonical corrected result is [P3_C_C0_CONSISTENT_CONTRACTION.md](P3_C_C0_CONSISTENT_CONTRACTION.md), based on workflow 44305980766 and artifact 14428247140.


**Workflow:** [44267886404](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44267886404)  
**Source commit:** eb1e598391a3e1aae41e07e3a8f78409f2c54007  
**Artifact:** full-three-body-current-nucleon-match-and-phase-space-tensor  
**Artifact ID:** 14410763795  
**Status:** PROVISIONAL_AFH_CONTRACTION_PASS

## 1. What passed

The workflow completed:
- 76 full-current regression tests;
- 16 native charge-sector engine unit tests;
- 9 selected component-wise quadrature-convergence benchmarks;
- 12 leading-static particle-coefficient benchmark points;
- 84 fixed-speed contractions (12 benchmark/width combinations times 7 xenon isotopes).

All 84 provisional contraction rows have positive total response kernels and no reported algebraic failures. The native response Cauchy--Schwarz and particle-side coefficient checks are exercised by the regression suite.

The separate phase-space tensor archive reports:
- Dirac-trace maximum relative residual: \(1.59813\times10^{-9}\), against \(2\times10^{-9}\);
- maximum Hermiticity residual: zero;
- maximum q-frame rotation residual: \(3.33\times10^{-16}\);
- Gram minimum eigenvalue: \(-2.70\times10^{-13}\), above the allowed \(-10^{-10}\) floor;
- tensor minimum eigenvalue: \(5.7463\times10^{-4}\).

The nine-benchmark convergence scan passes the successive-high-order criterion. Its largest final differences are:
\[
\begin{aligned}
\Delta_{\rm Gram}^{F}&=1.50126\times10^{-8},\\
\Delta_L^{F}&=1.50126\times10^{-8},\\
\Delta_{\rm active}&=1.56728\times10^{-5},\\
\Delta_{\rm point}&=1.51171\times10^{-8}.
\end{aligned}
\]
This is a medium-to-high-order convergence statement at the selected benchmarks, not a global error bound.

## 2. Leading-static coefficient hierarchy

Across the 12 particle-side benchmarks:
\[
\begin{aligned}
3.05\times10^{-9}
&\leq C_\Delta/C_M\leq1.26\times10^{-8},\\
5.08\times10^{-10}
&\leq C_{\Sigma'}/C_M\leq2.10\times10^{-9},\\
-1.03\times10^{-8}
&\leq C_{\Sigma'\Delta}/C_M\leq-2.49\times10^{-9}.
\end{aligned}
\]
The generic transverse helicity-odd contribution divided by the transverse sum is at most \(1.48\times10^{-15}\). The particle-side \(\Sigma'\)-\(\Delta\) Cauchy identity residual is at most \(1.72\times10^{-16}\).

The continuity-reduced charge weight differs from the direct Coulomb weight by at most \(5.13\times10^{-6}\) in this benchmark set. This reduction is conditional on conservation of the complete nuclear vector current; the point-nucleus identity validates kinematics and tensor conventions, not bound-nucleus current conservation.

## 3. Provisional seven-isotope response contraction

The response contraction uses the provisional Python translation of AFH v6.0 physical equal-proton/neutron responses, linearly interpolated in \(q_A\) on a 0.25 MeV grid. It uses zero-momentum form-factor anchors, not finite-\(t_N\) form factors. It is fixed-speed, with no halo fold.

The workflow reports 84 positive total kernels. The maximum absolute spatial-to-charge ratio is
\[
\boxed{
\max\left|\frac{\mathcal K_{\rm spatial}}{\mathcal K_{\rm charge}}\right|
=7.09596\times10^{-9}.
}
\]
This maximum occurs for Xe-131 at \(E_R=267\) keV, \(v_\chi=776\) km/s, benchmark \(\texttt{near\_pole\_362keV\_g2\_1}\), running-width scheme.

Selected Xe-131 rows (all at \(v_\chi=776\) km/s, \(g_2=1\), running-width scheme):

| Benchmark | \(E_R\) | \(q_A\) (GeV) | Charge kernel | Spatial kernel | Spatial/charge |
|---|---:|---:|---:|---:|---:|
| green_450keV | 200 keV | 0.2209306022 | \(1.3698541132\times10^9\) | \(8.66813\times10^{-3}\) | \(6.32778\times10^{-12}\) |
| near_pole_362keV_g2_1 | 267 keV | 0.2552681134 | \(2.1690554487\times10^7\) | \(1.53915\times10^{-1}\) | \(7.09596\times10^{-9}\) |

For the 267 keV row, the individual spatial contributions are:
\[
\begin{aligned}
C_\Delta W_\Delta&=0.11534877,\\
C_{\Sigma'}W_{\Sigma'}&=0.00881508,\\
C_{\Sigma'\Delta}W_{\Sigma'\Delta}&=0.02975141.
\end{aligned}
\]
The response inputs are
\[
\begin{aligned}
W_\Delta&=2.25720\times10^{-3},\\
W_{\Sigma'}&=1.03625\times10^{-3},\\
W_{\Sigma'\Delta}&=-7.13467\times10^{-4}.
\end{aligned}
\]
The Cauchy--Schwarz margin is
\[
\sqrt{W_\Delta W_{\Sigma'}}-|W_{\Sigma'\Delta}|
=8.15915\times10^{-4}>0.
\]
The negative interference coefficient and negative response give a positive interference contribution for this convention and benchmark.

## 4. Interpretation — do not overstate

Within this provisional leading-static contraction, the spatial-current contribution is numerically negligible compared with the charge-sector kernel at these fixed-speed benchmarks. This is consistent with the very small particle-side transverse coefficients.

It does **not** yet establish that spatial nuclear responses are negligible in the physical natural-xenon rate, because:
1. the response table is a provisional Python translation, not a native-Wolfram AFH PASS;
2. the current uses \(q=0\) form-factor anchors, not the finite-\(t_N\) Dirac--Pauli matching used in the separate charge-sector ratio audit;
3. the fold is fixed-speed, not halo-integrated;
4. the exact AFH spherical-multipole phase convention, especially the signed \(\Sigma'\)-\(\Delta\) cross term, still requires direct source-level verification;
5. the direct covariant one-nucleon contraction, q-frame-rotated contraction, and AFH multipole contraction have not yet passed the P3 pointwise tensor comparison;
6. the nuclear-current continuity reduction is conditional on a conserved complete bound-nucleus current, including any required interaction-current contribution.

Accordingly, keep the label **PROVISIONAL_AFH_CONTRACTION_PASS**. Do not call this a full-current natural-xenon spectrum or a final event-rate prediction.

## 5. Native AFH gate status

The private native seven-isotope/eight-response run 44222502400, attempt 2, remains QUEUED on the self-hosted Windows/X64/research-gpu runner and has no artifact. The 16,807-point native comparison is therefore still pending. A passing Python regression or a passing provisional contraction does not substitute for that native gate.

## 6. Next physics steps

1. Complete the 16,807-point native AFH v6.0 comparison and rerun this exact 84-row contraction against native responses.
2. Verify the AFH \(\Delta,\Sigma'\), and signed \(\Sigma'\Delta\) spherical multipole phase conventions directly against the v6.0 operator definitions.
3. Perform P3 at selected phase-space points: direct covariant current contraction, q-frame-rotated contraction, and AFH multipole contraction must agree.
4. Only after those gates pass, use finite-\(t_N\) form factors and perform the natural-xenon halo fold with pointlike-M, finite-\(t_N\)-M, charge-sector, and full matched-current baselines kept separate.
