#!/usr/bin/env python3
"""Verify the committed seven-isotope native AFH provenance and comparison gates."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_DIR = SCRIPT_DIR / "output" / "native"
DEFAULT_MANIFEST = DEFAULT_DIR / "sha256_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def parse_metadata(path: Path) -> dict:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--comparison", type=Path, default=DEFAULT_DIR / "native_comparison.json")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_DIR / "native_metadata.txt")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    comparison = json.loads(args.comparison.read_text(encoding="utf-8"))
    metadata = parse_metadata(args.metadata)
    failures = []

    for name, entry in manifest["files"].items():
        path = resolve(entry["path"])
        if not path.is_file():
            failures.append(f"missing {name}: {entry['path']}")
            continue
        actual = sha256(path)
        if actual != entry["sha256"]:
            failures.append(
                f"{name} sha256 mismatch: expected {entry['sha256']}, got {actual}"
            )

    if comparison.get("status") != "PASS":
        failures.append("native comparison status is not PASS")
    if not comparison.get("native_afh_validated"):
        failures.append("native comparison did not assert native_afh_validated")
    if comparison.get("rows_compared") != 16807:
        failures.append("native comparison did not cover 16807 rows")
    if comparison.get("expected_rows") != 16807:
        failures.append("native comparison expected row count is not 16807")

    if int(metadata.get("rows", "0")) != 16807:
        failures.append("native metadata rows != 16807")
    if metadata.get("AFH_source_sha256") != manifest["afh_source_sha256"]:
        failures.append("metadata AFH source hash disagrees with manifest")

    summary = {
        "status": "PASS_PROVENANCE_NATIVE_AFH_FULL" if not failures else "FAIL_PROVENANCE",
        "artifact": manifest["artifact"],
        "files_checked": len(manifest["files"]),
        "rows": 16807,
        "rows_compared": comparison.get("rows_compared"),
        "scope": manifest["scope"],
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
