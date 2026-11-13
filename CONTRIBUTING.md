# Contributing and research workflow

This repository is organized around reproducible research. Please read
research/WORKFLOW.md before starting a new calculation or submitting a change.

## In brief

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

## Merge strategy

Use **Merge Commit by default** for substantive research PRs so that individual
derivation, implementation, numerical-validation, and result-archival commits
remain in the `main` history. Use Squash Merge only for documentation-only,
minor maintenance, or small cohesive changes whose intermediate commits have
no independent audit value. Use Rebase and Merge only when clean atomic commits
and a deliberately linear history are required; remember that it rewrites
commit SHAs. Do not squash multi-stage scientific work merely to shorten the
history. See [research/WORKFLOW.md](research/WORKFLOW.md#merge-strategy-and-research-traceability)
for the full policy and the provenance requirements when an exception is used.

The original manuscript source belongs in paper-source/. Do not modify
paper-source/main_original.tex or replace original source assets as part of
an ordinary research-code PR.
