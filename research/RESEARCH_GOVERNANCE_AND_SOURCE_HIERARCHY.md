# Research governance and source-of-truth hierarchy

**Status:** mandatory project-wide research policy  
**Effective date:** 2026-11-19  
**Scope:** all theory, numerical calculations, nuclear-response work, code, validation records, and manuscript development in this repository.

This policy records the agreed distinction between the scientific basis of the project and the manuscript used to communicate its current state. The manuscript is a working research output. It is not the authority that determines whether a physical formula, approximation, normalization, or numerical result is correct.

## 1. Source-of-truth hierarchy

When sources differ, use the following order:

| Priority | Source | Role |
|---:|---|---|
| 1 | Approved physical derivations and research conventions | Theoretical basis for definitions, assumptions, approximations, signs, normalizations, and production formulas |
| 2 | Validated formulas, numerical calculations, and independent cross-checks | Evidence that a stated derivation and its numerical implementation behave as claimed |
| 3 | Topic-specific research documents, including AFH nuclear responses and nucleon form factors | Detailed technical definitions, input provenance, derivations, and limitations within each subject |
| 4 | GitHub source code, tests, run manifests, and calculation records | Executable implementation, reproducibility record, and evidence of what was actually computed |
| 5 | The current manuscript source (paper-source/main.tex), uploaded manuscript drafts, and manuscript PDFs | Reference for the current model presentation, equation organization, figures, and writing; not an independent source of physical authority |

This order is a decision rule, not a claim that one file is automatically correct because of its location. Each source must still be checked for scope, assumptions, provenance, and validation status.

A passing unit test establishes only the assertions exercised by that test. A successful workflow establishes only that the recorded workflow ran successfully on the recorded commit and inputs. Neither by itself proves that the underlying physical assumptions or model are correct.

## 2. Governing principles

1. **Physical derivation takes precedence over manuscript wording.** Do not treat an equation in a manuscript draft as immutable. If a derivation, approximation, sign, normalization, or numerical result is found to be wrong or incomplete, follow the independently checked physical reasoning and record the correction.
2. **Do not tune calculations to reproduce a draft.** Do not alter code, inputs, normalization, interpolation, integration settings, or benchmark definitions merely to make a result agree with a manuscript figure or sentence. A disagreement is an item to investigate, not a target to eliminate.
3. **Keep research records separate from manuscript editing.** First complete and validate the physical and numerical work. Then decide how the result should be incorporated into the manuscript. Research changes must not silently rewrite the paper, and manuscript edits must not silently redefine the research calculation.
4. **Make conflicts explicit.** If two sources disagree, preserve both source states, identify the exact conflicting equations or values, determine their assumptions and provenance, and create a dated discrepancy record. Do not silently reconcile, overwrite, or select the version that happens to agree with the current paper.
5. **Preserve historical results.** Do not overwrite an earlier CSV, figure, run manifest, or calculation record. Generate a new version with a clear baseline label and explain which assumptions or code changed.
6. **Separate implementation correctness from physical validity.** Report software tests, numerical convergence, independent implementation checks, and physical assumptions as separate validation dimensions.

## 3. Manuscript status and boundaries

- paper-source/main_original.tex is the preserved original source. Keep it immutable.
- paper-source/main.tex is an editable working manuscript. It may be revised as research develops, but its current contents do not define the project's physical conventions.
- A PDF is a snapshot of a manuscript version, not a separate authority.
- A manuscript file uploaded in a conversation is reference material unless the user explicitly designates it as the canonical source for a particular editing task.
- The manuscript files uploaded on 2026-11-19, including the uploaded main.tex, are reference drafts only. They are not the final manuscript source and must not be used to replace the repository's working manuscript.
- A research calculation PR should not modify manuscript files unless manuscript editing is explicitly part of the task. If both research and manuscript work are needed, keep the physical result and its manuscript presentation separately identifiable in the diff and review.
- The manuscript may temporarily lag behind the validated research record. This is acceptable and preferable to prematurely changing a physical result to match an unfinished draft.

## 4. How to resolve a disagreement

When a manuscript, code path, research note, or numerical result disagrees with another source:

1. **Freeze the relevant definitions.** Record the exact equation, variable, units, sign, normalization, approximation, parameter point, code revision, and input revision involved.
2. **Identify the source layer.** Decide whether the disagreement is theoretical, numerical, documentary, implementation-related, or merely editorial.
3. **Return to the derivation.** Re-derive the relevant relation from the stated Lagrangian/current, kinematics, matrix element, or nuclear-response definition. State the assumptions explicitly.
4. **Check the implementation independently.** Use analytic limits, dimensional checks, unit tests, convergence tests, and an independent implementation where appropriate.
5. **Record the outcome.** Mark each affected result as retained, corrected, provisional, diagnostic, historical, or superseded. Keep old outputs and explain why the new result differs.
6. **Update the manuscript only after the research decision.** The paper should report the accepted result and its assumptions; it should not decide the result.

If the physical derivation itself is not yet settled, retain the calculation as provisional or diagnostic. Do not promote it to a production baseline merely because its code runs or its plot looks plausible.

## 5. Calculation and result acceptance

Before a calculation is treated as a production result, its record should identify:

- the approved physical convention and the theory document or derivation supporting it;
- model assumptions, degrees of freedom, interaction structure, and coupling definitions;
- all kinematic variables and their frame/convention, especially spatial momentum versus Lorentz invariants;
- units, signs, normalization factors, and the location where each factor is applied;
- input provenance, versions, checksums, and data transformations;
- code revision, dependencies, commands, numerical settings, and a run manifest;
- tests and analytic limits actually checked;
- numerical convergence and independent cross-checks actually performed;
- the exact output files and the claim those outputs support;
- limitations and unresolved questions.

Use validation labels precisely:

- **Validated:** the stated claim has passed its documented analytic/numerical checks and independent cross-checks at the stated scope.
- **Reproducible:** the archived code, inputs, and commands reproduce the result; this label alone does not imply physical validation.
- **Provisional:** important derivation, input, numerical, or independent-validation work remains.
- **Diagnostic:** the calculation tests a restricted limit, approximation, or subsystem and is not the full production prediction.
- **Historical:** retained to preserve provenance but not the current adopted baseline.
- **Superseded:** replaced by a newer result, with the earlier record retained.

A result may have more than one applicable descriptor, for example “reproducible diagnostic” or “historical validated benchmark.” State the scope of every validation claim.

## 6. Current project example: nucleon and nuclear structure

For the current vector-current three-body calculation, the adopted B baseline distinguishes two physical layers:

- \(F_1^{V,N}(t_N)\) and \(F_2^{V,N}(t_N)\) describe the finite-momentum Dirac–Pauli structure of an individual nucleon.
- \(W_M^{\tau\tau'}(y_A)\) is the AFH finite-size nuclear mass/density response, which describes the coherent nuclear structure.

These objects are not interchangeable. In particular, AFH \(W_M\) is not a point-nucleus response. A point-nucleus treatment is a separate approximation or limiting model. A normalized whole-nucleus density form factor, if used, is a further distinct object and must have its definition and normalization stated explicitly.

For the adopted B prescription, the finite-\(t_N\) nucleon form factors and the finite-size AFH response are both retained. The specific impulse prescription for relating \(t_N\) to nuclear recoil kinematics must be taken from the approved current theory convention and recorded in the calculation metadata. A manuscript equation or an old diagnostic script cannot independently establish that prescription.

This example illustrates the hierarchy; it does not declare every possible one-body nuclear-current response complete. Additional response channels require their own matching and validation.

## 7. Versioning and change control

- Store governing conventions in dated, reviewable research records, not only in chat messages, figures, or source-code comments.
- When a convention changes, create a new version or a dated change record. State the old and new definitions, reason for the change, affected calculations, and outputs that must be regenerated.
- Update tests to lock the new convention and add regression checks that prevent accidental reversion.
- Do not delete or silently rewrite superseded research records. Link the new result to the old one and explain the relationship.
- Update the manuscript after the research record is accepted. Cite or point to the underlying research record where useful so that the paper remains traceable to the calculation.

## 8. Relationship to existing repository policy

This document supplements and clarifies:

- [Repository research workflow](WORKFLOW.md)
- [Repository instructions](../AGENTS.md)
- [Contribution guide](../CONTRIBUTING.md)
- [Research archive index](README.md)

If an older instruction appears to make a manuscript equation the authority for a physical prescription, apply this hierarchy: the manuscript is reference material, and the governing convention must be supported by an approved derivation and research record. Update the older instruction through a reviewed repository change rather than silently ignoring the discrepancy.
