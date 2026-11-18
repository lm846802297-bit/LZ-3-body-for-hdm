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

The module native_charge_sector_halo_fold.py currently calls
integrate_spin_resolved_tensor, but extracts only

\[
L_{00}=\texttt{point\_nucleus\_contractions["I00"]}.
\]

It then builds \(M,\Phi'',M\Phi''\) coefficients from this scalar weight.
Consequently it is a **charge-density-sector approximation**. It is not the
complete contraction \(L_{\mu\nu}^{(3)}W_A^{\mu\nu}\), and its output must not
be described as the final full-current rate.

The finite-\(t_N\) charge matching can be studied within this restricted
sector, provided its static/charge-density approximation is stated. It does
not settle the longitudinal-current contribution or its interference with
the charge multipoles.

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

## 4. Existing particle-coefficient extraction is an intermediate result

The module contract_three_body_afh_responses.py currently forms leading static
coefficients using \(L_{00}\) and \(L_T=L_{11}+L_{22}\). It includes
diagnostics for the transverse helicity-odd combination, but the present
coefficient table does not yet constitute a demonstrated complete projection
of every component of \(L_{\mu\nu}\) onto all AFH multipole bilinears.

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
