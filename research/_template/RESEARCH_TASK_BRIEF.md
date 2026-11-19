# Research Task Brief — <short task title>

> Copy this file, complete every field, and send the completed brief with the task. If a field does not apply, write `N/A` and explain why. Do not leave ambiguous blanks.

**Task ID:** `YYYYMMDD-short-kebab-case`  
**Status:** draft | assigned | in-progress | blocked | completed  
**Prepared on:** YYYY-MM-DD  
**Prepared by:** <person/model/agent>  
**Assigned to:** <person/model/agent/team>  
**Research topic:** <research/<topic> or cross-topic>  
**Baseline repository:** <owner/repository>  
**Baseline branch and commit:** <branch> @ `<full SHA>`  
**Related issue / PR / task:** <URL or N/A>

---

## 1. Research question

**Primary question**

<One precise, answerable question. Define the physical/computational object and requested parameter or kinematic range.>

**Scope**

- Included:
- Excluded:
- Intended claim this task may support:

## 2. Source papers, files, and repositories

List primary sources first. Include exact versions and locations within each source.

| Type | Exact source and version | Relevant pages / equations / paths / symbols | Provenance, URL, or SHA-256 |
|---|---|---|---|
| Primary paper | | | |
| Secondary/reference paper | | | |
| Repository and code | | | |
| Supplied file / dataset | | | |
| Other | | | |

Unavailable or inaccessible sources and their impact:

## 3. Git commit / version

- Repository:
- Baseline branch:
- Baseline commit SHA:
- Relevant code path(s) and commit(s):
- Input / dataset / release version:
- Submodule or external package versions:
- Working-tree state (clean or list local changes):
- Exact revision against which results must be compared:

## 4. Conventions

State definitions explicitly. Do not rely on names such as `q`, “positive transfer”, or “standard normalization” without defining them.

- Metric signature and four-vector ordering:
- Units and conversion constants:
- Momentum-transfer definitions, directions, and external legs:
- Spatial momentum versus Lorentz-invariant definitions:
- Fourier / plane-wave phase convention:
- Gamma matrices, `sigma^{mu nu}`, spinors, polarization and trace conventions:
- Interaction, propagator, width, and (i0^+) signs:
- State/current/nuclear-response normalization:
- Coupling and isospin normalization:
- Spin averages, polarization sums, identical-particle factors:
- Reference frames, axes, angles, and energy definitions:
- Other conventions:
- Conventions not fixed by sources (mark unresolved):

## 5. Assumptions and approximations

| Assumption / approximation | Reason and source | Validity range | Possible impact / omitted contribution |
|---|---|---|---|
| | | | |

Also state the model content, particle nature, interaction structure, benchmark parameters, truncation order, and any channels or effects deliberately omitted.

## 6. Known validated results

Only list results whose evidence and scope can be identified. Mark unverified prior conclusions as hypotheses, not validated results.

| Result / claim | Exact scope and benchmark | Evidence, code/input revision | Status and tolerance |
|---|---|---|---|
| | | | |

Relevant historical, provisional, diagnostic, or superseded results:

## 7. Required independent derivation

Specify the exact derivations required and the starting source for each.

1. <Equation/result to derive from the primary source or Lagrangian>
2. <Intermediate identities, signs, factors, or approximations to expose>
3. <Independent comparison target; do not use it as a substitute for derivation>

The derivation must show intermediate steps, assumptions, sign conventions, normalization factors, and the point at which each approximation is applied.

## 8. Required numerical checks

Set methods and acceptance criteria before interpreting the outputs. Mark irrelevant checks N/A with a reason.

| Check | Method / independent implementation | Acceptance criterion / tolerance | Result: PASS / FAIL / BLOCKED / NOT RUN / N/A |
|---|---|---|---|
| Dimensional and unit consistency | | | |
| Analytic limits / thresholds / endpoints | | | |
| Conservation and on-shell identities | | | |
| Signs, normalization, spin averages, symmetry factors | | | |
| Independent code or primary-source comparison | | | |
| Precision / quadrature / grid / interpolation convergence | | | |
| Regression against frozen benchmark | | | |
| Uncertainty and assumption sensitivity | | | |
| Output integrity and checksums | | | |

Record actual residuals, tolerances, commands, logs, and exact code/input revisions. A check not run must remain NOT RUN.

## 9. Expected output

| Deliverable | Required path / format | Required contents and metadata | Acceptance condition |
|---|---|---|---|
| Independent derivation | | | |
| Code / implementation | | | |
| Tests / validation | | | |
| Machine-readable results | | | |
| Figures / report | | | |
| Run manifest / provenance | | | |
| PR / archive record | | | |

**Reproduction commands and environment:**  

**Required conclusion level:** exploratory / diagnostic / reproducible / validated / other.

## 10. Unresolved questions

| Open question or discrepancy | Competing sources / conventions | Expected impact | Blocking? | Next discriminating check |
|---|---|---|---|---|
| | | | | |

---

## Execution instructions

- Derive independently from the supplied primary sources; do not assume earlier model conclusions are correct.
- Do not silently change metric, momentum, sign, unit, or normalization conventions.
- If sources disagree, preserve the alternatives and quantify their consequences before adopting one.
- Include explicit assumptions, derivation steps, dimensional checks, limiting cases, and numerical validation.
- Separate mathematical derivation, code correctness, numerical convergence, and physical validity.
- State what was not run, what failed, and what remains blocked.

## Return record (complete when the task is handed back)

- Answer and scope actually resolved:
- Independent derivation / key equations:
- Conventions confirmed or changed (with reasons):
- Assumptions and validity range:
- Numerical checks, tolerances, and actual residuals:
- Unresolved discrepancies and next checks:
- Output paths, checksums, reproduction commands:
- Exact completion commit SHA / PR:
- Final status and the precise claim it supports:

## Change log

| Date | Revision | Change and reason | Affected conclusions / outputs |
|---|---|---|---|
| | | | |
