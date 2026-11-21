#!/usr/bin/env python3
"""Write v1.0.0 research result records around existing LZ numerical outputs."""
from __future__ import annotations
import csv, hashlib, importlib.metadata, json, os, platform, shlex, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0.0"

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def git_value(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()

def relative_path(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()

def csv_units(column: str) -> str:
    """Strict unit map for the AFH-7/Hybrid-9 and Eq. (6) output tables."""
    labels = {"benchmark", "scenario", "isotope", "halo_model", "mass_scheme",
              "response_q_convention", "width_scheme", "kernel_order_low", "kernel_order_high",
              "case", "mapping", "dimension", "implementation"}
    booleans = {"AFH_default_available", "speed_phase_space_open", "detector_response_applied", "pole_inside_phase_space"}
    if column in booleans:
        return "boolean"
    if column in labels:
        return "label"
    exact = {
        "A": "1", "J_A": "1", "T_iso": "1", "y": "1", "W_M00_AFH_package": "1",
        "nW_or_nu": "1", "nz": "1", "nphi": "1", "nW": "1", "order": "1",
        "y_AFH": "1", "package_R0": "1", "package_R_at_q": "1",
        "normalization_factor_to_A2": "1", "R_A_archived_28_sample": "1",
        "R_A_direct_AFH": "1", "R_A_PCHIP_from_2401_grid": "1",
        "direct_vs_archived_relative_difference": "1",
        "PCHIP_vs_direct_relative_difference": "1",
        "PCHIP_vs_archived_relative_difference": "1",
        "fixed_nW": "1", "fixed_other_order": "1", "g2": "1", "sine2_reference_nW": "1",
        "raw_over_2pi_I6": "1", "direct_over_eq6": "1", "v_kms": "km s^-1",
        "relative_difference": "1", "relative_difference_to_threshold_reference": "1",
        "relative_to_archived": "1", "relative_to_high_order_reference": "1",
        "relative_to_sine2_reference": "1",
        "Delta_m_MeV": "MeV", "delta_W2_GeV2": "GeV^2",
        "Wmin_GeV": "GeV", "Wmax_GeV": "GeV", "pole_mass_GeV": "GeV",
        "sine2_reference_GeV2": "GeV^2", "pole_gap_keV": "keV",
        "pole_edge_delta_m_keV": "keV", "Gamma_pole_keV": "keV",
        "Gamma_at_Wmax_keV": "keV",
        "I6_GeV2": "GeV^2", "reference_I6_GeV2": "GeV^2", "archived_I6_GeV2": "GeV^2",
        "raw_phi_integral_GeV2": "GeV^2",
        "R_AFH_isoscalar_4pi_over_2Jplus1": "1", "R_equal_pn_normalized": "1", "R_over_A2": "1",
        "nv_low": "1", "nv_final": "1",
        "speed_quadrature_relative_difference": "1",
        "kernel_order_relative_difference": "1",
        "available_atom_fraction": "1", "missing_atom_fraction": "1",
        "natural_atom_fraction": "1", "A2_weighted_AFH_coverage_at_q0": "1",
        "coupling_product_sq": "1", "g2_for_pole_width": "1", "rhoDM_GeV_cm3": "GeV cm^-3",
        "relative_shift_vs_AFH7": "1",
        "R_AFH_direct_exact_q": "1", "R_AFH_PCHIP_grid": "1", "R_Helm": "1",
        "R_AFH_over_A2": "1", "R_Helm_over_A2": "1",
        "direct_minus_PCHIP_over_A2": "1", "relative_direct_vs_PCHIP": "1",
        "AFH_minus_Helm_over_A2": "1",
        "b_A_fm_archived": "fm", "b_A_fm_recomputed": "fm",
    }
    if column in exact:
        return exact[column]
    suffixes = (
        ("_events_kg_day_keV", "events kg^-1 day^-1 keV^-1"),
        ("_GeVminus3", "GeV^-3"), ("_GeV_minus3", "GeV^-3"), ("_km_s", "km s^-1"),
        ("_keV", "keV"), ("_MeV", "MeV"), ("_GeV", "GeV"), ("_fm", "fm"),
    )
    for suffix, unit in suffixes:
        if column.endswith(suffix):
            return unit
    if column.startswith("R_") or column.endswith(("_over_A2", "_fraction")):
        return "1"
    raise ValueError(f"CSV unit is not explicitly defined for column {column!r}")

def file_record(root: Path, path: Path, role: str) -> dict[str, Any]:
    path = path.resolve()
    suffix = path.suffix.lower()
    fmt = {".csv": "csv", ".json": "json", ".txt": "text", ".md": "markdown",
           ".root": "root", ".h5": "hdf5", ".hdf5": "hdf5",
           ".parquet": "parquet"}.get(suffix, suffix.lstrip(".") or "binary")
    item = {"path": relative_path(root, path), "role": role, "format": fmt,
            "bytes": path.stat().st_size, "sha256": sha256_file(path)}
    if fmt == "csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            columns = list(reader.fieldnames or [])
            rows = sum(1 for _ in reader)
        if not columns or len(columns) != len(set(columns)):
            raise ValueError(f"CSV has an empty or duplicate header: {path}")
        item.update({"rows": rows, "columns": columns,
                     "units": {name: csv_units(name) for name in columns}})
    return item

def input_record(root: Path, path: Path, name: str, source: str, commit: str) -> dict[str, Any]:
    path = path.resolve()
    suffix = path.suffix.lower()
    fmt = {".csv": "csv", ".json": "json", ".m": "mathematica-source",
           ".py": "python"}.get(suffix, suffix.lstrip(".") or "binary")
    return {"name": name, "source": source, "version": f"git:{commit}",
            "path": relative_path(root, path), "format": fmt,
            "bytes": path.stat().st_size, "sha256": sha256_file(path),
            "transformation": "read-only input; no archive-time modification"}

def validation_status(checks: list[dict[str, Any]]) -> str:
    states = {item["status"] for item in checks}
    if "failed" in states:
        return "failed"
    if "blocked" in states:
        return "blocked"
    if states and states == {"passed"}:
        return "passed"
    return "partial"

def write_result_records(*, repo_root: Path, out_dir: Path, metadata: dict[str, Any],
                          source_script: Path, started_at: str, started_monotonic: float,
                          input_paths: list[tuple[Path, str, str]],
                          output_paths: list[tuple[Path, str]],
                          checks: list[dict[str, Any]], observables: list[dict[str, Any]],
                          scope_included: list[str], scope_excluded: list[str],
                          assumptions: list[str], scientific_status: str = "provisional",
                          interpretation: str = "", extension_name: str = "direct_detection") -> dict[str, Path]:
    """Write run_manifest, result_summary, validation_report, README and SHA256SUMS."""
    root, out = repo_root.resolve(), out_dir.resolve()
    out.relative_to(root)
    if not checks:
        raise ValueError("at least one real validation check is required")
    commit = git_value(root, "rev-parse", "HEAD")
    if len(commit) != 40:
        raise ValueError(f"invalid source commit: {commit}")
    branch = os.environ.get("GITHUB_REF_NAME") or git_value(root, "branch", "--show-current")
    now = utc_now()
    run_id = f"LZ-AFH-{now[:10].replace('-', '')}-{now[11:19].replace(':', '')}-{os.getpid()}-{commit[:8]}"
    vstatus = validation_status(checks)
    inputs = [input_record(root, p, n, s, commit) for p, n, s in input_paths]
    preserved_output_paths = []
    for path, role in output_paths:
        if path.name == "SHA256SUMS.txt":
            preserved = path.with_name(f"SHA256SUMS.physics-{run_id}.txt")
            shutil.copyfile(path, preserved)
            preserved_output_paths.append((preserved, f"original physics checksum manifest preserved from {path.name}"))
        else:
            preserved_output_paths.append((path, role))
    outputs = [file_record(root, p, role) for p, role in preserved_output_paths]
    csv_records = [x for x in outputs if x["format"] == "csv"]
    if not csv_records:
        raise ValueError("the archive must include at least one native CSV table")
    project = {"repository": "lm846802297-bit/LZ-3-body-for-hdm",
               "project_id": "lz-three-body-afh-natural-xenon",
               "workstream_id": "three-body-phase-space-afh-response"}
    summary = {
        "schema_version": SCHEMA_VERSION, "record_type": "result_summary",
        "run_id": run_id, "created_at": now, "project": project,
        "calculation": metadata.get("calculation", "Three-body phase-space and AFH natural-xenon calculation"),
        "scope": {"included": scope_included, "excluded": scope_excluded, "assumptions": assumptions},
        "benchmark": {"particle_parameters": metadata.get("particle_parameters", {}),
                      "halo": metadata.get("halo", {}),
                      "recoil_grid_keV": metadata.get("recoil_grid_keV", {}),
                      "quadrature": metadata.get("quadrature", {}),
                      "rate_units": metadata.get("rate_units", "events kg^-1 day^-1 keV^-1")},
        "observables": observables,
        "data_files": [x for x in outputs if x["format"] in {"csv", "json"}],
        "scientific_status": scientific_status, "interpretation": interpretation,
        "extensions": {extension_name: metadata},
    }
    summary_path = out / "result_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    report = {
        "schema_version": SCHEMA_VERSION, "record_type": "validation_report",
        "run_id": run_id, "created_at": now, "status": vstatus, "checks": checks,
        "convergence": metadata.get("quadrature", {}),
        "extensions": {extension_name: {"metadata_status": metadata.get("status"),
            "detector_response_applied": metadata.get("detector_response_applied"),
            "not_included": metadata.get("not_included", [])}},
    }
    report_path = out / "validation_report.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    readme_path = out / "README.md"
    readme_path.write_text(
        "# Structured LZ three-body / AFH result archive\n\n"
        f"- Run ID: {run_id}\n- Source commit: {commit}\n"
        f"- Validation status: **{vstatus.upper()}**\n"
        f"- Scientific status: **{scientific_status}**\n\n"
        "Original physics CSV and metadata files are preserved byte-for-byte. "
        "The pre-standard checksum list is retained as SHA256SUMS.physics-<run_id>.txt. "
        "Run sha256sum -c SHA256SUMS.txt from this directory to verify the complete archive. "
        "These records document provenance, results, and checks; they do not alter "
        "the amplitude, phase-space integration, AFH responses, isotope weights, or halo fold.\n\n"
        f"Interpretation: {interpretation}\n", encoding="utf-8")
    checksum_paths = [root / x["path"] for x in outputs] + [summary_path, report_path, readme_path]
    sums_path = out / "SHA256SUMS.txt"
    sums_path.write_text("".join(
        f"{sha256_file(p)}  {p.resolve().relative_to(out).as_posix()}\n"
        for p in sorted(checksum_paths, key=lambda x: x.as_posix())
    ), encoding="utf-8")
    generated = outputs + [
        file_record(root, summary_path, "standard result summary"),
        file_record(root, report_path, "standard validation report"),
        file_record(root, readme_path, "archive guide"),
        file_record(root, sums_path, "SHA-256 inventory"),
    ]
    manifest = {
        "schema_version": SCHEMA_VERSION, "record_type": "run_manifest",
        "run_id": run_id, "created_at": now, "project": project,
        "source": {"commit_sha": commit, "branch": branch,
                   "script_path": relative_path(root, source_script),
                   "script_sha256": sha256_file(source_script)},
        "inputs": inputs,
        "configuration": {
            "physics": metadata.get("particle_parameters", {}),
            "numerics": metadata.get("quadrature", {}),
            "conventions": {"response_convention": metadata.get("response_convention"),
                "nuclear_mass_scheme": metadata.get("nuclear_mass_scheme"),
                "spatial_momentum": metadata.get("spatial_momentum"),
                "width": metadata.get("width", {}),
                "abundance_renormalization": metadata.get("abundance_renormalization")},
        },
        "environment": {"platform": platform.platform(),
            "runtime": {"python": platform.python_version()},
            "dependencies": {name: importlib.metadata.version(name)
                for name in ("numpy", "scipy") if _has_distribution(name)},
            "hardware": {"processor": platform.processor() or "not reported"}},
        "execution": {"status": "succeeded", "command": shlex.join([sys.executable, *sys.argv]),
            "started_at": started_at, "finished_at": now, "exit_code": 0,
            "wall_time_s": round(time.monotonic() - started_monotonic, 6)},
        "outputs": generated, "validation": {"status": vstatus, "checks": checks,
            "report_path": relative_path(root, report_path)},
        "archive": {"status": "local_only"},
        "extensions": {extension_name: {"calculation_metadata": metadata}},
    }
    manifest_path = out / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return {"run_manifest": manifest_path, "result_summary": summary_path,
            "validation_report": report_path, "checksums": sums_path, "readme": readme_path}

def _has_distribution(name: str) -> bool:
    try:
        importlib.metadata.version(name)
        return True
    except importlib.metadata.PackageNotFoundError:
        return False
