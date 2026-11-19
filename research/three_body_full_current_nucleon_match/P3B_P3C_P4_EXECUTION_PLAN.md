# P3-B → P3-C → P4 execution plan

**Project:** LZ-3-body-for-hdm  
**Formal nuclear input:** AFH v6.0 only; GCN/JJ55 are excluded.  
**Formal propagator prescription:** asymmetric Pole width (first \(p-k\) zero-width, second \(p'+k\) constant pole-width).

## Status snapshot

| Stage | Current state | Evidence / blocker |
|---|---|---|
| P3-B native AFH comparison | QUEUED / OPEN | [control run 44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069); self-hosted Windows/X64/research-gpu runner has no assigned runner |
| P3-C response-level contraction | PROVISIONAL PASS | 28 pole-only rows; all total kernels positive; maximum spatial/charge ratio \(7.03050\times10^{-9}\) |
| P3-C spatial amplitude subgate | PASS (provisional Python AFH) | Four Xe-131 Pole-width benchmarks; maximum helicity-vs-Cartesian residual \(6.09\times10^{-16}\) |
| P3-C full covariant nuclear amplitude | OPEN | Charge multipoles are not yet rank-resolved; independent coordinate-space bound-nucleus current and native AFH comparison remain required |
| P4 native seven-isotope halo fold | PREPARED / BLOCKED | Native charge-fold engine exists; must wait for P3-B and P3-C acceptance |

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

The current local interpolation audit finds Cheb8/Cheb10 stability at the selected q points, while PCHIP differs from Cheb10 by up to 1.6847% for \(W_M\) near the Xe-131 diffraction minimum. The corresponding normalized full/original-AFH-M-baseline ratio difference is at most 0.1182% in the selected scan. The denominator retains the native finite-q \(W_M(Q_A)\) response. This is not a native result. After the native dense export arrives, regenerate the absolute and ratio curves with native dense \(M,\Phi'',M\Phi''\) values in the dip region; do not smooth or fit away the minimum.

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
loads a provenance-checked native seven-isotope/eight-response bundle,
uses isotope-specific exact q kinematics, applies the Pole-width three-body
phase-space integral at each halo-speed node, and computes abundance-weighted
rates.

Formal P4 requirements:

- isotopes: Xe-128, Xe-129, Xe-130, Xe-131, Xe-132, Xe-134, Xe-136;
- natural atom-fraction coverage: 99.8158%; Xe-124/Xe-126 remain explicitly
  outside the AFH default-density set;
- use native AFH response columns only; no GCN/JJ55 substitution;
- use `width_scheme="pole"` only;
- report separately the original AFH M-only baseline \(F_1(0)^2W_M(Q_A)\),
  finite-\(t_N\) M-only, Coulomb \(M+\Phi''\), and the full matched-current
  candidate;
- preserve the original finite-q AFH nuclear shape factor \(W_M(Q_A)\) in
  every denominator; never add an extra nuclear form factor on top of AFH;
- report both \(R_{\rm charge}/R_{t_N,M}\) (multipole correction at fixed
  nucleon form factors) and \(R_{\rm charge}/R_{\mathrm{AFH},M}^{(0)}\)
  (total change relative to the original AFH M-only calculation);
- run the first-order low-\(Q_N^2\) bishara_linear diagnostic and the
  isoscalar_zexp alternative side by side; neither replaces the AFH nuclear
  form factor, and neither is silently identified with an unverified
  model-specific finite-\(t_N\) input;
- include both the truncated SHM and untruncated Maxwellian halo scenarios;
- run speed, three-body phase-space, and recoil-grid convergence;
- verify positivity, both response Cauchy-Schwarz inequalities, and the
  signed \(M\)-\(\Phi''\) and \(\Sigma'\)-\(\Delta\) interference;
- retain the seven-isotope abundance coverage and the isotope-by-isotope
  contributions in the output.

For exact recoil kinematics, keep the two momentum invariants separate:
\[
t_A=q_A^\mu q_{A,\mu}=-2m_AE_R,\qquad
Q_A^2=|\boldsymbol q_A|^2=2m_AE_R+E_R^2.
\]
The vector-mediator propagator uses \((m_V^2-t_A)^2\), whereas the static
one-body impulse form-factor diagnostic uses
\(Q_N^2=-t_N=|\boldsymbol q_N|^2\simeq Q_A^2\). Do not substitute the
spatial \(Q_A^2\) into the invariant mediator propagator.

The Coulomb-sector halo result can be reported after native P3-B validation
as a separately labelled baseline. The full-vector halo spectrum must not
be promoted until the P3-C amplitude-level gate passes. Detector efficiency,
energy resolution, exposure, and likelihood are a later detector-level stage.

## Stop conditions

- Native runner unavailable: keep P3-B queued; do not replace native results
  with the Python translation.
- P3-B mismatch: stop P3-C and P4 promotion until source, phase, or
  normalization discrepancies are resolved.
- P3-C amplitude mismatch: do not infer that the small response-level
  spatial/charge ratio makes the mismatch irrelevant.
- P4 convergence failure: keep the spectrum provisional and refine the
  affected isotope/speed/recoil nodes only.


## P3-C spatial amplitude-level subgate — completed locally

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
charge \(M,\Phi''\) multipoles are not yet rank-resolved. The native
Wolfram AFH comparison also remains queued. Full P3-C therefore remains
OPEN.

The workflow now runs this subgate after the C0-consistent response
contraction and appends its JSON result to the
`full-three-body-current-nucleon-match-and-phase-space-tensor` artifact.


## 2026-11-19 update: non-Mathematica work completed/prepared

The user will run the native Mathematica/Wolfram comparison locally later.
Until that comparison is supplied, do not claim native P3-B PASS or full
P3-C PASS. The remaining work that does not depend on Mathematica has been
advanced as follows:

1. The formal natural-xenon halo engine now rejects every width setting
   except `pole` at the Python API boundary. Its CLI exposes only
   `--width-scheme pole`. This prevents a zero- or running-width result
   from accidentally entering formal production.
2. A regression test explicitly checks that both `zero` and `running`
   are rejected before native files are loaded.
3. A manual P4 workflow,
   `.github/workflows/p4-native-afh-natural-xenon-pole-halo.yml`, has been
   added. It consumes a completed native AFH artifact by run ID and artifact
   ID, runs the seven-isotope fold for both SHM-cutoff and untruncated
   Maxwellian halos, and archives two separate outputs:
   - the Coulomb-sector result;
   - the leading-static full-vector candidate, explicitly unpromoted.
4. The workflow is intentionally manual and cannot run until the user's
   local native AFH comparison has produced an artifact with a PASS
   provenance manifest. No synthetic or Python-translated response archive
   is accepted as a substitute.

The P4 workflow defaults to (m_\chi=1\) TeV, (m_s=450\) keV,
\(\delta m=450\) keV, and recoil nodes 101, 200, 267, and 542 keV.
These are workflow defaults for a reproducible diagnostic, not a scan
over the model's preferred parameter space. The quadrature orders are
higher than the earlier smoke-test settings; a separate convergence
comparison is still required before treating any spectrum as numerically
final.

### Local Mathematica handoff

When the local comparison is complete, provide the complete native archive
root containing `native-comparison.json`, `run_manifest.json`,
`SHA256SUMS.txt`, `native/`, `native-spatial-multipoles/`, and
`native-dense-charge-dip/`. The P4 workflow must use the native response
artifact from that run, not a provisional Python archive. If the native
comparison fails, preserve the failed artifact and diagnose it; do not
force a PASS or relax tolerances.
