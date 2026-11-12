# LZ detector-response inputs and rate-level archive

This directory stores the detector-response inputs used to connect the
three-body natural-xenon recoil spectra to the published LZ 2026
high-efficiency nuclear-recoil region.

## Contents

- `lz_2026_extended_nr/lz_2026_figS2.svg`: vector source figure retained for
  the efficiency digitization.
- `lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv`: 303-point
  digitization of the central final WIMP-search ROI efficiency and the gray
  uncertainty envelope.
- `lz_2026_extended_nr/lz_2026_nr_efficiency_metadata.json`: source,
  extraction method, axis calibration, checks, and digitization caveats.
- `lz_2026_extended_nr/rate_level_event_yields/`: archived
  efficiency-weighted expected event yields and their calculation metadata.

## Provenance and interpretation

The efficiency curve is digitized from LZ Collaboration, arXiv:2609.02823v1,
Fig. S2 (PDF page 14). The corresponding HEPData release is
[doi:10.17182/hepdata.182472.v1](https://doi.org/10.17182/hepdata.182472.v1).
The metadata records the PDF SHA-256, vector-path extraction procedure, and
the comparison with an independent digitization.

The gray band is retained as a detector-systematic range. LZ does not assign
a confidence level to that envelope. The curve is not rescaled to force exact
agreement with the rounded published mean efficiency.

The rate-level event-yield files fold the continuous natural-xenon spectra
with the digitized central efficiency and its gray envelope over the
5.4–269.9 keV analysis window. They are rate-level diagnostics only: they do
not include the two-dimensional S1c/log10(S2c) signal PDFs, NEST nuisance
covariance, energy-resolution smearing, background likelihood, or profile
likelihood. They are not a 90% confidence-level exclusion and are not the
official LZ likelihood.

See the main study report and
`research/figure2_full_reproduction/fold_lz_2026_rate_level.py` for the
calculation and limitations.
