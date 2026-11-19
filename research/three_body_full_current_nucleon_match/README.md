# Full three-body current × nucleon Dirac–Pauli matching

**Status as of 2026-11-19:** P0, P1, P2, and P3-A are complete at their
stated scopes. A new Xe-131 spatial amplitude-level helicity reconstruction
subgate of P3-C also passes at \(6.09\times10^{-16}\) relative residual;
full P3-C remains open. P0 includes the 12 phase-space-integrated DM tensors and
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

The formal Pole-width response contraction is now 28 rows (four
benchmarks × seven isotopes), all with positive total kernels. Its maximum
spatial/charge ratio is \(7.03050\times10^{-9}\); the older 84-row,
three-width result from workflow 44305980766 is retained as a historical
sensitivity diagnostic only.

A new Xe-131 spatial amplitude-level helicity subgate of P3-C passes for
all four Pole-width benchmarks. The maximum helicity-amplitude versus
Cartesian Eq. (107) kernel residual is \(6.09\times10^{-16}\), and the
maximum coefficient residual is \(8.53\times10^{-16}\). The signed
\(\Sigma'\)-\(\Delta\) interference is retained and a deliberate
helicity-phase reversal is tested.

The native seven-isotope/eight-response gate remains separate. Its current
private workflow is [44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069),
queued on the self-hosted Windows/X64/research-gpu runner with no assigned
runner and no native artifact. P3-B is therefore not promoted to native
validation. Full P3-C also remains open: charge multipoles are not yet
rank-resolved and an independent direct coordinate-space bound-nucleus
current comparison remains to be implemented. The direct many-body comparison
\[
\mathcal A_{\rm cov}^{\rm nuclear}
\stackrel{?}{=}
\mathcal A_{q\text{-frame}}^{\rm nuclear}
\stackrel{?}{=}
\mathcal A_{\rm AFH\ multipoles}^{\rm nuclear}
\]
remains the next physics gate.

The P3-C amplitude subgate still uses constant \(q=0\) form-factor
anchors at fixed-speed points. The P4 halo engine exposes two finite-\(Q_N^2\)
diagnostics (bishara_linear and isoscalar_zexp) and reports the
Coulomb/full-current candidate relative to the same finite-\(t_N\) M-only
baseline. These are diagnostic prescriptions, not yet a pinned exact
legacy form-factor input or a native-AFH production result. P1 does not
claim a bound-nucleus/off-shell current.

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

The earlier diagnostic archive from workflow
[44231019823](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44231019823)
generated 12 tensors (four fixed-speed benchmarks, each with zero, pole, and
running widths). It is retained as a historical width-sensitivity comparison.
The formal-production rerun generates one tensor per benchmark with the
asymmetric Eq. (19) pole-width prescription only.

The numerical table below belongs to the historical multi-width diagnostic
archive; the pole-only formal rerun has its own artifact and acceptance record.

| Integrated-tensor diagnostic | Historical result | Acceptance |
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
point-nucleus contractions. The formal stress scan covers three benchmark families with the pole-width
prescription only. The earlier zero/running-width rows are diagnostic history,
not formal-production inputs:

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

The formal pole-only rerun contains 113,152 quadrature nodes across the three
benchmark families and three orders. Acceptance compares medium against high order, with tolerances
\(10^{-3}\) for Frobenius differences, \(10^{-2}\) for active-component
relative differences, and \(10^{-3}\) for point-nucleus contractions.

The historical three-width scan passed its reported medium-to-high
comparisons. The formal pole-only scan is rerun by the updated workflow; its
new result must be read from the newly generated artifact rather than inferred
from the historical multi-width archive.

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

## 7. Finite-\(t_N\) nucleon form factors and the correct AFH baseline

The original calculation already contains a finite-q nuclear form factor.
The paper source writes
\[
g_N\longrightarrow 3A g_{Vq}F_N(\boldsymbol q),\qquad F_N(0)=1,
\]
and the archived Mathematica engine implements this through
\[
R_A(Q_A)=A^2\frac{W_M(y_A)}{W_M(0)},\qquad
y_A=\left(\frac{Q_A b_A}{2}\right)^2.
\]
Thus \(W_M(Q_A)\) is the original finite nuclear shape factor. It must
remain in all comparison denominators; it is not a point-nucleus result,
and no additional Helm/AFH factor should be multiplied onto it.

The separate new layer is the finite-momentum single-nucleon Dirac-Pauli
current. For a fixed \(F_1(t_N),F_2(t_N)\) prescription, define
\[
R_{\mathrm{AFH},M}^{(0)}\propto F_1^V(0)^2W_M(Q_A),\qquad
R_{t_N,M}\propto c_M(t_N)^2W_M(Q_A),
\]
and
\[
R_{\rm charge}\propto c_M^2W_M+
c_{\Phi''}^2W_{\Phi''}+2c_Mc_{\Phi''}W_{M\Phi''}.
\]
The first ratio, \(R_{\rm charge}/R_{t_N,M}\), isolates the additional
AFH charge multipoles at fixed nucleon form factors. The second,
\(R_{\rm charge}/R_{\mathrm{AFH},M}^{(0)}\), is the direct comparison
with the original AFH M-only calculation, retaining its finite-q nuclear
form factor.

The current Python engine compares two finite-\(Q_N^2\) diagnostics:

- bishara_linear: \(F_1^V(Q_N^2)=3-(8.392\,{\rm GeV}^{-2})Q_N^2\), with \(F_2^V\) held at
  \(-0.552\); this is the first-order low-\(Q_N^2\) flavor-separated
  Dirac-slope approximation.
- isoscalar_zexp: a central isoscalar electromagnetic Sachs \(z\)-expansion
  reconstruction with the strange-current inputs.

Neither is silently identified with the exact legacy low-order quark
shape-factor input. Its original source and coefficients still need to be
pinned.

The Xe-131 fixed-speed Pole-width calculation gives:

| \(E_R\) | Prescription | \(R_{t_N,M}/R_{\mathrm{AFH},M}^{(0)}\) | \(R_{\rm charge}/R_{t_N,M}\) | \(R_{\rm charge}/R_{\mathrm{AFH},M}^{(0)}\) |
|---:|---|---:|---:|---:|
| 200 keV | bishara_linear | 0.739883 | 0.996955 | 0.737630 |
| 200 keV | isoscalar_zexp | 0.780997 | 0.996558 | 0.778309 |
| 267 keV | bishara_linear | 0.662175 | 0.914637 | 0.605649 |
| 267 keV | isoscalar_zexp | 0.721663 | 0.899610 | 0.649216 |

The finite-\(Q_N^2\) single-nucleon normalization changes the \(M\)-only
kernel by approximately 22–34% relative to the original AFH M-only baseline.
This does not remove or replace the finite-q nuclear form factor: the same
native \(W_M(Q_A)\) is present in both. Once the nucleon-current normalization
effect is factored out, the additional \(\Phi''\) plus signed
\(M-\Phi''\) interference changes the charge sector by only 0.30–0.34%
at 200 keV, but by 8.54–10.04% at 267 keV. The larger effect near 267 keV
is associated with the \(W_M\) diffraction minimum.

These are fixed-speed Xe-131 charge-sector results. They do not include
the validated spatial-current response or a natural-xenon halo fold.


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
XE131_FIXED_SPEED_CHARGE_DSIGMA_RESULTS.md. It uses native AFH v6.0
\(M,\Phi'',M\Phi''\) responses, finite-\(t_N\) Dirac-Pauli charge
coefficients \(c_M,c_{\Phi''}\), signed \(M-\Phi''\) interference, and the
full \(2\to3\) phase-space integral.

The primary ratio is the finite-\(t_N\) charge-sector result divided by the
\(M\)-only kernel evaluated with the **same** \(F_1^V(t_N),F_2^V(t_N)\).
The \(q=0\) \(M\)-only reference is reported separately:

| \(E_R\) | \(\Delta m\) | Form factor | \(R_{\rm charge}/R_{t_N,M}\) | \(R_{\rm charge}/R_{q=0,M}\) |
|---:|---:|---|---:|---:|
| 200 keV | 450 keV | bishara_linear | 0.99695540 (-0.30446%) | 0.737630 |
| 200 keV | 450 keV | isoscalar_zexp | 0.99655805 (-0.34420%) | 0.778309 |
| 267 keV | 362 keV | bishara_linear | 0.91463689 (-8.53631%) | 0.605649 |
| 267 keV | 362 keV | isoscalar_zexp | 0.89961039 (-10.03896%) | 0.649216 |

The Xe-131 dual-form-factor workflow passed on 2026-11-19
(run 44443361283, artifact 14491448839; 7/7 regression tests). The common
continuity-adjusted \(L_C^{(3)}\), propagator, flux, and phase-space factors
cancel in each normalized ratio. Here the q=0 single-nucleon-current
reference is the original AFH M-only baseline because it retains the same
finite-q native \(W_M(Q_A)\); it is not a point-nucleus approximation.

The full six-channel Xe-131 recoil scan now computes both bishara_linear
and isoscalar_zexp contractions after one shared phase-space tensor
integration at each recoil point. Each row carries both the
same-finite-\(t_N\) M-only ratio and the total ratio to the original AFH
M-only baseline. The spatial-response portion remains provisional until
the native Wolfram/P3-C gates pass; the new workflow run must pass before
these expanded rows are used as numerical results.

The earlier \(-21.48\%\) and \(-34.24\%\) numbers are historical
\(F_1^2\)-normalization diagnostics. The updated matched-\(c_M\) result
retains \(M,\Phi'',M\Phi''\) coherently. This remains a fixed-speed Xe-131
Coulomb-sector ratio, not an absolute differential cross section,
natural-xenon halo average, complete eight-response three-body contraction,
or detector prediction.


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
aa493b2b76727da2fd51609fe87c647910f7e456. This is the P3-B2 amplitude-level
acceptance gate; it remains pending until the private Windows Wolfram runner
executes the native workflow.


## 12. P3-C provisional C0-consistent response contraction

Workflow 44305980766 passed the fixed-speed AFH response-basis contraction:
84/84 positive kernels, with rankwise spatial contributions reconstructing
the total spatial sector to a maximum absolute residual of 1.11e-16. The
largest spatial/charge ratio in the selected historical benchmarks was
7.10e-9 (Xe-131, 267 keV, 776 km/s, near-pole running-width diagnostic); the
formal pole-only rerun is recorded separately.
This is a provisional fixed-speed result, not the final P3-C covariant
equivalence test or a halo-folded prediction.

Detailed normalization, rankwise contributions, provenance and limitations:
[P3_C_C0_CONSISTENT_CONTRACTION.md](P3_C_C0_CONSISTENT_CONTRACTION.md).

## 12. Xe-131 full-recoil charge-sector kernel scan (2026-11-18)

A 943-point scan has been added using the native Xe-131 AFH v6.0 \(W_M\), \(W_{\Phi''}\), and signed \(W_{M\Phi''}\) responses over the fixed-speed recoil window 109.64–652.94 keV. It compares the finite-\(Q^2\) matched \(M\)-only charge kernel with the coherent \(M+\Phi''\) charge kernel.

- Detailed method, benchmark, numerical results and limitations: [XE131_FULL_RECOIL_CHARGE_KERNEL_SCAN.md](results/2026-11-18/XE131_FULL_RECOIL_CHARGE_KERNEL_SCAN.md)
- 943-point native-grid data: [xe131_charge_kernel_full_recoil_scan.csv](results/2026-11-18/xe131_charge_kernel_full_recoil_scan.csv)
- Normalized kernel curves: [xe131_charge_kernel_full_recoil_curves.svg](results/2026-11-18/xe131_charge_kernel_full_recoil_curves.svg)
- Correction-ratio curves: [xe131_charge_kernel_full_recoil_ratios.svg](results/2026-11-18/xe131_charge_kernel_full_recoil_ratios.svg)
- Regeneration script: [build_xe131_full_recoil_charge_scan.py](build_xe131_full_recoil_charge_scan.py)

At the exact benchmark recoils, the full charge-sector kernel relative to the finite-\(Q^2\) \(M\)-only kernel is 0.99655805 at 200 keV and 0.89961039 at 267 keV for the isoscalar_zexp prescription. These are the same normalized charge-sector ratios reported in Section 8; the fixed-speed calculation additionally integrates the full \(2\to3\) phase space, whose common \(L_C^{(3)}\) factor cancels in the ratio. The present scan is not an absolute \(d\sigma/dE_R\), a halo-folded natural-xenon spectrum, or a detector prediction. Spatial multipoles remain outside this charge-sector plot.

The full-recoil scan regression is included in the standard unittest discovery: `test_xe131_full_recoil_charge_scan.py`. Rebuilding its CSV and SVG plots requires Python 3.12+, NumPy, pandas, and Matplotlib.

## Xe-131 publication figures and fixed-benchmark absolute spectrum (2026-11-18)

The 943-point native-grid charge-kernel figures are regenerated in a consistent serif/LaTeX-style publication format by the charge-scan plotting script. Both SVG and PDF versions are produced.

The fixed-benchmark absolute charge-sector spectrum is calculated by the fixed-benchmark absolute-dsigma script, using one fixed \(\Delta m=450\) keV across the entire kinematic interval, the current bare-nucleus Xe-131 mass convention, the asymmetric Eq. (19) pole-width prescription (first propagator zero-width, second propagator constant pole-width), the exact invariant mediator denominator \(m_V^2-t_A\), with \(t_A=-2m_AE_R\), while keeping spatial \(Q_A^2=2m_AE_R+E_R^2\) separate for AFH responses and static nucleon form factors, the relativistic incident momentum, and the public Eq. (6) prefactor. It includes the coherent native-AFH \(M+\Phi''+M\Phi''\) charge sector and outputs the full pointwise CSV, metadata, SVG and PDF.

- Method and scope: [XE131_FIXED_BENCHMARK_ABSOLUTE_DSIGMA.md](XE131_FIXED_BENCHMARK_ABSOLUTE_DSIGMA.md)
- Calculation: xe131_fixed_benchmark_absolute_dsigma.py
- Shared plot style: paper_plot_style.py
- Charge-figure plotting: build_xe131_full_recoil_charge_scan.py
- Regression tests: test_xe131_fixed_benchmark_absolute_dsigma.py
- CI workflow: [xe131-fixed-benchmark-absolute-dsigma.yml](../../.github/workflows/xe131-fixed-benchmark-absolute-dsigma.yml)

Important: the absolute spectrum is charge-sector only. It is not labelled as the complete six-channel \(L_{\mu\nu}W_A^{\mu\nu}\) result while native spatial AFH response validation and P3-C matching remain open.



## 13. Xe-131 six-channel fixed-speed recoil scan and interpolation audit

The fixed-speed Xe-131 six-channel scan now compares the coherent charge
responses \(M,\Phi'',M\Phi''\) with the leading-static spatial responses
\(\Delta,\Sigma',\Sigma'\Delta\), at identical recoil points and with the
full integrated three-body phase-space tensor. The formal scan now evaluates the pole-width prescription only, with one
row per accepted recoil point across the \(\Delta m=450\) keV off-pole and
\(\Delta m=362\) keV near-pole benchmarks. The earlier two-width row count
is retained only as a historical diagnostic.

A separate interpolation audit was added after finding a diffraction
minimum in \(W_M\) near \(q_A\simeq0.256\) GeV. It compares PCHIP with
local degree-8 and degree-10 Chebyshev interpolation on the archived
2,401-point AFH grid. The full charge-dominated kernel changes by at most
1.6589% under this interpolation comparison; the normalized full /
original-AFH-M-baseline ratio changes by at most 0.1182%. This baseline
retains finite-q \(W_M(Q_A)\); the finite-\(t_N\) correction is also
reported separately in the scan output.
The spatial kernel changes
by less than 1 ppm. These are interpolation diagnostics, not a dense native
AFH validation.

- Full method and numerical audit:
  [XE131_SIX_CHANNEL_INTERPOLATION_AUDIT.md](results/2026-11-18/XE131_SIX_CHANNEL_INTERPOLATION_AUDIT.md)
- Reproducible interpolation audit:
  [audit_xe131_six_channel_interpolation.py](audit_xe131_six_channel_interpolation.py)
- Regression tests:
  [test_audit_xe131_six_channel_interpolation.py](test_audit_xe131_six_channel_interpolation.py)

The next required calculation is a direct native Wolfram Xe-131 export of
AFH indices 1, 4, and 7 on \(0.2545\le q_A\le0.2575\) GeV with
\(0.000025\) GeV spacing, followed by a rerun of the fixed-speed
contraction. Until then, keep the result labelled
\`PASS_LOCAL_INTERPOLATION_STABILITY_DIAGNOSTIC\`; do not promote
\`native_afh_validated\` or claim a final continuous \(d\sigma/dE_R\).


The dense native export and overlap validator are now prepared in
[draft PR #63](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/63).
The private native workflow has been updated to include this 121-point
Xe-131 charge scan. The old queued run 44306907993 predates that update;
a fresh workflow dispatch is required after the Windows/Wolfram runner is
online. Until that run returns its artifact and validation PASS, the
diffraction-minimum interpolation gate remains open.


## Formal production policy — AFH only, pole width (2026-11-18)

The formal production pipeline is deliberately narrower than the historical
comparison suite:

- **Nuclear input:** AFH v6.0 native Xe-131 responses and the AFH seven-isotope
  response/multipole archives. GCN and JJ55 are excluded from formal results,
  plots, ratios, and acceptance criteria; their old scripts remain separate
  historical diagnostics and are not called by this pipeline.
- **Width:** `width_scheme="pole"` is the sole formal-production setting.
  It implements the asymmetric Eq. (19) prescription: the first `p-k`
  propagator retains `+i0+`, while the second `p'+k` propagator carries
  `+i m_chi2 Gamma_chi2(m_chi2)`. Zero-width and running-width calculations
  are sensitivity controls only.
- **Fixed-speed Xe-131 charge-sector absolute spectrum:** regenerated by
  `xe131_fixed_benchmark_absolute_dsigma.py`. This is explicitly the
  coherent `M + Phi'' + M Phi''` charge sector, not the complete six-channel
  result.
- **Fixed-speed six-channel AFH response scan:** regenerated by
  `xe131_full_afh_fixed_speed_recoil_scan.py`, retaining
  `M, Phi'', M Phi'', Delta, Sigma', Sigma' Delta` and their signed
  interference terms. The spatial OBDME archive remains provisional pending
  native-Wolfram validation and P3-C amplitude-level matching; this scan is
  therefore not promoted to a final absolute `d sigma/dE_R`.
- **Integrated three-body tensor and AFH contraction:** the default full-current
  workflow now emits pole-only `G^(3)`, `L_munu^(3)`, AFH multipole
  coefficients, and the fixed-speed AFH response contraction.
  Component-wise quadrature convergence is also rerun with pole width only.
- **Natural xenon:** the AFH-only hybrid and AME2020 halo-fold workflows already
  use the constant pole-width prescription. They remain downstream of the
  fixed-speed Xe-131 acceptance.

All new artifacts must report the width scheme, `g2`, pole width, recoil
kinematics, AFH source hashes, and convergence checks. Historical
zero/running-width outputs are not overwritten or relabelled as formal data.


### Pole-only rerun — completed artifacts (PR #65)

The PR-triggered full-current workflow
[44336338072](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44336338072)
completed successfully. Its artifact is
[full-three-body-current-nucleon-match-and-phase-space-tensor, artifact 14441427374](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44336338072).

- The phase-space-integrated tensor contains four benchmarks and pole width only.
- Maximum independent Dirac-trace residual: 1.58784e-9 (acceptance: 2e-9).
- Minimum Gram eigenvalue: -3.46081e-14 (PSD tolerance: -1e-10).
- AFH Eq. (107) coefficient extraction: maximum spatial Cauchy-identity residual 1.71779e-16; direct-versus-continuity residual 1.50736e-16.
- The AFH contraction contains 28 rows (four benchmarks x seven isotopes); all 28 total kernels are positive.
- Maximum spatial/charge ratio in this provisional contraction: 7.03050e-9.
- Rank-resolved spatial-response reconstruction residual: 1.11022e-16.

The component-wise pole-only convergence gate also passed in the same workflow.
Its artifact is
[three-body-phase-space-component-convergence, artifact 14440069866](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44336338072).
The worst final medium-to-high Frobenius difference is 1.45488e-8; the worst active-component relative difference is 1.53745e-5.

The fixed-speed charge-sector ratio workflow
[44336338146](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44336338146)
also passed. Its artifact is
[xe131-fixed-speed-charge-sector-dsigma-ratio, artifact 14441996611](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44336338146).
The pole-only ratios are 0.77830934 at 200 keV (Delta m=450 keV) and
0.64921591 at 267 keV (Delta m=362 keV). These normalized ratios are
unchanged by the common pole-width phase-space factor, which cancels between
numerator and denominator.

**Status qualification:** the seven-isotope AFH-8 charge archive is marked
PROVISIONAL_PYTHON, and the spatial P3-B archive is marked
PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES. The 28-row contraction
is therefore PROVISIONAL_AFH_CONTRACTION_PASS, not native-Wolfram-validated
or a final detector prediction. The separate one-point
`full_current_nucleon_match.json` retains zero/pole/running width controls
as a current-matching sensitivity diagnostic; those controls are not used
in the formal pole-only phase-space tensor or AFH contraction.


## 2026-11-19 P3-C spatial amplitude-level subgate

The new
[`p3c_amplitude_level_helicity_crosscheck.py`](p3c_amplitude_level_helicity_crosscheck.py)
uses the full complex three-body Gram tensor and signed Xe-131
\(\Delta_J,\Sigma'_J\) amplitudes. It compares the direct Cartesian
Eq. (107) contraction with a helicity-amplitude reconstruction before
summing over the two transverse polarizations and multipole ranks.

Four Pole-width benchmarks pass:
- maximum amplitude-kernel relative residual:
  \(6.09\times10^{-16}\);
- maximum Eq. (107) coefficient relative residual:
  \(8.53\times10^{-16}\);
- maximum PCHIP-amplitude versus linear-response interpolation difference:
  \(5.53\times10^{-6}\).

Four unit tests pass, including a test that deliberately reverses the
\(\Sigma'\) helicity phase and verifies that the signed
\(\Sigma'\)-\(\Delta\) interference changes sign.

This is a spatial-sector subgate only. Native Wolfram AFH validation,
rank-resolved charge multipoles, and the independent direct
coordinate-space bound-nucleus current comparison remain open. The
full-current workflow now runs and archives the subgate JSON result.


The reproducible PR #66 CI rerun completed successfully:
[workflow 44432440600](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44432440600).
Its full-current artifact is 14486904025 and its spatial-response artifact
is 14486014588. The response and multipole CSV SHA-256 hashes are identical
to the earlier PR #65 P3-B archive, so the native control workflow's pinned
input remains byte-identical.
