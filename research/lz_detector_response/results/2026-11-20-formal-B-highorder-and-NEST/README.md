# Frozen formal B high-order Halo and LZ NEST outputs

This archive combines three separately versioned native output artifacts:

1. PR #93 high-order seven-isotope Halo comparison (A/source nucleon baseline).
2. Formal B finite-nucleon reweight of that exact accepted high-order Halo source, with three strange-current alternatives and 3,000 correlated electromagnetic covariance draws.
3. PR #87 four-benchmark event-weighted NEST response fold.

These are not a single common benchmark: the PR #86 Halo comparison and PR #87 production detector benchmarks remain distinct, as recorded in their native metadata. The NEST fold is a diagnostic response product, not a completed official LZ selection or likelihood.

The NEST artifact explicitly records formal_pass = null and DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE. Its exact raw-rate closure is archived, while its replica spread and 2D map TV remain diagnostics. It uses a uniform active-TPC spatial proxy and does not include the official fiducial-volume map, SS/data-analysis response, Skin/OD sample migration, or background likelihood.

All source ZIP digests are checked against GitHub's artifact API. Each extracted artifact's own SHA256SUMS is verified or generated, and the top-level SHA256SUMS covers every archived file. Recheck with sha256sum -c SHA256SUMS from this directory.
