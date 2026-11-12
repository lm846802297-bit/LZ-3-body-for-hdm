# AFH default-density natural-xenon halo fold

This directory archives the selected-point natural-xenon halo-folded three-body rate using the AFH v6.0 built-in sdgXeA default density responses.

- Four Figure-2 benchmark parameter sets are retained.
- Each available isotope uses its own NIST-derived nuclear mass, AFH response sample and three-body threshold.
- Natural atomic abundances are used without renormalizing the seven available isotopes.
- The truncated Standard Halo Model is the baseline; the untruncated Maxwell-Boltzmann result is only a high-speed-tail diagnostic.
- Rates are before detector efficiency, resolution, exposure, cuts and likelihood.
- The 28 archived AFH response samples use the exact spatial momentum transfer q=sqrt(2*m_A*E_R+E_R^2), consistent with AFH's y=(q*b_A/2)^2 definition and the exact nuclear mass shell. q_NR=sqrt(2*m_A*E_R) is retained as a small-recoil approximation for comparison.

See results/NATURAL_XENON_HALO_FOLD_AUDIT.md for assumptions, results and convergence checks.

Run from the repository root:

    python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py

The script imports research/figure2_full_reproduction/eq6_kernel.py and reads the compact response samples and NIST isotope weights in this directory. The default response-q mode is exact_spatial. The optional nr_approx mode intentionally rejects these exact-q samples unless matching R_A values are supplied. The legacy_exact option remains as a backward-compatible alias for exact_spatial. The hash of the full AFH response input used to extract the samples is recorded in results/afh_response_input_sha256.txt.

The q-convention audit is archived in results/natural_xenon_q_convention_audit.csv, results/xe131_afh_response_shift_NR_vs_exact.csv and results/q_convention_audit_summary.json. The exact-spatial-q mode is rerun in CI and compared against all 98 isotope contributions and 14 total-rate rows; see the latest exact-spatial reproduction artifact and comparison summary.

## AME2020 seven-isotope extension — current research status

The AME2020 extension is maintained on
`research/ame2020-mass-exact-spatial-mainline`. It adds the seven AFH v6.0
default-density xenon matrices and their 2401-node response grids:

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
`run_ame2020_natural_xenon_halo_fold.py` and its
`output/ame2020_full_response/` tables remain PCHIP-based diagnostics.
They are not the primary rate result.

The selected-point precision calculation has since been completed by
`run_ame2020_direct_exactq_natural_xenon_halo_fold.py`. It consumes the
56-point direct exact-q response table and writes the native outputs under
`output/ame2020_direct_exactq_fold/`; the calculation, convergence checks,
and output manifests are documented in the following section. The older
PCHIP-based Xe-131 partial-rate and hybrid tables remain historical
diagnostics and must not be cited as direct exact-q predictions.

The direct exact-q result is primary only for the 14 selected recoil/halo
benchmark points and the seven AFH-supported isotopes. It is not a continuous
recoil spectrum or a detector-level LZ likelihood. Passing response-grid
generation or historical PCHIP reproduction alone does not establish either
of those broader predictions.

AFH v6.0 still has no built-in default-density matrices for Xe-124 and Xe-126.
The seven-isotope AFH result therefore covers 0.998158 of the natural atom
fraction without renormalization; the missing-isotope \(A^2\) values remain
a coherent-charge ceiling only, not an AFH central prediction.


## AME2020 direct exact-q recalculation (2026-11-12)

The selected-point seven-isotope natural-xenon halo fold has now been recomputed locally using the 56 archived direct AFH finite-sum responses at exact spatial q, for both NIST and AME2020 nuclear masses. **No GitHub Actions / CI was used.**

- Report: [AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md](AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md)
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
- Bundle manifest: `AME2020_DIRECT_EXACT_Q_SHA256SUMS.txt`
- Full calculation report: `AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md`

The calculation and numerical acceptance were performed locally; this runner is not a self-hosted GitHub Actions runner. The selected-point results are not a continuous recoil spectrum or a detector-level LZ prediction.
