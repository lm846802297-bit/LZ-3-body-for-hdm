#!/usr/bin/env python3
"""Validate research result JSON records and their local output files."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print("ERROR: install jsonschema>=4.18,<5 first.", file=sys.stderr)
    raise SystemExit(2)


def reject_nonstandard_constant(value: str):
    raise ValueError(f"non-standard JSON numeric constant is forbidden: {value}")


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream, parse_constant=reject_nonstandard_constant)


def referenced_files(record: dict):
    if record.get("record_type") == "run_manifest":
        return record.get("outputs", [])
    if record.get("record_type") == "result_summary":
        return record.get("data_files", [])
    return []


def resolve_repo_path(root: Path, relative_path: str, errors: list):
    rel = Path(relative_path)
    if rel.is_absolute() or ".." in rel.parts:
        errors.append(f"{relative_path}: path must be repository-relative and cannot escape the repo")
        return None
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        errors.append(f"{relative_path}: resolved path escapes repository root")
        return None
    return target


def verify_inputs(record: dict, repo_root: Path):
    errors, warnings = [], []
    if record.get("record_type") != "run_manifest":
        return errors, warnings
    root = repo_root.resolve()
    for item in record.get("inputs", []):
        if not item.get("path"):
            continue
        target = resolve_repo_path(root, item["path"], errors)
        if target is None:
            continue
        if not target.is_file():
            if item.get("uri"):
                warnings.append(f"{item['path']}: external input not present locally; URI/version retained")
            else:
                errors.append(f"{item['path']}: referenced input file does not exist")
            continue
        if item.get("bytes") is not None and target.stat().st_size != item["bytes"]:
            errors.append(f"{item['path']}: input byte size {target.stat().st_size} != manifest {item['bytes']}")
        if item.get("sha256"):
            digest = hashlib.sha256()
            with target.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != item["sha256"]:
                errors.append(f"{item['path']}: input SHA-256 mismatch")
    return errors, warnings


def verify_artifacts(record: dict, repo_root: Path):
    errors, warnings = [], []
    root = repo_root.resolve()
    for item in referenced_files(record):
        target = resolve_repo_path(root, item["path"], errors)
        if target is None:
            continue
        if not target.is_file():
            if item.get("uri"):
                warnings.append(f"{item['path']}: external artifact not present locally; URI/version retained")
            else:
                errors.append(f"{item['path']}: referenced output file does not exist")
            continue

        actual_bytes = target.stat().st_size
        if actual_bytes != item["bytes"]:
            errors.append(f"{item['path']}: byte size {actual_bytes} != manifest {item['bytes']}")

        digest = hashlib.sha256()
        with target.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if digest.hexdigest() != item["sha256"]:
            errors.append(f"{item['path']}: SHA-256 mismatch")

        if item["format"].lower() == "csv":
            try:
                with target.open("r", encoding="utf-8-sig", newline="") as stream:
                    reader = csv.reader(stream)
                    header = next(reader, None)
                    if header is None:
                        errors.append(f"{item['path']}: CSV is empty and has no header")
                        continue
                    if len(header) != len(set(header)):
                        errors.append(f"{item['path']}: duplicate CSV column names")
                    if item.get("columns") is not None and header != item["columns"]:
                        errors.append(f"{item['path']}: CSV header differs from manifest columns")
                    unit_columns = set(item.get("units", {}))
                    missing_unit_columns = set(header) - unit_columns
                    unknown_unit_columns = unit_columns - set(header)
                    if missing_unit_columns:
                        errors.append(f"{item['path']}: unit map is missing columns {sorted(missing_unit_columns)}")
                    if unknown_unit_columns:
                        errors.append(f"{item['path']}: unit map contains unknown columns {sorted(unknown_unit_columns)}")
                    row_count = 0
                    for row in reader:
                        row_count += 1
                        if len(row) != len(header):
                            errors.append(f"{item['path']}: row {row_count + 1} has {len(row)} fields; expected {len(header)}")
                            continue
                        for col_name, cell in zip(header, row):
                            if not cell.strip():
                                continue
                            try:
                                numeric = float(cell)
                            except ValueError:
                                continue
                            if not math.isfinite(numeric):
                                errors.append(f"{item['path']}: non-finite numeric value in {col_name}, data row {row_count}")
                    if item.get("rows") is not None and row_count != item["rows"]:
                        errors.append(f"{item['path']}: CSV has {row_count} data rows; manifest says {item['rows']}")
            except (OSError, UnicodeError, csv.Error) as exc:
                errors.append(f"{item['path']}: CSV read failed: {exc}")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path, help="JSON record files to validate")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="repository root for output paths")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().with_name("research-result-record-v1.0.0.schema.json"),
        help="JSON Schema Draft 2020-12 file",
    )
    args = parser.parse_args()

    try:
        schema = load_json(args.schema)
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        print(f"ERROR: invalid schema {args.schema}: {exc}", file=sys.stderr)
        return 2

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failed = False
    for record_path in args.records:
        try:
            record = load_json(record_path)
        except Exception as exc:
            print(f"FAIL {record_path}: JSON parse error: {exc}")
            failed = True
            continue

        errors = sorted(
            validator.iter_errors(record),
            key=lambda error: (list(map(str, error.absolute_path)), error.message),
        )
        if errors:
            print(f"FAIL {record_path}: schema validation")
            for error in errors:
                location = ".".join(map(str, error.absolute_path)) or "<root>"
                print(f"  - {location}: {error.message}")
            failed = True
            continue

        input_errors, input_warnings = verify_inputs(record, args.repo_root)
        file_errors, file_warnings = verify_artifacts(record, args.repo_root)
        integrity_errors = input_errors + file_errors
        if integrity_errors:
            print(f"FAIL {record_path}: input/output integrity")
            for error in integrity_errors:
                print(f"  - {error}")
            failed = True
        else:
            print(f"PASS {record_path}: schema and local input/output integrity")
        for warning in input_warnings + file_warnings:
            print(f"WARN {record_path}: {warning}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
