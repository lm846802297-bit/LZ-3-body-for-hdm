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
