# Provisional three-body × AFH fixed-speed response contraction

> **Superseded normalization record (2026-11-18).** This initial fixed-speed contraction predates the common-\(C_0(A)\) correction applied to the AFH-8 charge responses. Use [P3_C_C0_CONSISTENT_CONTRACTION.md](P3_C_C0_CONSISTENT_CONTRACTION.md) for the current 84-row result and corrected normalization policy.

> **Additional convention warning (2026-11-19).** This is a historical static-nucleon diagnostic, not the formal production transfer. It uses the full quark-current anchors \(F_1^{uds}(0)=3\), \(F_2^{uds}(0)=-0.552\) in coefficients before the common coupling factor is restored, and uses \(t_N=-Q_A^2\) for the static slice. The formal production basis instead places \((g_1g_2g_{VN})^2\) outside and uses \(\widehat F_i=F_i^{uds}/3\), with \(t_N=t_A\). The AFH nuclear response in this historical result is still finite-size; the warning concerns the nucleon-current and normalization convention, not a missing nuclear form factor. Do not use this file for absolute rates or as the formal P4 benchmark.


**Status: preliminary Python contraction; native AFH validation and finite-\(t_N\) form factors pending.**

## 1. Inputs and provenance

The calculation combines two independently archived inputs:

| Input | Provenance |
|---|---|
| Seven-isotope AFH response database | Workflow run 44222087512, artifact 14391456283 |
| AFH database source commit | dcefbeb7ad705b6c03f2b4689200eb1d9252e67b |
| AFH CSV SHA-256 | 59ea25093137a05b8ebcc158e2fe6a74fe5927599dbb16766b067aa1ad8e3caa |
| Three-body integrated DM tensors | Workflow run 44231019823, artifact 14394488484 |
| Form-factor inputs | \(F_1^V(0)=3\), \(F_2^V(0)=-0.552\), \(m_N=0.938918\) GeV |

The AFH database contains 2,401 momentum nodes for each of Xe-128,
Xe-129, Xe-130, Xe-131, Xe-132, Xe-134, and Xe-136. Its metadata status
is PROVISIONAL_PYTHON and native_afh_validated is false. The physical
equal-\(p=n\) response columns are used, so the AFH factor of four is
applied exactly once.

The three-body artifact contains 12 fixed-speed tensors: four benchmark
kinematic points and zero, pole, and running \(\chi_2\) widths.

## 2. Contracted response kernel

At each benchmark and isotope, the AFH physical response columns are
linearly interpolated in \(q_A\) on the 0.25 MeV grid. The kernel is
\[
\mathcal K_A^{(3)}=
C_M R_M+
C_{\Phi''}R_{\Phi''}+
C_{M\Phi''}R_{M\Phi''}+
C_\Delta R_\Delta+
C_{\Sigma'}R_{\Sigma'}+
C_{\Sigma'\Delta}R_{\Sigma'\Delta}.
\]
The coefficients are those derived from AFH Eq. (107), with
\(q_{\rm AFH}=-q_A\), \(q_N=+q_A\), and the static diagnostic Dirac--Pauli current \(q_N^0=0\), \(t_N=-Q_A^2\).
The signed \(R_{\Sigma'\Delta}\) term is retained.

This is a response kernel before the common mediator propagator and
coupling factors. It is not an absolute differential rate.

## 3. Preliminary results

The 12 DM tensors were contracted with all seven isotope response sets,
giving 84 benchmark/isotope combinations.

- All 84 total response kernels are non-negative.
- All interpolated diagonal spatial responses are non-negative.
- All 84 interpolated \(\Sigma'\)-\(\Delta\) responses satisfy the
  Cauchy--Schwarz bound.
- The minimum total response kernel is \(4.798497\times10^6\) in the
  code's common arbitrary normalization.

The absolute spatial-to-charge ratio is small in these fixed-speed
benchmarks:

| Isotope | Maximum \(|\mathcal K_{\rm spatial}/\mathcal K_{\rm charge}|\) |
|---|---:|
| Xe-129 | \(3.0993\times10^{-11}\) |
| Xe-131 | \(7.0959\times10^{-9}\) |
| Xe-128, Xe-130, Xe-132, Xe-134, Xe-136 | 0 |

The spin-zero isotopes have no leading \(\Delta\), \(\Sigma'\), or
\(\Sigma'\)-\(\Delta\) response in this calculation.

The largest spatial fraction occurs for Xe-131 at the near-pole
\(g_2=1\), running-width benchmark:
\[
E_R=267\ {\rm keV},\quad v_\chi=776\ {\rm km/s},\quad
Q_A=0.255268\ {\rm GeV}.
\]
At this point,
\[
\mathcal K_{\rm charge}=2.16906636\times10^7,\qquad
\mathcal K_{\rm spatial}=0.1539153,
\]
and
\[
\frac{\mathcal K_{\rm spatial}}{\mathcal K_{\rm charge}}
=7.0959\times10^{-9}.
\]

The three spatial contributions at this point are
\[
\begin{aligned}
C_\Delta R_\Delta&=0.115349,\\
C_{\Sigma'}R_{\Sigma'}&=0.008815,\\
C_{\Sigma'\Delta}R_{\Sigma'\Delta}&=0.029751.
\end{aligned}
\]
The mixed term is about 19.3% of the spatial sector. It is small relative
to the coherent charge sector, but it is not negligible relative to the
other spatial terms and must not be dropped from the spatial contraction.

The charge-sector contributions at the same point are
\[
\begin{aligned}
C_MR_M&=2.42392006\times10^7,\\
C_{\Phi''}R_{\Phi''}&=7.946806\times10^4,\\
C_{M\Phi''}R_{M\Phi''}&=-2.62800503\times10^6.
\end{aligned}
\]

## 4. What this result establishes—and what it does not

This is a useful first numerical contraction of the three-body current
with the seven-isotope AFH response database. It verifies that the
coefficient signs used in the current implementation produce positive
combined response kernels for the 84 tested points, and it shows that the
leading spatial-current sector is strongly suppressed relative to the
charge sector at these benchmarks.

It is still provisional for three independent reasons:

1. The seven-isotope AFH eight-response database is a Python translation
   and has not yet passed the native Wolfram AFH pointwise comparison.
2. The nucleon form factors are constant \(q=0\) anchors; the final result
   requires \(F_1^V(t_N)\) and \(F_2^V(t_N)\) at
   \(t_N=-Q_A^2\).
3. The 12 fixed-speed points do not constitute a recoil-energy grid,
   natural-isotope abundance sum, halo integral, detector response, or
   likelihood.

The workflow implementation verifies the AFH artifact source commit and
CSV SHA-256 before performing this contraction. The resulting JSON is
archived as three-body-afh-response-contraction.json in the full-current
workflow artifact.
