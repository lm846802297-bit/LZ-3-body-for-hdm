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
- tests and numerical checks actually run locally or on an approved runner;
- CI runs, if any (optional), with exact status and commit SHA;
- numerical convergence and independent checks;
- physical assumptions and what remains unresolved;
- whether paper-source/ changed and why.

The PR template supplies the checklist. Keep a PR focused on one coherent
research topic or one repository-maintenance task.

### Research branches are workspaces; main is the canonical archive

A topic branch is a development workspace, not the permanent location of a
completed research result. When a result is submitted for integration:

- Put its formal, reviewable research record under
  research/<topic>/ in the PR: the study README, relevant source code,
  tests, configuration, provenance information, and the essential
  machine-readable outputs and figures.
- If a required large input or output cannot be stored in Git, keep it in a
  versioned GitHub Release or another stable, versioned location and commit
  its manifest, source/version, size, and SHA-256 under the study directory.
- Do not treat a branch name, an Actions artifact that may expire, or an
  unmerged commit as the sole archive of a result described as merged.
- It is acceptable to merge an exploratory or incomplete study when its
  reproducible scope, status, assumptions, and limitations are explicit.
  The claim being merged must match the evidence actually archived.

After a PR is merged, verify the merge commit on main and inspect the
corresponding research/<topic>/ paths on main. Confirm that the README,
code, tests, required inputs or manifests, and claimed outputs are present
and that the documented reproduction instructions point to the main-branch
paths. The merged result on main, not the development branch, is the
canonical project record.

A completed branch may be deleted only after this verification and after
checking that it contains no unique, unmerged commits or follow-up work.
If unique work remains, preserve it on the branch or move it to a separate
topic branch before deletion. Branch deletion is a manual maintenance choice;
there is no requirement to minimize the number of branches or enable automatic
deletion after merge.

## 4. Reproducibility and data policy

- Prefer deterministic scripts with explicit parameters and units.
- Store parameter sets in version-controlled text formats where practical.
- Record the source commit, input checksums, software versions, and commands
  used to generate important results. For every substantial run, include a
  run_manifest.json or equivalent complete record; identify the exact code,
  inputs, environment, commands, numerical settings, outputs, and validation.
- Keep raw inputs immutable when their provenance matters. Do not overwrite
  a historical result; write a new versioned result and explain the difference.
- **Extract-before-upload is mandatory for research delivery bundles.** If a
  local runner, ChatGPT export, GitHub Actions artifact, collaborator, or other
  source supplies a ZIP/TAR containing calculation results, unpack it before
  committing and upload the required extracted files individually to the
  appropriate study directory. Commit native, uncompressed inputs and outputs
  (CSV, JSON/JSONL, ROOT, HDF5, TXT, source code, tests, reports, metadata,
  manifests, etc.) rather than the delivery ZIP/TAR. A delivery bundle must
  never be the only archived copy of its contents.
- An original upstream ZIP/TAR may be retained only when the exact source
  container is relevant to provenance or reproducibility, or when the
  extracted source cannot legally be redistributed. Record its source/version,
  size, SHA-256, extraction command, and per-file checksums; separately commit
  all extracted files that can be redistributed. If an upstream archive is
  too large for ordinary Git storage, use Git LFS or a versioned Release and
  commit a manifest; do not replace native calculation outputs with a newly
  generated opaque ZIP/TAR bundle.
- Do not commit secrets, credentials, private data, or files whose license
  does not permit redistribution.
- For files too large for ordinary GitHub Git storage, use Git LFS or a
  versioned GitHub Release/stable external storage. Prefer individual native
  files; do not replace results with newly generated opaque ZIP/TAR bundles.
  Commit a manifest with exact filename, immutable location/version, size,
  format, source, and SHA-256. Do not rely on expiring Actions artifacts as
  the only permanent record.
- Distinguish a diagnostic, an independently reproduced result, and a
  validated physical conclusion. Never promote one status to another merely
  because CI is green.
- After pushing, inspect the PR diff and retrieve the committed files from
  GitHub. Verify the expected paths, file count, sizes, and SHA-256 checksums
  against the local submission before reporting that archival is complete.
  A successful commit or checksum match is not scientific validation.

## 5. Main branch policy

The main branch is the curated, reproducible research record.

Recommended GitHub branch protection for main:

- require pull requests before merging;
- require conversation resolution;
- block force pushes and branch deletion;
- keep merge commits enabled so the PR boundary and topic history are retained;
- do not require CI status checks as branch-protection gates under this
  research policy.

For a single-maintainer repository, requiring an approval from another person
is optional and may make self-merging impossible. If collaborators join, add
at least one independent approval for substantive physics or numerical
changes. Administrators should avoid bypassing repository protections except
for a documented emergency.

CI is optional. Neither the lightweight layout check nor a topic-specific
scientific workflow is a prerequisite for starting or completing a
calculation, validating its numerical result, submitting its files, reviewing
its PR, or merging it. Run relevant calculations and checks locally or on an
approved compute runner when practical; record the exact checks actually
performed. A workflow may still start automatically or be dispatched
manually, but its status is supplemental evidence, not a merge gate.

A GitHub Actions workflow that performs a calculation is an execution run,
not a required CI pass. If Actions is queued, unavailable, disabled, billing
blocked, cancelled, or fails for infrastructure reasons, continue research
through an available execution route and record the CI status accurately.
Do not misclassify infrastructure failure as scientific failure or claim an
unrun check passed.

## 6. Merge strategy and commit-history policy

### Default: merge commit

Use **Create a merge commit** as the default GitHub PR merge method for research and substantive repository changes.

Rationale:

- Preserve the topic branch's individual commits and their parent/child relationships in the repository history.
- Keep the PR boundary explicit through the merge commit.
- Make it possible to trace a scientific change through its intermediate derivation, implementation, test, correction, and result commits.
- Retain useful bisect and provenance information when a later numerical or physical discrepancy must be traced to a particular change.

For research code, a commit may represent a distinct equation change, convention correction, numerical method, regression test, input update, or validation result. Do not discard that history merely to make the main log shorter.

### Allowed exceptions

Use **Squash and merge** only when the PR is genuinely one indivisible maintenance or documentation unit and its individual commits do not carry useful scientific or review provenance. Examples include formatting-only cleanup, typo fixes, or a small batch of trivial edits. If a research PR contains meaningful intermediate scientific decisions or independently useful validation steps, do not squash it by default.

Use **Rebase and merge** only when a linear history is explicitly desired and the topic commits have already been organized into meaningful, reviewable units. Note that rebase-and-merge rewrites commit identities; it does not preserve the original branch's exact commit graph.

### Before merging

1. Inspect the PR commit list and diff; do not choose a method solely by commit count.
2. Confirm that commit messages identify meaningful changes and that temporary, duplicate, or misleading commits have been cleaned up on the topic branch when appropriate.
3. Confirm the PR is focused and its scientific scope, tests, provenance, and limitations are documented.
4. Select **Create a merge commit** unless a documented exception above applies.
5. After merging, verify the merge commit and resulting files on main. Preserve the PR URL as the review record.

Do not rewrite or force-push a branch after review merely to obtain a prettier history. If history cleanup is necessary, coordinate it before final review and re-check the resulting diff.

The choice of merge strategy does not change the scientific acceptance criteria: a merge commit is not evidence that a calculation is correct, and a squash commit is not evidence that its intermediate work was invalid. Report archival status and physics validation separately.

## 7. Merge and cleanup

Before merging:

- the study README and PR checklist are complete;
- relevant local tests, numerical checks, convergence checks, and independent
  checks have been run as appropriate and their actual status is recorded;
- optional CI results, if any, are reported accurately but are not a merge
  condition;
- outputs are archived in the study directory or a versioned Release;
- assumptions, limitations, and validation status are explicit;
- no unrelated manuscript or research files have entered the PR.

Use a merge commit by default. After merging, verify that the result is on
main, then delete the topic branch if no further work depends on it.
Continue future work from a fresh branch created from the updated main.

## 8. Current repository convention

The current top-level research areas are:

- research/figure2_kinematic_audit/
- research/figure2_full_reproduction/

Cross-topic notes and references belong in research/docs/. New topics
should be added as siblings under research/ and indexed in research/README.md.
