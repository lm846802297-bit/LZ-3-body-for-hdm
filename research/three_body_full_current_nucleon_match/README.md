# Full three-body current × nucleon Dirac–Pauli matching

**Status as of 2026-11-18:** P0, P1, P2, and P3-A are complete at their
stated scopes. P0 includes the 12 phase-space-integrated DM tensors and
nine component-wise medium-to-high quadrature comparisons. P1 validates
the free on-shell one-body Dirac--Pauli current in the impulse
approximation. P2 fixes the particle-side AFH Eq. (107) coefficients and
the signed \(\Sigma'\)-\(\Delta\) coefficient. P3-A passes the direct
covariant versus q-frame spin-amplitude comparison and the particle-side
Eq. (107) projection.

P3-B now has a seven-isotope spatial-response grid, a rank-resolved
multipole archive, and an independent Python-to-Python comparison over
all 16,807 isotope/\(q_A\) points. The rank archive contains 9,604
multipole rows and reconstructs all three spatial responses to
\(2.22\times10^{-16}\) or better. These are source-translated Python
results; the native Wolfram AFH comparison and the selected-point
many-body covariant-versus-AFH amplitude comparison remain open.

P3-C has passed as a **provisional fixed-speed response contraction**:
workflow 44305980766 passed 100 full-current tests and 16 native
charge-engine tests, then contracted 12 three-body coefficient sets
with seven isotopes (84 rows). All total kernels are positive and the
maximum rank-sum reconstruction residual is \(1.11\times10^{-16}\).
The corrected contraction applies the common \(C_0(A)\) normalization
to AFH-8 charge responses while using the already-\(C_0\)-corrected
P3-B spatial responses; the AFH factor four is applied once. The
maximum spatial/charge ratio in these 84 fixed-speed rows is
\(7.09596\times10^{-9}\). This is not a global halo-integrated bound.

The native seven-isotope/eight-response gate remains separate. Its latest
private workflow is 44306907993, currently queued on the
self-hosted Windows/X64/research-gpu runner, with no native artifact
available. P3-B is therefore not promoted to native validation, and
P3 as a whole is not passed. The direct many-body comparison
\[
\mathcal A_{\rm cov}^{\rm nuclear}
\stackrel{?}{=}
\mathcal A_{q\text{-frame}}^{\rm nuclear}
\stackrel{?}{=}
\mathcal A_{\rm AFH\ multipoles}^{\rm nuclear}
\]
remains the next physics gate.

Finite-\(t_N\) form factors, a continuous recoil/halo fold, natural-xenon
spectra, and detector-level predictions remain downstream tasks. The
current P3-C result uses constant \(q=0\) form-factor anchors and fixed
speed points only. P1 does not claim a bound-nucleus/off-shell current.

## 1. Purpose and amplitude

This study combines the spin-resolved three-body DM current with the
one-nucleon vector current:
\[
\mathcal A=\mathcal T_3^0\otimes J_N^0
-\sum_{i=1}^3\mathcal T_3^i\otimes J_N^i.
\]
The one-point spinor diagnostic decomposes this \(4\times4\) operator into
the complete Pauli-product basis
\[
\mathcal A=\sum_{a,b=0}^{3}c_{ab}\,
\sigma_\chi^a\otimes\sigma_N^b.
\]
The phase-space calculation separately retains the full four-vector
\(\mathcal T_3^\mu\), both scalar-emission orderings, and their coherent
interference.

## 2. Momentum and nucleon-current conventions

The nuclear transfer and one-nucleon transfer are kept distinct:
\[
q_A^\mu=P_A'^\mu-P_A^\mu,\qquad
q_N^\mu=k_N'^\mu-k_N^\mu.
\]
In the static one-body impulse diagnostic,
\[
q_N^0=0,\qquad
\boldsymbol q_N=\boldsymbol q_A,\qquad
t_N=-|\boldsymbol q_A|^2.
\]
The AFH Fourier convention used in the matching note is
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\). The emitted scalar momentum
is not part of the nuclear Fourier transfer:
\[
\boldsymbol p_\chi'-\boldsymbol p_\chi
=-\boldsymbol q_A-\boldsymbol k_s.
\]
It remains inside the exact three-body DM current and its two \(\chi_2\)
propagators.

The nucleon vertex is
\[
\Gamma_N^\mu=
F_1^{V,N}(t_N)\gamma^\mu+
\frac{iF_2^{V,N}(t_N)}{2m_N}
\sigma^{\mu\nu}q_{N,\nu},
\]
with the Pauli sign tied to \(q_N=k_N'-k_N\). Before identifying AFH
one-body coefficients, the covariant spinor matrix element is divided by
\(2\sqrt{E_NE_N'}\).

The leading nonrelativistic current used by the diagnostic is
\[
J_N^0=c_M(t_N)M+c_{\Phi''}(t_N)\Phi''+\cdots,
\]
\[
\boxed{
\boldsymbol J_N=
\frac{F_1^V(t_N)}{m_N}\boldsymbol K_N+
\frac{i[F_1^V(t_N)+F_2^V(t_N)]}{2m_N}
(\boldsymbol\sigma_N\times\boldsymbol q_N)
+\mathcal O(p^3/m_N^3),
}
\qquad
\boldsymbol K_N=\frac{\boldsymbol k_N+\boldsymbol k_N'}{2}.
\]
The convection and magnetization pieces are physically distinct. Their
leading AFH multipole content is \(\Delta\) and \(\Sigma'\), respectively;
their signed mixed response is \(W_{\Sigma'\Delta}\). The exact spherical
projectors and their normalization are documented in
SPATIAL_CURRENT_AFH_MULTIPOLE_MATCHING.md.

## 3. Static one-nucleon validation

The one-point benchmark uses \(m_N=0.938918\) GeV,
\(F_1/F_1(0)=1\), and the provisional zero-momentum anchor
\(F_2/F_1(0)=-0.184\). These are diagnostic inputs, not a finite-\(t_N\)
form-factor model.

| Diagnostic | Result |
|---|---:|
| Free nucleon Ward residual using \(q_N\) | \(3.84\times10^{-18}\) |
| Scaled residual when static current is tested with physical \(q_A\) | \(5.35\times10^{-4}\) |
| \(q_A^0/Q_A\) | \(9.05\times10^{-4}\) |
| DM-current spin-trace comparison with independent PR #53 tensor | \(4.46\times10^{-16}\) |

The residual with \(q_A\) quantifies the static energy-transfer
approximation; it is not a failure of the free-nucleon Ward identity using
\(q_N\). The spatial-only Pauli coefficient is nonzero even though it does
not modify the selected charge spin-orbit projection at the reference point.
Therefore the spatial current cannot be discarded on the basis of that
single projection.

At the reference point, the nonrelativistically normalized coefficient
of \(\boldsymbol\sigma_N\cdot(\boldsymbol q_A\times\boldsymbol\ell)\)
for the charge piece is \(-8.41409\times10^6 i\) in the code's
per-\((q_A\times\ell)\) convention. The spatial-only contribution to this
same odd projection is about \(8.35\times10^{-12}i\), while a different
transverse-spin Pauli coefficient is
\[
c_{0,2}^{\rm spatial}=-3.75817\times10^3 i.
\]
The latter is a \(\Sigma'\)-type candidate, not yet an AFH Wilson
coefficient or nuclear response.

## 4. Phase-space-integrated spin-resolved DM tensor (P0-B1)

The Python module three_body_phase_space_tensor.py integrates the exact
spin-resolved three-body current over the threshold-stable Eq. (6) phase
space. It rotates the spatial components into a local right-handed frame
\((e_1,e_2,\widehat{\boldsymbol q}_A)\), decomposes the DM \(2\times2\)
matrices into Pauli components, and stores
\[
G_{\mu a,\nu b}^{(3)}
=\int d\Phi_3\,c_a^\mu c_b^{\nu *},
\qquad
L_{\mu\nu}^{(3)}=\sum_aG_{\mu a,\nu a}^{(3)}.
\]
The before-emission, after-emission, and coherent interference Gram
tensors are archived separately.

Workflow run [44231019823](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44231019823)
completed successfully. It generated 12 tensors (four fixed-speed
benchmarks, each with zero, pole, and running widths) and passed the
23-test full-current regression suite.

| Integrated-tensor diagnostic | Result | Acceptance |
|---|---:|---:|
| Maximum independent Dirac-trace contraction residual | \(1.59813\times10^{-9}\) | \(<2\times10^{-9}\) |
| Maximum Gram/tensor Hermiticity residual | 0 | \(<10^{-12}\) |
| Minimum Gram eigenvalue | \(-3.20\times10^{-14}\) | \(>-10^{-10}\) |
| Minimum spin-averaged tensor eigenvalue | \(5.75\times10^{-4}\) | \(>-10^{-10}\) |
| Maximum q-frame rotation residual | \(3.16\times10^{-16}\) | \(<10^{-12}\) |

The minimum negative Gram eigenvalue is roundoff-level and remains within
the explicit PSD tolerance.

- Integrated-tensor artifact: full-three-body-current-nucleon-match-and-phase-space-tensor
- Artifact ID: 14394488484
- Artifact SHA-256: 6e9a78fa3306eec4df24574bfc68863e0757a6971baf20bcdfc3958c0c38bf3a

This is the DM-side tensor, not yet the AFH nuclear response
\(\mathcal R_{\alpha\beta}^{(3)}\).

## 5. Component-wise phase-space quadrature convergence (P0-B2)

The Python module phase_space_tensor_convergence.py compares every complex
component of the \(16\times16\) Gram tensor (256 entries), every complex
component of the \(4\times4\) Lorentz tensor (16 entries), and the
point-nucleus contractions. The stress scan covers three benchmark
families, each with zero, pole, and running widths:

| Benchmark | \(\Delta m\) | \(E_R\) | \(g_2\) | Mapping |
|---|---:|---:|---:|---|
| Near-pole narrow coupling | 362 keV | 267 keV | 0.1 | \(\sin^2\) endpoint |
| Near-pole larger coupling | 362 keV | 267 keV | 1 | \(\sin^2\) endpoint |
| Off-pole green benchmark | 450 keV | 200 keV | 1 | threshold \(u^2\) |

The quadrature orders \((n_W,n_z,n_\phi)\) are:

| Case family | Low | Medium | High |
|---|---:|---:|---:|
| Near pole | \(32\times16\times8\) | \(40\times24\times12\) | \(48\times32\times16\) |
| Off pole | \(24\times16\times8\) | \(32\times24\times12\) | \(40\times32\times16\) |

The total number of nodes across all nine scans and three orders is
339,456. Acceptance compares medium against high order, with tolerances
\(10^{-3}\) for Frobenius differences, \(10^{-2}\) for active-component
relative differences, and \(10^{-3}\) for point-nucleus contractions.

**Result: all nine medium-to-high comparisons PASS.**

| Metric | Worst observed | Tolerance |
|---|---:|---:|
| Gram Frobenius relative difference | \(1.5013\times10^{-8}\) | \(10^{-3}\) |
| Lorentz tensor Frobenius relative difference | \(1.5013\times10^{-8}\) | \(10^{-3}\) |
| Active Gram component relative difference | \(1.5673\times10^{-5}\) | \(10^{-2}\) |
| Active Lorentz component relative difference | \(1.5673\times10^{-5}\) | \(10^{-2}\) |
| Point-nucleus contraction relative difference | \(1.5118\times10^{-8}\) | \(10^{-3}\) |

- Convergence workflow run: [44231019823](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44231019823)
- Convergence artifact ID: 14395277591
- Convergence artifact SHA-256: f86c44548efc271c49f2e1e5846c6485280265ba28cd4f3223f896d9eba29e73
- Detailed results: QUADRATURE_CONVERGENCE_RESULTS.md

The PASS establishes numerical stability of the DM-side tensor at the
reported fixed-speed stress benchmarks and quadrature orders. It does not
establish convergence over the full recoil-energy or halo-velocity domain.

### Leading AFH spatial coefficients from Eq. (107)

The AFH multipole formula gives the spatial coefficients in terms of
\(\boldsymbol l_M\) (convection) and \(\boldsymbol l_5\) (spin density):
\[
C_\Delta=\frac12\left[
\frac{q^2}{m_N^2}l_M\cdot l_M^*
-\left(\frac{\boldsymbol q}{m_N}\cdot l_M\right)
 \left(\frac{\boldsymbol q}{m_N}\cdot l_M^*\right)\right],
\]
\[
C_{\Sigma'}=\frac12\left[
l_5\cdot l_5^*
-(\hat{\boldsymbol q}\cdot l_5)
 (\hat{\boldsymbol q}\cdot l_5^*)\right],
\qquad
C_{\Sigma'\Delta}=\frac{\boldsymbol q}{m_N}\cdot
\operatorname{Re}[i l_M\times l_5^*].
\]
With \(q_{\rm AFH}=-q_A\), the static Dirac--Pauli matching gives the candidate expressions
\(l_M=-F_1^V\boldsymbol{\mathcal T}_3\) and
\(l_5=i(F_1^V+F_2^V)(\boldsymbol q_{\rm AFH}\times
\boldsymbol{\mathcal T}_3)/(2m_N)\). The AFH Fourier convention and the exact v6.0 operator definitions
fix the particle-side vectors
\[
\boldsymbol l_M=-F_1^V\boldsymbol{\mathcal T}_3,\qquad
\boldsymbol l_5=
\frac{i(F_1^V+F_2^V)}{2m_N}
(\boldsymbol q_{\rm AFH}\times\boldsymbol{\mathcal T}_3),
\qquad \boldsymbol q_{\rm AFH}=-\boldsymbol q_A.
\]
The resulting Eq. (107) coefficients are
\[
C_\Delta^{(3)}
=\frac{(F_1^V)^2Q_A^2}{2m_N^2}(L^{11}+L^{22}),
\]
\[
C_{\Sigma'}^{(3)}
=\frac{(F_1^V+F_2^V)^2Q_A^2}{8m_N^2}(L^{11}+L^{22}),
\]
\[
\boxed{
C_{\Sigma'\Delta}^{(3)}
=-\frac{F_1^V(F_1^V+F_2^V)Q_A^2}{2m_N^2}
(L^{11}+L^{22}).
}
\]
The negative sign and normalization have now been independently checked
by evaluating AFH Eq. (107) on complex spin-resolved amplitudes before
spin averaging, and comparing with the 4x4 Lorentz-tensor coefficient
extractor. This confirms the **particle-side** signed coefficient; it
does not yet validate the complete many-body AFH OBDME contraction. The
Cauchy--Schwarz check bounds response magnitude and is a separate test.

For the provisional zero-momentum anchors \(F_1^V(0)=3\),
\(F_2^V(0)=-0.552\), and \(m_N=0.938918\) GeV, the coefficient ratios
relative to the leading charge coefficient \(C_M=F_1^2L^{00}\) over the
12 archived benchmarks are:

| Spatial coefficient | Range relative to \(C_M\) |
|---|---:|
| \(C_\Delta^{(3)}/C_M\) | \(2.71\times10^{-8}\) to \(1.12\times10^{-7}\) |
| \(C_{\Sigma'}^{(3)}/C_M\) | \(4.52\times10^{-9}\) to \(1.87\times10^{-8}\) |
| \(C_{\Sigma'\Delta}^{(3)}/C_M\) | \(-9.17\times10^{-8}\) to \(-2.21\times10^{-8}\) |

These are particle-side coefficient ratios, not recoil-rate corrections:
the corresponding AFH nuclear responses have not yet been contracted.
The coefficient identity
\[
C_{\Sigma'\Delta}^{(3)}
=-2\sqrt{C_\Delta^{(3)}C_{\Sigma'}^{(3)}}
\]
holds for the stated sign convention and \(F_1(F_1+F_2)>0\). The nuclear
responses themselves need not saturate their Cauchy--Schwarz bound.

At this leading static order \(C_{\Sigma''}^{(3)}=0\) and
\(C_{\widetilde\Phi'}^{(3)}=0\), because the magnetization current is
transverse and there is no leading spin-velocity current. These are
order-by-order current statements, not claims that the AFH responses
vanish generally.

For completeness, the generic transverse helicity-odd diagnostic
\[
\max\frac{|-i(L^{12}-L^{21})|}{|L^{11}+L^{22}|}
=7.39\times10^{-16}
\]
is also consistent with zero at floating-point precision. It is a
different multipole factor and does not set the AFH
\(C_{\Sigma'\Delta}^{(3)}\) coefficient to zero.

The coefficient ratios above use constant zero-momentum form-factor
anchors. The final calculation must use finite-\(t_N\)
\(F_1^V(t_N)\) and \(F_2^V(t_N)\), and must contract with the physical
equal-\(p=n\) AFH response columns so the factor of four is applied once.

## 6. Provisional seven-isotope AFH fixed-speed contraction (P0-C2)

The AFH Eq. (107) particle coefficients are now contracted with the
seven-isotope Python AFH response database at the 12 archived three-body
benchmarks. The contraction script is
contract_three_body_afh_responses.py. It uses the physical equal-\(p=n\)
AFH columns and verifies the database CSV checksum and exact source commit
before reading the responses.

The AFH input is the provisional Python artifact from workflow run
44222087512, artifact 14391456283, source commit
dcefbeb7ad705b6c03f2b4689200eb1d9252e67b. Its CSV SHA-256 is
59ea25093137a05b8ebcc158e2fe6a74fe5927599dbb16766b067aa1ad8e3caa.
The artifact has 2,401 q nodes for each of seven isotopes and 99.8158%
natural-xenon atom-fraction coverage. Its native_afh_validated flag is
false, so the contraction is explicitly provisional. The spatial-to-charge values below also use the candidate \(C_{\Sigma'\Delta}\) sign; treat them as provisional until P3 confirms the particle-side phase.

The 12 three-body tensors times seven isotopes give 84 fixed-speed
benchmark/isotope contractions. Using the provisional anchors
\(F_1^V(0)=3\), \(F_2^V(0)=-0.552\), and \(m_N=0.938918\) GeV:

- all 84 combined response kernels are non-negative;
- all interpolated diagonal spatial responses are non-negative;
- all 84 interpolated \(\Sigma'\)-\(\Delta\) responses satisfy
  Cauchy--Schwarz;
- the maximum spatial-to-charge ratio is \(7.0959\times10^{-9}\)
  (Xe-131, near-pole \(g_2=1\), running width);
- Xe-129 has a maximum spatial-to-charge ratio of
  \(3.0993\times10^{-11}\);
- the leading spatial responses vanish for the five spin-zero isotopes
  Xe-128, Xe-130, Xe-132, Xe-134, and Xe-136.

At the largest spatial benchmark, \(E_R=267\) keV and
\(Q_A=0.255268\) GeV, the Xe-131 spatial terms are
\[
C_\Delta R_\Delta=0.115349,\quad
C_{\Sigma'}R_{\Sigma'}=0.008815,\quad
C_{\Sigma'\Delta}R_{\Sigma'\Delta}=0.029751.
\]
The mixed term is about 19.3% of the spatial sector. It is therefore
incorrect to drop \(W_{\Sigma'\Delta}\), even though the total spatial
sector is only \(7.10\times10^{-9}\) of the charge sector at this point.

Detailed preliminary results and provenance are in
AFH_FIXED_SPEED_CONTRACTION_RESULTS.md. The workflow now downloads the
pinned AFH artifact, checks its source commit and CSV SHA-256, computes the
coefficients from the integrated DM tensor, and contracts all 84 points.

**Limitations:** this is not yet a native-AFH result, because the seven-isotope
database awaits its native Wolfram pointwise comparison. The form factors
are zero-momentum anchors rather than finite-\(t_N\) functions. No
recoil-grid scan, natural-abundance sum, halo fold, detector response, or
likelihood is included.

## 7. Finite-t_N form-factor effect: a separate and potentially larger correction

The old (W_M)-only baseline treats the universal light-quark nucleon
current as pointlike when the reference nucleon coupling is written as
(g_{VN}=3g_{Vq}). The complete Dirac--Pauli matching instead requires
(F_1^V(t_N)) and (F_2^V(t_N)).

Bishara et al. give the proton flavor-separated Dirac slopes
[
F_1^{u/p\,\prime}(0)=5.57(9),quad
F_1^{d/p\,\prime}(0)=2.84(5),quad
F_1^{s/p\,\prime}(0)=-0.018(9) {\rm GeV}^{-2},
]
so the universal light-flavor sum has the diagnostic slope
[
F_1^{V\,\prime}(0)=8.392(0.137) {\rm GeV}^{-2}.
]
The same input gives (F_2^{s/p}(0)=-0.064(17)) and the total
(F_2^V(0)=-0.552). These are low-(Q^2) matching inputs, not a complete
finite-(t_N) form-factor model.

The script `nucleon_vector_form_factors.py` provides two diagnostics:
the Bishara linear (F_1) slope benchmark and a central reconstruction from
the isoscalar proton+neutron electromagnetic z expansion of
Borah--Hill--Lee--Tomalak, supplemented by the strange (F_1) slope and
(F_2^s(0)). Neither is the final model-specific finite-(Q^2) input.

At Xe-131 (E_R=200) keV, the native AFH grid gives
(q_A=0.220930602) GeV and
[
\frac{W_{\Phi''}}{W_M}=0.0371914,qquad
\frac{W_{M\Phi''}}{W_M}=-0.191819.
]
The central finite-(t_N) diagnostic gives
[
F_1^V=2.66287,qquad F_2^V=-0.46800,
]
and the charge-sector correction is
[
\boxed{delta_{\Phi''}^{\rm finite-t_N}=-0.346\%},
qquad
\boxed{delta_{\rm charge}^{\rm pointlike}=-21.5\%}.
]

At the Xe-131 (W_M) cancellation region around (E_R=267) keV,
(q_A=0.255146957) GeV, the native AFH grid gives
[
\frac{W_{\Phi''}}{W_M}=19.6361,qquad
\frac{W_{M\Phi''}}{W_M}=-4.23930.
]
The pointlike (M+\Phi'') charge correction is then
[
\boxed{delta_{\Phi''}^{\rm pointlike}=-9.68\%}.
]
With the central finite-(t_N) form-factor diagnostic,
[
F_1^V=2.56389,qquad F_2^V=-0.44977,
]
and the total charge-sector change relative to the old pointlike
(F_1^V(0)^2W_M) baseline is
[
\boxed{delta_{\rm charge}^{\rm pointlike}=-34.2\%}.
]

The \(-21.5\%\) and \(-34.2\%\) total-charge figures above are legacy \(F_1^2\)-normalization diagnostics. The updated matched-\(c_M\) fixed-speed result in Section 8 supersedes them for the coherent-charge ratio: \(0.77830934\) \((-22.1691\%)\) at 200 keV and \(0.64921591\) \((-35.0784\%)\) at 267 keV, relative to pointlike \(9W_M\).

The last number is **Xe-131 only**. It must not be promoted to a natural-xenon
spectrum because the native Mathematica pointwise validation currently covers
Xe-131 (M,Phi'',MPhi''), whereas the seven-isotope spatial-response
translation is still a provisional Python AFH database.

The hierarchy established by the present calculations is therefore:

1. The spatial (Delta,Sigma',Sigma'') sector is tiny:
   (<7.1\times10^{-9}) of the charge sector in the tested fixed-speed
   contractions.
2. The explicit (Phi'') correction is normally small away from a deep
   (W_M) cancellation, but can reach (mathcal O(10\%)) locally near
   the Xe-131 cancellation.
3. The finite-(t_N) coherent charge normalization can change the old
   pointlike (W_M)-only prediction by tens of percent.

Therefore the final natural-xenon spectrum must be built in the order
[
W_M^{\rm pointlike}
;\rightarrow;
(M+\Phi'')^{\rm finite-t_N}
;\rightarrow;
(\Delta,\Sigma',\Sigma'')^{\rm finite-t_N},
]
with each isotope evaluated using its own exact (q_A), and without mixing
the native Xe-131 response grid with the provisional seven-isotope AFH
translation.

## 8. Leading AFH response content and remaining work

At leading static one-body vector-current order, the candidate response set
is
\[
M,\quad \Phi'',\quad M\Phi'',\quad
\Delta,\quad \Sigma',\quad \Sigma'\Delta.
\]
The AFH \(\Sigma''\) and \(\widetilde\Phi'\) channels remain in the complete
eight-response database, but are not generated by the leading static
convection and magnetization structures above. This is an order-by-order
statement, not a claim that the nuclear responses vanish generally.

The remaining work is:

1. perform P3 at selected phase-space points: compare the direct covariant
   one-body-current contraction, the same contraction after q-frame
   rotation, and the AFH OBDME/multipole contraction, including the signed
   \(\\Sigma'-\\Delta\) response;
2. complete the separate native seven-isotope/eight-response AFH input
   validation and bind its exact artifact/source checksum to the P3 run;
3. replace constant \(F_1^V(0)\), \(F_2^V(0)\) anchors with the
   model-specific finite-\(t_N\) form factors;
4. extend the three-body phase-space tensor from the 12 benchmark points
   to a converged \(E_R\)- and velocity-dependent grid;
5. perform the natural-xenon abundance sum, halo integral, detector
   response, and comparison with the charge-only baseline.

No full natural-xenon three-body spectrum, halo-folded rate, or
detector-level correction is claimed yet.

## 9. Reproduction

Python 3.12+ and NumPy are required.

~~~bash
python -m unittest discover \
  -s research/three_body_full_current_nucleon_match \
  -p 'test_*.py' -v

python research/three_body_full_current_nucleon_match/full_current_nucleon_match.py \
  --out /tmp/full-current-nucleon-match.json

python research/three_body_full_current_nucleon_match/three_body_phase_space_tensor.py \
  --out /tmp/three-body-phase-space-tensor.json

python research/three_body_full_current_nucleon_match/phase_space_tensor_convergence.py \
  --out /tmp/three-body-phase-space-convergence.json

python research/three_body_full_current_nucleon_match/three_body_multipole_leptonic_weights.py \
  --input /tmp/three-body-phase-space-tensor.json \
  --out /tmp/three-body-multipole-leptonic-weights.json \
  --f1 3.0 --f2 -0.552 --mN 0.938918

python research/three_body_full_current_nucleon_match/contract_three_body_afh_responses.py \
  --afh-dir /path/to/afh-seven-isotope-artifact \
  --weights-json /tmp/three-body-multipole-leptonic-weights.json \
  --out /tmp/three-body-afh-response-contraction.json
~~~

## 10. References

- Anand, Fitzpatrick, and Haxton, Phys. Rev. C 89, 065501 (2014),
  https://arxiv.org/abs/1308.6288: AFH nuclear responses.
- Hoferichter, Klos, Menéndez, and Schwenk, Phys. Rev. D 94, 063505 (2016),
  https://arxiv.org/abs/1605.08043: coherent nuclear responses and
  vector-current matching.
- Hoferichter, Menéndez, and Schwenk, Phys. Rev. D 102, 074018 (2020),
  https://arxiv.org/abs/2007.08529: vector charge and nuclear multipole
  expansion.
- Repository AFH source: v6/dmformfactor-V6.m.


## 7. Nuclear-current continuity: conditional Coulomb reduction

The charge/longitudinal DM weight used by the Coulomb-sector contraction is

\[
L_C^{(3)}=L_{00}^{(3)}
-\frac{E_R}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}^{(3)}.
\]

This reduction is **conditional on conservation of the complete nuclear
vector current**. It does not impose a Ward identity on the inelastic DM
transition current. The direct point-nucleus contraction and its
continuity-reduced form are algebraically equivalent, but this identity
checks the metric, kinematics and tensor-index conventions; it does not
prove that a truncated many-body one-body current is dynamically conserved.
The archive reader now checks the exact nuclear mass-shell relation
\(Q_A^2=2m_AE_R+E_R^2\), recomputes the point-nucleus contraction, and
compares it with the stored direct/reduced result.

The static free-nucleon diagnostic has
\(q_N^0=0\) when the internal momentum is perpendicular to \(q_A\), whereas
the physical nuclear transfer has \(q_A^0=E_R\). Its free-nucleon Ward
residual is tiny with \(q_N\), but nonzero when that static current is tested
against \(q_A\). The bound-nucleon energy transfer, binding/off-shell
prescription and interaction-current contributions therefore remain part
of the P1 operator-level continuity audit.

Latest integrated-tensor archive check (12 benchmark/width rows):
- maximum \(Q_A^2-(2m_AE_R+E_R^2)\) relative residual:
  \(1.42\times10^{-16}\);
- maximum direct-vs-continuity point-nucleus contraction residual:
  \(2.71\times10^{-16}\);
- largest \(|L_C/L_{00}-1|\): \(5.13\times10^{-6}\).

These are kinematic and algebraic checks, not a claim that the many-body
continuity problem is closed.

## 8. Fixed-speed Xe-131 differential cross-section ratio

The dedicated fixed-speed Xe-131 calculation is archived in
XE131_FIXED_SPEED_CHARGE_DSIGMA_RESULTS.md.

It uses native AFH v6.0 Xe-131 \(M,\Phi'',M\Phi''\) responses, finite-\(t_N\)
Dirac-Pauli charge coefficients \(c_M,c_{\Phi''}\), the signed
\(M-\Phi''\) interference, and the full \(2\to3\) phase-space integral.
For \(m_{\chi_1}=1000\) GeV, \(m_s=300\) keV, \(v_\chi=776\) km/s and
\(g_2=1\), the fixed-speed ratios relative to the original pointlike
\(9W_M\) baseline are:

| \(E_R\) | \(\Delta m\) | Ratio |
|---:|---:|---:|
| 200 keV | 450 keV | 0.77830934 (-22.1691%) |
| 267 keV | 362 keV | 0.64921591 (-35.0784%) |

Pole/running widths give the same ratio to \(2.3\times10^{-16}\) or better:
the common \(L_C^{(3)}\) phase-space factor cancels from this ratio. The
medium-to-high phase-space differences are below \(4.8\times10^{-10}\) for
both recoil points and both width prescriptions.

The earlier \(-21.48\%\) and \(-34.24\%\) values are historical
\(F_1^2\)-normalization diagnostics. The updated result uses the matched
Darwin-Foldy charge coefficient
\[
c_M=F_1^V+\frac{t_N(F_1^V+2F_2^V)}{8m_N^2}
\]
and retains \(M,\Phi'',M\Phi''\) coherently. The result is still a
**fixed-speed Xe-131 Coulomb-sector ratio**, not an absolute differential
cross section, natural-xenon halo average, complete eight-response
three-body contraction, or detector prediction.

Workflow 44262472992 passed and uploaded artifact 14408816831 (SHA-256
3d63f0d4896946129e1692ee0915da9b6d791323f65da85d0ee242bc1ae498bd.
The native Xe-131 archive provenance is pinned to archive commit
e6d9dee3527cab200ee6b21198d577b987282fac, with original Wolfram export
commit 54e1ff10bba0cbffe7acc6af428014415c708475.


## 10. Energy-transfer-matched free on-shell nucleon scan

The static reference uses \(\ell\perp q_A\), which gives \(q_N^0=0\).
For comparison, the new kinematic scan constructs free on-shell momenta
\[
\boldsymbol p_i=\boldsymbol\ell-\frac{\boldsymbol q_A}{2},\qquad
\boldsymbol p_f=\boldsymbol\ell+\frac{\boldsymbol q_A}{2}
\]
such that \(E_f-E_i=E_R\), hence \(q_N^\mu=q_A^\mu\). The required
longitudinal internal momentum is
\[
\ell_\parallel=
\frac{E_R\sqrt{m_N^2+\ell_\perp^2+(Q_A^2-E_R^2)/4}}
{\sqrt{Q_A^2-E_R^2}}.
\]

The current workflow test uses the static one-nucleon diagnostic reference
four-transfer
\[
q_A^\mu=(0.0002,\ 0.0705063355,\ 0,\ 0.2093780973)\ {\rm GeV},
\qquad Q_A=0.2209306022\ {\rm GeV}.
\]
For \(\ell_\perp=0,50,100,200\) MeV, the exact free on-shell construction
returns
\[
\ell_\parallel=(0.855829,\ 0.857025,\ 0.860604,\ 0.874771)\ {\rm MeV}.
\]
Across these four points, \(|q_N^0-q_A^0|\le 8.90\times10^{-17}\) GeV,
the largest free-nucleon Ward residual using \(q_N^\mu\) is
\(2.40\times10^{-16}\), and the largest residual using \(q_A^\mu\) is
\(1.49\times10^{-17}\).

For comparison, the original static slice has \(q_N^0=0\), a free-current
Ward residual \(3.84\times10^{-18}\) with \(q_N^\mu\), but a residual
\(5.3513\times10^{-4}\) when the same current is tested with the physical
\(q_A^\mu\). Thus the free on-shell vertex itself is not the problem; the
static \(q_N^0=0\) impulse kinematics are not the physical nuclear energy
transfer.

The exact Xe-131 q values used in the separate fixed-speed calculation are
\(Q_A=0.220825560\) GeV (200 keV) and \(0.255146745\) GeV (267 keV).
Applying the analytic \(\ell_\parallel\) formula to those q values gives
0.8562--0.8752 MeV and 0.9916--1.0134 MeV, respectively, for
\(\ell_\perp=0\)--200 MeV. These latter values are kinematic estimates;
the workflow's matrix-level Ward test above was run at the diagnostic
reference four-transfer, not at both fixed-speed Xe-131 points.

This is a kinematic free-nucleon slice, not a bound-nucleon momentum
distribution or a many-body continuity proof. It does **not** determine
the energy-sharing distribution of a bound nucleon, off-shell/binding
effects, or exchange currents from the nuclear Hamiltonian.


## 11. P3-B independent Python spatial-response cross-check

The seven-isotope P3-B spatial grid has been compared row by row against the
independent AFH-8 Python implementation. All 16,807 rows pass the raw and
physical-response comparisons at rtol=5e-12 and atol=2e-14. This is a
Python-to-Python consistency PASS only; native Wolfram validation remains
pending.

- Detailed provenance and numerical results:
  [P3_B_INDEPENDENT_PYTHON_CROSSCHECK.md](results/2026-11-18/P3_B_INDEPENDENT_PYTHON_CROSSCHECK.md)
- Reproducible Python cross-implementation comparator:
  [compare_p3_spatial_vs_afh8.py](../afh_response_crosschecks/compare_p3_spatial_vs_afh8.py)
- Direct P3-B versus native Wolfram comparator (run after the native artifact is available):
  [compare_p3_spatial_vs_native.py](../afh_response_crosschecks/compare_p3_spatial_vs_native.py)
- Native AFH workflow:
  [research-compute-control run 44222502400](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44222502400)

Do not set native_afh_validated=true until the native Wolfram ResponseNuclear
outputs for indices 3, 6 and 8 have been compared pointwise with the P3-B CSV.


The refreshed P3-B artifact also includes the rank-resolved
afh_spatial_obdme_multipoles_7isotope_2401.csv file. Its rankwise diagonal
and signed interference contributions are checked to reconstruct the three
total spatial responses at every isotope/q point. The CI job validates this
archive before upload using
[validate_afh_spatial_multipole_archive.py](validate_afh_spatial_multipole_archive.py).


Latest rank-resolved artifact: workflow 44305980766, artifact 14428386181.
It contains 16,807 total-response rows and 9,604 rank-resolved multipole rows.
The archive validator passed; rank sums reconstruct the raw responses exactly
and the physical equal-p/n responses to at most 2.22e-16 absolute residual.
The refreshed total-response CSV again passes the independent AFH-8 Python
comparison over all 16,807 rows. Native Wolfram validation remains pending.


A second native gate is prepared for the rank-resolved amplitudes themselves:
[compare_p3_multipoles_vs_native.py](../afh_response_crosschecks/compare_p3_multipoles_vs_native.py).
It compares all 9,604 Xe-129/Xe-131 \((A,q_A,J)\) rows for native AFH DeltaJ
and SigmaPJ amplitudes, after the full seven-isotope ResponseNuclear native
gate passes. The corresponding WLS export is pinned to native source commit
e1e9c85530a7d609561b34e2c2df5ab36e5c5b89. This is the P3-B2 amplitude-level
acceptance gate; it remains pending until the private Windows Wolfram runner
executes the native workflow.
