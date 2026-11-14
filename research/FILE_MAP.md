# Repository file map and research navigation

This file is the navigation index for the LZ three-body dark-matter project. It explains the scientific role of each directory and identifies the boundaries between theory, numerical implementation, nuclear inputs, detector folding, and manuscript assets.

## 1. Repository-level layout

| Path | Role | What belongs here |
|---|---|---|
| `.github/workflows/` | Reproducibility automation | Explicit, version-controlled calculation and validation workflows |
| `AGENTS.md` | Repository-wide agent instructions | Mandatory scientific and repository constraints |
| `CONTRIBUTING.md` | Contributor entry point | Contribution and review expectations |
| `paper-source/` | Manuscript source | Original source, editable working manuscript, bibliography, style, original figures, build and checksum records |
| `research/` | Research archive | Theory notes, numerical code, tests, input data, outputs, audits and figure packs |
| `v6/` | Upstream AFH/DMFormFactor source package | Preserved upstream package and accompanying documentation/PDF assets used by AFH calculations |

Do not move files across these boundaries merely to make the tree look uniform. Existing workflow paths, manuscript build paths, provenance records and external-source conventions are part of the reproducibility contract.

## 2. Scientific workflow map

The project is organized by scientific responsibility, not by file extension alone.

| Research stage | Canonical directory | Main responsibility | Important boundary |
|---|---|---|---|
| Model and manuscript reasoning | `research/docs/` | Model definition, amplitude derivations, cosmology, references, source audits and roadmap | Cross-topic explanations; not a substitute for calculation-specific run records |
| Three-body kinematics | `research/figure2_kinematic_audit/` | `calculations/` contains the threshold runner; `results/` contains the report, CSV, run manifest and checksum; `tests/` contains regression checks | Kinematic checks only; not a recoil-rate calculation |
| Three-body kernel and numerical implementation | `research/figure2_full_reproduction/` | Eq. (6) kernel, Dirac trace, propagator/width studies, scalar self-energy, mass schemes, tests and selected rate-level drivers | Keep model assumptions and unresolved Dirac/Majorana or mediator-sector inputs explicit |
| AFH Xe-131 nuclear response | `research/afh_default_density_xe131/` | `input/` holds the AFH default density matrix; `tests/` holds five regression suites; `audit/` holds normalization/q-convention reports and audit scripts; `output/` holds response grids and corrected cross sections, with `output/native_exports/` for direct Wolfram exports and `output/native_audit/` for independent Python/Wolfram comparisons. Root-level calculation runners remain stable workflow entry points. | Distinguish Python translation, mpmath checks and native Wolfram execution; never conflate the raw direct export with the independent comparison archive |
| Natural-xenon isotope and halo fold | `research/afh_default_density_natural_xenon_halo/` | Isotope-resolved AFH response, isotope weights, halo folding, exact-q recalculation, interpolation audits and nuclear-model sensitivity | Seven-isotope AFH coverage is not a full nine-isotope AFH prediction; selected-point folds are not continuous spectra |
| Detector efficiency and rate-level yields | `research/lz_detector_response/` | LZ 2026 efficiency inputs, digitization provenance and efficiency-weighted expected-yield archives | Rate-level diagnostics are not detector-level likelihoods, exclusions or official LZ results |
| Scientific figure collections | `research/figure_packs/` | Figure indexes, manifests, checksums and scope notes | Metadata/checksum records do not imply that image binaries are committed |
| Formula navigation | `research/docs/formula_symbol_code_cross_reference.md` | Equation-to-symbol-to-code-to-result cross-reference | Use this to trace a formula into its implementation and archived output |

## 3. Inside a study directory

Use the following semantic categories when a study becomes large enough to benefit from subfolders:

- `input/` or `inputs/`: immutable source data, benchmark configurations and small redistributable inputs.
- `output/` or `results/`: generated native CSV/JSON/TXT data, summaries, plots and run manifests.
- `audit/`: independent checks, convention comparisons, interpolation studies, convergence and provenance audits.
- `tests/`: unit and regression tests.
- `appendices/` and `supplements/`: focused derivations and supporting research documents.
- Study-root scripts: stable entry points and small modules that are imported by other scripts.

Use the spelling already established by a study; do not rename `input` to `inputs` or `output` to `results` as a cosmetic cleanup. A README must explain any flat or mixed layout. Create only directories that contain real material.

## 4. Which result should I use?

Before using a numerical file, check the relevant study README and its manifest/index. In particular:

1. For the four-benchmark Xe-131 cross sections, use the canonical corrected long-form CSV and the matching wide audit named in `research/afh_default_density_xe131/output/CROSS_SECTION_FILE_INDEX.md`. The historical AFH-column-mispopulated CSV is superseded and must not feed new plots or calculations.
2. For AFH natural-xenon precision work, distinguish direct exact-q selected-point outputs from historical PCHIP/interpolated diagnostics. Do not promote a historical interpolation table to a primary precision prediction.
3. AFH-7 means the seven isotopes with AFH v6.0 default-density matrices. Hybrid-9 uses Helm only for Xe-124/Xe-126; it is not full AFH-9. Keep Helm-9, GCN and JJ55 as separately labelled response models.
4. LZ efficiency-weighted event yields are one-dimensional rate-level diagnostics. They are not energy-resolution-smeared event predictions, a profile likelihood, a 90% CL exclusion or an official LZ likelihood.
5. The AFH factor of four is part of the physical response convention and must be applied exactly once. The small finite-decimal correction factor is a separate q=0 normalization correction; do not conflate the two.
6. A Python result, an independent high-precision mpmath check, a CI test and a native Mathematica execution are different evidence types. State exactly which one was performed.

## 5. Safe navigation and maintenance rules

- Start at the study README, then follow its links to scripts, tests, inputs, results and audits.
- Preserve original source files and historical outputs. Mark superseded material in place rather than deleting provenance.
- Do not move or rename scripts until all workflow YAML, test imports, README commands and manuscript references have been searched and updated together.
- Do not commit ZIP/TAR delivery bundles as the only record of a calculation. Extract native files and preserve manifests/checksums.
- Do not infer scientific validation from a successful workflow alone; read the physical assumptions and validation boundary.
- For new work, follow `research/WORKFLOW.md` and start from `research/_template/README.md`.

## 6. Recommended reading order

1. `README.md` — project purpose and high-level status.
2. `research/README.md` — research archive entry point.
3. This file — directory and scientific-pipeline map.
4. `research/WORKFLOW.md` — rules for adding, validating and archiving work.
5. `research/docs/09_afh_xe131_three_body_scattering_natural_xenon.md` — integrated AFH/natural-xenon physics report.
6. The README in the specific calculation directory — exact code, inputs, outputs and validation status.
