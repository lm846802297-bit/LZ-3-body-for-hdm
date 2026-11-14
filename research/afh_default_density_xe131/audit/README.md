# Xe-131 AFH audit records

This directory contains the source-level, normalization, momentum-convention, and mass-scheme audit material for the AFH default Xe-131 study.

## Reports

- `AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md`: extraction of the official 67-entry AFH v6.0 density matrix, oscillator prescription, isoscalar normalization, and physical equal-p/n response.
- `AFH_COUPLING_NORMALIZATION_MAPPING.md`: mapping between the AFH isoscalar convention and the physical equal-proton/equal-neutron coupling; the factor of four is applied exactly once.
- `AME2020_CODATA2022_MASS_RECALC.md`: AME2020/CODATA-2022 Xe-131 nuclear-mass conversion and the scope of the Xe-131-only hybrid diagnostic.

## Audit programs

- `audit_response_momentum_conventions.py`: compares exact spatial recoil momentum with the small-recoil approximation and checks the stored natural-xenon sample convention.
- `audit_xe131_only_ame2020_hybrid.py`: replaces only the Xe-131 term in the archived NIST natural-xenon baseline; it is explicitly a hybrid diagnostic, not a full AME2020 natural-xenon prediction.

The audit programs write to explicit `--outdir` / `--out-dir` destinations. They do not overwrite canonical response or cross-section tables.
