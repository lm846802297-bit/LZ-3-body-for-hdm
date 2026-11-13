## Research question / purpose

<!-- What question does this PR answer? -->

## Scope and files

<!-- Which research topic is affected? List important code, inputs, results, and documents. -->

## Reproduction

- Environment / dependency versions:
- Exact command(s):
- Input data and provenance:
- Input checksums / run manifest:

## Validation

- [ ] Relevant unit and regression tests pass.
- [ ] Analytic limits / independent cross-checks are recorded where applicable.
- [ ] Numerical convergence and acceptance criteria are recorded where applicable.
- [ ] Relevant scientific GitHub Actions run(s) are linked below.
- [ ] Outputs are archived under the relevant research/<topic>/ directory or a versioned Release.
- [ ] Assumptions, limitations, and validation status are stated in the study README.

Scientific workflow links:

<!-- Paste the relevant Actions run URLs. -->

## Repository organization

- [ ] Research-specific files are under research/<topic>/.
- [ ] The formal result is archived on main under research/<topic>/, not only on the source branch.
- [ ] After merge, the main-branch paths and required artifacts will be checked before deciding whether to delete the source branch.
- [ ] The study README and research/README.md index are updated if needed.
- [ ] No temporary files, local caches, secrets, or unrelated outputs are included.
- [ ] paper-source/ is unchanged, or every intentional manuscript-source change is identified and justified.
- [ ] The lightweight repository layout check passes.

## Scientific status

Choose one and explain briefly:

- [ ] exploratory
- [ ] reproducible
- [ ] validated
- [ ] superseded / archival-only

Known limitations / unresolved assumptions:

<!-- State what this PR does NOT establish. -->

## Baseline and merge provenance

- Base `main` commit SHA:
- Source branch HEAD SHA:
- Related PR / research record:
- Proposed merge strategy: **Create a merge commit** (default for substantive research). Explain any Squash/Rebase exception:

## Validation evidence and exact revision

- Exact commit SHA on which each test/run was performed:
- Commands and test counts:
- Passed:
- Failed:
- Not run:
- Independent cross-check / convergence evidence:
- Input/output SHA-256 manifests:
- Claims not established / remaining limitations:

## Post-merge verification

- [ ] Verify the integrated main SHA and all archived artifact paths.
- [ ] Verify checksums after merge.
- [ ] Report archival status separately from scientific validation.
