# Research artifact archives

This directory contains versioned requests and standard-library tooling for preserving GitHub Actions numerical artifacts as permanent research records.

## Rules

- A successful workflow artifact is a transport/source record, not a permanent archive.
- Preserve the exact source workflow run ID, source commit SHA, artifact ID/name, GitHub-reported digest, artifact byte size, and source URL.
- Download the original artifact ZIP and verify its SHA-256 against GitHub metadata before extraction.
- Extract and commit native CSV/JSON/TXT outputs; do not rely on the ZIP alone.
- Generate a run manifest and per-file SHA256SUMS. The checksum list covers the manifest, README, raw ZIP, and extracted files; it excludes only SHA256SUMS itself.
- Preserve superseded source runs when they establish provenance. If a later rerun has byte-identical extracted files, record the equivalence and keep the canonical extraction unambiguous.
- Keep archive status separate from scientific validation status and detector-level prediction status.

## PR #78 / PR #80 archive

The request [lz-pr78-pr80-2026-11-20.json](requests/lz-pr78-pr80-2026-11-20.json) pins the original PR #78 artifact, the final PR #74 integration rerun containing the PR #78 work, and the PR #80 B-baseline artifact.

The standard-library builder [build_pr78_pr80_archive.py](build_pr78_pr80_archive.py) verifies run/artifact metadata, source ZIP digests, ZIP member paths, byte-identical halo payloads, expected CSV row counts and isotope grids, B-baseline conventions, covariance settings, and quadrature-convergence summaries. The GitHub Actions workflow .github/workflows/archive-lz-pr78-pr80-artifacts.yml downloads and extracts the pinned artifacts, runs the builder, verifies SHA256SUMS, and commits the native outputs to the integration branch.

The resulting archives live in the corresponding study directories:

- [Halo/seven-isotope output archive](../three_body_phase_space_ID_validation/results/2026-11-19-halo-seven-isotope-full-vs-ID-full-recoil-scan/README.md).
- [Finite-nucleon B-baseline output archive](../nucleon_form_factor_B_baseline/results/2026-11-19-finite-nucleon-form-factor-B-baseline/README.md).

## Reuse

For another study, create a new request JSON with pinned successful run IDs, artifact IDs, expected SHA-256 digests, source commit SHAs, and destination paths. Add a corresponding narrowly scoped workflow trigger and validator. Do not overwrite a prior archive; create a new dated result directory and link the successor from the study README.
