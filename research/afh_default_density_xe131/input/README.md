# Xe-131 AFH inputs

This directory contains immutable source inputs used by the Xe-131 response and four-benchmark calculations.

- `afh_default_xe131_density_matrix.csv`: 67-entry extraction of the built-in AFH v6.0 `sdgXe131` default density matrix. Its SHA-256 is `f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45`. The source AFH archive and source-file hashes are recorded in the study README and native-audit manifest.
- `figure2_recalc_mV10_g2_1_v800_Xe131_full_5keV.csv`: precomputed fixed-speed Eq. (6) base grid used for controlled nuclear-response substitution. It is not a new Eq. (6) recomputation.

Do not edit either input in place. New source versions or recalculated base grids should be added as separately versioned files with provenance and checksums.
