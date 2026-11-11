# Repository research workflow

This document turns the repository's research-management principles into
operational rules.

## 1. What belongs where

The repository root is intentionally small:

- README.md, CONTRIBUTING.md, and repository-level configuration files;
- .github/ for GitHub workflows and PR templates;
- paper-source/ for the manuscript source and original paper assets;
- research/ for research notes, calculations, tests, inputs, outputs,
  figures, and audit records.

Do not create new research-specific directories at the repository root.

### Manuscript source

- paper-source/main_original.tex is the preserved original source.
- paper-source/main.tex is the working manuscript.
- Original figures, bibliography, style files, and source-build material stay
  under paper-source/.
- A research PR must not silently alter the manuscript. Any intentional
  manuscript edit must be clearly identified, justified, and reviewed as a
  separate part of the PR.

### Research archive

Use one directory per research topic:

~~~text
research/
  README.md
  WORKFLOW.md
  docs/                         # cross-topic research notes
  <topic>/
    README.md                   # required entry point for the study
    theory/                     # derivations and conventions, when needed
    calculations/               # source code and scripts, when useful
    tests/                      # unit, regression, and cross-check tests
    inputs/                     # small, redistributable input data/configs
    results/                    # machine-readable outputs and summaries
    figures/                    # generated figures
    audit/                      # numerical, physical, and provenance audits
~~~

Create only the subdirectories that the study actually needs. A study may keep
a compact flat layout if that is clearer, but its README must identify where
the code, tests, inputs, and results live.

## 2. Required study README

Every immediate study directory under research/ must contain a README.md.
Use research/_template/README.md as the starting template.

At minimum, document:

1. **Question and scope** — what is being calculated and what is not.
2. **Status** — choose one:
   - exploratory: active investigation; not yet independently reproduced;
   - reproducible: code, inputs, and commands reproduce the archived result;
   - validated: independent or analytic cross-checks and convergence tests
     support the stated numerical result;
   - superseded: retained for history but replaced by a later result.
3. **Model assumptions** — field nature, interaction convention, approximations,
   units, sign/normalization conventions, and thresholds where relevant.
4. **Inputs and provenance** — source, version, DOI/URL, license or access
   conditions, and SHA-256 for files whose exact contents matter.
5. **Environment** — language/runtime and dependency versions.
6. **Reproduction** — exact commands, configuration, and random seeds.
7. **Tests and convergence** — unit tests, limiting cases, independent checks,
   quadrature/grid convergence, and acceptance criteria as applicable.
8. **Results** — paths to CSV/JSON tables, plots, and concise numerical
   conclusions.
9. **Limitations and next steps** — unresolved assumptions and work still
   required.

A result can be merged before the physics question is fully settled, but only
if the archived calculation is reproducible and its status and limitations
are explicit. A passing software test is not, by itself, validation of the
physical model.

## 3. Branch and PR lifecycle

### Branch naming

Create each new branch from the latest main:

- research/<topic>-<phase> for a research calculation;
- fix/<topic> for a focused correction;
- docs/<topic> for documentation-only changes;
- chore/<topic> for repository maintenance.

Examples:

- research/chi2-pole-width
- research/natural-xenon-rate
- docs/research-workflow

Do not reuse an old branch whose history has already been merged. If work
continues after a merge, create a fresh branch from the new main.

### Development

1. Confirm that the working tree starts from the latest main.
2. Create or update the topic directory and its README before adding many files.
3. Keep code, tests, inputs, outputs, figures, and audit notes inside that
   topic directory.
4. Record important intermediate decisions in the study README or audit log.
5. Keep temporary files, caches, local environments, and unreviewed scratch
   outputs out of Git.

### Pull request

Open a PR from the topic branch to main. The PR must state:

- the research question and files changed;
- exact reproduction commands and required dependencies;
- input provenance and checksums;
- tests and relevant CI runs;
- numerical convergence and independent checks;
- physical assumptions and what remains unresolved;
- whether paper-source/ changed and why.

The PR template supplies the checklist. Keep a PR focused on one coherent
research topic or one repository-maintenance task.

## 4. Reproducibility and data policy

- Prefer deterministic scripts with explicit parameters and units.
- Store parameter sets in version-controlled text formats where practical.
- Record the source commit, input checksums, software versions, and commands
  used to generate important results. A small run_manifest.json or
  equivalent record is recommended for substantial runs.
- Keep raw inputs immutable when their provenance matters. Do not overwrite
  a historical result; write a new versioned result and explain the difference.
- Commit small, redistributable inputs and essential machine-readable outputs.
- Do not commit secrets, credentials, private data, or files whose license
  does not permit redistribution.
- For large datasets or generated archives, use Git LFS or a versioned GitHub
  Release asset. Include a manifest with filename, size, source, and SHA-256.
  Do not rely on expiring Actions artifacts as the only permanent record.
- Distinguish a diagnostic, an independently reproduced result, and a
  validated physical conclusion. Never promote one status to another merely
  because CI is green.

## 5. Main branch policy

The main branch is the curated, reproducible research record.

Recommended GitHub branch protection for main:

- require pull requests before merging;
- require the lightweight layout-check status check;
- require relevant topic-specific scientific checks when the PR changes that
  study's calculation;
- require conversation resolution;
- block force pushes and branch deletion;
- keep merge commits enabled so the PR boundary and topic history are retained.

For a single-maintainer repository, requiring an approval from another person
is optional and may make self-merging impossible. If collaborators join, add
at least one independent approval for substantive physics or numerical
changes. Administrators should avoid bypassing the rules except for a
documented emergency.

Do not require every long-running scientific workflow on every PR. Require
the lightweight repository-layout check globally; run and inspect the
appropriate scientific workflow for the topic being changed. This avoids
making unrelated research PRs wait for expensive calculations.

The repository's CI currently starts the Figure 2 scientific workflows on
pushes to main and matching research/** branches. A successful run on the
topic branch should be linked in the PR before merging a change to that
calculation.

## 6. Merge and cleanup

Before merging:

- the study README and PR checklist are complete;
- the layout check passes;
- relevant tests and scientific workflows pass;
- outputs are archived in the study directory or a versioned Release;
- assumptions, limitations, and validation status are explicit;
- no unrelated manuscript or research files have entered the PR.

Use a merge commit by default. After merging, verify that the result is on
main, then delete the topic branch if no further work depends on it.
Continue future work from a fresh branch created from the updated main.

## 7. Current repository convention

The current top-level research areas are:

- research/figure2_kinematic_audit/
- research/figure2_full_reproduction/

Cross-topic notes and references belong in research/docs/. New topics
should be added as siblings under research/ and indexed in research/README.md.
