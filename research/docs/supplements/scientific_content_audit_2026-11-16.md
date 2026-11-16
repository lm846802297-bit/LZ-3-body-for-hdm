# LZ-3-body scientific content audit — Phase 1

**Audit date:** 2026-11-16  
**Baseline:** `main` at `58f97ab27e104cdb65c3ce542bb3d7f1bc1c2648`  
**Scope:** Eq. (6) phase-space integration, AFH-7/Hybrid-9 natural-xenon spectra, GCN/JJ55 comparison, result provenance, and the corresponding high-impact documentation.  
**Status:** First-pass audit; this is not yet a review of all 106 research Markdown files.

## Executive result

No new algebraic defect was established in the inspected three-body kinematic boundaries, exact spatial momentum convention, AFH equal-(p,n) normalization, or natural-xenon target-number formula. The current repository nevertheless contains important **status and numerical-method inconsistencies** that must be kept visible:

1. The seven-isotope AFH default-density response grid and an 84-point AFH-7/Hybrid-9 recoil-grid spectrum are already committed to `main`. Several older documents still say AFH is selected-point-only.
2. The old AFH selected-point rate table uses the legacy low-order linear-(W^2) kernel. The newer AFH-7 grid uses threshold-(u^2) integration. Their common points differ by about (2.3\times10^{-4})–(2.6\times10^{-4}) relatively, consistent with the previously measured low-order linear-(W^2) quadrature bias. The old table must remain historical, not be silently mixed with the new grid.
3. The committed GCN/JJ55 continuous spectra still use the legacy linear-(W^2), (8×8×4) kernel. Their (16×16×8) spot checks reach (2.18895×10^{-4}) in the kernel, whereas the AFH-7 grid uses threshold-(u^2). At the production 24-speed-node setting, the final internal-kernel increment is (5.96430×10^{-10}); the separate 12-speed-node comparison is (6.02323×10^{-10}). Cross-model comparisons therefore do not yet have matched numerical integration.
4. The final (24\times8\times8\times4) AFH-7/Hybrid-9 high-order spectra are described by a committed audit and checksum, but the complete 1,344-row high-order archive is external; the committed 1,344-row spectrum is the (24\times6\times6\times3) baseline.
5. The full Mathematica–Python (d\sigma_A/dE_R) comparison and the official LZ detector likelihood remain incomplete.

The documentation updates in this branch correct the current status and preserve the historical outputs. They do **not** change model parameters, numerical inputs, or archived physics results.

## 1. AFH-7 response and recoil-grid coverage

The following inputs and outputs are present on `main`:

- Seven official AFH v6.0 default-density isotope matrices: Xe-128, 129, 130, 131, 132, 134, and 136.
- Seven 2,401-node isotope response tables, plus the combined 16,807-row response table.
- The response convention is direct finite-sum evaluation at exact isotope-specific spatial momentum (q_A=\sqrt{2m_AE_R+E_R^2}); the older 28-row PCHIP sample file is not the source of the new full-grid calculation.
- The AFH-7/Hybrid-9 recoil calculation contains 84 recoil-energy points over 5–800 keV, four particle benchmarks, and four response scenarios, giving 1,344 spectrum rows.
- The AFH-7 atom-fraction coverage is 0.998158. Xe-124 and Xe-126 remain absent from the official AFH default-density input; their 0.001842 abundance is not renormalized into the other isotopes.

The grid is **sampled on 84 recoil points**; “continuous spectrum” in older descriptions means a full-range grid-sampled spectrum rather than an analytic continuum or a 1-keV grid.

The committed baseline spectrum uses threshold-(u^2) phase-space integration with 24 speed nodes and (6×6×3) internal quadrature. The convergence audit additionally uses a 12-speed-node (12×6×6×3) reference to isolate the speed-order increment; its final comparison uses 24×8×8×4. The separate high-order audit reports:

| Check | Maximum relative difference |
|---|---:|
| Speed order 12 → 24, all open points | (6.63735\times10^{-6}) |
| Internal order (6\times6\times3\to8\times8\times4), all open points | (6.02323\times10^{-10}) |
| 12×6×6×3 kernel integral → 24×8×8×4, all open points | (6.63746×10^{-6}) |
| Committed spectrum 24×6×6×3 → high-order spectrum 24×8×8×4 | (6.46772×10^{-6}) |
| Speed order 24 → 48, worst 32 points | (2.21749\times10^{-7}) |
| Independent Numba/Python reference, 12 points | (5.32907\times10^{-15}) |

All reported differences are below the (10^{-5}) acceptance threshold. Two comparisons must not be conflated: (6.63746×10^{-6}) is the maximum pointwise kernel-integral difference between the 12-speed-node reference and the 24-speed-node high-order calculation; (6.46772×10^{-6}) is the maximum difference between the committed 24-speed-node baseline spectrum and the high-order spectrum. The full high-order 1,344-row output is recorded as a 736,245-byte external ZIP with SHA-256 `e55442d3ad4289dfd6c16e8e6cdb43d669561df074beddefcf87e8d1024f3471`; the repository currently contains the audit summary and the baseline spectrum, not the full high-order ZIP contents.

## 2. Legacy selected-point rates versus the new AFH-7 grid

The historical selected-point table and the current AFH-7 grid are not numerically identical. At common points:

| Benchmark | (E_R) | Historical rate | Current AFH-7 grid rate | Relative shift |
|---|---:|---:|---:|---:|
| Red | 101 keV | (5.281045\times10^{-11}) | (5.279789\times10^{-11}) | (-237.7) ppm |
| Green | 101 keV | (2.599528\times10^{-22}) | (2.598864\times10^{-22}) | (-255.4) ppm |
| Green | 200 keV | (1.813604\times10^{-11}) | (1.813160\times10^{-11}) | (-245.0) ppm |
| Green | 267 keV | (2.727114\times10^{-13}) | (2.726493\times10^{-13}) | (-228.0) ppm |
| Green | 542 keV | (1.456137\times10^{-15}) | (1.455774\times10^{-15}) | (-249.5) ppm |

The phase-space audit independently found that the legacy linear-(W^2), (8\times8\times4) integration differs from a high-order threshold-(u^2) reference by up to (2.42445\times10^{-4}) at the tested fixed-speed benchmarks. The threshold-(u^2), (6\times6\times4) values in that audit differ from its high-order reference by at most (1.62\times10^{-10}).

This is consistent with the observed rate shifts. The old selected-point files are retained as reproducible historical outputs; the new AFH-7 grid is the current full-range seven-isotope result. The historical table should not be overwritten or presented as the new grid.

A separate 2026-11-16 Xe-131 mapping audit used **zero width and fixed speed**. It found that threshold-(u^2) at (48\times40\times24) and (64\times48\times32) agrees to (1.40\times10^{-11}), while threshold-(u^2) differs from the historical high-order archive by about (2.2\times10^{-6}). This is an (I_6)-only, fixed-speed diagnostic; it is not a full natural-xenon pole-width rate validation.

## 3. GCN/JJ55 integration is not yet matched to AFH-7

The four GCN/JJ55 natural-xenon spectra are also 84-point full-range grids, but their metadata show:

- production kernel: linear-(W^2), (8\times8\times4);
- spot-check kernel: (16\times16\times8);
- maximum kernel-order difference across the four benchmark metadata files: (2.18895152\times10^{-4});
- maximum speed-quadrature difference: (1.60400147\times10^{-6}).

The high-energy-tail report's earlier (2.07\times10^{-4}) summary understated the maximum; the maximum across the four current metadata files is (2.18895\times10^{-4}).

The reported GCN/JJ55 tail shifts of roughly 12–19% are much larger than this numerical difference. The Hybrid-9/AFH-7 shifts of 0.66–1.16% also exceed it, but have less numerical margin. The current model comparisons are therefore useful diagnostics, not yet a matched-precision final comparison. The next numerical task is to rerun GCN/JJ55 on the same threshold-(u^2) mapping and a common convergence target, then regenerate the efficiency-weighted tail table and dependent rate-level yields.

## 4. AFH normalization, isotope sum, and detector boundary

The inspected AFH response implementation keeps the raw isoscalar (A^2/4) convention distinct from the physical equal-proton/equal-neutron response (R_A(0)=A^2); the factor 4 is applied once at the response-definition layer. The Python-only full Xe-131 Eq. (6) audit at v=800 km/s under the conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions passed 652 rows (500 open, 152 closed): maximum I6 relative difference 1.66367e-11, factor-four mapping residual 3.55679e-16, and physical/no-factor-four ratio residual 0. Thus the response-to-cross-section factor-four transfer is verified end-to-end within the Python implementation. The independent native Wolfram 652-row run and pointwise Mathematica/Python comparison remain pending. The natural-xenon target number uses the full nine-isotope abundance-weighted mean atomic mass, while the AFH response sum includes only the seven supported isotopes and does not renormalize their abundance.

The AFH-7/Hybrid-9 outputs are pre-detector nuclear-recoil spectra. The NEST paired-S1/2D response archive is a separate intermediate detector-response study. Neither result is an official waveform-level LZ selected PDF, background/profile likelihood, or 90% CL exclusion.

## 5. Current status matrix

| Work item | Audit status | Current boundary |
|---|---|---|
| Three-body kinematic limits and exact spatial (q) | PASS_WITH_NOTES | Inspected formula/code conventions are internally consistent; full parameter scan not claimed |
| AFH factor-four normalization | PASS_WITH_NOTES | Xe-131 native response comparison passes; Python-only 652-row full Eq. (6) factor-four ledger passes with mapping residual 3.55679e-16 and physical/no-factor-four ratio residual 0 | Independent native Wolfram 652-row run and Mathematica/Python pointwise comparison remain open |
| AFH-7/Hybrid-9 84-point spectra | PASS_WITH_NOTES | (10^{-5}) high-order summary passes; full high-order ZIP is external; not AFH-9 |
| Legacy AFH selected-point rate table | HISTORICAL | Reproducible old linear-(W^2) low-order result; do not mix with new threshold-(u^2) grid |
| GCN/JJ55 continuous spectra | PASS_WITH_NOTES | 84-point outputs exist; kernel-order check is (2.19\times10^{-4}); matched threshold-(u^2) rerun pending |
| High-energy nuclear-model tail comparison | PROVISIONAL | Broad GCN/JJ55 shifts exceed numerical error; Hybrid-9 comparison should be rerun at matched precision |
| Full Mathematica–Python (d\sigma_A/dE_R) | OPEN | Native AFH Xe-131 response-level PASS does not close the full Eq. (6) cross-section check |
| Official LZ detector likelihood | OPEN | No official 2D selected PDF/profile likelihood/90% CL exclusion |

## 6. Documentation records reviewed in this phase

The first-pass review covers the root and research navigation, the main AFH/natural-xenon report, the Eq. (6) kernel README and code, the AFH natural-xenon README and generator, the AFH response interpolation and phase-space audits, the GCN/JJ55 spectrum generator and metadata, the high-energy-tail report, the Figure 2 formula/status/result indices, and the LZ extended-NR README/bootstrap report.

This is a high-impact first batch, not a claim that all 106 research Markdown files have been scientifically reviewed. Remaining documents will be reviewed by topic in subsequent batches.

An additional cross-document status-reconciliation pass on 2026-11-16 updated Appendix D (natural-xenon coverage), Appendix E (historical selected-point versus current AFH-7 grid), Appendix F (numerical validation matrix and detector boundary), Appendix G (committed 16,807-row response grid), the missing-isotope appendix, the high-energy-tail appendix, the research decision register, the formula cross-reference, and the formula/status audit. These edits correct stale completion labels and preserve historical calculations as historical; they do not change physical inputs or recompute numerical outputs.

A second topic pass covered the LZ detector-response record set: the P0 closure report, public-input audit, NEST configuration provenance, event-response pilot, flat-band pilot, full-band drift audit, ER-tail bootstrap audit, energy-resolved black-tail audit, and the three-body response-selection audit. Their current summaries now distinguish completed public-candidate calculations from the still-open official-build, calibration-geometry, nuisance, background, and likelihood requirements. In particular, the local black-support 5-keV point-estimate gate is not a full-range 5-keV grid PASS; the event-weighted fold retains 1 keV as its numerical reference, and the ER empirical PDF still has zero support in the candidate's 2D cell. No detector or particle-physics numerical outputs were recomputed in this documentation pass.

A third consistency pass checked the Xe-131 AFH README, the Figure 2 Anand-response audit, the historical Eq. (6) calculation note, the native full-dsigma audit, the Mathematica/Python cross-check review, and the output archive index. The 2,401-node Xe-131 AFH response comparison is a verified response-level PASS. The Python-only v=800 km/s fixed-speed Xe-131 d-sigma job under the conditional width assumptions has completed and its artifact is archived; its 652-row factor-four ledger also passes end-to-end within Python (maximum mapping residual 3.56e-16, physical/no-factor-four ratio residual 0). The separate native Wolfram 652-row Eq. (6) run and pointwise Mathematica/Python comparator have **not** been executed, so no full-cross-section cross-code PASS is claimed. The older Eq. (6) note is now explicitly labelled as a historical snapshot, and the Xe-131 README distinguishes the AFH-7 84-point full-range grid from the old 28-row selected-sample file.

## 7. Next actions

1. Recompute GCN/JJ55 spectra with threshold-(u^2), common speed/kernel convergence criteria, and matching output metadata.
2. Recompute the high-energy-tail comparison and downstream GCN/JJ55 rate-level yields from the matched spectra.
3. Archive the full AFH-7/Hybrid-9 high-order outputs and the independent Numba implementation as native files or a versioned Release; do not leave the full output as checksum-only external provenance.
4. Complete the native Mathematica–Python full (I_6) and (d\sigma_A/dE_R) pointwise comparison.
5. Continue the detector-response audit without upgrading the current NEST proxy to an official LZ likelihood.
