# P3-C precursor: C0-consistent three-body × AFH response contraction

> **Current formal-width status (2026-11-19):** the pole-only rerun is
> [workflow 44432440600](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44432440600),
> full-current artifact 14486904025. It contains 28 response-level rows
> (four benchmarks × seven isotopes), all positive, with maximum
> \(|K_{\rm spatial}/K_{\rm charge}|=7.0304970964\times10^{-9}\) and
> maximum rank-sum reconstruction residual \(1.11022\times10^{-16}\).
> The run uses Pole width only.
>
> **The response-level contraction is not, by itself, the requested full
> P3-C amplitude-level PASS.** A separate Xe-131 spatial helicity-amplitude
> subgate now passes at the four formal Pole-width benchmarks; see
> [P3C_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RESULTS.md](P3C_SPATIAL_AMPLITUDE_LEVEL_HELICITY_RESULTS.md).
> The seven-isotope and spatial AFH inputs remain Python translations until
> the native Wolfram gate passes. The older 84-row, three-width results below
> are retained as historical diagnostics and are not formal-production results.  
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

## 4. Historical benchmark coverage (superseded by the pole-only rerun)

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
2. uses constant zero-momentum anchors in this historical structural diagnostic. The archived input values \\(F_1^{uds}(0)=3\\), \\(F_2^{uds}(0)=-0.552\\) are raw flavor sums. In the external-\\(g_{VN}=3g_{Vq}\\) rate convention, the corresponding coefficient inputs are \\(\\widehat F_1^N(0)=1\\), \\(\\widehat F_2^N(0)=-0.184\\). The dimensionless spatial-to-charge ratios are unchanged by the common factor-three rescaling, but the old raw absolute coefficients must not be used with an external \\(g_{VN}\\) prefactor;
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
   The current native P3-B workflow is
   [44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069),
   configured by [research-compute-control PR #2](https://github.com/lm846802297-bit/research-compute-control/pull/2).
   It is pinned to native exporter source commit
   `5afc500a3102b857dd16e29432db8e6e068d65d1` and P3 artifact
   run `44337928314`, artifact `14443055701`. The run is queued on the
   self-hosted Windows/X64/research-gpu runner and currently has no assigned
   runner; no native artifact is available yet.
2. Implement the selected-point many-body comparison
   \(\mathcal A_{\rm cov}^{\rm nuclear}\) versus the q-frame and AFH
   spherical-multipole amplitudes using identical OBDMEs, phases,
   normalization, and current truncation.
3. Complete the selected-point direct covariant-current to AFH multipole
   amplitude reconstruction, retaining the OBDME phases, Wigner-Eckart
   factors, and signed \(\Sigma'\)-\(\Delta\) interference.
4. The P3-C structural subgate now uses the normalized q=0 effective anchors
   \\(\\widehat F_1^N=1\\), \\(\\widehat F_2^N=-0.184\\) in the external
   \\(g_{VN}\\) basis. The adopted B production path separately uses the
   finite-\\(t_N\\) Bishara Dirac slope and leading Pauli term; keep the P3-C
   algebraic subgate distinct from the B absolute-rate calculation.
5. Only after native P3-B and amplitude-level P3-C pass, perform the
   seven-isotope natural-xenon halo fold and compare the q=0 M reference,
   finite-\(t_N\)-M, Coulomb-sector, and full matched-current spectra.


## 7. P3-C spatial amplitude-level helicity reconstruction

A new amplitude-level subgate has been implemented in
`p3c_amplitude_level_helicity_crosscheck.py`. It starts from the full
complex phase-space Gram tensor
\[
G_{\mu a,\nu b}^{(3)}
=\int d\Phi_3\,c_a^\mu c_b^{\nu *},
\]
retains the four DM Pauli channels, and contracts the signed Xe-131
\(\Delta_J\) and \(\Sigma'_J\) reduced amplitudes rank by rank. The
helicity amplitudes are formed before summing over the two transverse
polarizations, DM spin channels, or nuclear multipole ranks.

For the AFH convention \(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\), the
helicity reconstruction reproduces all three Eq. (107) coefficients,
including the signed \(\Sigma'\)-\(\Delta\) interference. The direct
Cartesian Eq. (107) kernel and the helicity-amplitude kernel agree at
\(10^{-16}\) relative precision for all four Xe-131 Pole-width benchmarks.

| Benchmark | \(E_R\) | \(K_{\rm helicity}\), PCHIP amplitudes | Amp-vs-Cartesian residual |
|---|---:|---:|---:|
| green_450keV | 200 keV | 0.00835366938272 | \(2.08\times10^{-16}\) |
| green_1MeV | 200 keV | 0.000514111110719 | \(4.22\times10^{-16}\) |
| near_pole_362keV_g2_0p1 | 267 keV | 0.610748897628 | \(5.45\times10^{-16}\) |
| near_pole_362keV_g2_1 | 267 keV | 0.136728078354 | \(6.09\times10^{-16}\) |

The maximum relative residuals are
\[
\max\delta_{\rm amp/cart}=6.09\times10^{-16},\qquad
\max\delta_{C_{\rm Eq.(107)}}=8.53\times10^{-16}.
\]
The full \(G^{(3)}\) Gram matrix is Hermitian; its most negative numerical
eigenvalue is \(-3.20\times10^{-14}\), within the existing
\(-10^{-10}\) PSD tolerance.

### Interpolation cross-check

The existing response-level contraction linearly interpolates the total
\(\Delta,\Sigma',\Sigma'\Delta\) responses. The new amplitude-level
calculation interpolates the signed reduced multipole amplitudes and then
reconstructs the responses. At these four selected benchmarks:

- PCHIP-amplitude versus linear-response kernel differs by at most
  \(5.53\times10^{-6}\);
- linear-amplitude versus linear-response kernel differs by at most
  \(1.95\times10^{-6}\);
- PCHIP versus linear-amplitude kernel differs by at most
  \(3.58\times10^{-6}\).

These are few-ppm differences at the selected points, not a global
interpolation bound. The formal recoil engine should interpolate the signed
rank amplitudes and reconstruct the diagonal and interference responses
consistently; the full q-grid interpolation audit remains required.

**Scope qualification:** this is a spatial-sector amplitude-level
reconstruction using the provisional source-translated AFH amplitudes. It
does not yet validate the charge multipoles \(M,\Phi''\) at amplitude
level, an independent direct coordinate-space bound-nucleus current, or
the native Wolfram AFH source. Therefore it is a **P3-C spatial subgate
PASS**, not a full P3-C PASS. The full P3-C gate remains open until the
native P3-B comparison and the independent covariant/q-frame/AFH nuclear
amplitude comparison are completed.
