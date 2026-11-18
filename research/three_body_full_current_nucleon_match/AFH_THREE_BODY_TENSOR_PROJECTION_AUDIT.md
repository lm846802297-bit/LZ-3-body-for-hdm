# Audit: projection of the integrated three-body tensor onto AFH nuclear responses

## Status

**Theory/implementation audit opened. No full AFH three-body response coefficients are claimed yet.**

This audit follows the project rule that the 15 elastic NR operators are not
a complete basis for the full \(\chi_1 N\to\chi_1 N s\) amplitude. The intended
factorization is instead

\[
{\cal M}_3={\cal K}_3 L_\mu^{(3)}J_A^\mu(q_A),
\qquad
\overline{|{\cal M}_3|^2}
=|{\cal K}_3|^2 L_{\mu\nu}^{(3)}W_A^{\mu\nu}.
\]

The AFH nuclear multipoles may be retained for a one-body nuclear current,
but the particle-side coefficients must be derived for the actual three-body
tensor and the chosen current convention.

## 1. What the current implementation actually stores

The module three_body_phase_space_tensor.py integrates the full q-aligned
\(4\times4\) tensor and stores L_q_aligned_real_imag. Its intermediate
point-nucleus contractions explicitly distinguish

\[
I_{\rm charge}=J_0^2L_{00},\quad
I_{\rm spatial}=Q_A^2L_{33},\quad
I_{\rm interference}=-J_0Q_A(L_{03}+L_{30}).
\]

It also stores transverse information \(L_{11}+L_{22}\), and the full
tensor retains \(L_{12},L_{21}\) and the other off-diagonal entries.

This is the correct dynamical object to feed into the multipole projection.

## 2. What the current charge-sector halo engine does

The module native_charge_sector_halo_fold.py calls
integrate_spin_resolved_tensor and reads the continuity-reduced Coulomb
weight

\[
L_C=L_{00}-\frac{\omega}{Q_A}(L_{03}+L_{30})
+\left(\frac{\omega}{Q_A}\right)^2L_{33}.
\]

It then builds the \(M,\Phi'',M\Phi''\) charge-multipole terms from this
weight and the corresponding native AFH response functions. The input gate
requires the complete seven-isotope/eight-response native AFH artifact,
although this diagnostic uses only the three charge-sector response
functions.

This is a **Coulomb-sector approximation conditional on conservation of the
complete nuclear vector current**. It is not the complete contraction
\(L_{\mu\nu}^{(3)}W_A^{\mu\nu}\), because the transverse nuclear-current
multipoles and their interference have not been projected and included.
The point-nucleus direct-vs-continuity identity is an algebraic check of the
four-vector and metric conventions; it does not prove that the truncated
many-body one-body current is dynamically conserved.

The finite-\(t_N\) charge matching can be studied within this restricted
sector, with the continuity assumption and one-body approximation stated.

## 3. Why the point-nucleus check is not yet a full AFH projection

The point-nucleus diagnostic already makes the distinction explicit:

\[
I_{\rm full}=J_0^2L_{00}
+Q_A^2L_{33}
-J_0Q_A(L_{03}+L_{30}).
\]

A nonzero \(L_{03}\) or \(L_{33}\) is not automatically an independent
nuclear response; its contribution must be combined with the corresponding
nuclear current multipoles and continuity relation using consistent
four-momentum and metric conventions.

In particular, the nuclear vector-current continuity equation must be
implemented at the operator level before eliminating or combining
longitudinal multipoles. The dark-matter transition current is not conserved
when \(m_{\chi_2}\ne m_{\chi_1}\), so one must not impose
\(q_{A\mu}L^\mu=0\) on the DM side.

## 3.1 Longitudinal reduction from nuclear-current continuity

For an unpolarized target and a conserved one-body nuclear vector current,
the q-aligned transfer is
\[
q_A^\mu=(\omega,0,0,Q_A),\qquad
q_{A\mu}J_A^\mu=0
\quad\Longrightarrow\quad
J_A^3=\frac{\omega}{Q_A}J_A^0.
\]
The metric is \(g_{\mu\nu}=(+,-,-,-)\). Thus
\[
T_\mu J_A^\mu
=\left(T^0-\frac{\omega}{Q_A}T^3\right)J_A^0
-\boldsymbol T_\perp\cdot\boldsymbol J_\perp,
\]
and the charge/longitudinal part of the phase-space-integrated DM tensor
enters the Coulomb multipoles through
\[
\boxed{
L_C^{(3)}
=L_{00}^{(3)}
-\frac{\omega}{Q_A}(L_{03}^{(3)}+L_{30}^{(3)})
+\left(\frac{\omega}{Q_A}\right)^2L_{33}^{(3)}.
}
\]

This is a use of **nuclear-current continuity**, not conservation of the
inelastic DM transition current. No condition \(q_{A\mu}T_3^\mu=0\) is
imposed. The charge coefficients multiplying \(M\), \(\Phi''\), and
\(M\Phi''\) must use \(L_C^{(3)}\), not \(L_{00}^{(3)}\) alone.

The identity is independently checked by the point-nucleus current
\(J_A^\mu=(2m_A+\omega,0,0,Q_A)\), for which
\(Q_A^2=\omega(2m_A+\omega)\):
\[
(2m_A+\omega)^2L_C^{(3)}
=(2m_A+\omega)^2L_{00}^{(3)}
+Q_A^2L_{33}^{(3)}
-(2m_A+\omega)Q_A(L_{03}^{(3)}+L_{30}^{(3)}).
\]
The implementation now reports the continuity-reduced contraction and its
relative residual alongside the direct point-nucleus contraction.

For the 12 integrated benchmark/width rows in workflow 44262472963,
\(\omega/Q_A\) is \(9.05692\times10^{-4}\) at 200 keV and
\(1.04646\times10^{-3}\) at 267 keV, using the canonical Xe-131 bare-nucleus
mass \(m_A=121.90971983538435\) GeV. The continuity-adjusted Coulomb weight
differs from \(L_{00}\) by approximately \(-4.35\times10^{-6}\) at 200 keV
and \(-5.03\times10^{-6}\) at 267 keV. The maximum absolute correction over
the 12 rows is \(5.12783\times10^{-6}\).

The latest extraction reports a maximum direct-versus-continuity residual
\(2.70280\times10^{-16}\) and a maximum mass-shell residual
\(1.42160\times10^{-16}\). These validate the kinematic and tensor-index
implementation of the reduction. They do not prove that the truncated
many-body one-body current is dynamically conserved.

The particle-coefficient extractor now uses \(L_C^{(3)}\) for
\(C_M,C_{\Phi''},C_{M\Phi''}\), while the transverse coefficients continue
to use \(L_T=L_{11}+L_{22}\). The archive reader checks
\(Q_A^2=2m_AE_R+E_R^2\), recomputes the direct point-nucleus contraction,
and verifies the stored continuity-reduced contraction. These checks close
the kinematic/index-convention audit at the leptonic-weight level only.

## 3.2 Rotational structure and the leading static vector-current channels

For the unpolarized, parity-even, time-reversal-invariant nuclear ensemble
used in the AFH response calculation, the spin-averaged nuclear tensor is
invariant under rotations about \(\hat{\boldsymbol q}_A\). In a q-aligned
basis this removes mixed longitudinal/transverse components,
\[
W_A^{0a}=W_A^{3a}=0,\qquad a=1,2,
\]
and makes the symmetric transverse block proportional to
\(\delta^{ab}\). The antisymmetric transverse response is absent under these
assumptions. Consequently, the off-diagonal components of the DM tensor with
one transverse index do not by themselves imply additional AFH nuclear
responses. The independent leptonic weights relevant to this unpolarized
vector-current problem reduce to
\[
L_C^{(3)},\qquad L_T^{(3)}=L_{11}^{(3)}+L_{22}^{(3)}.
\]
The helicity-odd diagnostic \(-2i(L_{12}-L_{21})\) is not the AFH
\(\Sigma'\)-\(\Delta\) coefficient and must not be used in its place.

At leading static one-body Dirac-Pauli order, the candidate AFH operator
content is:

| Nuclear-current piece | AFH channel | Particle-side weight |
|---|---|---|
| Coulomb charge | \(M\) | \(C_M=c_M^2L_C\) |
| Charge spin-orbit correction | \(\Phi''\) | \(C_{\Phi''}=c_{\Phi''}^2L_C\) |
| Charge interference | \(M\Phi''\) | \(C_{M\Phi''}=2c_Mc_{\Phi''}L_C\) |
| Transverse convection | \(\Delta\) | \(C_\Delta\propto F_1^2Q_A^2L_T\) |
| Transverse magnetization | \(\Sigma'\) | \(C_{\Sigma'}\propto(F_1+F_2)^2Q_A^2L_T\) |
| Convection-magnetization interference | \(\Sigma'\Delta\) | \(C_{\Sigma'\Delta}\propto-F_1(F_1+F_2)Q_A^2L_T\) |

The explicit leading-static coefficients in the current convention are
\[
\begin{aligned}
C_\Delta&=\frac{(F_1^V)^2Q_A^2}{2m_N^2}L_T^{(3)},\\
C_{\Sigma'}&=\frac{(F_1^V+F_2^V)^2Q_A^2}{8m_N^2}L_T^{(3)},\\
C_{\Sigma'\Delta}&=-\frac{F_1^V(F_1^V+F_2^V)Q_A^2}{2m_N^2}L_T^{(3)}.
\end{aligned}
\]
For \(F_1^V(F_1^V+F_2^V)>0\),
\[
C_{\Sigma'\Delta}=-2\sqrt{C_\Delta C_{\Sigma'}}.
\]
The latest 12-benchmark extraction satisfies this particle-side identity
with maximum relative residual \(1.72121\times10^{-16}\).

At this order, the magnetization current is transverse and gives no
independent \(\Sigma''\) coefficient; the leading vector one-body current
also gives no \(\widetilde\Phi'\) coefficient. These zeros are conditional
on the stated current and NR truncation. They are not universal statements
about higher-order operators, two-body currents, or other interactions.

The resulting leading-static kernel candidate is
\[
\begin{aligned}
{\cal K}_{\rm AFH}^{(3)}={}&
C_MW_M+C_{\Phi''}W_{\Phi''}+C_{M\Phi''}W_{M\Phi''}\\
&+C_\Delta W_\Delta+C_{\Sigma'}W_{\Sigma'}
+C_{\Sigma'\Delta}W_{\Sigma'\Delta}.
\end{aligned}
\]
This is the structural particle-side projection to be validated. It is not
yet promoted to a complete many-body result: the direct covariant
one-body-current contraction and the AFH multipole contraction still need
to agree at the tensor level, including the bound-nucleon/current-continuity
assumptions described in P1 and P3.

## 4. Existing particle-coefficient extraction is an intermediate result

The module three_body_multipole_leptonic_weights.py forms the leading-static
particle coefficients using \(L_C^{(3)}\) for the Coulomb sector and
\(L_T=L_{11}+L_{22}\) for the transverse sector. The downstream
contract_three_body_afh_responses.py contracts the six candidate nonzero
coefficients with the provisional Python AFH response archive. It retains
the helicity-odd quantity as a diagnostic, separate from the AFH
\(\Sigma'\)-\(\Delta\) interference. The symmetry reduction above is the
working unpolarized-target projection; explicit tensor-level P3 validation
remains open.

The coefficients labelled \(C_M,C_{\Phi''},C_{M\Phi''},
C_\Delta,C_{\Sigma'},C_{\Sigma'\Delta}\) should therefore be treated as
a leading static matching layer. In particular, setting
\(C_{\Sigma''}=C_{\widetilde\Phi'}=0\) is a result of that truncation, not a
proof that every corresponding contribution vanishes in the full
three-body multipole problem.

The earlier spatial-sector bound
\(|R_{\rm spatial}/R_{\rm charge}|<7.1\times10^{-9}\) applies to its
tested 84 fixed-speed rows and stated approximation only. It is not a
global bound over all isotope/recoil/halo phase space.

## 5. Required derivation before the full halo fold

### P0 — Fix conventions

Record explicitly:
- metric \(g_{\mu\nu}=(+,-,-,-)\);
- \(q_A^\mu=P'^\mu-P^\mu\), and the AFH sign convention for the Fourier
  momentum in the multipole operators;
- the q-aligned frame and rotation convention;
- normalization of nuclear states and one-body current;
- whether the mediator propagator is evaluated at \(t_A=q_A^2\);
- the precise definition of each AFH response and interference response.

### P1 — Decompose the one-body nuclear vector current

The current full_current_nucleon_match.py is an exact Dirac-Pauli spinor
diagnostic for an on-shell impulse-approximation nucleon. Its reference
configuration takes \(q_N^0=0\) with internal momentum perpendicular to
\(\mathbf q\), and separately reports the residual obtained by contracting
that same current with the physical nuclear \(q_A^\mu\). This does not yet
supply the bound-nucleon energy transfer or the many-body continuity
equation. The next derivation must keep \(q_N^\mu\), \(q_A^\mu\), and the
internal nucleon momentum distinct, and state how off-shell/binding and
interaction-current effects are treated.

Starting from the same Dirac-Pauli current used by the code,

\[
J_N^\mu=\bar u_N'
\left[F_1^V(t_A)\gamma^\mu+
\frac{iF_2^V(t_A)}{2m_N}\sigma^{\mu\nu}q_{A,\nu}\right]u_N,
\]

derive charge, longitudinal convection, transverse convection, and
magnetization operators to a declared order in \(Q_A/m_N\) and
\(|\mathbf p_N|/m_N\).

Do not mix a static charge truncation with a claim of a complete vector
current.

### P2 — Perform the AFH multipole projection

**Status: leading-static particle-side coefficients derived and implemented;
full projection validation remains open.**

Section 3.2 gives the unpolarized-target symmetry reduction and the six
candidate nonzero leading-static coefficients
\(C_M,C_{\Phi''},C_{M\Phi''},C_\Delta,C_{\Sigma'},C_{\Sigma'\Delta}\).
The coefficient extractor and provisional 84-row contraction exercise
these terms, including the signed \(\Sigma'\)-\(\Delta\) interference.
The \(\Sigma''\) and \(\widetilde\Phi'\) zeros are restricted to the stated
one-body vector-current order.

The remaining P2 work is to derive the explicit Coulomb, longitudinal,
transverse-electric, and transverse-magnetic nuclear multipole matrix
elements with the same AFH phase and normalization conventions, and to
demonstrate that the symmetry reduction is consistent with the actual
many-body response definitions. The provisional Python response archive
is not a substitute for native seven-isotope response validation.

### P3 — Validate at the tensor level

At each selected phase-space point:
1. contract the covariant current tensor directly with the one-body nuclear
   current tensor;
2. contract the same result after q-frame rotation;
3. contract the AFH multipole decomposition;
4. compare all three, including charge-longitudinal interference and
   transverse interference.

The three results must agree within a declared numerical tolerance before
the AFH response coefficients are promoted.

### P4 — Only then perform native-AFH isotope and halo folding

For each isotope and recoil, interpolate the absolute native AFH responses
at exact \(q_A(E_R)\), evaluate the derived \(R_k^{(3)}\), and fold the
velocity and three-body phase-space integrals. Keep pointlike-M-only,
finite-\(t_N\)-M-only, and full-current results as separate baselines.

## 6. Acceptance language

Until the bound-current consistency and P3 tensor-level validation pass, use the labels:
- three_body_tensor_integrated;
- leading_static_coulomb_sector;
- partial_AFH_particle_coefficients;
- provisional_fixed_speed_AFH_contraction.

Do not use:
- full_AFH_three_body_response;
- complete_full_current_rate;
- final_natural_xenon_spectrum.

A native AFH database PASS validates the nuclear response input. It does not
by itself validate the three-body particle-side multipole projection.


## 7. Fixed-speed Xe-131 \(d\sigma/dE_R\) result and normalization correction

Workflow 44262472992 completed the fixed-speed Xe-131 differential
cross-section ratio calculation using the native AFH v6.0 \(M,\Phi''\),
and signed \(M\Phi''\) response archive, the finite-\(t_N\) Dirac--Pauli
charge coefficients, and the full \(2\to3\) phase-space integral.

The benchmark is \(m_{\chi_1}=1000\) GeV, \(m_s=300\) keV,
\(v_\chi=776\) km/s, \(g_2=1\), with the benchmark-specific mass splittings
shown below. The ratio is
\[
\mathcal Q(E_R)=
\frac{(d\sigma/dE_R)_{\rm finite-t_N,\ M+\Phi''}}
     {(d\sigma/dE_R)_{\rm pointlike,\ M}},
\]
where the denominator is the original pointlike \(9W_M\) baseline.

| \(E_R\) | \(\Delta m\) | \(\mathcal Q(E_R)\) | Relative change |
|---:|---:|---:|---:|
| 200 keV | 450 keV | 0.7783093394 | -22.1691% |
| 267 keV | 362 keV | 0.6492159107 | -35.0784% |

The width-scheme ratios agree to \(2.22\times10^{-16}\) (200 keV) and
\(1.11\times10^{-16}\) (267 keV), because the same \(L_C^{(3)}\)
phase-space factor multiplies numerator and denominator. The medium/high
relative differences in \(L_C\) are \(1.90\)--\(1.98\times10^{-10}\) at
200 keV and \(3.05\)--\(4.72\times10^{-10}\) at 267 keV.

The decomposition of the dimensionless charge-sector ratio is:

| Quantity | 200 keV | 267 keV |
|---|---:|---:|
| \(F_1^V(t_N)\) | 2.66316341 | 2.56388626 |
| \(F_2^V(t_N)\) | -0.46805344 | -0.44977451 |
| \(c_M\) | 2.65122188 | 2.54852325 |
| \(c_{\Phi''}\) | 0.02388306 | 0.03072600 |
| \(W_{\Phi''}/W_M\) | 0.03695594 | 19.84506258 |
| \(W_{M\Phi''}/W_M\) | -0.19120930 | -4.28296439 |
| \(Q_{\Phi''}\), relative to finite-\(t_N\) M-only | 0.99655805 | 0.89961039 |
| finite-\(t_N\) M-only / pointlike M | 0.78099749 | 0.72166342 |
| full coherent charge ratio | 0.77830934 | 0.64921591 |

The earlier \(-21.48\%\) and \(-34.24\%\) numbers in §45.2--45.3 are
consistent with the legacy \(F_1^2\) normalization audit, not the final
matched \(c_M\) numerator. On the same updated q points, the legacy
\(F_1^2\) ratios are \(-21.4664\%\) and \(-34.2933\%\). The updated full
coherent charge-sector result uses the Darwin--Foldy term in \(c_M\) and
retains the signed \(M\)-\(\Phi''\) interference. Small remaining
differences between the historical percentages and the same-q legacy
values also reflect the updated Xe-131 mass/q input.

The adopted mass convention in this run is
\(m_A=(m_{\rm atom}-Z m_e)u\), using the archived Xe-131 atomic mass
\(130.90508406\,u\), which gives \(m_A=121.90971983538435\) GeV.
The pointwise result is conditional on this bare-nucleus mass convention
and the central isoscalar \(z\)-expansion form-factor prescription.

Artifact 14408816831 (SHA-256
3d63f0d4896946129e1692ee0915da9b6d791323f65da85d0ee242bc1ae498bd)
contains the complete JSON, width comparisons, phase-space convergence
checks and provenance. This remains a fixed-speed Xe-131 Coulomb-sector
ratio; it is not an absolute \(d\sigma/dE_R\), a halo average, a
natural-xenon spectrum, or the complete eight-response nuclear-current
contraction.


### P1 follow-up: free on-shell energy-transfer-matched slice

The static \(q_N^0=0\) reference is now compared with a separate free
on-shell kinematic slice in which \(E_N'-E_N=E_R\), so that
\(q_N^\mu=q_A^\mu\). For \(p_i=\ell-q_A/2\) and
\(p_f=\ell+q_A/2\), the longitudinal internal momentum is fixed
analytically by
\[
\ell_\parallel=
\frac{E_R\sqrt{m_N^2+\ell_\perp^2+(Q_A^2-E_R^2)/4}}
{\sqrt{Q_A^2-E_R^2}}.
\]
The workflow's matrix-level test uses the diagnostic reference transfer
\(q_A^\mu=(0.0002,0.0705063355,0,0.2093780973)\) GeV, with
\(Q_A=0.2209306022\) GeV. For
\(\ell_\perp=0,50,100,200\) MeV it obtains
\(\ell_\parallel=0.855829,0.857025,0.860604,0.874771\) MeV.
The maximum \(|q_N^0-q_A^0|\) is \(8.90\times10^{-17}\) GeV; the largest
Ward residual is \(2.40\times10^{-16}\) with \(q_N^\mu\) and
\(1.49\times10^{-17}\) with \(q_A^\mu\).

The original static slice has \(q_N^0=0\), Ward residual
\(3.84\times10^{-18}\) with \(q_N^\mu\), but
\(5.3513\times10^{-4}\) with physical \(q_A^\mu\). This establishes that
the static \(q_N^0=0\) mismatch is a consequence of that particular
impulse kinematics, not a failure of the free Dirac--Pauli vertex.

For the separate exact-mass Xe-131 fixed-speed points, the analytic
formula gives \(\ell_\parallel=0.8562\)--0.8752 MeV at 200 keV and
0.9916--1.0134 MeV at 267 keV for
\(\ell_\perp=0\)--200 MeV. Those are kinematic estimates; the matrix-level
Ward test was performed at the diagnostic reference four-transfer, not
at both fixed-speed points.

This does **not** identify the physical bound-nucleon energy sharing,
off-shell prescription, or interaction currents. The many-body continuity
equation and the consistency of the one-body AFH truncation remain open.


## 2026-11-18 implementation update

The leading-static six-channel particle-side candidate is now wired into the
optional native halo-fold path. The candidate consumes the full integrated
q-aligned three-body tensor and all eight native AFH responses; it does not
reduce the input to the charge-only three columns. The engine checks both
nuclear interference-response Cauchy-Schwarz bounds:
\[
|W_{M\Phi''}|\leq\sqrt{W_MW_{\Phi''}},\qquad
|W_{\Sigma'\Delta}|\leq\sqrt{W_{\Sigma'}W_\Delta}.
\]
These are separate from the particle-side identity for
\(C_{\Sigma'\Delta}\).

This implementation does not close P2/P3 promotion. The signed
Sigma'-Delta phase still requires the exact AFH spherical-multipole check,
and the direct covariant, q-frame-rotated, and AFH multipole contractions
must still agree. The 16,807-point native input gate is still queued.
Use the label provisional_leading_static_vector_current_candidate only.


## 8. P1 completion update — 2026-11-18

P1 is now **complete within the free on-shell one-body impulse approximation**.
The exact Dirac--Pauli current has been decomposed into the Darwin--Foldy
and spin-orbit charge terms, longitudinal convection, transverse convection,
and transverse magnetization. The exact longitudinal relation
\[
J_{N,\parallel}=(q_N^0/Q_N)J_N^0
\]
is retained for the on-shell free nucleon; it is not replaced by the leading
\(F_1K_{N,\parallel}/m_N\) approximation when testing continuity.

The exact spinor current is compared with its Pauli-reduced expansion at
the Xe-131 200 and 267 keV transfers for four transverse internal momenta
(0, 50, 100, 200 MeV). The largest relative errors are 0.0592% in the charge
component, 3.1327% in the transverse spatial current, and 0.7846% in the
full four-current. Exact free-nucleon Ward and longitudinal-continuity
residuals are below \(2\times10^{-12}\).

The dedicated derivation, benchmark table, and test are in
P1_DIRAC_PAULI_CURRENT_DECOMPOSITION.md and
test_one_body_nr_current_expansion.py.

This does **not** close the bound-nucleus/off-shell current problem:
energy sharing, binding, the nuclear Hamiltonian, and any required
interaction currents remain outside the free on-shell diagnostic. P2
therefore starts from the established one-body operators but must still
derive their exact AFH spherical multipoles and signed interference phase.


## 9. P0 scope clarification and P2 particle-side phase closure — 2026-11-18

The project P0 in Section 5 is the **convention-fixing gate** (metric,
momentum-transfer signs, q-aligned frame, state/current normalization,
mediator transfer, and AFH response definitions). P0 is closed. It must not
be relabeled as the separate native-AFH database/input gate.

The native seven-isotope/eight-response archive and its 16,807-point
validation are nuclear-input acceptance tasks for the later native-AFH
folding stage; they are not the definition of P0.

P1 is closed within the free on-shell one-body impulse approximation, as
documented in P1_DIRAC_PAULI_CURRENT_DECOMPOSITION.md.

The particle-side P2 phase is now independently checked by evaluating AFH
Eq. (107) on complex spin-resolved three-body amplitudes before spin
averaging, then comparing against the q-aligned Lorentz-tensor coefficient
extractor. The regression fixes the negative sign of
C_{Sigma' Delta}, verifies transverse-axis rotation invariance, and shows
that this coefficient is not the generic helicity-odd L12-L21 weight.

P2 is therefore **closed at the particle-side coefficient/phase level**.
The full nuclear multipole/OBDME contraction and pointwise P3 tensor
comparison remain open. Do not promote the 84-row provisional contraction
to a full natural-xenon prediction.


## 10. P3-A: direct full-current q-frame covariance — 2026-11-18

The exact three-body DM current and exact free on-shell Dirac--Pauli
nucleon current have now been contracted as a full
DM-spin \(\otimes\) nucleon-spin \(4\times4\) amplitude in the lab frame
and after a common right-handed rotation to the q-aligned frame. The
regression checks the full, charge, and spatial amplitude operators, the
spin-summed norm, and the DM Lorentz tensor transformation. The
energy-transfer-matched nucleon satisfies \(q_N^\mu=q_A^\mu\).

The same test extracts the actual three-body spin-resolved DM amplitudes
in the q frame, evaluates AFH Eq. (107) before spin averaging, and compares
the three spatial coefficients with the independent Lorentz-tensor
extractor using the correct initial-DM-spin average. This joins the
actual three-body current to the signed particle-side AFH coefficient
calculation.

This closes P3-A (direct covariant vs q-frame and actual-T3 Eq. (107)
particle-side comparison) at the reference point. P3-B remains open:
the AFH nuclear OBDME/multipole contraction must agree with the direct
nuclear-current contraction at the same point. No full natural-xenon
spectrum or halo-folded rate is promoted by this test.
