# Natural-xenon results and audit archive

This directory contains interpreted result tables, continuous spectra, convergence studies and study-level reports.

| File or directory | Purpose |
|---|---|
| `NATURAL_XENON_HALO_FOLD_AUDIT.md` | Main audit of the selected-point natural-xenon halo fold and its scope |
| `metadata.json`, `natural_xenon_halo_rates.csv`, `isotope_halo_contributions_compact.csv` | Historical selected-point NIST/PCHIP halo-fold archive |
| `full_afh_v6_default_7_isotope_response/` | Full 16,807-row response archive: seven AFH-supported isotopes × 2,401 q nodes, with matrices and metadata |
| `afh7_hybrid9_continuous_2026-11-14/` | AFH-7, Hybrid-9, AFH-7 plus the Xe-124/Xe-126 coherent-charge ceiling, and Helm-9 continuous spectra with quadrature checks |
| `afh7_hybrid9_full_grid_highorder_2026-11-14/` | High-order global quadrature and isotope/speed refinement audit |
| `AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md` | Selected-point AME2020 direct exact-q calculation report |
| `AME2020_DIRECT_EXACT_Q_SHA256SUMS.txt` | Bundle-level checksum manifest for that report, input, runner and numerical archive |

The seven-isotope AFH response coverage is 0.998158 of the natural atom fraction; Xe-124 and Xe-126 remain unsupported by the AFH v6.0 default-density matrices. Do not relabel the Helm-2 hybrid as AFH-9. The rate-level spectra are not detector-resolution-smeared event predictions or an LZ likelihood.

Before citing a table, read its adjacent metadata and checksum file. Historical PCHIP products, direct exact-q selected-point results and continuous spectra are distinct numerical products.
