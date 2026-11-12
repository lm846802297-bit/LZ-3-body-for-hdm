#!/usr/bin/env python3
"""Extract the seven built-in xenon density matrices from AFH DMFormFactor v6.0.

The official package is treated as an immutable upstream input. This script
stores only the compact default-density matrices needed by the Python AFH
response translation; it does not redistribute the package itself.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ISOTOPES = (128, 129, 130, 131, 132, 134, 136)
FIELDS = (
    "index", "coefficient", "rank", "isospin",
    "Nprime", "two_jprime", "N", "two_j",
)
EXPECTED_PACKAGE_SHA256 = "dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372"
EXPECTED_ARCHIVE_SHA256 = "4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_density_matrix(package_text: str, A: int) -> list[dict]:
    marker = f"sdgXe{A}[1]"
    start = package_text.find(marker)
    if start < 0:
        raise RuntimeError(f"AFH source does not contain {marker}")
    end_marker = f"sdgXe{A}length"
    end = package_text.find(end_marker, start)
    if end < 0:
        raise RuntimeError(f"AFH source does not contain {end_marker}")
    block = package_text[start:end]

    number = r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    pattern = re.compile(
        rf"sdgXe{A}\[(\d+)\]\s*=\s*\{{[^=]+?=\s*{number}\s*,\s*"
        r"(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\}\s*;",
        re.S,
    )
    rows = []
    for match in pattern.finditer(block):
        index, coefficient, rank, isospin, nprime, two_jprime, n, two_j = match.groups()
        rows.append({
            "index": int(index),
            "coefficient": float(coefficient),
            "rank": int(rank),
            "isospin": int(isospin),
            "Nprime": int(nprime),
            "two_jprime": int(two_jprime),
            "N": int(n),
            "two_j": int(two_j),
        })

    if not rows:
        raise RuntimeError(f"No {A}Xe density-matrix entries parsed")
    indices = [row["index"] for row in rows]
    expected = list(range(1, len(rows) + 1))
    if indices != expected:
        raise RuntimeError(
            f"{A}Xe density-matrix indices are not contiguous: "
            f"first={indices[:5]}, last={indices[-5:]}, count={len(indices)}"
        )

    length_match = re.search(rf"{end_marker}\s*=\s*(\d+)", package_text[end:end + 256])
    if length_match and len(rows) != int(length_match.group(1)):
        raise RuntimeError(
            f"{A}Xe parsed {len(rows)} entries but AFH declares "
            f"{length_match.group(1)}"
        )
    return rows


def read_reference(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = []
        for row in csv.DictReader(handle):
            rows.append({
                "index": int(row["index"]),
                "coefficient": float(row["coefficient"]),
                "rank": int(row["rank"]),
                "isospin": int(row["isospin"]),
                "Nprime": int(row["Nprime"]),
                "two_jprime": int(row["two_jprime"]),
                "N": int(row["N"]),
                "two_j": int(row["two_j"]),
            })
    return rows


def write_matrix(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True,
                        help="Official dmformfactor-V6.m extracted from v6.zip")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--xe131-reference", type=Path, default=None,
                        help="Existing 67-entry Xe-131 CSV for exact regression")
    parser.add_argument("--expected-package-sha256", default=EXPECTED_PACKAGE_SHA256)
    parser.add_argument("--archive-sha256", default=EXPECTED_ARCHIVE_SHA256)
    args = parser.parse_args()

    package = args.package.resolve()
    package_hash = sha256(package)
    if args.expected_package_sha256 and package_hash != args.expected_package_sha256:
        raise RuntimeError(
            f"AFH package SHA-256 mismatch: {package_hash} != "
            f"{args.expected_package_sha256}"
        )
    source_text = package.read_text(encoding="utf-8", errors="strict")
    if "Welcome to DMFormFactor version 1.1." not in source_text:
        raise RuntimeError("Unexpected AFH DMFormFactor source/version marker")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    matrix_metadata = {}
    for A in ISOTOPES:
        rows = parse_density_matrix(source_text, A)
        if A == 131 and args.xe131_reference is not None:
            reference = read_reference(args.xe131_reference)
            if rows != reference:
                raise RuntimeError(
                    "Re-extracted sdgXe131 does not match the archived 67-entry CSV"
                )
        path = args.out_dir / f"afh_default_xe{A}_density_matrix.csv"
        write_matrix(path, rows)
        matrix_metadata[str(A)] = {
            "entries": len(rows),
            "file": path.name,
            "sha256": sha256(path),
            "rank_counts_tau0": {
                str(rank): sum(1 for row in rows
                               if row["rank"] == rank and row["isospin"] == 0)
                for rank in sorted({row["rank"] for row in rows})
            },
        }

    metadata = {
        "source": "AFH DMFormFactor v6.0",
        "source_url": "https://www.ocf.berkeley.edu/~nanand/software/dmformfactor/v6.zip",
        "source_archive_sha256": args.archive_sha256,
        "source_file": package.name,
        "source_file_sha256": package_hash,
        "source_selection": 'SetIsotope[54,A,"default","default"]',
        "isotopes": list(ISOTOPES),
        "matrices": matrix_metadata,
        "note": (
            "AFH v6.0 default xenon matrices exist for 128,129,130,131,132,134,136Xe. "
            "124Xe and 126Xe are not part of this built-in default set."
        ),
    }
    (args.out_dir / "density_matrix_extraction_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "source_file_sha256": package_hash,
        "isotopes": list(ISOTOPES),
        "entries": {A: matrix_metadata[str(A)]["entries"] for A in ISOTOPES},
        "out_dir": str(args.out_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
