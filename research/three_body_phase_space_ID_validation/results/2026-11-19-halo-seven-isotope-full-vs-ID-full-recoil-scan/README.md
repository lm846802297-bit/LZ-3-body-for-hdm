# Archived outputs: halo-folded full three-body vs I(D) validation

**Archive status:** native outputs preserved; source artifact digests and every extracted file are checked by RUN_MANIFEST.json and SHA256SUMS.

## Provenance and dependency chain

- **PR #78 original workflow:** run [44560087038](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44560087038), source commit 9ca1801cdded7002c93776f8a0f5bce894135356, artifact ID 14551462445.
- **PR #74 final integration rerun:** run [44568592064](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44568592064), source commit b6b1452b96c5e4697410c92a8ad3e4c358eed80c, artifact ID 14555201585. This run completed successfully after the PR #74 integration branch incorporated the PR #78 work.
- The PR #78 original artifact and the PR #74 final rerun have different ZIP-container SHA-256 values, while all nine extracted member files are byte-identical. Both original ZIPs are retained here; the extracted canonical payload is from the final integration rerun.
- PR #74 was merged into main as 070dc89cc58699633d0009c1fbaea7fa400ee337. PR #74 includes the PR #78 seven-isotope halo-validation dependency.

## Calculation and numerical record

Benchmark: \(m_{\chi_1}=1\,\mathrm{TeV}\), \(m_s=300\,\mathrm{keV}\), \(\Delta m=10\,\mathrm{MeV}\), \(m_V=5\,\mathrm{GeV}\). The truncated Standard Halo Model uses \(v_0=220\), \(v_E=232\), and \(v_{\rm esc}=544\,\mathrm{km/s}\).

The AFH v6.0 calculation includes Xe-128, 129, 130, 131, 132, 134, and 136. These seven isotopes cover 0.998158 of the natural atom fraction; the abundances are not renormalized. Xe-124 and Xe-126 are omitted because no AFH v6.0 default-density responses are supplied for them.

- 208 recoil-energy points from 5 to 800 keV, including 1-keV refinement from 180 to 320 keV and anchors at 248 and 267 keV.
- 1,456 isotope/recoil rows in each seven-isotope table.
- Baseline quadrature: halo speed order 24 and internal \((n_W,n_z,n_\phi)=(8,4,4)\).
- Higher-order quadrature: halo speed order 32 and internal \((12,4,4)\).
- On the archived higher-order natural-xenon grid, the maximum absolute full-integral versus \(I(D_{NR})\) rate difference is approximately 0.352762%.
- The baseline-to-higher-order active-region rate shifts are below \(2\times10^{-5}\%\) for the full natural-xenon rate and below \(2\times10^{-5}\%\) for the \(I(D)\) rate. The convergence summary reports zero support mismatches.

## Files

- source-artifact-pr78-original.zip: original PR #78 Actions artifact.
- source-artifact-pr74-final-rerun.zip: final successful PR #74 integration-run artifact.
- extracted/halo-seven-isotope-baseline/: baseline CSVs and metadata.
- extracted/halo-seven-isotope-highorder/: higher-order CSVs and metadata.
- extracted/halo-seven-isotope-quadrature-comparison/: pointwise quadrature comparison and convergence summary.
- RUN_MANIFEST.json: source run IDs, commits, artifact IDs/digests, payload equivalence, calculation summary, and per-file inventory.
- SHA256SUMS: checksums for both source ZIPs, all extracted files, this README, and the run manifest.

## Scientific scope

This is a halo-folded rate-ratio and quadrature-convergence record. It is not a detector-level LZ prediction: detector response, exposure, efficiency, energy resolution, cuts, and likelihood are not included. The full-versus-\(I(D)\) comparison is the DM-side approximation check on the same halo and AFH nuclear weighting.


## Final archive integrity check

The final extraction, run-manifest generation, and complete SHA-256 verification passed in [archive workflow run 44579411941](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44579411941). The manifest inventory lists the README, two original source ZIPs, and nine extracted native files. `SHA256SUMS` additionally covers `RUN_MANIFEST.json` itself (13 checksum entries total). The manifest is deliberately excluded from its own embedded inventory to avoid a self-referential digest.
