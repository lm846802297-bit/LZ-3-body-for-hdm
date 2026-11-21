# Research Task Brief — Archive Xe-131 charge–longitudinal projection

- Task ID: `20261120-xe131-charge-longitudinal-archive`; status: completed (archival).
- Prepared 2026-11-20 by Codex; assigned to Codex.
- Repository `lm846802297-bit/LZ-3-body-for-hdm`; archival base `main` at `98fc6e3b3de9c7d282b6a68855b0dc50114d5618`; original calculation records baseline `7456b7743adbed46b09b430ea2a54e8d0545aaa6` and comparison commit `c5bfcf6c5494d036b078af8299a2fca2e86248ce`.
- Purpose: archive the already completed fixed-speed Xe-131 charge–longitudinal projection and its reproduction materials. This archival task does not claim a new derivation or rerun the full calculation.
- Primary sources and detailed conventions: [study README](../charge_longitudinal/README.md), including momentum transfer, frame, trace, current normalization, width and phase-space definitions; [AFH nuclear responses](https://arxiv.org/abs/1308.6288); [PDG kinematics](https://pdg.lbl.gov/2024/reviews/rpp2024-rev-kinematics.pdf). Upstream run [44324056946](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44324056946), artifact 14437568189. Input and source hashes and software versions are in [checks.json](../charge_longitudinal/results/checks.json).
- Model and scope: conditional Dirac, real scalar, vector nuclear current; Xe-131, speed 776 km/s, mχ=1000 GeV, ms=300 keV, Δm=450 keV and mV=10 GeV. Central 299-point grid uses zero width; asymmetric pole width is a six-point control. No halo fold, transverse nuclear multipoles, detector response or likelihood.
- Historical numerical evidence: study README and `checks.json` record 297 open points, comparison to the spinor archive, six refined quadrature controls and width controls. These are archived claims, not independent new calculations in this task. Bound-nucleus current matching remains a separate question.
- Acceptance for this archive: preserve input, code, numerical tables, figures, and run metadata; verify hashes using the stated LF-normalized text policy; run the existing charge projection tests. No new scientific threshold is introduced retrospectively; derivation and historical convergence checks are recorded in the study README and manifest.
- Current verification: `python -B -m unittest discover -s research/three_body_calculation_and_validation/tests -p test_charge_longitudinal.py -v`: four tests passed. All 13 input, source and output hashes in `checks.json` matched. Full 299-point calculation and new independent derivation were not rerun for archival.
- Deliverables: `charge_longitudinal/`, its test, and the topic README index. Reproduction commands and dependencies are in the study README; final revision and PR are recorded in Git history and PR metadata.
- Status: reproducible archival record, with the stated limitations; no inference of detector-level predictions or full finite-width production results.

## Change log

| Date | Change |
|---|---|
| 2026-11-20 | Prepared archival handoff for pre-existing local research; original run details are preserved in the study record. |
