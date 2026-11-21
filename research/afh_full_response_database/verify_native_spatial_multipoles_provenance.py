#!/usr/bin/env python3
"""Verify the committed native rank-resolved spatial multipole provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DEFAULT_DIR = SCRIPT_DIR / "output" / "native-spatial-multipoles"
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
    parser.add_argument("--validation", type=Path, default=DEFAULT_DIR / "spatial_multipoles_validation.json")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_DIR / "native_spatial_multipole_metadata.txt")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validation = json.loads(args.validation.read_text(encoding="utf-8"))
    metadata = parse_metadata(args.metadata)
    failures = []

    for name, entry in manifest["files"].items():
        path = resolve(entry["path"])
        if not path.is_file():
            failures.append(f"missing {name}: {entry['path']}")
            continue
        actual = sha256(path)
        if actual != entry["sha256"]:
            failures.append(f"{name} sha256 mismatch: expected {entry['sha256']}, got {actual}")

    if validation.get("status") != "PASS_NATIVE_AFH_SPATIAL_MULTIPOLES":
        failures.append("spatial validation status is not PASS")
    if validation.get("rows") != 9604:
        failures.append("spatial validation rows != 9604")
    if int(metadata.get("rows", "0")) != 9604:
        failures.append("spatial metadata rows != 9604")
    if metadata.get("rank_map") != "129=1;131=1,2,3":
        failures.append("spatial metadata rank map mismatch")
    if "q=0 value is the analytic y=0 limit" not in metadata.get("q_grid", ""):
        failures.append("spatial metadata does not document the q=0 analytic limit")

    summary = {
        "status": "PASS_PROVENANCE_NATIVE_AFH_SPATIAL" if not failures else "FAIL_PROVENANCE",
        "artifact": manifest["artifact"],
        "files_checked": len(manifest["files"]),
        "rows": 9604,
        "ranks": {"129": [1], "131": [1, 2, 3]},
        "scope": manifest["scope"],
        "failures": failures,
    }
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
