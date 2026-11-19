#!/usr/bin/env python3
"""Export CSV tables and paper-style diagnostic plots from a provisional P4 halo fold."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

RATE_FIELDS = (
    "rate_A_original_AFH_M_events_kg_day_keV",
    "rate_B_baseline_M_events_kg_day_keV",
    "rate_C_charge_extension_events_kg_day_keV",
    "rate_leading_static_vector_candidate_events_kg_day_keV",
)
RATE_LABELS = {
    RATE_FIELDS[0]: r"A: q=0 nucleon current $\\times W_M$",
    RATE_FIELDS[1]: r"B: finite-$t_N$ nucleon current $\\times W_M$",
    RATE_FIELDS[2]: r"C: $M+\\Phi''$ charge extension",
    RATE_FIELDS[3]: "D candidate: leading-static six-channel current",
}
HALO_LABELS = {
    "shm_cutoff": "Truncated SHM",
    "mb_untruncated": "Untruncated Maxwellian",
}

def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def export(data: dict, out_dir: Path) -> dict:
    if data.get("native_afh_validated") is not False:
        raise ValueError("this plotting route is reserved for explicitly provisional AFH input")
    if data.get("width_scheme") != "pole":
        raise ValueError("P4 plot must use the formal asymmetric Pole prescription")
    out_dir.mkdir(parents=True, exist_ok=True)
    spectra = sorted(data["results"], key=lambda r: (r["halo_model"], float(r["ER_keV"])))
    spec_rows = []
    isotope_rows = []
    for row in spectra:
        base = {k: row[k] for k in (
            "ER_keV", "halo_model", *RATE_FIELDS,
            "relative_C_vs_A",
            "relative_B_vs_A",
            "relative_phi_vs_finite_t_M",
            "relative_full_candidate_vs_A",
            "relative_spatial_candidate_vs_coulomb",
            "open_abundance_fraction",
        ) if k in row}
        base["native_afh_validated"] = False
        spec_rows.append(base)
        weights = [
            float(x["abundance"]) * float(x["leading_static_vector_candidate_halo_integral"])
            if x.get("open") else 0.0
            for x in row["isotope_rows"]
        ]
        total = sum(weights)
        for iso, weight in zip(row["isotope_rows"], weights):
            fraction = weight / total if total else 0.0
            isotope_rows.append({
                "ER_keV": row["ER_keV"],
                "halo_model": row["halo_model"],
                "A": iso["A"],
                "natural_atom_fraction": iso["abundance"],
                "vmin_km_s": iso["vmin_km_s"],
                "open": iso["open"],
                "fraction_of_natural_xenon_candidate_rate": fraction,
                "relative_spatial_vs_coulomb": iso.get("relative_spatial_candidate_vs_coulomb"),
            })
    write_csv(out_dir / "natural_xenon_recoil_spectrum.csv", spec_rows, list(spec_rows[0]))
    write_csv(out_dir / "natural_xenon_isotope_contributions.csv", isotope_rows, list(isotope_rows[0]))

    pdf_path = out_dir / "p4_provisional_natural_xenon_spectra.pdf"
    with PdfPages(pdf_path) as pdf:
        for halo in ("shm_cutoff", "mb_untruncated"):
            subset = [r for r in spectra if r["halo_model"] == halo]
            subset.sort(key=lambda r: float(r["ER_keV"]))
            er = [float(r["ER_keV"]) for r in subset]
            fig, ax = plt.subplots(figsize=(8.2, 5.4))
            for field in RATE_FIELDS:
                y = [float(r[field]) for r in subset]
                ax.plot(er, y, marker="o", markersize=2.8, linewidth=1.4, label=RATE_LABELS[field])
            ax.set_yscale("log")
            ax.set_xlabel(r"Nuclear recoil energy $E_R$ [keV]")
            ax.set_ylabel(r"$dR/dE_R$ [events/(kg day keV)]")
            ax.set_title(f"Natural xenon three-body recoil spectrum — {HALO_LABELS[halo]}")
            ax.grid(True, which="both", alpha=0.25)
            ax.legend(fontsize=8)
            fig.text(0.5, 0.01, "PROVISIONAL: source-translated AFH v6.0; native Mathematica comparison pending",
                     ha="center", fontsize=7)
            fig.tight_layout(rect=(0,0.035,1,1))
            pdf.savefig(fig)
            fig.savefig(out_dir / f"p4_absolute_spectrum_{halo}.png", dpi=180)
            plt.close(fig)

            fig, ax = plt.subplots(figsize=(8.2, 5.4))
            ratio_fields = (
                ("relative_B_vs_A", r"B/A: finite-$t_N$ nucleon-current correction"),
                ("relative_C_vs_A", r"C/A: total charge-sector change"),
                ("relative_full_candidate_vs_A", "D candidate/A: provisional full-current change"),
                ("relative_spatial_candidate_vs_coulomb", "Spatial candidate/Coulomb sector"),
            )
            for field, label in ratio_fields:
                y = [float(r[field]) for r in subset]
                ax.plot(er, y, marker="o", markersize=2.8, linewidth=1.4, label=label)
            ax.axhline(0.0, linewidth=0.8)
            ax.set_xlabel(r"Nuclear recoil energy $E_R$ [keV]")
            ax.set_ylabel("Relative change")
            ax.set_title(f"Response ratios — {HALO_LABELS[halo]}")
            ax.grid(True, alpha=0.25)
            ax.legend(fontsize=8)
            fig.text(0.5, 0.01, "PROVISIONAL: full-current candidate is not a P3-C PASS",
                     ha="center", fontsize=7)
            fig.tight_layout(rect=(0,0.035,1,1))
            pdf.savefig(fig)
            fig.savefig(out_dir / f"p4_response_ratios_{halo}.png", dpi=180)
            plt.close(fig)

        subset = [r for r in isotope_rows if r["halo_model"] == "shm_cutoff"]
        isotope_set = sorted({int(r["A"]) for r in subset})
        er_grid = sorted({float(r["ER_keV"]) for r in subset})
        fig, ax = plt.subplots(figsize=(8.2, 5.4))
        bottom = [0.0] * len(er_grid)
        for A in isotope_set:
            lookup = {(float(r["ER_keV"]), int(r["A"])): float(r["fraction_of_natural_xenon_candidate_rate"])
                      for r in subset}
            values = [lookup.get((er, A), 0.0) for er in er_grid]
            ax.fill_between(er_grid, bottom, [b+v for b,v in zip(bottom,values)],
                            label=f"Xe-{A}", alpha=0.75)
            bottom = [b+v for b,v in zip(bottom,values)]
        ax.set_xlabel(r"Nuclear recoil energy $E_R$ [keV]")
        ax.set_ylabel("Fraction of natural-xenon rate")
        ax.set_ylim(0,1)
        ax.set_title("Isotope composition of the provisional SHM rate")
        ax.grid(True, alpha=0.25)
        ax.legend(ncol=4, fontsize=8)
        fig.text(0.5, 0.01, "Seven AFH default-density isotopes; atom-fraction coverage = 99.8158%",
                 ha="center", fontsize=7)
        fig.tight_layout(rect=(0,0.035,1,1))
        pdf.savefig(fig)
        fig.savefig(out_dir / "p4_isotope_composition_shm.png", dpi=180)
        plt.close(fig)

    summary = {
        "status": "PROVISIONAL_P4_PLOTS_EXPORTED",
        "native_afh_validated": False,
        "width_scheme": data["width_scheme"],
        "formal_width_prescription": data["formal_width_prescription"],
        "natural_atom_fraction_coverage": data["natural_atom_fraction_coverage"],
        "recoil_points": sorted({float(r["ER_keV"]) for r in spectra}),
        "halo_models": sorted({r["halo_model"] for r in spectra}),
        "spectrum_rows": len(spec_rows),
        "isotope_contribution_rows": len(isotope_rows),
        "pdf": pdf_path.name,
        "plots": sorted(p.name for p in out_dir.glob("*.png")),
        "interpretation": "Diagnostic spectra only; no native AFH or complete P3-C claim.",
    }
    (out_dir / "plot_manifest.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-json",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    data=json.loads(a.input_json.read_text(encoding="utf-8"))
    print(json.dumps(export(data,a.out_dir),indent=2))

if __name__=="__main__":
    main()
