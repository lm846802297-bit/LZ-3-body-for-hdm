# Figure 2 and natural-xenon results master index

**Source integration:** PR #45 merged into `main` via merge commit `15eb3a24e5295868ca208166a94c078fbc1747a7` (201 research/audit commits preserved)
**Follow-up:** PR #46, branch `docs/scientific-content-audit-20261116`, targeting `main`
**Updated:** 2026-11-16 (native full-grid and higher-order comparisons synchronized)
**Coverage:** 13 result groups; 98 file entries with SHA-256 and byte sizes.

The [2026-11-13 index](three_body_results_master_index_2026-11-13.md) is retained as a historical snapshot. This index supersedes its statement that the full 16,807-row AFH seven-isotope response grid is checksum-only and not committed.

## Current additions

### 1. AFH v6.0 seven-isotope default-density response grid

Path: `research/afh_default_density_natural_xenon_halo/results/full_afh_v6_default_7_isotope_response/`

- Seven isotopes: Xe-128, 129, 130, 131, 132, 134, 136.
- Seven 2,401-node response tables and the combined 16,807-row response table.
- Seven source density matrices, metadata, isotope summary, and SHA-256 manifest.
- Exact spatial (q_A=\sqrt{2m_AE_R+E_R^2}); no PCHIP evaluation is used as the source of the new full-grid response.
- AFH-7 natural atom-fraction coverage: 0.998158; Xe-124/Xe-126 remain missing and are not renormalized away.

### 2. AFH-7 / Hybrid-9 84-point full-range spectra

Path: `research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14/`

- 84 recoil points from 5 to 800 keV, four benchmarks and four response scenarios; 1,344 spectrum rows.
- Direct finite-sum AFH response at each exact isotope-specific spatial momentum.
- Threshold-(u^2) phase-space mapping, 24 speed nodes and (6\times6\times3) internal quadrature.
- Pre-detector theory rates. “Continuous” means a full-range sampled recoil grid, not an analytic continuum or a 1-keV grid.

### 3. AFH-7 / Hybrid-9 high-order convergence audit

Path: `research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_full_grid_highorder_2026-11-14/`

- 1,726 kinematically open and 1,298 closed isotope/benchmark/recoil points.
- (24\times8\times8\times4) final quadrature.
- Maximum baseline-to-final spectrum difference (6.46772\times10^{-6}), below (10^{-5}).
- The full 1,344-row high-order output is a 736,245-byte external ZIP with SHA-256 `e55442d3ad4289dfd6c16e8e6cdb43d669561df074beddefcf87e8d1024f3471`. The ZIP contents are not committed; only the audit report, metadata and summary CSVs are included in this manifest.

### 4. Python-only full Xe-131 Eq. (6) and AFH factor-four audit

- Workflow [run 43591097068](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43591097068) completed successfully; head commit `c2d0590114ad0bf90fc741278e21868af52b65cf`; artifact [14112736343](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43591097068) is retained.
- The v=800 km/s fixed-speed Xe-131 calculation covers 652 rows (500 open, 152 closed) and 16 high-order anchors. Maximum I6 relative difference: 1.66367e-11; AFH factor-four mapping residual: 3.55679e-16; physical/no-factor-four ratio residual: 0.
- This is a Python-only full Eq. (6) and factor-four PASS_WITH_NOTES under the conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions. It is not a natural-xenon halo fold.
- The independent native Wolfram 652-row execution and pointwise Mathematica/Python full-cross-section comparison are now complete and archived in Section 5 below; the 2,401-node response-level PASS remains a distinct earlier validation layer.

### 5. Native Mathematica/Python full Xe-131 Eq. (6) cross-code comparison

Path: `research/afh_default_density_xe131/output/full_dsigma_mathematica/`

- Native Wolfram 14.2.0 run and independent Python recomputation: 652 rows, 4 benchmarks, 163 recoil energies per benchmark; 500 open and 152 closed phase-space points.
- Fixed speed 800 km/s, pole-width scheme, threshold-\(u^2\) mapping, \(16\times16\times8\) quadrature; conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions.
- Maximum relative differences: \(I_6=1.33872\times10^{-12}\), physical/no-factor-four \(d\sigma=1.33872\times10^{-12}\), AFH response \(3.36051\times10^{-16}\), factor-four mapping residual \(4.30300\times10^{-16}\).
- Mathematica/Python unit-conversion identities are checked separately at \(2\times10^{-12}\); observed residuals are \(3.35\times10^{-16}\) and 0. The cross-code converted-\(d\sigma\) difference is \(1.33872\times10^{-12}\) and uses the same \(2\times10^{-7}\) observable tolerance as unconverted \(d\sigma\).
- Corrected comparison JSON reports **PASS**; row-level comparison CSV and SHA-256 checksums are committed. This is fixed-speed Xe-131, not a natural-xenon halo fold or LZ detector likelihood.
- A separate higher-order Green benchmark at 200, 300 and 500 keV (48×40×24) reports PASS at all three open points. Maximum I6/dσ/converted-dσ cross-code differences are 1.04e-12 / 1.04e-12 / 1.04e-12; low-to-high-order change is at most 6.70e-12. CSV, metadata, comparison and checksums are archived in the same directory.

## Numerical comparison caveat

The GCN/JJ55 84-point spectra currently use the legacy linear-(W^2), (8×8×4) kernel; their (16×16×8) spot-check reaches (2.18895×10^{-4}) maximum kernel-order difference across the four benchmark metadata files. The AFH-7/Hybrid-9 spectra use threshold-(u^2). At the production 24-speed-node setting, the final internal-kernel increment is (5.96430×10^{-10}); the separate 12-speed-node comparison is (6.02323×10^{-10}). The cross-model comparison is therefore not yet a matched-precision comparison. GCN/JJ55 should be recomputed with threshold-(u^2) before final precision claims, especially for the 0.66–1.16% Hybrid-9 shifts.

The historical selected-point AFH rates are retained and reproducible, but their old low-order linear-(W^2) integration differs from the new AFH-7 threshold-(u^2) grid by about 230–255 ppm at common points. Do not mix the historical selected-point table with the current full-grid result.

## Scope boundaries

- AFH-7 is not AFH-9: Xe-124 and Xe-126 lack AFH v6.0 default-density matrices.
- Hybrid-9 is AFH-7 plus a Helm fallback for those two isotopes; it is a labelled diagnostic.
- The native Mathematica Xe-131 response-level comparison and the full fixed-speed Xe-131 Eq. (6) cross-code comparison are distinct validation layers; the latter passes for the 652-row, 800 km/s, conditional pole-width benchmark, but neither result is a natural-xenon halo fold or LZ likelihood.
- The LZ NEST response archive remains an intermediate detector-response diagnostic, not an official waveform-level selected PDF, profile likelihood or 90% CL exclusion.

## Historical index

The original nine-group, 60-file index is preserved in [three_body_results_master_index_2026-11-13.md](three_body_results_master_index_2026-11-13.md) and its JSON companion. It remains useful for tracing the earlier selected-point and response-level milestones, but its external-input table is superseded for the AFH-7 response grid.
