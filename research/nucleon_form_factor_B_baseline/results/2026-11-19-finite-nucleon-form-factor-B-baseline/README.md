# Archived outputs: finite nucleon form factors in the AFH B baseline

**Archive status:** native outputs preserved; source artifact digest and every extracted file are checked by RUN_MANIFEST.json and SHA256SUMS.

## Provenance and dependency chain

- The upstream halo input is the PR #78 artifact from [workflow run 44560087038](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44560087038), artifact ID 14551462445, source commit 9ca1801cdded7002c93776f8a0f5bce894135356.
- PR #80's B-baseline workflow completed successfully in [run 44565778594](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44565778594), source commit 42309444866454bdfc27f45316bd3628815209fe, artifact ID 14551033657.
- The B workflow consumed the halo artifact from run 44560087038. The later successful PR #74 integration rerun (run 44568592064) has byte-identical extracted halo payloads and is preserved in the linked halo archive.
- PR #74 is now merged to main as 070dc89cc58699633d0009c1fbaea7fa400ee337. PR #82 integrates the B implementation and these permanent outputs into main.

## Adopted B prescription

The archived implementation uses finite nucleon Dirac–Pauli form factors \(F_1(t_N)\), \(F_2(t_N)\) multiplying the finite-size AFH \(W_M(y_A)\) response:

\[
Q_A^2=2m_AE_R+E_R^2,\qquad t_N=-Q_A^2,
\]
\[
F_M(t_N)=c_M(t_N)/3,\qquad \mathcal C_N(Q_A^2)=|F_M(t_N)|^2.
\]

The form factors use the exact spatial nuclear transfer \(Q_A\); \(q_{NR}\) is not substituted. The AFH finite-size response is retained, with no point-nucleus replacement.

Two strange-current scenarios are kept separate and are not averaged:

1. sufian2017_unit_current — primary unit-strange-current input.
2. alexandrou2020_charge_weighted_converted — published charge-weighted input converted to the unit-current convention.

The Ye2020 electromagnetic coefficient covariance is propagated with 3,000 correlated draws using seed 20261119. Strange-lattice uncertainties are not sampled in this first pass.

## Archived numerical results

Each scenario contains baseline and higher-order results on 208 recoil points, with 1,456 isotope-level rows per table.

| Quantity | Sufian unit-current | Alexandrou converted |
|---|---:|---:|
| Maximum absolute B/A full-rate shift | 56.4346% | 58.2429% |
| Maximum absolute full-vs-\(I(D)\) error in B | 0.3528% | 0.3528% |

The higher-order B quadrature comparison gives maximum natural-xenon full-rate and \(I(D)\)-rate shifts of order \(9.89\times10^{-6}\%\) and \(1.71\times10^{-5}\%\), respectively. The pointwise comparison and summary JSONs are preserved for both strange-current scenarios.

## Files

- source-artifact-pr80.zip: original successful PR #80 Actions artifact.
- extracted/B-baseline/: baseline outputs for both strange-current scenarios.
- extracted/B-highorder/: higher-order outputs and metadata for both scenarios.
- extracted/B-quadrature-comparison/: pointwise quadrature comparisons and summary JSONs.
- RUN_MANIFEST.json: source run IDs, upstream halo lineage, artifact ID/digest, calculation summary, and per-file inventory.
- SHA256SUMS: checksums for the source ZIP, all extracted files, this README, and the run manifest.

## Scientific scope

This is the rate-level B baseline: finite nucleon \(F_1,F_2\) correction multiplied by the AFH finite-size charge response. Detector response, efficiency, energy resolution, exposure, cuts, and likelihood are not included. The quoted B/A shifts are specific to this benchmark and the two stated strange-current inputs.


## Final archive integrity check

The final extraction, run-manifest generation, and complete SHA-256 verification passed in [archive workflow run 44579411941](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44579411941). The manifest inventory lists the README, original PR #80 source ZIP, and 19 extracted native files. `SHA256SUMS` additionally covers `RUN_MANIFEST.json` itself (21 checksum entries total). The manifest is deliberately excluded from its own embedded inventory to avoid a self-referential digest.
