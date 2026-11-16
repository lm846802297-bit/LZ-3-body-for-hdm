# LZ 2026 extended NR/ER detector-response archive

**Archive status:** reproducible intermediate detector-response diagnostics. The calculations and archived outputs are reproducible within their stated scopes; they are not an official LZ waveform-level selected-event PDF or a final likelihood.

## Purpose and current decision

This study connects the three-body natural-xenon recoil spectra to public LZ 2026 detector-response information. It audits the public NEST release/configuration candidate, NR and ER response bands, event-level response, two-dimensional response folding, selection-stage closure, and paired Parametric/Full S1 migration.

- The pinned public NEST candidate is commit `541b6430dae6ea289cf110c99f174a9187f7fdee`, using `LZ_Detector_2024::SetEFT2024Configuration()`. It is a well-supported public candidate, not proof of the exact collaboration production build.
- Keep the **1-keV full-range grid** as the numerical reference. The independent full-range 1/5-keV study passes its accepted-rate comparison but fails the 1% 2D mean-map TV gate for both EFT2024 (1.4812%) and Table S5 (1.4681%). The restricted black-support 1/5-keV result and the 0.5-keV high-tail refinement do not override this full-range result.
- The paired S1 production contains ten independent seeds and 4.7 million unique events. Its follow-up uses 100,000 paired seed-cluster bootstrap replicates and all 1,024 within-seed mode-label swaps. For the black 360-keV WS-ROI case, the point TVs are 0.943% (GCN) and 0.932% (JJ55), but the bootstrap percentile upper endpoints exceed 1%; no robust 1% equivalence claim is supported.
- The red 200-keV WS-ROI rows show a small but statistically detectable mode-shape difference (exact p = 0.00195; Holm-adjusted p = 0.03125 across all 16 tests). Failure to reject for other rows is not evidence of equivalence.
- The NEST response remains an intermediate proxy. DAQ trigger, waveform-level S1 timing, SS reconstruction and data-analysis cuts, official fiducial-volume and Skin/OD selections, live-time migration, detector-systematic covariance, backgrounds, and profile likelihood are not complete.

## Navigation: principal reports

| Question | Canonical record |
|---|---|
| Overall response-selection status and limitations | [Three-body response-selection audit](LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md) |
| Two-dimensional three-body response fold | [NR 2D response-fold report](LZ_2026_THREE_BODY_NR_2D_RESPONSE_FOLD_REPORT.md) |
| Differential-rate event-weighted fold and grid checks | [Event-weighted fold audit](LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md) |
| Energy-resolved selection bridge and black-tail MC uncertainty | [Energy-resolved selection audit](LZ_2026_ENERGY_RESOLVED_SELECTION_MC_AND_BLACK_TAIL_AUDIT.md) |
| Paired S1 seed uncertainty and exact randomization | [Paired S1 bootstrap audit](LZ_2026_PAIRED_S1_ENSEMBLE_BOOTSTRAP_AUDIT_2026-11-16.md) |
| Public NEST configuration and parameter-family provenance | [NEST configuration provenance](LZ_2026_NEST_CONFIGURATION_PROVENANCE.md) |
| NEST source/release lineage | [NEST release-lineage audit](LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md) |
| NR/ER candidate response bands and conditional PDFs | [NR/ER response candidate report](LZ_2026_NR_ER_FULL_RESPONSE_CANDIDATE_REPORT.md) |
| ER candidate-tail support | [ER tail-support audit](LZ_2026_ER_TAIL_SUPPORT_AUDIT.md) |
| Fig. S2 rate-level stage closure | [Selection-stage closure](LZ_2026_SELECTION_STAGE_RATE_LEVEL_CLOSURE.md) |
| Public event-data archive | [HEPData v1 archive audit](HEPDATA_V1_ARCHIVE_AUDIT.md) |
| WS2024 detector-class source comparison | [WS2024 detector cross-check](LZ_WS2024_DETECTOR_CROSSCHECK.md) |
| NR full-band parameter sensitivity | [NR full-band sensitivity audit](LZ_2026_NR_FULL_BAND_PARAMETER_SENSITIVITY_AUDIT.md) |

Historical one-energy and flat-band pilots are retained for provenance, not as the current full-response result: [248-keV event pilot](LZ_2026_NR_EVENT_LEVEL_PILOT_248KEV.md), [event-response pilot](LZ_2026_NR_EVENT_RESPONSE_PILOT.md), and [flat-band pilot](LZ_2026_NR_FLAT_BAND_PILOT.md).

## Implementation map

The code is kept in the parent study directory so existing workflow paths and Python imports remain stable. This is intentional; do not move these entry points as a cosmetic cleanup.

| Layer | Location |
|---|---|
| C++ NEST event-response implementations | [cpp/](../cpp/) |
| Python calculation, folding, and audit entry points | [parent study directory](../) |
| Python regression tests | [tests/](../tests/) |
| NEST candidate and Table S5 parameter inputs | `lz_2026_nest_eft2024_configuration_candidate.json`, `lz_2026_nest_nr_mean_yield_parameters.json`, `lz_2026_nr_yield_params_s5.txt` |
| Main selection audit | `LZ_2026_THREE_BODY_RESPONSE_SELECTION_AUDIT.md` |

Key entry points include `../converge_lz_2026_three_body_energy_grid.py`, `../fold_lz_2026_three_body_2d_response.py`, `../fold_lz_2026_three_body_event_weighted_response.py`, `../fold_lz_2026_paired_s1_mode_2d_response.py`, and `../paired_s1_ensemble_tv_bootstrap.py`.

## Machine-readable archives

- `paired_s1_independent_seeds_2026-11-15/`: ten per-seed fold maps, per-seed rate and split-half summaries, ensemble maps, binning-stability outputs, the four-benchmark upper-tail audit, run manifest, and checksums. The raw event CSVs remain in the immutable Actions artifact; `raw_event_artifact_SHA256SUMS.txt` preserves its 75-file manifest. See [archive README](paired_s1_independent_seeds_2026-11-15/ARCHIVE_README.md).
- `paired_s1_bootstrap_2026-11-16/`: bootstrap summary, exact paired-randomization table, leave-one-seed-out table, reproduction-closure table, metadata, and SHA-256 manifest. See [bootstrap archive README](paired_s1_bootstrap_2026-11-16/README.md).
- `rate_level_event_yields/`: earlier GCN/JJ55 efficiency-weighted rate-level event yields.
- `afh7_hybrid9_rate_level_yields/`: AFH-7 and Hybrid-9 rate-level folds; Hybrid-9 is a labelled Helm fallback for Xe-124/Xe-126, not a full AFH-9 calculation.

## Reproduction and validation

The paired S1 bootstrap audit gives the exact reproduction command, RNG seed, pinned NEST commit, and input provenance. From the repository root:

```bash
python -m unittest research.lz_detector_response.tests.test_paired_s1_ensemble_tv_bootstrap -v
python research/lz_detector_response/paired_s1_ensemble_tv_bootstrap.py \
  --seed-root research/lz_detector_response/lz_2026_extended_nr/paired_s1_independent_seeds_2026-11-15 \
  --out-dir /tmp/lz-s1-bootstrap \
  --n-bootstrap 100000 \
  --rng-seed 2026111601
```

The dedicated workflow is [lz-2026-paired-s1-bootstrap.yml](../../../.github/workflows/lz-2026-paired-s1-bootstrap.yml). Other production and audit workflows are grouped by task under `.github/workflows/lz-2026-*.yml`; the exact workflow used by each result is linked in its report.

## Interpretation rules

1. GCN and JJ55 are nuclear-response spectra; they are not alternative NEST NR-yield configurations.
2. EFT2024 and the rounded Table S5 parameter vector are distinct response hypotheses; do not silently mix their inputs.
3. A rate-level Fig. S2 efficiency fold is not the same object as a two-dimensional S1c/log10(S2c) response map.
4. A NEST/WS-ROI map is not the official LZ selected-event PDF. Do not multiply the full Fig. S2 efficiency into an existing 2D map as an extra scalar correction.
5. A successful software workflow validates only the assertions it executes. It does not by itself validate the physical model or authorize a final likelihood.