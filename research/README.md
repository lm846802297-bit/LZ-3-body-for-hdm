# Research archive

All research materials are kept under this directory so the repository root stays uncluttered. The current canonical archive is the repository's main branch.

## Research workflow

Read [WORKFLOW.md](WORKFLOW.md) before starting a new study. Use [_template/README.md](_template/README.md) for each new topic, and follow the repository PR checklist. A successful software test or workflow run validates only the code paths and assertions that it actually covers.

## Directory map

- [docs/](docs/README.md): cross-topic model definitions, phenomenology notes, the AFH/natural-xenon main report, appendices A–G, formula cross-reference index, source audits, and research decisions.
- figure2_kinematic_audit/: threshold conditions, maximum scalar mass, and phase-space checks.
- [figure2_full_reproduction/](figure2_full_reproduction/README.md): Eq. (6) kernel, GCN/JJ55 natural-xenon halo-folded continuous spectra, fixed-speed Xe-131 diagnostics, the supplied 450 keV pointwise benchmark, tests, and numerical outputs. The 450 keV fixed-speed curve is a single-isotope zero-width diagnostic, not a halo or detector-level prediction.
- afh_default_density_xe131/: AFH v6.0 Xe-131 response, response normalization and momentum-convention audits, plus AME2020/CODATA-2022 mass and Xe-131-only hybrid diagnostics. The legacy PCHIP partial-rate tables are not the primary direct-exact-q result.
- afh_default_density_natural_xenon_halo/: isotope-resolved AFH default-density natural-xenon halo fold, seven-isotope response extraction, selected-q 60-digit mpmath validation, interpolation-accuracy audit, and the AFH-7/Hybrid-9 continuous recoil spectra with high-order quadrature checks. The selected-point AME2020 fold remains a distinct mass-scheme record; none of these results is a detector-level LZ likelihood.
- [lz_detector_response/](lz_detector_response/README.md): LZ 2026 Fig. S2 efficiency digitization, source/provenance metadata, and one-dimensional efficiency-weighted GCN/JJ55 rate-level event yields. This is not the official LZ likelihood or an exclusion.

## Current result layers

Keep the following quantities separate:

1. **Microscopic level:** single-isotope, fixed-speed \(d\sigma_A/dE_R\).
2. **Nuclear/target level:** isotope-specific responses and natural-xenon abundance weighting.
3. **Astrophysical level:** laboratory-frame halo average \(dR/dE_R\).
4. **Detector interface:** one-dimensional efficiency-weighted expected event counts.
5. **Experiment likelihood:** two-dimensional detector response, calibration/background nuisance parameters, and profile likelihood; this layer is not implemented here.

## Phase II high-energy tail audit

- [High-energy tail nuclear-model sensitivity](docs/appendices/09H_high_energy_tail_nuclear_model_sensitivity.md): efficiency-weighted 225–269.9 keV comparison of AFH-7, Hybrid-9, Helm-9, GCN and JJ55.

## Organization rules

- Keep research-specific scripts, tests, numerical tables, plots, and audit reports together under the relevant study directory.
- Keep project-level research notes in research/docs/.
- Keep the manuscript source and original figures in paper-source/.
- Record assumptions and validation boundaries alongside each result; passing software tests does not by itself settle unspecified model assumptions.
- Preserve native outputs, run manifests, source/input revisions, and checksums; do not use ZIP/TAR delivery bundles as substitutes for extracted research files.


## Figure 2 P0–P2 audit records

- [Figure 2 numerical-results master index](docs/supplements/figure2_results_master_index_2026-11-13.md): benchmark/input/output provenance and SHA-256 inventory, including the native AFH Xe-131 Mathematica audit.
- [Figure 2 physics-formula audit](docs/supplements/figure2_physics_formula_audit_2026-11-13.md): equation, implementation, normalization, and validation cross-checks.
- [Figure 2 scientific-status table](docs/supplements/figure2_scientific_status_2026-11-13.md): verified scope and remaining scientific boundaries.
