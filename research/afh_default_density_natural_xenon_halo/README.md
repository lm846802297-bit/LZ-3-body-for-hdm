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

    python research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold.py

The script imports research/figure2_full_reproduction/eq6_kernel.py and reads the compact response samples and NIST isotope weights in this directory. The hash of the full AFH response input used to extract the samples is recorded in results/afh_response_input_sha256.txt.
