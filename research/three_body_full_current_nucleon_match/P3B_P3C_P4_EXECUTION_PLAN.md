# P3-B → P3-C → P4 execution plan

**Project:** LZ-3-body-for-hdm  
**Formal nuclear input:** AFH v6.0 only; GCN/JJ55 are excluded.  
**Formal propagator prescription:** asymmetric Pole width (first \(p-k\) zero-width, second \(p'+k\) constant pole-width).

## Status snapshot

| Stage | Current state | Evidence / blocker |
|---|---|---|
| P3-B native AFH comparison | QUEUED / OPEN | [control run 44346207069](https://github.com/lm846802297-bit/research-compute-control/actions/runs/44346207069); self-hosted Windows/X64/research-gpu runner has no assigned runner |
| P3-C response-level contraction | PROVISIONAL PASS | 28 pole-only rows; all total kernels positive; maximum spatial/charge ratio \(7.03050\times10^{-9}\) |
| P3-C amplitude-level comparison | NOT STARTED / OPEN | Need native multipole amplitudes and direct covariant/q-frame/AFH amplitude reconstruction with common OBDMEs |
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

The current local interpolation audit finds Cheb8/Cheb10 stability at the selected q points, while PCHIP differs from Cheb10 by up to 1.6847% for \(W_M\) near the Xe-131 diffraction minimum. The corresponding normalized full/pointlike ratio difference is at most 0.1182% in the selected scan. This is not a native result. After the native dense export arrives, regenerate the absolute and ratio curves with native dense \(M,\Phi'',M\Phi''\) values in the dip region; do not smooth or fit away the minimum.

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
- report separately pointlike \(M\), finite-\(t_N\) \(M\), Coulomb
  \(M+\Phi''\), and the full matched-current result;
- include both the truncated SHM and untruncated Maxwellian halo scenarios;
- run speed, three-body phase-space, and recoil-grid convergence;
- verify positivity, both response Cauchy-Schwarz inequalities, and the
  signed \(M\)-\(\Phi''\) and \(\Sigma'\)-\(\Delta\) interference;
- retain the seven-isotope abundance coverage and the isotope-by-isotope
  contributions in the output.

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
