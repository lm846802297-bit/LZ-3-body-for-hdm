# Natural-xenon generated outputs

This directory contains native generated response and selected-point integration products.

- `afh_default_xenon_responses/`: AFH v6.0 isotope-response generation outputs, selected-sample regression data, and independent selected-q mpmath summaries.
- `ame2020_direct_exactq_fold/`: selected-point seven-isotope NIST/AME2020 direct exact-q halo-fold archive. It contains the 392 kernel/halo integrals, 784 isotope contributions, 112 total-rate summaries, convergence tables, metadata and an output-level `SHA256SUMS.txt`.

The direct exact-q fold is the primary selected-point calculation. The historical PCHIP-based fold is retained only as a comparison diagnostic. Neither output directory by itself represents a continuous recoil spectrum or a detector-level LZ likelihood.
