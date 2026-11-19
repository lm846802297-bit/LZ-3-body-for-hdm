# Contributing and research workflow

This repository is organized around reproducible research. Before starting
work or submitting a change, read [research/WORKFLOW.md](research/WORKFLOW.md),
the mandatory [research source hierarchy](research/RESEARCH_GOVERNANCE_AND_SOURCE_HIERARCHY.md),
and the [Research Task Handoff Standard](research/RESEARCH_TASK_HANDOFF_STANDARD.md).

## In brief

For every substantive research task, first create a filled [Research Task Brief](research/_template/RESEARCH_TASK_BRIEF.md) and follow the [handoff standard](research/RESEARCH_TASK_HANDOFF_STANDARD.md). Keep the brief with the topic archive and link it from the PR. A brief may be marked not applicable for a trivial editorial or maintenance-only change, with a short reason in the PR.


1. Create a topic branch from the latest main.
2. Put research-specific material under research/<topic>/.
3. Include a study README describing the question, assumptions, inputs,
   environment, reproduction command, tests, results, and limitations.
   **When a submission or calculation result is supplied as ZIP/TAR, extract it
   before committing. Upload the extracted native files individually** (source
   code, tests, inputs, CSV/JSON/ROOT/HDF5/TXT outputs, reports, metadata, and
   manifests) into the appropriate research directory. A delivery ZIP/TAR is
   a transfer container, not the repository archive, and must not be committed
   as a substitute for its extracted contents. Preserve an original upstream
   archive only when its exact container is needed for provenance or
   reproducibility; record its source/version, size, SHA-256, extraction
   command, and per-file checksums, and still commit the required extracted
   files when redistribution is permitted. Commit the run manifest,
   provenance, and checksums alongside the native files.
4. Run the relevant tests and research workflow before opening a PR.
5. Submit a pull request to main using the repository PR template.
6. Merge only after the structure check and all relevant scientific checks
   have passed and the result's validation status is stated accurately.
7. After merge, verify the archived files on main against the submitted paths,
   file counts, sizes, and SHA-256 checksums. Report archival and physics
   validation as separate statuses.

The original manuscript source belongs in paper-source/. Do not modify
paper-source/main_original.tex or replace original source assets as part of
an ordinary research-code PR.

## Merge strategy

The default merge method for research and substantive changes is **Create a merge commit**. This preserves the topic branch's individual commits and makes the PR boundary explicit, which is valuable for tracing equations, numerical implementations, tests, corrections, and result provenance. Use Squash and merge only for genuinely trivial, indivisible maintenance or documentation batches whose individual commits carry no useful research history. Use Rebase and merge only when a linear history is intentionally required and the topic commits are already meaningful and reviewable. See [research/WORKFLOW.md](research/WORKFLOW.md#6-merge-strategy-and-commit-history-policy) for the full policy.
