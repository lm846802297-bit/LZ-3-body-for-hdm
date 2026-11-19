# Research Task Handoff Standard

**Status:** mandatory for substantive research tasks  
**Effective date:** 2026-11-19  
**Scope:** theory, derivations, numerical calculations, code implementation, data analysis, validation, and cross-model or collaborator handoffs in this repository.

## 1. Purpose

A research task must be reproducible as an instruction, not reconstructed from chat history or inferred from a previous model's summary. This standard gives every model, agent, researcher, and collaborator the same task definition: what question is being answered, which exact sources and revisions apply, which conventions are fixed, what must be derived independently, which checks must be run, and what files must be returned.

The handoff brief is a task specification. It is not evidence that a derivation, calculation, test, or validation has been completed. Completion evidence belongs in the returned task record, study README, audit report, run manifest, and/or pull request.

## 2. When a brief is required

Create a completed Research Task Brief before starting any substantive task that involves one or more of:

- a physical derivation, matching calculation, or interpretation of a paper;
- a numerical calculation, parameter scan, data transformation, or figure;
- a change to production code, physics conventions, input data, or validation logic;
- independent work by multiple models, agents, researchers, or collaborators;
- a task whose result will be used as a benchmark, research conclusion, manuscript statement, or formal repository result.

For a trivial editorial or repository-maintenance change with no scientific content, the PR may state that a brief is not applicable and explain why. Existing historical work does not need to be retroactively rewritten; apply this standard to new tasks and to substantial follow-up work.

## 3. Canonical location and naming

Use the [Research Task Brief template](_template/RESEARCH_TASK_BRIEF.md).

Store each filled brief with the topic it governs:

- Topic-specific task: `research/<topic>/task_briefs/<task-id>.md`
- Cross-topic or repository-wide task: `research/docs/task_briefs/<task-id>.md`

Use a stable task ID such as `YYYYMMDD-short-kebab-case`. If multiple tasks share the same date and topic, append a short sequence or distinguishing suffix. Link the brief from the relevant study README, issue, or PR. The branch name, a chat message, and a PR title are not substitutes for the brief.

## 4. Required fields

Every substantive brief must complete all ten fields below. If a field genuinely does not apply, write `N/A` and explain why. Do not leave an empty field that could be mistaken for an oversight.

### 4.1 Research question

State one answerable question, the physical or computational object being studied, the requested parameter/energy/momentum range, and the boundary of the task. Separate the primary question from optional follow-up work. State what the task is not intended to establish.

### 4.2 Source papers, files, and repositories

List primary sources before secondary summaries. For papers, give the title, authors, DOI/arXiv identifier, version/date, and the exact pages, equations, appendices, or tables to use. For repository material, give the full repository, path, branch/tag/commit, and relevant symbol or line range. For supplied files, give the exact filename and, when content identity matters, SHA-256. Record access restrictions or unavailable source material.

A citation or a model-generated summary is a locator, not a substitute for checking the underlying source. If a source cannot be accessed, state that explicitly and identify which part of the task it blocks.

### 4.3 Git commit and version

Pin the baseline repository commit SHA, branch, and any relevant submodule, package, data-release, or external-code version. Identify the exact code and input revisions used for comparison. A moving branch name such as `main` is not sufficient by itself; record its resolved SHA at handoff time. If the working tree contains uncommitted changes, list them.

### 4.4 Conventions

Explicitly state every convention that can change a sign, factor, variable meaning, or numerical value. As applicable, include:

- metric signature and four-vector/component ordering;
- units, conversion constants, and natural-unit conventions;
- momentum-transfer definitions and directions, including which external legs define each transfer;
- distinction between spatial magnitudes and Lorentz invariants;
- Fourier-transform and plane-wave phase conventions;
- gamma-matrix, `sigma^{mu nu}`, spinor, polarization, and trace conventions;
- signs of interaction terms, propagator prescriptions, widths, and (i0^+) terms;
- normalization of states, currents, nuclear responses, couplings, isospin coefficients, and form factors;
- initial-state averages, final-state sums, identical-particle factors, and phase-space conventions;
- frames, axes, angular variables, and energy definitions.

For this repository's three-body work, do not collapse distinct quantities such as `q_A`, `q_N`, `q_chi`, `k_s`, `t_A`, and `t_N` into one generic `q`. Define each quantity and state where it enters. This is an example of the required level of precision, not a universal convention imposed on every task.

If a convention is not fixed by an approved source or derivation, mark it **unresolved**. Do not silently choose a familiar textbook convention or inherit one from a variable name.

### 4.5 Assumptions and approximations

List the model content, degrees of freedom, parameter benchmark, kinematic regime, approximations, truncation order, omitted contributions, and validity range. For each material approximation, state why it is used and what observable or conclusion could be affected. Distinguish an assumption adopted for the task from a fact established by data or derivation.

### 4.6 Known validated results

List only results that have evidence at the stated scope. For each, give the claim, exact parameter point/range, code and input revision, source of the result, validation method, residual/tolerance, and status. Distinguish **validated**, **reproducible**, **provisional**, **diagnostic**, **historical**, and **superseded** results according to the repository governance policy.

A result from a previous model, an old chat, a passing test, or a visually similar plot is not automatically validated. Treat prior conclusions as hypotheses to re-check unless the brief identifies the evidence and its scope.

### 4.7 Required independent derivation

Specify exactly which equations or conclusions must be derived afresh from the primary Lagrangian, source paper, definitions, or data. Require the derivation to show intermediate steps, assumptions, signs, normalization factors, and any approximations. Identify which existing expressions may be used as comparison targets, but do not instruct the researcher to copy them as proof.

If a derivation depends on an ambiguous source convention, require the competing interpretations to be written side by side and their consequences evaluated before one is adopted.

### 4.8 Required numerical checks

List checks with a method and an acceptance criterion. Select those relevant to the task:

- dimensional and unit checks, including explicit conversion factors;
- analytic limits and threshold/end-point behavior;
- conservation laws, on-shell conditions, and exact kinematic identities;
- sign, normalization, spin-average, symmetry-factor, and factor-counting checks;
- independent implementation or independent source/table comparison;
- quadrature, interpolation, grid, precision, and parameter-scan convergence;
- regression tests against a frozen benchmark;
- uncertainty propagation and sensitivity to material assumptions;
- output integrity, row counts, metadata, and SHA-256 checksums.

For each check, report one of **PASS**, **FAIL**, **BLOCKED**, **NOT RUN**, or **N/A** with evidence. State numerical tolerances before judging the result whenever practical. A software test, a numerical convergence test, and a physical validation are separate claims.

### 4.9 Expected output

Name the required deliverables and their intended repository paths: derivation note, code/module, tests, configuration, source/input manifest, machine-readable data, figures, run manifest, audit report, and/or PR. Specify formats, required metadata, reproduction commands, and the level of conclusion the output is allowed to support.

Do not promise a result that depends on unavailable data or an unrun calculation. If an output is blocked, return the available partial work and state the blocker.

### 4.10 Unresolved questions

List open physical, documentary, numerical, and implementation discrepancies. For each, record the competing definitions or values, source of each, likely impact, whether it blocks the requested result, and the next discriminating check. Preserve disagreements explicitly; do not silently reconcile or delete them.

## 5. Execution rules

1. **Derive independently from primary sources.** Reconstruct the requested result from the specified Lagrangian, equations, definitions, or data. Previous model outputs are useful leads and comparison points, not authorities.
2. **Do not silently change conventions.** Keep the handed-off definitions fixed. If a change is necessary, record the old and proposed conventions, the reason, and the impact on every affected formula and result; obtain clarification when the choice changes the requested physics.
3. **Separate derivation from implementation.** First establish the formula and its assumptions, then implement it. Verify the implementation independently rather than treating code output as a derivation.
4. **Show the checks.** Include dimensional analysis, limiting cases, normalization/sign checks, and numerical validation appropriate to the claim. Give actual residuals and tolerances, not only the word “passed.”
5. **Report incomplete work honestly.** Do not convert a planned, inferred, sampled, or partially executed check into a completed result. Record failed and blocked attempts.
6. **Preserve provenance.** Record exact source revisions, input checksums, code SHA, runtime/dependencies, commands, numerical settings, and output checksums when relevant.
7. **Keep historical results.** If a convention or implementation changes, create a new versioned result and explain the difference rather than overwriting the previous result.

## 6. Required return record

The receiving researcher/model returns a concise but complete close-out with:

1. **Answer to the research question** — including the scope actually resolved.
2. **Independent derivation** — equations, intermediate steps, assumptions, signs, and normalizations.
3. **Conventions used** — confirm each handed-off convention or list every justified deviation.
4. **Assumptions and approximations** — including validity range and omitted terms.
5. **Numerical checks** — method, tolerance, actual result, and PASS/FAIL/BLOCKED/NOT RUN/N/A status.
6. **Known results reused** — with exact provenance and scope.
7. **Unresolved discrepancies** — competing options, impact, and next check.
8. **Artifacts** — repository paths, formats, checksums, commands, and exact commit SHA/PR.
9. **Final status** — validated, reproducible, provisional, diagnostic, historical, or superseded, with a sentence defining what that label covers.

## 7. Change control

The brief is versioned research metadata. If scope, source revision, model assumptions, or conventions change after work begins, update the brief with a dated change-log entry or create a successor brief linked to the original. Do not replace the original handoff silently. A completed brief should remain alongside the derivation, audit, and result records it governed.

## 8. Relationship to existing policy

This standard supplements:

- [Repository instructions](../AGENTS.md)
- [Repository research workflow](WORKFLOW.md)
- [Research source-of-truth hierarchy](RESEARCH_GOVERNANCE_AND_SOURCE_HIERARCHY.md)
- [Contribution guide](../CONTRIBUTING.md)
- [Study README template](_template/README.md)
- [Task brief template](_template/RESEARCH_TASK_BRIEF.md)

The existing policy that CI is optional remains in force. A task may require a particular workflow run if its brief says so, but a green CI badge is not a substitute for the independent derivation and scientific checks specified above.
