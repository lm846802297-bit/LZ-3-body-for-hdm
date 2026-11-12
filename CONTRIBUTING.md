# Contributing and research workflow

This repository is organized around reproducible research. Please read
research/WORKFLOW.md before starting a new calculation or submitting a change.

## In brief

1. Create a topic branch from the latest main.
2. Put research-specific material under research/<topic>/.
3. Include a study README describing the question, assumptions, inputs,
   environment, reproduction command, tests, results, and limitations. Commit
   the essential native/uncompressed result files, run manifest, provenance,
   and checksums; do not create a new ZIP/TAR archive as a substitute for the
   extracted result files.
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
