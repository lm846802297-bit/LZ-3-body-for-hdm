# Research archive

All research materials are kept under this directory so the repository root stays uncluttered.

## Research workflow

Read WORKFLOW.md before starting a new study. Use _template/README.md for each new topic, and follow the PR checklist in .github/PULL_REQUEST_TEMPLATE.md.

## Directory map

- `docs/`: model definitions, phenomenology notes, source audits, editorial records, references, and the research roadmap.
- `figure2_kinematic_audit/`: threshold conditions, maximum scalar mass, and phase-space checks.
- `figure2_full_reproduction/`: Eq. (6) three-body kernel, Xe-131 and natural-xenon nuclear responses, GCN/JJ55 comparisons, propagator-width and scalar self-energy audits, numerical outputs, tests, and the standalone chi2 decay-width calculation.
- `afh_default_density_xe131/`: AFH v6.0 Xe-131 response, response normalization and momentum-convention audits, plus AME2020/CODATA-2022 mass and Xe-131-only hybrid diagnostics. The legacy PCHIP partial-rate tables are not the primary direct-exact-q result.
- `afh_default_density_natural_xenon_halo/`: isotope-resolved AFH default-density natural-xenon halo fold, seven-isotope response extraction, selected-q 60-digit mpmath validation, and the interpolation-accuracy audit. The primary AME2020 result is the seven-isotope **selected-point direct-exact-q** fold with native rate/convergence tables and SHA-256 manifests; it is not a continuous recoil spectrum or detector-level LZ likelihood.

## Organization rules

- Keep research-specific scripts, tests, numerical tables, plots, and audit reports together under the relevant study directory.
- Keep project-level research notes in `research/docs/`.
- Keep the manuscript source and original figures in `paper-source/`.
- Record assumptions and validation boundaries alongside each result; passing software tests does not by itself settle unspecified model assumptions.
