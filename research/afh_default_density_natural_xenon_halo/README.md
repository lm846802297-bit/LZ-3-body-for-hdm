# AFH default-density natural-xenon halo fold

This directory archives the selected-point natural-xenon halo-folded three-body rate using the AFH v6.0 built-in sdgXeA default density responses.

- Four Figure-2 benchmark parameter sets are retained.
- Each available isotope uses its own NIST-derived nuclear mass, AFH response sample and three-body threshold.
- Natural atomic abundances are used without renormalizing the seven available isotopes.
- The truncated Standard Halo Model is the baseline; the untruncated Maxwell-Boltzmann result is only a high-speed-tail diagnostic.
- Rates are before detector efficiency, resolution, exposure, cuts and likelihood.
- The 28 archived AFH response samples were evaluated at exact spatial recoil q, while the manuscript response definition y=b_A^2*m_A*E_R/2 requires q_response=sqrt(2*m_A*E_R). The current archived rates are therefore labeled legacy exact-q-response results, not the final manuscript-NR response fold.

See results/NATURAL_XENON_HALO_FOLD_AUDIT.md for assumptions, results and convergence checks.

Run from the repository root:

    python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py --response-q-convention legacy_exact

The script imports research/figure2_full_reproduction/eq6_kernel.py and reads the compact response samples and NIST isotope weights in this directory. The default response-q mode is manuscript_nr and intentionally rejects the archived exact-q samples until their R_A values are regenerated. Use the explicit legacy_exact option only to reproduce the historical archive. The hash of the full AFH response input used to extract the samples is recorded in results/afh_response_input_sha256.txt.

The q-convention audit is archived in results/natural_xenon_q_convention_audit.csv, results/xe131_afh_response_shift_NR_vs_exact.csv and results/q_convention_audit_summary.json. The legacy_exact mode was rerun in CI: all 98 isotope contributions and 14 total rates reproduce the archived tables, with a maximum total-rate relative difference of 2.67e-12; see results/legacy_exact_reproduction_comparison.json and workflow run 43040078335.
