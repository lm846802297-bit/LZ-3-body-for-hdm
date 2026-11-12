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

**Consequently, the existing seven-isotope AME2020 fold script is still
exploratory.** It currently uses PCHIP interpolation on the 2401-node grid.
The precision rate fold must be updated to consume the direct exact-q response
table produced by the mpmath validator, or use a separately validated refined
or adaptive response grid. The response-grid generation and historical
archive-reproduction checks passing does not validate the halo-fold rates.

The same interpolation issue affects the previously reported Xe-131 AME2020
partial rates and the Xe-131-only hybrid ppm diagnostic. The nuclear-mass
table and mass-conversion tests remain valid, but those rate-level numbers are
provisional until the direct exact-q response is used and the rates are
recomputed.

AFH v6.0 still has no built-in default-density matrices for Xe-124 and Xe-126.
The seven-isotope AFH result therefore covers 0.998158 of the natural atom
fraction without renormalization; the missing-isotope \(A^2\) values remain
a coherent-charge ceiling only, not an AFH central prediction.
