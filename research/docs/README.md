# Research documentation

## Main report

- [AFH v6.0 Xe-131 response, Eq. (6) three-body scattering, natural xenon, and LZ rate-level interface](09_afh_xe131_three_body_scattering_natural_xenon.md): current main report. Its main text now walks through the interaction and virtual-state picture, the two-diagram Dirac amplitude and interference, three-body phase space and Eq. (6) prefactor, nuclear-response minima, isotope/halo folding, and the detector-efficiency projection; full technical derivations remain in formal Appendices A–G.
- [Formula–symbol–text–code–result cross-reference](formula_symbol_code_cross_reference.md): stable F1–F12 identifiers, definitions, units, approximations, code entry points, archived outputs, and validation boundaries.
- [Research decision register](supplements/research_decision_register.md): discussion candidates, adopted conventions, and scope boundaries. This is supplementary record H, not a formal main-report appendix.

## Current audit and status registers

- [Figure 2 results master index](supplements/figure2_results_master_index_2026-11-13.md): benchmark-to-input/parameter/output map, 48-file SHA-256 manifest, and explicit checksum-only / missing-input records.
- [Machine-readable result manifest](supplements/figure2_results_master_index_2026-11-13.json): 8 result groups with repository paths, full SHA-256 digests, byte sizes, parameter sets, and scope boundaries.
- [Physics formula cross-audit](supplements/figure2_physics_formula_audit_2026-11-13.md): original Lagrangian, two radiation diagrams, Dirac trace, three-body phase-space Jacobian, \(256\pi^3\), AFH factor four, \(v_{\min}\), and natural-xenon rate normalization.
- [Scientific result status table](supplements/figure2_scientific_status_2026-11-13.md): separates verified, partially verified, missing-input, and not-yet-completed tasks.
- [Anand / AFH coherent-response audit](../figure2_full_reproduction/ANAND_WM_RESPONSE_AUDIT.md): source-level AFH isoscalar convention and the physical equal-\(p,n\) response mapping.

## Earlier project notes

- 01_model_and_amplitude.md: model definition, three-body amplitude, and propagator structure.
- 02_lz_recast.md: LZ data, detector response, and statistical-recast plan.
- 03_cosmology.md: freeze-out and Delta N_eff.
- 04_audit_and_roadmap.md: open issues, validation status, and research roadmap.
- 05_references.md: reference bibliography and source mapping.
- 06_original_source_audit.md: audit of the supplied manuscript source.
- 07_source_build_and_figure_audit.md: source build and figure audit.
- 08_chi2_decay_width.md: analytic derivation, benchmark, and validation boundary for chi2 -> chi1 s.
- 08_final_editorial_pass_2026-11-11.md: historical editorial pass record.

## Formal Appendices A–G

The standalone files below are navigation/citation copies of the corresponding sections embedded in the main report. When editing an appendix, update both copies in the same change and verify that their scientific content remains synchronized.

- [A — Three-body kinematics, phase-space limits, and Dirac amplitude](appendices/09A_three_body_kinematics_amplitude.md)
- [B — AFH v6.0 density matrix and nuclear response](appendices/09B_afh_v6_density_matrix_response.md)
- [C — AFH isoscalar normalization and factor-of-four mapping](appendices/09C_afh_isoscalar_factor4_normalization.md)
- [D — Natural-xenon isotopes, abundances, and target normalization](appendices/09D_natural_xenon_isotope_target.md)
- [E — Laboratory-frame halo, three-body minimum speed, and rate folding](appendices/09E_halo_velocity_vmin_folding.md)
- [F — Numerical validation, archived data, and reproduction commands](appendices/09F_numerical_validation_reproduction.md)
- [G — Exact spatial momentum and the non-relativistic recoil approximation](appendices/09G_recoil_momentum_convention_audit.md)

## 450 keV benchmark records

These are deliberately separate diagnostics with different assumptions; neither should be conflated with the natural-xenon halo-folded spectra or the LZ rate-level yields.

- [Supplied pointwise L00 benchmark and conditional pole-width comparison](../figure2_full_reproduction/results/USER_L00_BENCHMARK_G1_G2_GVN_1_DELTA_M_450KEV.md)
- [Local acceptance record for the pointwise benchmark](../figure2_full_reproduction/results/USER_L00_BENCHMARK_450KEV_LOCAL_2026-11-13/LOCAL_VALIDATION_2026-11-13.md)
- [Fixed-speed Xe-131 differential curve and its limitations](../figure2_full_reproduction/results/USER_DSIGMA_CURVE_450KEV_LOCAL_2026-11-13.md)

## LZ detector-response documentation

- [Detector-response inputs and rate-level archive README](../lz_detector_response/README.md)
- Main report: §11.1–§11.5; numerical interface and remaining requirements: Appendix F.5.


## Figure 2 audit supplements

- [Numerical-results master index](supplements/figure2_results_master_index_2026-11-13.md)
- [Physics-formula cross-audit](supplements/figure2_physics_formula_audit_2026-11-13.md)
- [Scientific-status table](supplements/figure2_scientific_status_2026-11-13.md)
