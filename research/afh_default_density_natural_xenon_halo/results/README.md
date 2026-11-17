# Natural-xenon results and audit archive

This directory contains the current natural-xenon results calculated with the AME2020/CODATA-2022 bare nuclear masses, together with source response tables and numerical audits.

| File or directory | Purpose |
|---|---|
| `../完整运行与数值对照.md` | Current exact-mass benchmark results, method comparisons, convergence and limitations |
| `../独立验证/xenon_isotope_masses_ame2020_codata2022.csv` | Nine isotope masses, natural abundances and AFH coverage |
| `full_afh_v6_default_7_isotope_response/` | Seven AFH-supported isotope response grids |
| `afh7_hybrid9_ame2020_exact_2026-11-17/` | Current 84-point spectra and isotope kernel results using exact masses |
| `AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md` | Earlier selected-point direct exact-q calculation report; use the 2026-11-17 full-grid archive for current spectra |
| `AME2020_DIRECT_EXACT_Q_SHA256SUMS.txt` | Checksums for the selected-point report bundle |

The AFH-7 coverage is 0.998158 of natural xenon by atom fraction and remains unrenormalized. AFH v6.0 has no default-density matrices for Xe-124 or Xe-126. Hybrid-9 is AFH-7 plus explicitly labelled Helm fallback for those two isotopes; it is not AFH-9. The LZ rate-level fold is stored separately under `research/lz_detector_response/lz_2026_extended_nr/afh7_hybrid9_rate_level_yields/` and is derived from the exact-mass spectrum.
