#!/usr/bin/env python3
"""Verify and manifest the corrected PR #83 finite-nucleon B outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REL = Path("research/nucleon_form_factor_B_baseline/results/2026-11-20-corrected-B-baseline-pr83")
MODELS = (
    "sufian2017_unit_current",
    "alexandrou2020_charge_weighted_converted",
    "alexandrou2026_continuum_unit_current",
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


def verify_internal_sums(directory: Path, filename: str = "SHA256SUMS.txt") -> int:
    path = directory / filename
    require(path.exists(), f"missing internal checksum file: {path}")
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        target = directory / rel
        require(target.exists(), f"internal checksum target missing: {target}")
        require(sha256(target) == digest, f"internal checksum mismatch: {target}")
        count += 1
    return count


def check_source(meta_dir: Path, request: dict) -> dict:
    run = read_json(meta_dir / "source_run.json")
    artifact = read_json(meta_dir / "source_artifact.json")
    require(run.get("id") == request["run_id"], "wrong source workflow run ID")
    require(run.get("name") == request["workflow_name"], "wrong source workflow name")
    require(run.get("conclusion") == "success", "source workflow did not succeed")
    require(run.get("head_sha") == request["head_sha"], "source commit SHA mismatch")
    require(run.get("head_branch") == request["head_branch"], "source branch mismatch")
    require(artifact.get("id") == request["artifact_id"], "wrong artifact ID")
    require(artifact.get("name") == request["artifact_name"], "wrong artifact name")
    require(artifact.get("digest") == "sha256:" + request["artifact_sha256"],
            "GitHub artifact digest metadata mismatch")
    require(artifact.get("size_in_bytes") == request["artifact_size_bytes"],
            "GitHub artifact size mismatch")
    require(not artifact.get("expired", False), "source artifact is expired")
    workflow_run = artifact.get("workflow_run") or {}
    require(workflow_run.get("id") == request["run_id"], "artifact/run association mismatch")
    require(workflow_run.get("head_sha") == request["head_sha"], "artifact source SHA mismatch")
    return {
        "workflow_run": {
            "id": run["id"],
            "name": run["name"],
            "conclusion": run["conclusion"],
            "event": run.get("event"),
            "head_branch": run.get("head_branch"),
            "head_sha": run["head_sha"],
            "workflow_id": run.get("workflow_id"),
            "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"),
            "url": run.get("html_url"),
        },
        "artifact": {
            "id": artifact["id"],
            "name": artifact["name"],
            "size_in_bytes": artifact["size_in_bytes"],
            "digest": artifact["digest"],
            "digest_verified": True,
            "created_at": artifact.get("created_at"),
            "expires_at_at_source": artifact.get("expires_at"),
            "url": artifact.get("url"),
        },
    }


def file_inventory(root: Path) -> list[dict]:
    items = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name in {"RUN_MANIFEST.json", "SHA256SUMS"}:
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
        require(sha256(root / rel) == digest, f"archive checksum self-check failed: {rel}")


def validate_outputs(root: Path) -> dict:
    extracted = root / "extracted"
    row_counts = {}
    b_summary = {}
    max_quad_full = 0.0
    max_quad_id = 0.0
    max_quad_approx = 0.0
    max_abs_full_vs_id = 0.0
    max_abs_BA_shift = {}

    for tier in ("B-baseline", "B-highorder"):
        for model in MODELS:
            d = extracted / tier / model
            meta = read_json(d / "metadata.json")
            require(meta.get("status") == "COMPUTED", f"{tier}/{model}: not COMPUTED")
            require(meta.get("strange_form_factor_model") == model,
                    f"{tier}/{model}: strange model label mismatch")
            require("Borah" in meta.get("electromagnetic_form_factor_source", ""),
                    f"{tier}/{model}: wrong electromagnetic source")
            transfer = meta["momentum_transfer"]
            require(transfer["Q_A2_GeV2"] == "2*m_A*E_R+E_R^2",
                    f"{tier}/{model}: Q_A^2 convention mismatch")
            require(transfer["t_N_GeV2"] == "-Q_A^2",
                    f"{tier}/{model}: t_N convention mismatch")
            require(transfer["q_NR_used_for_FF"] is False,
                    f"{tier}/{model}: q_NR was used for form factors")
            matching = meta["matching"]
            require(matching["normalized_nucleon_factor"] == "F_M=c_M/3",
                    f"{tier}/{model}: F_M normalization mismatch")
            require(matching["rate_multiplier"] == "|F_M|^2",
                    f"{tier}/{model}: rate multiplier mismatch")
            require("finite-size W_M" in matching["nuclear_response"],
                    f"{tier}/{model}: finite-size AFH W_M is missing")
            unc = meta["uncertainty"]
            require(unc["Borah2020_EM_form_factor_covariance_draws"] == 3000,
                    f"{tier}/{model}: wrong covariance draw count")
            require(unc["seed"] == 20261119, f"{tier}/{model}: wrong covariance seed")
            require(unc["detector_response_applied"] is False,
                    f"{tier}/{model}: B output must remain rate-level")
            require("not sampled" in unc["strange_lattice_errors"],
                    f"{tier}/{model}: strange-lattice uncertainty status mismatch")

            iso = read_csv(d / "seven_isotope_B_baseline.csv")
            nat = read_csv(d / "natural_xenon_B_baseline.csv")
            require(len(iso) == 1456, f"{tier}/{model}: expected 1456 isotope rows")
            require(len(nat) == 208, f"{tier}/{model}: expected 208 natural-xenon rows")
            require({r["A"] for r in iso} == ISOTOPES, f"{tier}/{model}: isotope set mismatch")
            require(len({r["ER_keV"] for r in nat}) == 208,
                    f"{tier}/{model}: recoil grid mismatch")
            row_counts[f"{tier}/{model}"] = {
                "seven_isotope_rows": len(iso),
                "natural_xenon_rows": len(nat),
            }
            summary = meta["summary"]
            max_abs_full_vs_id = max(max_abs_full_vs_id,
                                     abs(summary["max_abs_full_vs_ID_error_B_pct"]))
            max_abs_BA_shift[model] = max(
                max_abs_BA_shift.get(model, 0.0),
                abs(summary["max_abs_B_over_A_full_rate_shift_pct"]),
            )
            if tier == "B-highorder":
                b_summary[model] = summary

    for model in MODELS:
        q = read_json(extracted / "B-quadrature-comparison" / model / "summary.json")
        nx = q["natural_xenon"]
        max_quad_full = max(max_quad_full, abs(nx["max_abs_full_B_rate_shift_pct"]))
        max_quad_id = max(max_quad_id, abs(nx["max_abs_I_D_B_rate_shift_pct"]))
        max_quad_approx = max(max_quad_approx, abs(nx["max_abs_approximation_error_shift_pp"]))
    require(max_quad_full < 2e-5, "B full-rate quadrature shift exceeds threshold")
    require(max_quad_id < 2e-5, "B I(D) quadrature shift exceeds threshold")
    require(max_quad_approx < 2e-5, "B approximation-error quadrature shift exceeds threshold")

    absolute_summary = {}
    detector_summary = {}
    for model in MODELS:
        d = extracted / "B-absolute" / model
        meta = read_json(d / "metadata.json")
        require(meta.get("status") == "PASS", f"B-absolute/{model}: status is not PASS")
        counts = meta["row_counts"]
        require(counts["natural_xenon_spectra"] == 672,
                f"B-absolute/{model}: expected 672 natural spectrum rows")
        require(counts["isotope_contributions"] == 3102,
                f"B-absolute/{model}: expected 3102 isotope rows")
        validation = meta["validation"]
        require(validation["maximum_A_reconstruction_relative_difference"] < 2e-11,
                f"B-absolute/{model}: A reconstruction closure failed")
        matching = meta["matching"]
        require(matching["Q_A2"] == "q_exact_spatial_GeV^2 = 2*m_A*E_R+E_R^2",
                f"B-absolute/{model}: wrong spatial transfer")
        require(matching["t_N"] == "-Q_A2 = -(2*m_A*E_R+E_R^2)",
                f"B-absolute/{model}: wrong nucleon invariant")
        require(matching["t_A"] == "-2*m_A*E_R (invariant transfer used in mediator propagator)",
                f"B-absolute/{model}: missing separate mediator transfer")
        require("AFH v6.0" in matching["nuclear_response"],
                f"B-absolute/{model}: AFH response provenance missing")
        abs_csv = read_csv(d / "afh_hybrid9_B_natural_xenon_spectrum.csv")
        iso_csv = read_csv(d / "afh_hybrid9_B_isotope_contributions.csv")
        require(len(abs_csv) == 672 and len(iso_csv) == 3102,
                f"B-absolute/{model}: CSV row counts mismatch")
        internal = verify_internal_sums(d)
        absolute_summary[model] = {
            "natural_xenon_spectrum_rows": len(abs_csv),
            "isotope_contribution_rows": len(iso_csv),
            "maximum_A_reconstruction_relative_difference":
                validation["maximum_A_reconstruction_relative_difference"],
            "internal_checksum_entries": internal,
            "benchmarks": list(meta["particle_parameters"]["benchmarks"]),
        }

        d = extracted / "B-detector" / model
        meta = read_json(d / "lz_2026_afh7_hybrid9_rate_level_metadata.json")
        require(meta.get("status") == "PASS", f"B-detector/{model}: status is not PASS")
        require(meta["exposure_tonne_year"] == 2.84,
                f"B-detector/{model}: exposure mismatch")
        require("LZ 2026 Fig. S2" in meta["efficiency_source"],
                f"B-detector/{model}: efficiency source mismatch")
        scope = meta["detector_level_scope"]
        require(scope["efficiency_applied"] is True, f"B-detector/{model}: efficiency not applied")
        require(scope["energy_resolution_smearing_applied"] is False,
                f"B-detector/{model}: unexpected energy smearing")
        require(scope["two_dimensional_signal_pdf_applied"] is False,
                f"B-detector/{model}: unexpected 2D signal PDF")
        require(scope["background_likelihood_applied"] is False,
                f"B-detector/{model}: unexpected background likelihood")
        require(scope["is_exclusion_limit"] is False,
                f"B-detector/{model}: output must not be labelled an exclusion")
        yields = read_csv(d / "lz_2026_afh7_hybrid9_rate_level_event_yields.csv")
        require(len(yields) == 8, f"B-detector/{model}: expected eight event-yield rows")
        internal = verify_internal_sums(d)
        detector_summary[model] = {
            "event_yield_rows": len(yields),
            "exposure_tonne_year": meta["exposure_tonne_year"],
            "efficiency_source": meta["efficiency_source"],
            "integration_method": meta["integration_method"],
            "energy_resolution_smearing_applied": scope["energy_resolution_smearing_applied"],
            "two_dimensional_signal_pdf_applied": scope["two_dimensional_signal_pdf_applied"],
            "background_likelihood_applied": scope["background_likelihood_applied"],
            "is_exclusion_limit": scope["is_exclusion_limit"],
            "internal_checksum_entries": internal,
        }

    return {
        "status": "COMPUTED; regression suite passed and numerical closure checks passed",
        "electromagnetic_form_factor_source": "Borah et al. (2020), separate proton/neutron low-Q2 z-expansion",
        "strange_current_models": list(MODELS),
        "recoil_points": 208,
        "isotopes": [128, 129, 130, 131, 132, 134, 136],
        "natural_atom_fraction_AFH_coverage": 0.998158,
        "abundances_not_renormalized": True,
        "baseline_and_highorder_row_counts": row_counts,
        "highorder_summaries": b_summary,
        "max_abs_full_vs_ID_error_B_pct": max_abs_full_vs_id,
        "max_abs_B_over_A_full_rate_shift_pct_by_model": max_abs_BA_shift,
        "quadrature_convergence": {
            "max_abs_full_B_rate_shift_pct": max_quad_full,
            "max_abs_I_D_B_rate_shift_pct": max_quad_id,
            "max_abs_approximation_error_shift_pp": max_quad_approx,
        },
        "absolute_AFH7_Hybrid9_outputs": absolute_summary,
        "LZ_2026_efficiency_weighted_rate_level_fold": detector_summary,
        "scope": "Rate-level B baseline plus efficiency-weighted rate-level yields; no energy resolution, 2D signal PDF, background likelihood, or exclusion construction.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-dir", required=True, type=Path)
    args = parser.parse_args()
    request_path = ROOT / "research/artifact_archives/requests/lz-pr83-corrected-B-2026-11-20.json"
    request = read_json(request_path)
    meta_dir = args.metadata_dir

    provenance = check_source(meta_dir, request)
    root = ROOT / REL
    zip_path = root / "source-artifact-pr83.zip"
    require(zip_path.exists(), f"missing source artifact ZIP: {zip_path}")
    require(sha256(zip_path) == request["artifact_sha256"], "source artifact ZIP SHA-256 mismatch")
    payload_hashes = verify_extracted(zip_path, root / "extracted")
    require(len(payload_hashes) == 48, f"expected 48 artifact members, found {len(payload_hashes)}")

    source_inputs = root / "source-inputs"
    source_code = root / "source-code"
    for p in (source_inputs, source_code):
        require(p.exists(), f"missing source snapshot directory: {p}")
        require(any(x.is_file() for x in p.rglob("*")), f"empty source snapshot directory: {p}")

    summary = validate_outputs(root)
    request["source_run"]["upstream_halo"] = request["upstream_halo"]
    manifest = {
        "manifest_schema_version": 1,
        "archive_generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository": request["repository"],
        "archive_status": "ARCHIVED_AND_INTEGRITY_CHECKED",
        "scientific_validation_status": summary["status"],
        "study": "Corrected finite-nucleon Dirac-Pauli B baseline with AFH-7/Hybrid-9 spectra and LZ 2026 efficiency-weighted rate-level fold",
        "source_workflow": provenance,
        "source_run": request["source_run"],
        "upstream_halo": request["upstream_halo"],
        "source_artifact_payload": {
            "member_file_count": len(payload_hashes),
            "extracted_payload_matches_source_zip": True,
        },
        "input_and_code_snapshots": {
            "source_inputs": "Borah2020 electromagnetic coefficients/covariance and LZ 2026 efficiency source files are copied into source-inputs/.",
            "source_code": "The B form-factor implementation, continuous-spectrum postprocessor, and efficiency-fold script are copied into source-code/.",
        },
        "result_summary": summary,
        "file_inventory": file_inventory(root),
    }
    write_manifest_and_sums(root, manifest)
    print(json.dumps({
        "archive_status": manifest["archive_status"],
        "source_artifact_sha256": sha256(zip_path),
        "archive_inventory_files": len(manifest["file_inventory"]),
        "checksum_entries": len((root / "SHA256SUMS").read_text().splitlines()),
        "result_summary": summary,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
