# Figure 2 and natural-xenon results master index

**Source integration:** PR #45 merged into `main` via merge commit `15eb3a24e5295868ca208166a94c078fbc1747a7` (index updated locally for exact-mass recalculation)
**Follow-up:** PR #46, branch `docs/scientific-content-audit-20261116`, targeting `main`
**Updated:** 2026-11-17 (current exact-mass spectra and downstream LZ fold synchronized)
**Coverage:** 12 result groups; manifest contains the current files and checksums.

The [2026-11-13 index](three_body_results_master_index_2026-11-13.md) is retained as a historical snapshot. This index supersedes its statement that the full 16,807-row AFH seven-isotope response grid is checksum-only and not committed.

## Current additions

### 1. AFH v6.0 seven-isotope default-density response grid

Path: `research/afh_default_density_natural_xenon_halo/results/full_afh_v6_default_7_isotope_response/`

- Seven isotopes: Xe-128, 129, 130, 131, 132, 134, 136.
- Seven 2,401-node response tables and the combined 16,807-row response table.
- Seven source density matrices, metadata, isotope summary, and SHA-256 manifest.
- Exact spatial (q_A=\sqrt{2m_AE_R+E_R^2}); no PCHIP evaluation is used as the source of the new full-grid response.
- AFH-7 natural atom-fraction coverage: 0.998158; Xe-124/Xe-126 remain missing and are not renormalized away.

### 2. AFH-7 / Hybrid-9 84-point spectra with exact isotope masses

Path: `research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_ame2020_exact_2026-11-17/`

- Four benchmarks, four response scenarios and 84 recoil-energy points (1,344 rows).
- AME2020 atomic isotope masses converted to bare nuclear masses with CODATA-2022 constants and the AME electron-binding correction.
- Direct finite-sum AFH response at each exact isotope-specific spatial momentum; threshold-\(u^2\) mapping, 32 speed nodes and \(8\times8\times4\) internal quadrature.
- AFH-7 covers natural atom fraction 0.998158 without renormalization. Xe-124/Xe-126 are unavailable in AFH v6.0; Hybrid-9 uses labelled Helm fallback for those isotopes.
- Metadata and checksums are stored beside the spectra. The former approximate-mass spectra and detached high-order output directories have been removed.

### 3. Exact-mass convergence and derived LZ rate-level fold

- Mathematica Gauss, Mathematica `NIntegrate`, and independent Python phase-space comparisons use the exact Xe-131 mass; maximum Python vs `NIntegrate` relative difference is below \(1.6\times10^{-7}\) on open sample points.
- The fixed-speed and natural-xenon halo convergence CSVs are in `research/three_body_natural_xenon/独立验证/` and `research/three_body_calculation_and_validation/mathematica_halo_notebook/`.
- GCN/JJ55 four-benchmark natural-xenon spectra were recalculated using the same AME2020/CODATA-2022 nuclear masses. Their 84-point output and convergence checks are in `research/three_body_calculation_and_validation/results/natural_xenon_continuous_spectrum_ame2020_exact/`.
- LZ 2026 one-dimensional NR-efficiency folding and AFH/GCN/JJ55 high-energy tail comparisons were rerun from the exact-mass spectra. They remain rate-level diagnostics, not detector likelihoods or exclusion limits.

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


## Exact isotope mass update (2026-11-17)

All current natural-xenon spectra and dependent rate-level folds listed here use AME2020 isotope atomic masses converted to bare nuclear masses with CODATA-2022 constants and the AME electron-binding correction. The 2026-11-14 A*u spectrum and high-order output directories were removed; their exact-mass replacement is in
esearch/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_ame2020_exact_2026-11-17/. The LZ efficiency fold was rerun from that input and is under
esearch/lz_detector_response/lz_2026_extended_nr/afh7_hybrid9_rate_level_yields/. The cross-model GCN/JJ55 spectra are being recomputed under the same AME2020 mass scheme.


Historical A*u AFH full-grid outputs were removed on 2026-11-17 after the exact-mass AFH and GCN/JJ55 spectra and LZ rate-level folds were recomputed. The current outputs, rather than earlier numerical rows in older appendices, are authoritative for the AME2020/CODATA-2022 mass scheme.
