# P3-B → P3-C → P4 execution plan

**Project:** LZ-3-body-for-hdm  
**Formal nuclear input:** AFH v6.0 only; GCN/JJ55 are excluded.  
**Formal propagator prescription:** asymmetric Pole width (first \(p-k\) zero-width, second \(p'+k\) constant pole-width).

## Status snapshot

| Stage | Current state | Evidence / blocker |
|---|---|---|
| P3-B native AFH comparison | QUEUED / OPEN | [control run 44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069); self-hosted Windows/X64/research-gpu runner has no assigned runner |
| P3-C response-level contraction | PROVISIONAL / HISTORICAL NORMALIZATION | 28 pole-only rows; spatial/charge ratios are retained, but archived absolute coefficients used raw flavor sums and are not physical g_VN-normalized rates; effective-basis rerun required |
| P3-C spatial amplitude subgate | STRUCTURAL PASS (provisional Python AFH; normalized rerun pending) | Four Xe-131 Pole-width benchmarks; relative helicity-vs-Cartesian residual is scale-invariant, but archived coefficient output used raw form factors |
| P3-C full covariant nuclear amplitude | OPEN | Charge multipoles are not yet rank-resolved; independent coordinate-space bound-nucleus current and native AFH comparison remain required |
| P4 native seven-isotope halo fold | PREPARED / BLOCKED | Native production input still waits for local MMA comparison |
| P4 provisional seven-isotope halo fold | PRIOR WORKFLOW PASS; CURRENT B/C0 HEAD UNVALIDATED | Explicit source-translated AFH-8 + P3-B loader, hash/C0/Cauchy gates, Pole-only halo integration, exact Lorentz-invariant t_A mediator denominator; output remains provisional |

## P3-B — native Wolfram AFH comparison

### Pinned inputs

- P3-B source archive: LZ workflow run `44337928314`, artifact `14443055701`.
- Native exporter source commit: `5afc500a3102b857dd16e29432db8e6e068d65d1`.
- Native control workflow PR: [research-compute-control PR #2](https://github.com/lm846802297-bit/research-compute-control/pull/2).
- Native run: [44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069).
- AFH source hash: `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`.

### Required comparisons

1. Compare all seven isotopes × 2,401 q nodes × eight AFH responses: 16,807 total-response rows.
2. Compare 9,604 rank-resolved \(\Delta_J\), \(\Sigma'_J\), and signed \(\Sigma'_J\)-\(\Delta_J\) rows for Xe-129 and Xe-131.
3. Compare both raw AFH package responses and physical equal-\(p=n\), \(C_0(A)\)-corrected responses.
4. Check source hashes, canonical q/y grids, rank map, imaginary residuals, signed interference, and Cauchy-Schwarz bounds.
5. Use the 121-point native Xe-131 dense charge export on \(0.2545\le q_A\le0.2575\) GeV to settle the diffraction-minimum interpolation.

The comparator's tolerances are fixed in the version-pinned script. Do not relax them to obtain PASS. If it fails, classify the failure as source mismatch, OBDME phase/rank mismatch, normalization mismatch, interpolation mismatch, or numerical precision.

### Interpolation disposition

The current local interpolation audit finds Cheb8/Cheb10 stability at the selected q points, while PCHIP differs from Cheb10 by up to 1.6847% for \(W_M\) near the Xe-131 diffraction minimum. The corresponding normalized full/A-reference ratio difference is at most 0.1182% in the selected scan. This is not a native result. After the native dense export arrives, regenerate the absolute and ratio curves with native dense \(M,\Phi'',M\Phi''\) values in the dip region; do not smooth or fit away the minimum.

## P3-C — amplitude-level covariant-to-AFH validation

The current 28-row pole-only result is a response-level contraction. It checks
\[
\mathcal K_A^{(3)}=\sum_X C_X^{(3)}R_X
\]
and rank-sum reconstruction, but does not prove equality of the nuclear
amplitudes.

The required selected-point comparison is:

1. Choose Xe-129 and Xe-131, including all allowed native multipole ranks.
2. Use the same external kinematics and the same Pole-width three-body
   amplitude for the direct covariant and q-aligned calculations.
3. Contract the exact Dirac-Pauli one-nucleon current with the nuclear
   OBDMEs before spin averaging; keep the complex amplitudes and all phases.
4. Construct the AFH spherical-multipole amplitude from native
   \(M_{\Delta,J}\) and \(M_{\Sigma',J}\), with the same Wigner-Eckart
   convention and magnetic-substate sums.
5. Compare direct covariant, q-frame, and AFH multipole amplitudes before
   squaring; separately compare the spin-summed kernels and signed
   \(\Sigma'\)-\(\Delta\) interference.
6. Verify the charge-sector \(M+\Phi''+M\Phi''\) limit, rotation covariance,
   normalization, and the factor-four / \(C_0(A)\) bookkeeping.
7. Report exact-covariant versus leading-NR truncation differences
   separately. Do not interpret higher-order Dirac terms as an AFH phase
   mismatch.

A particle-side Eq. (107) coefficient test or a rank-sum reconstruction
alone is not P3-C PASS. The amplitude-level artifact must contain the
complex direct and AFH amplitudes, per-rank contributions, signed
interference, residuals, and source hashes.

## P4 — seven-isotope natural-xenon halo fold

The existing `native_charge_sector_halo_fold.py` is the P4 engine. It
supports a provenance-checked native seven-isotope/eight-response bundle
and a separate, explicitly provisional Python AFH bundle. The latter loads
the AFH-8 charge responses and the P3-B spatial OBDME responses, applies the
common C0 correction to charge responses exactly once, and never labels the
result native. The native path independently derives C0(A) from the raw
M(q_A=0) anchor and applies the factor four and C0 once to all eight channels.
The engine uses the exact spatial magnitude
Q_A=sqrt(2*m_A*E_R+E_R^2), the invariant t_A=-2*m_A*E_R, applies the Pole-width three-body
phase-space integral at each halo-speed node, and computes abundance-weighted
rates.

Formal P4 requirements:

- isotopes: Xe-128, Xe-129, Xe-130, Xe-131, Xe-132, Xe-134, Xe-136;
- natural atom-fraction coverage: 99.8158%; Xe-124/Xe-126 remain explicitly
  outside the AFH default-density set;
- use native AFH response columns only; no GCN/JJ55 substitution;
- use `width_scheme="pole"` only;
- report separately A-reference \(M\), finite-\(t_N\) \(M\), Coulomb
  \(M+\Phi''\), and the full matched-current result;
- include both the truncated SHM and untruncated Maxwellian halo scenarios;
- run speed, three-body phase-space, and recoil-grid convergence;
- verify positivity, both response Cauchy-Schwarz inequalities, and the
  signed \(M\)-\(\Phi''\) and \(\Sigma'\)-\(\Delta\) interference;
- retain the seven-isotope abundance coverage and the isotope-by-isotope
  contributions in the output.

Before local MMA comparison, the provisional engine can calculate a
selected-grid Coulomb baseline and a leading-static six-channel candidate.
These are end-to-end numerical diagnostics only; they are not native AFH
results or a full P3-C PASS. The final full-vector halo spectrum must not be
promoted until the local native AFH comparison and the full P3-C
amplitude-level gate pass. Detector efficiency,
energy resolution, exposure, and likelihood are a later detector-level stage.

## Stop conditions

- Native runner unavailable: keep P3-B queued; do not replace native results
  with the Python translation. The provisional P4 path may still be run for
  pipeline completion, but all outputs must retain
  `native_afh_validated=false` until the user's local MMA comparison.
- P3-B mismatch: stop P3-C and P4 promotion until source, phase, or
  normalization discrepancies are resolved.
- P3-C amplitude mismatch: do not infer that the small response-level
  spatial/charge ratio makes the mismatch irrelevant.
- P4 convergence failure: keep the spectrum provisional and refine the
  affected isotope/speed/recoil nodes only.


## P3-C spatial amplitude-level subgate — previous provisional structural run

The new reproducible calculation
[`p3c_amplitude_level_helicity_crosscheck.py`](p3c_amplitude_level_helicity_crosscheck.py)
uses the full complex \(G_{\mu a,\nu b}^{(3)}\) tensor and signed Xe-131
\(\Delta_J,\Sigma'_J\) amplitudes. It compares the direct Cartesian
Eq. (107) contraction against a helicity-amplitude reconstruction before
summing over transverse helicity and multipole rank.

- Pole-width benchmarks: four (200 and 267 keV).
- Maximum amplitude-kernel relative residual:
  \(6.09\times10^{-16}\).
- Maximum Eq. (107) coefficient relative residual:
  \(8.53\times10^{-16}\).
- Maximum PCHIP-amplitude versus existing linear-response interpolation
  difference: \(5.53\times10^{-6}\).
- Four unit tests pass, including a deliberate sign-flip test showing that
  the wrong \(\Sigma'\)-helicity phase reverses the signed interference.

This closes only the **spatial helicity reconstruction subgate**. It is not
an independent coordinate-space many-body current calculation, and the
charge \(M,\Phi''\) multipoles are not yet rank-resolved. The archived
coefficient output used raw \(F_1^{uds}=3\), \(F_2^{uds}=-0.552\); the
current producer and P3-C consumer now use explicit effective-nucleon
fields \(\widehat F_{1,2}^{N}\). The relative structural residuals are
unchanged by a common normalization, but the serialized output must be
regenerated in the effective basis. The native Wolfram AFH comparison
also remains queued. Full P3-C therefore remains OPEN.

The workflow now runs this subgate after the C0-consistent response
contraction and appends its JSON result to the
`full-three-body-current-nucleon-match-and-phase-space-tensor` artifact.

## Latest-head validation boundary (2026-11-19)

The prior workflow set at commit `cb89294c891cfa6ac7ffa52ba89065df84823c28`
passed the full-current regression, provisional P4 halo fold, fixed-speed
charge-sector, and continuous-spectrum jobs. PR #67 has since received
additional changes to the adopted B finite-\(t_N\) form factors, explicit
raw/effective field names, native AFH \(C_0(A)\) handling, and the Xe-131
absolute A/B/C workflow. No workflow run is currently attached to the
latest PR head. Therefore the earlier PASS is historical and does not
validate the current B/C0 code; rerun all affected workflows before merge.

The adopted production convention is B:
\[
\widehat F_{1,2}^{N}(t_N)\,W_M^{\rm phys}(y_A),\qquad
t_N=t_A=-2m_AE_R,\qquad
y_A=b_A^2Q_A^2/4.
\]
A is the zero-transfer nucleon-current reference with the same finite-size
AFH \(W_M\); C is a separate \(\Phi''\) charge extension; D remains the
full one-body-current target, not yet complete.
