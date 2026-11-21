# P3-C: C0-consistent fixed-speed three-body × AFH contraction

**Status: PROVISIONAL_AFH_CONTRACTION_PASS — 84/84 benchmark/isotope rows pass.**  
**Workflow:** [44305980766](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44305980766)  
**PR head:** 1201d03c11030d71c7259277ee98937bf41c8025  
**Contraction artifact:** 14428247140  
**Spatial-response artifact:** 14428386181

## 1. What this stage tests

The three-body phase-space tensor and the leading-static one-body
Dirac--Pauli coefficients are contracted with the seven-isotope AFH
responses:
\[
\begin{aligned}
\mathcal K_A^{(3)}={}&
C_M R_M+C_{\Phi''}R_{\Phi''}+C_{M\Phi''}R_{M\Phi''}\\
&+C_\Delta R_\Delta+C_{\Sigma'}R_{\Sigma'}
+C_{\Sigma'\Delta}R_{\Sigma'\Delta}.
\end{aligned}
\]

The signed \(\Sigma'\)-\(\Delta\) term is retained. The calculation is a
fixed-speed response-kernel contraction before the common mediator and
coupling prefactors; it is not an absolute differential rate.

This stage is deliberately distinguished from P3-B's pointwise
many-body-amplitude comparison. It verifies the response-level contraction
and rankwise reconstruction, but it does not by itself establish
\[
\mathcal A_{\rm cov}^{\rm nuclear}
=\mathcal A_{q\text{-frame}}^{\rm nuclear}
=\mathcal A_{\rm AFH\ multipoles}^{\rm nuclear}.
\]

## 2. Corrected normalization policy

The earlier contraction implementation mixed two OBDME conventions:
the P3-B spatial responses already carried the common OBDME correction
\(C_0(A)\), while the AFH-8 charge responses did not. The corrected
implementation applies the same \(C_0(A)\) to the three charge responses
and does not multiply the spatial responses again:
\[
\boxed{
R_{M,\Phi'',M\Phi''}^{\rm consistent}
=C_0(A)R_{M,\Phi'',M\Phi''}^{\rm AFH8},
\qquad
R_{\Delta,\Sigma',\Sigma'\Delta}^{\rm consistent}
=R_{\rm spatial}^{\rm P3-B}.
}
\]

The AFH equal-\(p=n\) factor four remains a separate convention and is
applied exactly once in the physical response columns. \(C_0\) is not
another isospin factor; it is the common correction fixed by the
\(M(q_A=0)=A^2\) normalization anchor.

| Isotope | \(C_0(A)\) | \(C_0-1\) |
|---|---:|---:|
| Xe-128 | 1.0000924953327093 | \(9.2495\times10^{-5}\) |
| Xe-129 | 1.0001103230777202 | \(1.1032\times10^{-4}\) |
| Xe-130 | 1.0001260610682259 | \(1.2606\times10^{-4}\) |
| Xe-131 | 1.0000825298069376 | \(8.2530\times10^{-5}\) |
| Xe-132 | 1.0000445028489864 | \(4.4503\times10^{-5}\) |
| Xe-134 | 1.0002068258192740 | \(2.0683\times10^{-4}\) |
| Xe-136 | 1.0000015063597723 | \(1.5064\times10^{-6}\) |

The correction is small but must be common to the charge and spatial
OBDME normalization. The contraction code checks the per-isotope \(C_0\)
against the P3-B response CSV and metadata, and requires the canonical
2,401-point \(q_A\) grid with 0.25 MeV spacing for both inputs.

## 3. Inputs and provenance

| Input | Provenance |
|---|---|
| AFH-8 Python response database | Run 44222087512, artifact 14391456283 |
| AFH-8 source commit | dcefbeb7ad705b6c03f2b4689200eb1d9252e67b |
| AFH-8 response CSV SHA-256 | 59ea25093137a05b8ebcc158e2fe6a74fe5927599dbb16766b067aa1ad8e3caa |
| P3-B spatial response + rank archive | Run 44305980766, artifact 14428386181 |
| P3-B total response CSV SHA-256 | 4e0a23c18d29df3af04a2531e75b7bffeaa3251d0efe97674b2287cf3c25e7e3 |
| P3-B multipole CSV SHA-256 | e83f7499cd0af4ec8f1974238f09daf4899ca1b87205ec837ae0964a2e8532c6 |
| Three-body contraction output | Run 44305980766, artifact 14428247140 |

Both nuclear inputs contain seven isotopes and 2,401 \(q_A\) nodes per
isotope. The P3-B archive has 16,807 total-response rows and 9,604
rank-resolved multipole rows. The source-translated AFH-8 and P3-B
metadata both explicitly set native AFH validation to false.

## 4. Benchmark coverage and numerical acceptance

The phase-space calculation supplies 12 coefficient sets:
- green_450keV, \(E_R=200\) keV, \(q_A=0.2209306022\) GeV;
- green_1MeV, \(E_R=200\) keV, \(q_A=0.2209306022\) GeV;
- near_pole_362keV_g2_0p1, \(E_R=267\) keV,
  \(q_A=0.2552681134\) GeV;
- near_pole_362keV_g2_1, \(E_R=267\) keV,
  \(q_A=0.2552681134\) GeV.

Each benchmark is evaluated with zero, pole, and running \(\chi_2\)
widths. All points use \(v_\chi=776\) km/s. Contracting these 12 sets
with seven isotopes gives 84 rows.

| Acceptance check | Result |
|---|---:|
| Full-current regression tests | 100 passed |
| Native charge-sector engine tests | 16 passed |
| P3-B spatial grid generation | PASS |
| Rank-resolved archive validator | PASS |
| P0 quadrature regression in this run | skipped (previously accepted) |
| Contracted rows | 84 |
| Positive total response kernels | 84/84 |
| Algebraic failures | 0 |
| Maximum rank-sum reconstruction residual | \(1.11\times10^{-16}\) |

The run's full-current job and spatial-response job both completed
successfully. The quadrature job was explicitly skipped; this is not a
new P0 quadrature scan.

## 5. Contracted response hierarchy

The particle-side coefficient ratios over the 12 benchmarks are:
\[
\begin{aligned}
3.05096\times10^{-9}
&\le C_\Delta/C_M\le1.25962\times10^{-8},\\
5.07874\times10^{-10}
&\le C_{\Sigma'}/C_M\le2.09681\times10^{-9},\\
-1.02785\times10^{-8}
&\le C_{\Sigma'\Delta}/C_M\le-2.48958\times10^{-9}.
\end{aligned}
\]

After multiplying by the nuclear responses, the maximum spatial-to-charge
ratio over the 84 rows is
\[
\boxed{
\max\left|\frac{\mathcal K_{\rm spatial}}{\mathcal K_{\rm charge}}\right|
=7.0959581690\times10^{-9}.
}
\]

| Isotope | Maximum \(|\mathcal K_{\rm spatial}/\mathcal K_{\rm charge}|\) |
|---|---:|
| Xe-129 | \(3.09936\times10^{-11}\) |
| Xe-131 | \(7.09596\times10^{-9}\) |
| Xe-128, Xe-130, Xe-132, Xe-134, Xe-136 | 0 |

The maximum occurs for Xe-131 at
\[
E_R=267\ {\rm keV},\quad v_\chi=776\ {\rm km/s},\quad
q_A=0.2552681134\ {\rm GeV},
\]
with \(m_s=362\) keV, \(g_2=1\), and the running-width prescription.

At this point:
\[
\begin{aligned}
\mathcal K_{\rm charge}&=2.1692344604\times10^7,\\
\mathcal K_{\rm spatial}&=1.5392796990\times10^{-1},\\
\mathcal K_{\rm total}&=2.1692344758\times10^7.
\end{aligned}
\]

The rank-resolved spatial contribution is:
\[
\begin{array}{c|r}
J & \mathcal K_{{\rm spatial},J}\\ \hline
1 & 1.1180846057\times10^{-1}\\
2 & 0\\
3 & 4.2119509330\times10^{-2}
\end{array}
\]
whose sum reconstructs the total spatial sector with an absolute
residual \(5.55\times10^{-17}\).

The \(\Sigma'\Delta\) interference remains numerically important relative
to the spatial sector itself. It is retained with its signed response and
signed particle coefficient; it is not dropped merely because the whole
spatial sector is small compared with the coherent charge sector.

## 6. Interpretation and limitations

Within the present leading-static one-body vector-current benchmark, the
transverse spatial contribution is extremely small relative to the
charge-sector kernel at the 84 tested points. This follows from the
particle-side transverse coefficients and the available xenon spatial
responses.

This is **not** a global upper bound on the physical natural-xenon rate.
The calculation:
1. uses provisional Python translations of AFH v6.0 responses, not a
   native Wolfram seven-isotope/eight-response PASS;
2. uses constant zero-momentum anchors
   \(F_1^V(0)=3\), \(F_2^V(0)=-0.552\), \(m_N=0.938918\) GeV, not
   finite-\(t_N\) form factors;
3. evaluates 12 fixed-speed benchmark tensors, not a continuous
   recoil-energy or halo-velocity integral;
4. does not include the mediator/coupling prefactors, detector efficiency,
   energy resolution, or likelihood;
5. does not validate the direct bound-nucleus covariant amplitude against
   the AFH spherical-multipole amplitude, including all OBDME phases.

Accordingly, retain the status
\[
\boxed{\texttt{PROVISIONAL\_AFH\_CONTRACTION\_PASS}}
\]
and do not label this a full P3 pass or a final natural-xenon prediction.

## 7. Remaining gates

1. Complete the native Wolfram seven-isotope/eight-response comparison.
   The most recent private native workflow is
   [44306907993](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44306907993),
   currently queued on the self-hosted Windows/X64/research-gpu runner;
   no native artifact is available yet.
2. Implement the selected-point many-body comparison
   \(\mathcal A_{\rm cov}^{\rm nuclear}\) versus the q-frame and AFH
   spherical-multipole amplitudes using identical OBDMEs, phases,
   normalization, and current truncation.
3. Replace the constant \(q=0\) form-factor anchors with the approved
   finite-\(t_N\) \(F_1^V(t_N)\), \(F_2^V(t_N)\) prescription.
4. Only after the native and pointwise P3 gates pass, perform the
   natural-xenon halo fold and compare the pointlike-M, finite-\(t_N\)-M,
   Coulomb-sector, and full matched-current spectra separately.
