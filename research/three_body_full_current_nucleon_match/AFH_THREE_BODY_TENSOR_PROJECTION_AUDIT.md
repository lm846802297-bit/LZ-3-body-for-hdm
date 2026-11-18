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

For the 12 integrated benchmark/width rows in workflow 44256878592,
\(\omega/Q_A\) is \(9.0526\times10^{-4}\) at 200 keV and
\(1.0460\times10^{-3}\) at 267 keV. The continuity-adjusted Coulomb weight
differs from \(L_{00}\) by approximately \(-4.33\times10^{-6}\) to
\(-5.13\times10^{-6}\). This is small numerically, but it is retained because
it is required by the conserved nuclear vector current.

The particle-coefficient extractor now uses \(L_C^{(3)}\) for
\(C_M,C_{\Phi''},C_{M\Phi''}\), while the transverse coefficients continue
to use \(L_T=L_{11}+L_{22}\). The archive reader also checks
\(Q_A^2=2m_A E_R+E_R^2\), recomputes the direct point-nucleus contraction,
and verifies that the stored continuity-reduced contraction agrees.
These checks close the kinematic/index-convention audit at the leptonic
weight level. They do not establish dynamical current conservation for the
truncated many-body one-body current or complete the AFH multipole
validation.

## 4. Existing particle-coefficient extraction is an intermediate result

The module three_body_multipole_leptonic_weights.py forms leading-static
particle coefficients using \(L_C^{(3)}\) for the Coulomb sector and
\(L_T=L_{11}+L_{22}\) for the transverse sector. The downstream
contract_three_body_afh_responses.py contracts these coefficients with the
provisional Python AFH response archive. It includes diagnostics for the
transverse helicity-odd combination, but the present coefficient table does
not yet constitute a demonstrated complete projection of every component
of \(L_{\mu\nu}\) onto all AFH multipole bilinears.

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

Project the charge and spatial current into the appropriate Coulomb,
longitudinal, transverse-electric, and transverse-magnetic multipoles.
Derive the particle-side bilinears from the full integrated
\(L_{\mu\nu}^{(3)}\), including any allowed off-diagonal/helicity structures.

The result must identify exactly which AFH nuclear responses occur and
which vanish by a demonstrated symmetry, continuity equation, or the
declared order of the NR expansion.

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

Until P0–P3 pass, use the labels:
- three_body_tensor_integrated;
- leading_static_charge_sector;
- partial_AFH_particle_coefficients.

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
