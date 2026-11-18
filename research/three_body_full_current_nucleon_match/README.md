# Full three-body current × nucleon Dirac–Pauli matching

**Status:** the static one-nucleon Dirac–Pauli diagnostic and the
phase-space-integrated DM-side three-body tensor are validated. The
component-wise quadrature scan passes at the reported stress benchmarks.
The exact AFH spatial-multipole coefficient projection and isotope nuclear
contraction remain open.

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
With \(q_{\rm AFH}=-q_A\), the static Dirac--Pauli matching gives
\(l_M=-F_1^V\boldsymbol{\mathcal T}_3\) and
\(l_5=i(F_1^V+F_2^V)(\boldsymbol q_{\rm AFH}\times
\boldsymbol{\mathcal T}_3)/(2m_N)\). Consequently,
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
The mixed coefficient is therefore nonzero in general. The earlier
inference that a tiny transverse antisymmetric component of \(L^{ij}\)
would force \(C_{\Sigma'\Delta}^{(3)}=0\) was incorrect: AFH Eq. (107)
shows that this coefficient depends on the transverse-even trace
\(L^{11}+L^{22}\), because \(l_5\) is the q-rotated spin-current
coefficient. The signed \(W_{\Sigma'\Delta}\) term must be retained.

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
false, so the contraction is explicitly provisional.

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

The old (W_M)-only baseline effectively treats the universal light-quark
nucleon current as pointlike when the reference nucleon coupling is written
as (g_{VN}=3g_{Vq}). The complete Dirac--Pauli matching instead requires
(F_1^V(t_N)) and (F_2^V(t_N)).

Bishara et al. give the proton flavor-separated Dirac slopes
[
F_1^{u/p,\prime}(0)=5.57(9),quad
F_1^{d/p,\prime}(0)=2.84(5),quad
F_1^{s/p,\prime}(0)=-0.018(9) {m GeV}^{-2},
]
so the universal light-flavor sum has the diagnostic slope
[
F_1^{V,\prime}(0)=8.392(0.137) {m GeV}^{-2}.
]
The same input gives (F_2^{s/p}(0)=-0.064(17)) and the total
(F_2^V(0)=-0.552). These are low-(Q^2) matching inputs, not a complete
finite-(t_N) form-factor model.

As a second diagnostic, `nucleon_vector_form_factors.py` reconstructs the
universal light-flavor current from the isoscalar proton+neutron
electromagnetic form factors using the Borah--Hill--Lee--Tomalak z expansion,
with the strange (F_1) slope from Bishara and (F_2^s) held at its
zero-momentum value. This is explicitly a central diagnostic, not the final
model input.

For the Xe-131 point (q_A=256.271868) MeV, the central finite-(t_N)
diagnostic gives
[
F_1^V=2.5605,qquad F_2^V=-0.4492,
]
[
c_M=2.5450,qquad c_{Phi''}=0.03096,qquad eta=0.01216.
]
Using the native-validated Xe-131 response ratios at this point gives
[
Q_{Phi''}-1simeq-1.84%
]
relative to the finite-(t_N) (M)-only charge response.

However, relative to the old pointlike (F_1^V(0)^2W_M) baseline, the
same central diagnostic gives
[
oxed{rac{R_{m charge}^{m finite-t}}
{R_{M,m pointlike}}-1simeq-29.4%}.
]

Thus the finite-(t_N) Dirac form factor can be a much larger correction to
the old (W_M)-only spectrum than the explicit (Phi'') term.

This distinction is essential:

- (Phi'') changes the charge-sector response by only percent level relative
  to the finite-(t_N) (M) term at this selected point.
- The finite-(t_N) normalization of the coherent charge itself can change
  the pointlike (W_M)-only prediction by tens of percent.
- The spatial-current (Delta,Sigma',Sigma'Delta) sector remains at the
  (10^{-8})-level relative to the charge sector in the current fixed-speed
  benchmarks.

The finite-(t_N) result is still a diagnostic because the available inputs
do not provide a single, fully validated finite-(Q^2) form-factor set for
the universal (u+d+s) current, especially for (F_2^V(Q^2)). The natural
xenon spectrum must therefore be reported in layers: pointlike (W_M)-only,
finite-(t_N) charge benchmark, then (M+Phi''), and finally the spatial
current sector.


## 7. Leading AFH response content and remaining work

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

1. verify the \(\Delta\), \(\Sigma'\), and signed
   \(\Sigma'\)-\(\Delta\) coefficient phases against native AFH
   single-particle multipoles and the native Wolfram response functions;
2. replace constant \(F_1^V(0)\), \(F_2^V(0)\) anchors with the
   model-specific finite-\(t_N\) form factors;
3. extend the three-body phase-space tensor from the 12 benchmark points
   to a converged \(E_R\)- and velocity-dependent grid;
4. perform the natural-xenon abundance sum and halo integral;
5. include the detector response and compare the resulting spectrum with
   the charge-only baseline.

No full natural-xenon three-body spectrum, halo-folded rate, or
detector-level correction is claimed yet.

## 7. Reproduction

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

## 8. References

- Anand, Fitzpatrick, and Haxton, Phys. Rev. C 89, 065501 (2014),
  https://arxiv.org/abs/1308.6288: AFH nuclear responses.
- Hoferichter, Klos, Menéndez, and Schwenk, Phys. Rev. D 94, 063505 (2016),
  https://arxiv.org/abs/1605.08043: coherent nuclear responses and
  vector-current matching.
- Hoferichter, Menéndez, and Schwenk, Phys. Rev. D 102, 074018 (2020),
  https://arxiv.org/abs/2007.08529: vector charge and nuclear multipole
  expansion.
- Repository AFH source: v6/dmformfactor-V6.m.
