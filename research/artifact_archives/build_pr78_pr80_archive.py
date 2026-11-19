#!/usr/bin/env python3
"""Validate and manifest the preserved PR #78/#80 GitHub Actions outputs.

Uses only the Python standard library. Run from the repository root after the
workflow downloads the source artifacts and extracts the selected payloads.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HALO_REL = Path(
    "research/three_body_phase_space_ID_validation/results/"
    "2026-11-19-halo-seven-isotope-full-vs-ID-full-recoil-scan"
)
B_REL = Path(
    "research/nucleon_form_factor_B_baseline/results/"
    "2026-11-19-finite-nucleon-form-factor-B-baseline"
)
ISOTOPES = {"128", "129", "130", "131", "132", "134", "136"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def zip_payload_hashes(path: Path) -> dict[str, str]:
    result = {}
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            member = PurePosixPath(info.filename)
            require(not member.is_absolute() and ".." not in member.parts,
                    f"unsafe ZIP member path: {info.filename}")
            result[info.filename] = hashlib.sha256(z.read(info.filename)).hexdigest()
    return result


def verify_extracted(zip_path: Path, extracted_dir: Path) -> dict[str, str]:
    expected = zip_payload_hashes(zip_path)
    actual = {
        p.relative_to(extracted_dir).as_posix(): sha256(p)
        for p in extracted_dir.rglob("*") if p.is_file()
    }
    require(expected == actual,
            f"extracted payload differs from {zip_path.name}: "
            f"expected {len(expected)} files, found {len(actual)}")
    return actual


def check_run_and_artifact(meta_dir: Path, key: str, expected: dict) -> dict:
    run = read_json(meta_dir / f"{key}_run.json")
    artifact = read_json(meta_dir / f"{key}_artifact.json")
    require(run.get("id") == expected["run_id"], f"{key}: wrong workflow run ID")
    require(run.get("conclusion") == "success", f"{key}: workflow run not successful")
    require(run.get("head_sha") == expected["head_sha"], f"{key}: wrong source commit")
    require(run.get("name") == expected["workflow_name"], f"{key}: wrong workflow name")
    require(artifact.get("id") == expected["artifact_id"], f"{key}: wrong artifact ID")
    require(artifact.get("name") == expected["artifact_name"], f"{key}: wrong artifact name")
    require(artifact.get("digest") == f"sha256:{expected['sha256']}",
            f"{key}: GitHub artifact digest does not match the pinned digest")
    require(not artifact.get("expired", False), f"{key}: source artifact is expired")
    wr = artifact.get("workflow_run") or {}
    require(wr.get("id") == expected["run_id"], f"{key}: artifact/run association mismatch")
    require(wr.get("head_sha") == expected["head_sha"], f"{key}: artifact source SHA mismatch")
    return {
        "key": key,
        "workflow_run": {
            "id": run["id"],
            "name": run["name"],
            "conclusion": run["conclusion"],
            "head_branch": run.get("head_branch"),
            "head_sha": run["head_sha"],
            "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"),
            "url": run.get("html_url"),
            "workflow_id": run.get("workflow_id"),
            "event": run.get("event"),
        },
        "artifact": {
            "id": artifact["id"],
            "name": artifact["name"],
            "size_in_bytes": artifact.get("size_in_bytes"),
            "digest": artifact["digest"],
            "digest_verified": True,
            "created_at": artifact.get("created_at"),
            "expires_at_at_source": artifact.get("expires_at"),
            "url": artifact.get("url"),
        },
        "expected_sha256": expected["sha256"],
    }


def file_inventory(root: Path) -> list[dict]:
    items = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name == "SHA256SUMS":
            continue
        items.append({
            "path": p.relative_to(root).as_posix(),
            "size_bytes": p.stat().st_size,
            "sha256": sha256(p),
        })
    return items


def write_manifest_and_sums(root: Path, manifest: dict) -> None:
    (root / "RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS":
            lines.append(f"{sha256(p)}  {p.relative_to(root).as_posix()}")
    (root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for line in lines:
        digest, rel = line.split("  ", 1)
        require(sha256(root / rel) == digest, f"checksum self-check failed: {rel}")


def validate_halo(root: Path) -> dict:
    extracted = root / "extracted"
    baseline = extracted / "halo-seven-isotope-baseline"
    high = extracted / "halo-seven-isotope-highorder"
    qcmp = extracted / "halo-seven-isotope-quadrature-comparison"

    baseline_meta = read_json(baseline / "metadata.json")
    high_meta = read_json(high / "metadata.json")
    require(baseline_meta["status"] == "COMPUTED" and high_meta["status"] == "COMPUTED",
            "halo metadata is not COMPUTED")
    require(baseline_meta["isotopes"] == [128, 129, 130, 131, 132, 134, 136],
            "unexpected AFH isotope set")
    require(high_meta["isotopes"] == baseline_meta["isotopes"], "isotope-set mismatch")
    require(abs(baseline_meta["natural_atom_fraction_AFH_coverage"] - 0.998158) < 1e-12,
            "unexpected natural-xenon AFH coverage")
    require(baseline_meta["abundances_not_renormalized"] is True,
            "natural isotope abundances were unexpectedly renormalized")
    require(baseline_meta["benchmark"]["speed_order_per_smooth_segment"] == 24,
            "unexpected baseline halo speed order")
    require(high_meta["benchmark"]["speed_order_per_smooth_segment"] == 32,
            "unexpected higher-order halo speed order")
    require(baseline_meta["benchmark"]["internal_quadrature_nw_nz_nphi"] == [8, 4, 4],
            "unexpected baseline internal quadrature")
    require(high_meta["benchmark"]["internal_quadrature_nw_nz_nphi"] == [12, 4, 4],
            "unexpected higher-order internal quadrature")

    row_counts = {}
    max_isotope_error = 0.0
    for label, directory in (("baseline", baseline), ("highorder", high)):
        iso = read_csv(directory / "seven_isotope_halo_comparison.csv")
        nat = read_csv(directory / "natural_xenon_halo_comparison.csv")
        require(len(iso) == 1456, f"{label}: expected 1456 isotope rows")
        require(len(nat) == 208, f"{label}: expected 208 natural-xenon rows")
        require({r["A"] for r in iso} == ISOTOPES, f"{label}: isotope IDs mismatch")
        require(len({r["ER_keV"] for r in iso}) == 208, f"{label}: isotope recoil grid mismatch")
        require(len({r["ER_keV"] for r in nat}) == 208, f"{label}: natural recoil grid mismatch")
        errors = [abs(float(r["isotope_relative_error_pct"]))
                  for r in iso if r["isotope_relative_error_pct"]]
        if errors:
            max_isotope_error = max(max_isotope_error, max(errors))
        row_counts[label] = {"seven_isotope_rows": len(iso), "natural_xenon_rows": len(nat)}
    summary = read_json(qcmp / "quadrature_convergence_summary.json")
    require(summary["status"] == "COMPUTED", "halo quadrature summary is not COMPUTED")
    require(summary["natural_xenon"]["support_mismatch_count"] == 0,
            "natural-xenon quadrature support mismatch")
    require(summary["seven_isotopes"]["support_mismatch_count"] == 0,
            "isotope quadrature support mismatch")
    require(summary["natural_xenon"]["max_abs_full_rate_shift_active_pct"] < 2e-5,
            "natural-xenon full-rate quadrature shift exceeds archive threshold")
    require(summary["natural_xenon"]["max_abs_ID_rate_shift_active_pct"] < 2e-5,
            "natural-xenon I(D) quadrature shift exceeds archive threshold")
    require(summary["seven_isotopes"]["max_abs_full_rate_shift_active_pct"] < 2e-5,
            "isotope full-rate quadrature shift exceeds archive threshold")
    high_nat = read_csv(high / "natural_xenon_halo_comparison.csv")
    natural_errors = [abs(float(r["relative_error_pct"]))
                      for r in high_nat if r["relative_error_pct"]]
    require(bool(natural_errors), "no active natural-xenon comparison points")
    return {
        "status": "COMPUTED; quadrature-converged on the archived grid",
        "benchmark": baseline_meta["benchmark"],
        "isotopes": baseline_meta["isotopes"],
        "natural_atom_fraction_AFH_coverage": baseline_meta["natural_atom_fraction_AFH_coverage"],
        "abundances_not_renormalized": True,
        "recoil_points": 208,
        "row_counts": row_counts,
        "max_abs_isotope_full_vs_ID_error_pct_highorder": max_isotope_error,
        "max_abs_natural_xenon_full_vs_ID_error_pct_highorder": max(natural_errors),
        "quadrature_convergence": summary,
        "scope": "Halo-folded rate-ratio validation; no detector response, exposure, efficiency, or likelihood.",
    }


def validate_B(root: Path) -> dict:
    extracted = root / "extracted"
    models = ("sufian2017_unit_current", "alexandrou2020_charge_weighted_converted")
    row_counts = {}
    model_summaries = {}
    max_abs_error = 0.0
    max_abs_shift = {}
    max_quad_shift = 0.0

    for tier in ("B-baseline", "B-highorder"):
        for model in models:
            d = extracted / tier / model
            meta = read_json(d / "metadata.json")
            require(meta["status"] == "COMPUTED", f"{tier}/{model}: not COMPUTED")
            require(meta["baseline"] == "B = finite nucleon F1(t_N), F2(t_N) times finite-size AFH W_M(y_A)",
                    f"{tier}/{model}: wrong physical baseline")
            require(meta["momentum_transfer"]["Q_A2_GeV2"] == "2*m_A*E_R+E_R^2",
                    f"{tier}/{model}: wrong nuclear momentum transfer")
            require(meta["momentum_transfer"]["t_N_GeV2"] == "-Q_A^2",
                    f"{tier}/{model}: wrong nucleon invariant")
            require(meta["momentum_transfer"]["q_NR_used_for_FF"] is False,
                    f"{tier}/{model}: q_NR incorrectly used for form factors")
            require(meta["matching"]["normalized_nucleon_factor"] == "F_M=c_M/3",
                    f"{tier}/{model}: wrong normalization")
            require(meta["matching"]["rate_multiplier"] == "|F_M|^2",
                    f"{tier}/{model}: wrong rate multiplier")
            require("finite-size W_M" in meta["matching"]["nuclear_response"],
                    f"{tier}/{model}: AFH finite-size response missing")
            unc = meta["uncertainty"]
            require(unc["Ye2020_EM_form_factor_covariance_draws"] == 3000,
                    f"{tier}/{model}: covariance draw count mismatch")
            require(unc["seed"] == 20261119, f"{tier}/{model}: covariance seed mismatch")
            require(unc["detector_response_applied"] is False,
                    f"{tier}/{model}: detector response flag must be false")
            require("not sampled" in unc["strange_lattice_errors"],
                    f"{tier}/{model}: strange-lattice uncertainty status changed")
            iso = read_csv(d / "seven_isotope_B_baseline.csv")
            nat = read_csv(d / "natural_xenon_B_baseline.csv")
            require(len(iso) == 1456, f"{tier}/{model}: expected 1456 isotope rows")
            require(len(nat) == 208, f"{tier}/{model}: expected 208 natural-xenon rows")
            require({r["A"] for r in iso} == ISOTOPES, f"{tier}/{model}: isotope IDs mismatch")
            require(len({r["ER_keV"] for r in nat}) == 208, f"{tier}/{model}: recoil grid mismatch")
            row_counts[f"{tier}/{model}"] = {
                "seven_isotope_rows": len(iso), "natural_xenon_rows": len(nat)
            }
            summary = meta["summary"]
            max_abs_error = max(max_abs_error, abs(summary["max_abs_full_vs_ID_error_B_pct"]))
            max_abs_shift[model] = max(
                max_abs_shift.get(model, 0.0),
                abs(summary["max_abs_B_over_A_full_rate_shift_pct"]),
            )
            if tier == "B-highorder":
                model_summaries[model] = {
                    "strange_form_factor_model": model,
                    "max_abs_full_vs_ID_error_B_pct": summary["max_abs_full_vs_ID_error_B_pct"],
                    "max_abs_B_over_A_full_rate_shift_pct": summary["max_abs_B_over_A_full_rate_shift_pct"],
                    "form_factor_source": meta["form_factor_source"],
                    "input_halo_directory": meta["input_halo_directory"],
                }

    for model in models:
        q = read_json(extracted / "B-quadrature-comparison" / model / "summary.json")
        nx = q["natural_xenon"]
        max_quad_shift = max(
            max_quad_shift,
            abs(nx["max_abs_full_B_rate_shift_pct"]),
            abs(nx["max_abs_I_D_B_rate_shift_pct"]),
            abs(nx["max_abs_approximation_error_shift_pp"]),
        )
    require(max_quad_shift < 2e-5, "B quadrature shift exceeds archive threshold")
    return {
        "status": "COMPUTED; B baseline quadrature-converged on the archived grid",
        "baseline": "finite nucleon F1(t_N), F2(t_N) multiplied by finite-size AFH W_M(y_A)",
        "momentum_transfer": {
            "Q_A2_GeV2": "2*m_A*E_R+E_R^2",
            "t_N_GeV2": "-Q_A^2",
            "q_NR_used_for_form_factors": False,
        },
        "strange_current_scenarios": list(models),
        "Ye2020_covariance_draws": 3000,
        "covariance_seed": 20261119,
        "recoil_points": 208,
        "row_counts": row_counts,
        "models_highorder": model_summaries,
        "max_abs_full_vs_ID_error_B_pct": max_abs_error,
        "max_abs_B_over_A_full_rate_shift_pct_by_model": max_abs_shift,
        "max_abs_B_quadrature_shift_pct_or_pp": max_quad_shift,
        "scope": "Rate-level B baseline; no detector response, efficiency, energy resolution, exposure, cuts, or likelihood.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-dir", required=True, type=Path)
    args = parser.parse_args()
    meta_dir = args.metadata_dir

    request_path = ROOT / "research/artifact_archives/requests/lz-pr78-pr80-2026-11-20.json"
    request = read_json(request_path)
    expected = {x["key"]: x for x in request["artifacts"]}
    provenance = {
        key: check_run_and_artifact(meta_dir, key, item)
        for key, item in expected.items()
    }

    halo_root = ROOT / HALO_REL
    b_root = ROOT / B_REL
    halo_original_zip = halo_root / "source-artifact-pr78-original.zip"
    halo_final_zip = halo_root / "source-artifact-pr74-final-rerun.zip"
    b_zip = b_root / "source-artifact-pr80.zip"

    for path, key in (
        (halo_original_zip, "halo_pr78_original"),
        (halo_final_zip, "halo_pr74_final"),
        (b_zip, "b_pr80"),
    ):
        require(path.exists(), f"missing source artifact ZIP: {path}")
        require(sha256(path) == expected[key]["sha256"], f"source artifact SHA-256 mismatch: {key}")

    original_payload = zip_payload_hashes(halo_original_zip)
    final_payload = verify_extracted(halo_final_zip, halo_root / "extracted")
    require(original_payload == final_payload,
            "PR #78 original and PR #74 final-rerun extracted payloads are not byte-identical")
    b_payload = verify_extracted(b_zip, b_root / "extracted")

    halo_summary = validate_halo(halo_root)
    b_summary = validate_B(b_root)

    halo_manifest = {
        "manifest_schema_version": 1,
        "archive_generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": request["repository"],
        "archive_status": "ARCHIVED_AND_VALIDATED",
        "study": "Halo-folded full three-body L00 vs I(D_NR), AFH seven-isotope natural xenon",
        "integration_lineage": {
            "pr_78": "Merged into the PR #74 research branch; its calculation and outputs are present in the PR #74 integration.",
            "pr_74": {
                "merged_to_main": True,
                "merge_commit": request["main_integration"]["pr74_merge_commit"],
            },
            "pr_82": "Current integration PR carrying the B baseline and this permanent output archive.",
        },
        "source_workflow_runs": {
            "pr78_original_run": provenance["halo_pr78_original"],
            "pr74_final_rerun": provenance["halo_pr74_final"],
        },
        "payload_equivalence": {
            "pr78_original_vs_pr74_final_rerun": "BYTE_IDENTICAL",
            "member_file_count": len(original_payload),
            "note": "The two ZIP containers have different archive-level SHA-256 values; every extracted member has the same path and SHA-256.",
        },
        "result_summary": halo_summary,
        "file_inventory": file_inventory(halo_root),
    }
    b_manifest = {
        "manifest_schema_version": 1,
        "archive_generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": request["repository"],
        "archive_status": "ARCHIVED_AND_VALIDATED",
        "study": "Finite nucleon Dirac-Pauli form factors multiplied by finite-size AFH W_M",
        "integration_lineage": {
            "upstream_halo": {
                "workflow_run_id": 44560087038,
                "artifact_id": 14551462445,
                "artifact_sha256": "6d3d711341cdd33200721fc9371c0dcac2ba3b0354043c09c903d89650b40103",
                "source_commit": "9ca1801cdded7002c93776f8a0f5bce894135356",
                "note": "This is the halo artifact run consumed by the PR #80 B-baseline workflow; its extracted payload is byte-identical to the later PR #74 final rerun.",
            },
            "pr80": "B-baseline implementation and successful numerical workflow.",
            "pr74_main_merge_commit": request["main_integration"]["pr74_merge_commit"],
            "pr82": "Current integration PR carrying this permanent output archive.",
        },
        "source_workflow_run": provenance["b_pr80"],
        "result_summary": b_summary,
        "file_inventory": file_inventory(b_root),
    }

    write_manifest_and_sums(halo_root, halo_manifest)
    write_manifest_and_sums(b_root, b_manifest)
    print(json.dumps({
        "halo": {
            "files": len(file_inventory(halo_root)),
            "zip_sha256": {
                "pr78_original": sha256(halo_original_zip),
                "pr74_final": sha256(halo_final_zip),
            },
            "summary": halo_summary,
        },
        "B": {
            "files": len(file_inventory(b_root)),
            "zip_sha256": sha256(b_zip),
            "summary": b_summary,
        },
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
