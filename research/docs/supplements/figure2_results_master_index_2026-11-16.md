# Figure 2 and natural-xenon results master index

**Current source:** `main` at `58f97ab27e104cdb65c3ce542bb3d7f1bc1c2648`  
**Updated:** 2026-11-16  
**Machine-readable manifest:** [figure2_results_master_index_2026-11-16.json](figure2_results_master_index_2026-11-16.json)  
**Coverage:** 12 result groups; 87 file entries with SHA-256 and byte sizes.

The [2026-11-13 index](figure2_results_master_index_2026-11-13.md) is retained as a historical snapshot. This index supersedes its statement that the full 16,807-row AFH seven-isotope response grid is checksum-only and not committed.

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
- The independent native Wolfram 652-row execution and pointwise Mathematica/Python full-cross-section comparison remain pending. The 2,401-node Xe-131 response-level PASS does not substitute for that cross-code gate.

## Numerical comparison caveat

The GCN/JJ55 84-point spectra currently use the legacy linear-(W^2), (8×8×4) kernel; their (16×16×8) spot-check reaches (2.18895×10^{-4}) maximum kernel-order difference across the four benchmark metadata files. The AFH-7/Hybrid-9 spectra use threshold-(u^2). At the production 24-speed-node setting, the final internal-kernel increment is (5.96430×10^{-10}); the separate 12-speed-node comparison is (6.02323×10^{-10}). The cross-model comparison is therefore not yet a matched-precision comparison. GCN/JJ55 should be recomputed with threshold-(u^2) before final precision claims, especially for the 0.66–1.16% Hybrid-9 shifts.

The historical selected-point AFH rates are retained and reproducible, but their old low-order linear-(W^2) integration differs from the new AFH-7 threshold-(u^2) grid by about 230–255 ppm at common points. Do not mix the historical selected-point table with the current full-grid result.

## Scope boundaries

- AFH-7 is not AFH-9: Xe-124 and Xe-126 lack AFH v6.0 default-density matrices.
- Hybrid-9 is AFH-7 plus a Helm fallback for those two isotopes; it is a labelled diagnostic.
- The native Mathematica Xe-131 response-level comparison is distinct from the Python-only full Eq. (6) result above; neither by itself closes the native-Wolfram/Python full-cross-section cross-code gate.
- The LZ NEST response archive remains an intermediate detector-response diagnostic, not an official waveform-level selected PDF, profile likelihood or 90% CL exclusion.

## Historical index

The original nine-group, 60-file index is preserved in [figure2_results_master_index_2026-11-13.md](figure2_results_master_index_2026-11-13.md) and its JSON companion. It remains useful for tracing the earlier selected-point and response-level milestones, but its external-input table is superseded for the AFH-7 response grid.
