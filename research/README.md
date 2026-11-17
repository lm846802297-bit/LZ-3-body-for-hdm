# Research archive

All research materials are kept under this directory so the repository root stays uncluttered.

## Directory map

- `docs/`: model definitions, phenomenology notes, source audits, editorial records, references, and the research roadmap.
- `figure2_kinematic_audit/`: threshold conditions, maximum scalar mass, and phase-space checks.
- `figure2_full_reproduction/`: Eq. (6) three-body kernel, Xe-131 and natural-xenon nuclear responses, GCN/JJ55 comparisons, propagator-width and scalar self-energy audits, numerical outputs, tests, and the standalone chi2 decay-width calculation.

## Organization rules

- Keep research-specific scripts, tests, numerical tables, plots, and audit reports together under the relevant study directory.
- Keep project-level research notes in `research/docs/`.
- Keep the manuscript source and original figures in `paper-source/`.
- Record assumptions and validation boundaries alongside each result; passing software tests does not by itself settle unspecified model assumptions.

### Mathematica three-body natural-xenon calculation

`three_body_natural_xenon/` contains the reorganized main Mathematica notebook, AFH v6 xenon response data, usage notes, and archived comparison tables. The main calculation is inline in the notebook and uses FeynCalc plus Mathematica `NIntegrate`. Optional FeynRules/FeynArts checks need those external packages and a local model-export environment; the notebook keeps their saved outputs, but the third-party packages are not bundled. The run record is explicitly marked historical because this reorganization did not rerun all calculations.
