#!/usr/bin/env python3
"""Verify the committed 121-node Xe-131 dense charge-dip provenance manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_MANIFEST = (
    SCRIPT_DIR / "output" / "xe131-dense-charge-dip" / "sha256_manifest.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return path if path.is_absolute() else REPO_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
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

    validation_path = resolve(manifest["files"]["validation_json"]["path"])
    if validation_path.is_file():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        if validation.get("status") != manifest["validation"]["status"]:
            failures.append(
                "validation status mismatch: "
                f"{validation.get('status')!r} != {manifest['validation']['status']!r}"
            )
        if validation.get("rows") != manifest["validation"]["rows"]:
            failures.append("validation row count mismatch")
        if validation.get("common_nodes_compared") != manifest["validation"]["common_nodes_compared"]:
            failures.append("validation overlap-node count mismatch")
        if not validation.get("native_afh_dense_q_validated"):
            failures.append("validation did not assert native_afh_dense_q_validated")

        recorded = {
            "dense_csv": validation.get("dense_csv_sha256"),
            "dense_metadata": validation.get("dense_metadata_sha256"),
            "afh_source": validation.get("AFH_source_sha256"),
            "coarse_native_csv": validation.get("coarse_native_csv_sha256"),
        }
        for name, digest in recorded.items():
            if digest != manifest["files"][name]["sha256"]:
                failures.append(f"validation JSON records stale {name} sha256")

    summary = {
        "status": "PASS_PROVENANCE_XE131_DENSE_CHARGE_DIP" if not failures else "FAIL_PROVENANCE",
        "artifact": manifest["artifact"],
        "files_checked": len(manifest["files"]),
        "responses": manifest["scope"]["responses"],
        "rows": manifest["validation"]["rows"],
        "common_nodes_compared": manifest["validation"]["common_nodes_compared"],
        "not_validated_here": manifest["scope"]["not_validated_here"],
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
