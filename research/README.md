# Research archive

All research materials are kept under this directory so the repository root stays uncluttered.

## Research workflow

Read WORKFLOW.md before starting a new study. Use _template/README.md for each new topic, and follow the PR checklist in .github/PULL_REQUEST_TEMPLATE.md.

## Directory map

- `docs/`: model definitions, phenomenology notes, source audits, editorial records, references, and the research roadmap.
- `figure2_kinematic_audit/`: threshold conditions, maximum scalar mass, and phase-space checks.
- `figure2_full_reproduction/`: Eq. (6) three-body kernel, Xe-131 and natural-xenon nuclear responses, GCN/JJ55 comparisons, propagator-width and scalar self-energy audits, numerical outputs, tests, and the standalone chi2 decay-width calculation.

## Organization rules

- Keep research-specific scripts, tests, numerical tables, plots, and audit reports together under the relevant study directory.
- Keep project-level research notes in `research/docs/`.
- Keep the manuscript source and original figures in `paper-source/`.
- Record assumptions and validation boundaries alongside each result; passing software tests does not by itself settle unspecified model assumptions.
