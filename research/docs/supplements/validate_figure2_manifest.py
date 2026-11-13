#!/usr/bin/env python3
"""Validate the Figure 2 benchmark/input/output SHA-256 master manifest."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = Path(__file__).with_name(
    "figure2_results_master_index_2026-11-13.json"
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def fail(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}")
    raise SystemExit(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checked_repo_path(raw: str, label: str, errors: list[str]) -> Path | None:
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{label}: path must be repository-relative and traversal-free: {raw}")
        return None
    resolved = (ROOT / relative).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError:
        errors.append(f"{label}: path escapes repository root: {raw}")
        return None
    return resolved


def main() -> None:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        fail([f"missing manifest: {MANIFEST_PATH.relative_to(ROOT)}"])

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail([f"cannot read valid JSON manifest: {exc}"])

    entries = manifest.get("files")
    groups = manifest.get("groups")
    if not isinstance(entries, list) or not isinstance(groups, list):
        fail(["manifest must contain top-level 'files' and 'groups' arrays"])

    seen_paths: set[str] = set()
    entry_by_path: dict[str, dict] = {}
    total_bytes = 0

    for index, entry in enumerate(entries):
        label = f"files[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected an object")
            continue

        raw_path = entry.get("path")
        expected_hash = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        role = entry.get("role")

        if not isinstance(raw_path, str) or not raw_path:
            errors.append(f"{label}: missing non-empty path")
            continue
        if raw_path in seen_paths:
            errors.append(f"{label}: duplicate manifest path: {raw_path}")
        seen_paths.add(raw_path)
        entry_by_path[raw_path] = entry

        if not isinstance(role, str) or not role.strip():
            errors.append(f"{label} ({raw_path}): missing descriptive role")
        if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
            errors.append(f"{label} ({raw_path}): sha256 must be 64 lowercase hex characters")
            continue
        if not isinstance(expected_bytes, int) or expected_bytes < 0:
            errors.append(f"{label} ({raw_path}): missing non-negative byte count")
            continue

        path = checked_repo_path(raw_path, label, errors)
        if path is None:
            continue
        if not path.is_file():
            errors.append(f"{label}: committed file does not exist: {raw_path}")
            continue

        actual_bytes = path.stat().st_size
        total_bytes += actual_bytes
        if actual_bytes != expected_bytes:
            errors.append(
                f"{raw_path}: byte count mismatch; manifest={expected_bytes}, actual={actual_bytes}"
            )
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            errors.append(
                f"{raw_path}: SHA-256 mismatch; manifest={expected_hash}, actual={actual_hash}"
            )

    group_ids: set[str] = set()
    for index, group in enumerate(groups):
        label = f"groups[{index}]"
        if not isinstance(group, dict):
            errors.append(f"{label}: expected an object")
            continue
        group_id = group.get("id")
        if not isinstance(group_id, str) or not group_id:
            errors.append(f"{label}: missing non-empty id")
        elif group_id in group_ids:
            errors.append(f"{label}: duplicate group id: {group_id}")
        else:
            group_ids.add(group_id)

        group_files = group.get("files")
        if not isinstance(group_files, list):
            errors.append(f"{label}: files must be an array")
            continue
        local_paths: set[str] = set()
        for item in group_files:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                errors.append(f"{label}: each group file must contain a path")
                continue
            raw_path = item["path"]
            if raw_path in local_paths:
                errors.append(f"{label}: duplicate file path in group: {raw_path}")
            local_paths.add(raw_path)
            master_entry = entry_by_path.get(raw_path)
            if master_entry is None:
                errors.append(f"{label}: group file is absent from top-level manifest: {raw_path}")
                continue
            group_hash = item.get("sha256")
            if group_hash is not None and group_hash != master_entry.get("sha256"):
                errors.append(f"{label}: group SHA-256 disagrees with top-level entry: {raw_path}")

    external = manifest.get("external_or_checksum_only_inputs", [])
    if not isinstance(external, list):
        errors.append("external_or_checksum_only_inputs must be an array")
    else:
        for index, item in enumerate(external):
            label = f"external_or_checksum_only_inputs[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: expected an object")
                continue
            digest = item.get("sha256")
            if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                errors.append(f"{label}: sha256 must be 64 lowercase hex characters")
            raw_path = item.get("repository_path")
            availability = str(item.get("availability", "")).lower()
            if raw_path is not None and "committed" in availability:
                path = checked_repo_path(str(raw_path), label, errors)
                if path is not None:
                    if not path.is_file():
                        errors.append(f"{label}: marked committed but file is missing: {raw_path}")
                    elif sha256(path) != digest:
                        errors.append(f"{label}: committed input SHA-256 mismatch: {raw_path}")
                    if str(raw_path) not in entry_by_path:
                        errors.append(f"{label}: committed input is not in top-level files: {raw_path}")

    if errors:
        fail(errors)

    print(
        f"Figure 2 manifest validation passed: {len(entries)} files, "
        f"{len(groups)} result groups, {total_bytes:,} verified bytes."
    )


if __name__ == "__main__":
    main()
