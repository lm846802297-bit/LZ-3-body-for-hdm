# AFH default-density natural-xenon halo fold

This directory archives both the historical selected-point natural-xenon halo fold and the current AFH-7/Hybrid-9 84-point full-range recoil-grid spectra using the AFH v6.0 built-in sdgXeA default density responses. `main` is the canonical archive; old development branches are retained for provenance only.

## Directory map

- `input/`: isotope weights, AFH density-matrix extracts, historical 28-point PCHIP samples, and 56-point direct exact-q selected-point inputs.
- `audit/`: AFH response-interpolation audit, high-energy nuclear-model sensitivity, and source-level checks.
- `tests/`: regression tests for AFH response generation, Hybrid-9 kinematics, target normalization, and the high-energy tail audit.
- `output/`: generated isotope-response grids and selected-point direct exact-q fold tables.
- `results/`: historical selected-point rates, the committed 16,807-row AFH response grid, 84-point AFH-7/Hybrid-9 spectra, convergence summaries, audit reports, and manifests.
- Study-root Python files remain stable calculation and validation entry points; their paths are kept unchanged for existing workflows and documented commands.

Run the regression suite from the repository root:

~~~bash
python -m unittest discover -s research/afh_default_density_natural_xenon_halo/tests -p 'test_*.py' -v
~~~

- Four Figure-2 benchmark parameter sets are retained.
- Each available isotope uses its own NIST-derived nuclear mass, AFH response sample and three-body threshold.
- Natural atomic abundances are used without renormalizing the seven available isotopes.
- The truncated Standard Halo Model is the baseline; the untruncated Maxwell-Boltzmann result is only a high-speed-tail diagnostic.
- Rates are before detector efficiency, resolution, exposure, cuts and likelihood.
- The historical 28-row AFH response sample file evaluates the 2401-node PCHIP grid at exact spatial momenta q=sqrt(2*m_A*E_R+E_R^2); it is not a direct finite-sum evaluation at every off-grid q. The newer 84-point spectrum runner evaluates the AFH finite sum directly at each exact isotope-specific q. q_NR=sqrt(2*m_A*E_R) remains a separate small-recoil approximation.

See results/NATURAL_XENON_HALO_FOLD_AUDIT.md for assumptions, results and convergence checks.

Run from the repository root:

    python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py

The script imports research/three_body_calculation_and_validation/eq6_kernel.py and reads the compact response samples and NIST isotope weights in this directory. The default response-q mode is exact_spatial. The optional nr_approx mode intentionally rejects these exact-q samples unless matching R_A values are supplied. The legacy_exact option remains as a backward-compatible alias for exact_spatial. The hash of the full AFH response input used to extract the samples is recorded in results/afh_response_input_sha256.txt.

The q-convention audit is archived in results/natural_xenon_q_convention_audit.csv, results/xe131_afh_response_shift_NR_vs_exact.csv and results/q_convention_audit_summary.json. The exact-spatial-q mode is rerun in CI and compared against all 98 isotope contributions and 14 total-rate rows; see the latest exact-spatial reproduction artifact and comparison summary.

## AME2020 seven-isotope extension — current research status

The seven-isotope AME2020 response-grid extension is now archived on `main`. The historical branch `research/ame2020-mass-exact-spatial-mainline` is 337 commits behind `main` and has no unique commits; it is not the current source of truth. The extension contains the seven AFH v6.0 default-density xenon matrices and their 2401-node response grids:

- Isotopes: Xe-128, Xe-129, Xe-130, Xe-131, Xe-132, Xe-134, Xe-136.
- Native response rows: \(7\times2401=16807\).
- Matrix and response checksums: `output/afh_default_xenon_responses/SHA256SUMS.txt`.
- Generator: `run_afh_default_xenon_responses.py`.
- Independent selected-point high-precision check:
  `verify_afh_selected_q_mpmath.py`.
- Detailed failure and interpolation audit:
  `audit/AFH_RESPONSE_INTERPOLATION_AUDIT.md`.

A key distinction is now explicit: the historical 28-row
`input/afh_response_samples.csv` contains PCHIP interpolants from the
historical 2401-node grid. It does not contain direct AFH finite-sum
evaluations at the off-grid exact spatial momenta. The regenerated PCHIP
values reproduce that historical file to \(1.19\times10^{-9}\), while
direct exact-q evaluation can differ from PCHIP by up to \(8.91\times10^{-3}\)
at a selected point (Xe-128, 542 keV). An independent 60-digit mpmath
finite-sum evaluation confirms the direct response at the selected NIST-q
points.

**The legacy seven-isotope AME2020 fold script**
`run_ame2020_natural_xenon_halo_fold.py` writes the legacy
`output/ame2020_full_response/` tables when run. These are PCHIP-based
diagnostics, not the committed direct exact-q output or the primary rate result.

The selected-point precision calculation has since been completed by
`run_ame2020_direct_exactq_natural_xenon_halo_fold.py`. It consumes the
56-point direct exact-q response table and writes the native outputs under
`output/ame2020_direct_exactq_fold/`; the calculation, convergence checks,
and output manifests are documented in the following section. The older
PCHIP-based Xe-131 partial-rate and hybrid tables remain historical
diagnostics and must not be cited as direct exact-q predictions.

The 56-point direct exact-q response input and its 14 selected-point halo fold remain a selected-point calculation. A separate full-grid runner now evaluates the AFH finite sum directly at all 84 recoil points for all seven AFH-supported isotopes; see the next section. Neither calculation is a detector-level LZ likelihood. Passing response-grid generation or historical PCHIP reproduction alone does not establish detector-level predictions.

AFH v6.0 still has no built-in default-density matrices for Xe-124 and Xe-126.
The seven-isotope AFH result therefore covers 0.998158 of the natural atom
fraction without renormalization; the missing-isotope \(A^2\) values remain
a coherent-charge ceiling only, not an AFH central prediction.


## AFH-7/Hybrid-9 84-point full-range recoil-grid spectra (2026-11-14)

The full seven-isotope AFH response grid and the corresponding natural-xenon recoil-grid calculation are now committed on `main`.

- Response archive: `results/full_afh_v6_default_7_isotope_response/`
  - seven isotope density matrices;
  - seven 2,401-node response tables;
  - combined 16,807-row response table;
  - metadata and SHA-256 manifest.
- Spectrum runner: `run_afh7_hybrid9_continuous_spectrum.py`.
- Spectrum archive: `results/afh7_hybrid9_continuous_2026-11-14/`
  - 84 recoil-energy points from 5 to 800 keV;
  - four particle benchmarks and four response scenarios (1,344 spectrum rows);
  - isotope-level kernel integrals, response-model comparison, quadrature checks, metadata and checksums.
- The response is evaluated by the AFH finite sum at each exact isotope-specific spatial (q); the old 28-row PCHIP sample table is not used as the full-grid response source.
- The committed baseline uses threshold-(u^2) integration, 24 speed nodes and (6\times6\times3) internal quadrature.
- The separate high-order audit reports a maximum baseline-to-final spectrum difference of (6.47\times10^{-6}), below its (10^{-5}) acceptance threshold. Its final (24\times8\times8\times4), 1,344-row high-order archive is currently external (736,245 bytes; SHA-256 `e55442d3ad4289dfd6c16e8e6cdb43d669561df074beddefcf87e8d1024f3471`); only the audit summary is committed.

The 84-point output is a grid-sampled full-range spectrum, not an analytic continuum or a 1-keV recoil grid. AFH-7 covers natural atom fraction 0.998158 without renormalization. Xe-124/Xe-126 remain absent from the official AFH default-density matrices. Hybrid-9 uses Helm only for those two missing isotopes; it is not a full AFH-9 prediction.

## AME2020 direct exact-q recalculation (2026-11-12)

The selected-point seven-isotope natural-xenon halo fold has now been recomputed locally using the 56 archived direct AFH finite-sum responses at exact spatial q, for both NIST and AME2020 nuclear masses. **No GitHub Actions / CI was used.**

- Report: [AME2020 direct exact-q recalculation](results/AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md)
- Primary response: direct exact-q; PCHIP retained only as a diagnostic.
- NIST/PCHIP historical total-rate reproduction: maximum relative difference 3.432e-12.
- Speed quadrature 32 vs 64 nodes: maximum total-rate difference 3.303e-6.
- Kernel quadrature 8x8x4 vs 16x16x8: maximum difference 2.108e-4 over 21 anchor checks.
- Replacing PCHIP by direct exact-q changes the selected natural-xenon total rates by at most 15.995 ppm (NIST) / 15.999 ppm (AME2020).
- Xe-131-only hybrid correction, with other isotope terms held at the historical NIST/PCHIP baseline: maximum absolute total-rate shift 15.277 ppm. This is a hybrid diagnostic, not a full AME2020 prediction.

The full local numerical bundle includes 392 kernel/halo integrals, 784 isotope contributions, 112 rate summaries, convergence tables, metadata and SHA-256 manifest. It is not part of the continuous recoil spectrum or detector-level LZ likelihood. Xe-124 and Xe-126 remain unsupported by the AFH v6.0 default density matrices; the seven-isotope abundance coverage is 0.998158 without renormalization.


### Local runner and native numerical archive

The selected-point AME2020 direct exact-q calculation is archived as native source and data files (not as a ZIP in the repository):

- Runner: `run_ame2020_direct_exactq_natural_xenon_halo_fold.py`
- Local validator: `validate_ame2020_direct_exactq_outputs.py`
- 56-point exact-q input: `input/afh_selected_exact_q_responses.csv`
- 392 kernel/halo integrals and 784 isotope contributions: `output/ame2020_direct_exactq_fold/`
- Output manifest: `output/ame2020_direct_exactq_fold/SHA256SUMS.txt`
- Bundle manifest: `results/AME2020_DIRECT_EXACT_Q_SHA256SUMS.txt`
- Full calculation report: `results/AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md`

The calculation and numerical acceptance were performed locally; this runner is not a self-hosted GitHub Actions runner. The selected-point results are not a continuous recoil spectrum or a detector-level LZ prediction.


## Phase II: high-energy candidate-window nuclear-model sensitivity

The candidate-window tail (E_R=225\text{--}269.9\,\mathrm{keV}) has been integrated against the LZ 2026 one-dimensional final-ROI efficiency, using the 2.84 tonne-year exposure. The product of the piecewise-linear rate and efficiency is integrated analytically on the union of their knots.

- Runner: `audit/audit_high_energy_tail_model_sensitivity.py`
- Tests: `tests/test_high_energy_tail_model_sensitivity.py`
- Output: `results/high_energy_tail_model_sensitivity_2026-11-14.csv`
- Full interpretation and model-scope boundaries:
  [09H — high-energy tail nuclear-model sensitivity](../docs/appendices/09H_high_energy_tail_nuclear_model_sensitivity.md)
- CI: `.github/workflows/high-energy-tail-model-audit.yml`

The comparison keeps AFH-7, Hybrid-9, Helm-9, GCN and JJ55 distinct. In particular, Helm-9 is a full nine-isotope phenomenological model; Hybrid-9 uses Helm only for Xe-124/Xe-126 and retains AFH for the other seven isotopes. The AFH response has deep high-q diffraction minima, so relative response ratios near these minima are more informative than an absolute difference divided by (A^2) alone. Numerical-method caveat: AFH-7/Hybrid-9 use threshold-u^2 integration, while the archived GCN/JJ55 spectra use legacy linear-W^2 8x8x4 integration; their 16x16x8 spot checks reach a maximum kernel-order difference of 2.18895e-4. Recompute GCN/JJ55 with the same threshold-u^2 mapping before treating sub-percent Hybrid-9 shifts as precision final values.

All yields remain one-dimensional efficiency-weighted rate-level expectations. They are not energy-resolution-smeared event predictions or an LZ likelihood.

## Structured result records

The AFH-7/Hybrid-9 continuous-spectrum runner now writes the standard v1.0.0 records by default when its output directory is inside the repository:

```powershell
python research/afh_default_density_natural_xenon_halo/run_afh7_hybrid9_continuous_spectrum.py --outdir research/afh_default_density_natural_xenon_halo/results/<run-label>
```

The runner preserves its original physics CSVs, metadata and SHA-256 file, then adds `run_manifest.json`, `result_summary.json`, `validation_report.json`, `README.md` and a standard `SHA256SUMS.txt`. It records the three-body kernel/halo-integral tables and exact-spatial-q AFH response comparisons without changing the physics calculation. The archive validator is `research/schemas/validate_result_records.py`; the shared writer is `research/result_archive.py`.

For a temporary smoke run outside the repository, pass `--no-standard-archive`; such a run is not treated as a repository archive. The generated manifest starts with `archive.status=local_only` and must only be updated after the files are actually committed and verified.

Implementation task brief: [2026-11-20 LZ structured result archive](../../docs/task_briefs/20261120-lz-standard-result-archive.md). Validation-only workflow: `.github/workflows/lz-structured-result-archive-validation.yml`.
