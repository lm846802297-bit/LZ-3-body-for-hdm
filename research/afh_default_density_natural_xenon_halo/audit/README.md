# Natural-xenon audit material

This directory contains independent response and nuclear-model audits.

- `AFH_RESPONSE_INTERPOLATION_AUDIT.md`: compares the historical PCHIP response samples with direct exact-spatial-q finite-sum evaluations and records the precision boundary.
- `audit_high_energy_tail_model_sensitivity.py`: reproducible high-energy candidate-window comparison using the LZ 2026 one-dimensional final-ROI efficiency. It keeps AFH-7, Hybrid-9, Helm-9, GCN and JJ55 distinct and writes its results to an explicit `--outdir`.

The high-energy tail program produces efficiency-weighted rate-level expectations. It is not an energy-resolution-smeared event prediction, profile likelihood, exclusion or official LZ result. It does not overwrite the canonical response grids or committed rate tables.
