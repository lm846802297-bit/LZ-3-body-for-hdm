# LZ 2026 HEPData v1 archive audit

**Status:** archive received, parsed, and structurally validated. This is an audit of the user-supplied HEPData ZIP, not a claim that it contains the full detector-response resource set.

## 1. Provenance

- Supplied archive: `HEPData-ins3199115-v1.zip`
- Archive size: 40,657 bytes
- SHA-256: `ab02f6eacd1008a260f0eb8f441beb206069e18f10c6b7b2f44fcfd70463f1f1`
- Paper: LZ Collaboration, arXiv:2609.02823v1, *Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment*.
- Data-release DOI cited by the paper: https://doi.org/10.17182/hepdata.182472.v1

The archive contents match the paper's three WIMP-search samples and its Lagrangian/inelastic-model limit tables. In particular, the Science sample contains the event of interest.

## 2. Archive inventory

The ZIP contains `submission.yaml` and 46 data-table YAML files:

| Class | Tables | Rows |
|---|---:|---:|
| Science sample | 1 | 1,710 |
| Prompt-veto sample | 1 | 66 |
| Delayed-veto sample | 1 | 55 |
| Lagrangian limits/significance, L01s–L20v | 40 | mostly 13 per table |
| Inelastic limits/significance | 3 | 20 per table |
| **Total** | **46** | — |

The three event samples contain paired coordinates `S1c [phd]` and `log(S2c [phd])`.

The 40 L tables contain the columns `Upper Limit`, `Lower Limit`, `Median`, `+1 sigma`, `-1 sigma`, `+2 sigma`, `-2 sigma`, and `Local Significance`, against `Mass (GeV)`.

The three inelastic tables are `O01s`, `O01v`, and `O04s`. They additionally contain `Delta (keV)`. No `O04v` table is present in this archive.

## 3. Structural validation

- All 46 table YAML files parse successfully.
- Every independent/dependent variable column within each table has a consistent row count.
- All tabulated values are numeric and finite.
- No YAML table-level qualifiers or per-row uncertainty objects are present in these files.
- No parse, non-finite-value, or column-length mismatch was found.

The nominal L-table mass grid is:
`10, 12, 14, 17, 21, 30, 40, 50, 100, 200, 400, 1000, 4000 GeV`.

The following L tables have fewer points than this nominal grid:
- `L04s`: no 30 GeV point;
- `L04v`: no 17 GeV point;
- `L14s`: no 17 or 200 GeV points;
- `L14v`: no 17 GeV point.

Each O table has 20 rows. For each of the three WIMP masses (400, 1000, 4000 GeV), the listed splittings omit 100 keV; the 400 GeV entries also omit 350 keV. These are recorded as source-table coverage facts, not assumed to be errors.

## 4. Event-of-interest cross-check

The largest-`S1c` point in `Science.yaml` is row 1,077 (one-based):

- (S1_c = 540.07916\,\mathrm{phd})
- (log_{10}(S2_c/\mathrm{phd}) = 3.966964)
- (S2_c = 9,267.53\,\mathrm{phd})

This matches the paper's reported event at approximately (S1_c=540.1\,\mathrm{phd}) and its supplemental-text value (S2_c=9268\,\mathrm{phd}). This is a strong content-level check that the supplied archive is the intended LZ 2026 search data release.

## 5. What this archive does and does not provide

### Present

- Observed science, prompt-veto, and delayed-veto event coordinates in ((S1_c,\log_{10}S2_c)).
- Lagrangian and selected inelastic-model upper-limit, expected-band, and local-significance tables.

### Not present in this ZIP

- DD, AmBe, tritium, or (^{212}\mathrm{Pb}) calibration event samples;
- the NEST configuration/parameter resource file;
- an explicit NR fluctuation-parameter vector such as a tuned `NRERWidthsParam`;
- detector spatial response maps, S1/S2 PDFs, or nuisance-parameter covariance;
- the NR-efficiency curve as a tabulated YAML table.

The paper states that the best-fit NEST response parameters are provided in the Data Release, and its Supplemental Table S5 gives the 15-parameter NR **mean** light-/charge-yield vector. The already archived `lz_2026_nest_nr_mean_yield_parameters.json` records that Table S5 vector. The 46-table ZIP inspected here does not contain a separate NEST configuration resource. The mean-yield vector must not be conflated with a fluctuation model or a complete event-level detector response.

The 303-point Figure S2 efficiency extraction is separately archived in `lz_2026_nr_efficiency_digitized.csv`; it is not one of the 46 YAML tables in this ZIP.

## 6. Consequences for the analysis

1. The event-coordinate samples can now be used for an observed-data cross-check and, with the paper's definitions, for reconstructing the three sample point clouds.
2. They are not calibration samples and cannot be used to tune or validate the NEST NR fluctuation model.
3. The ZIP resolves the missing observed-sample tables, but it does **not** by itself close the event-level NEST input gap.
4. Before producing a production S1/S2 Monte Carlo, obtain the separate Data Release resource/configuration or document exactly which NEST fluctuation defaults and detector-response settings are adopted.
5. Keep the final likelihood and broad parameter scan frozen until the missing response inputs and the statistical implementation are independently validated.

## 7. Reproducibility note

The original ZIP was inspected directly from the supplied conversation upload. Its SHA-256 is recorded above. This audit file records the archive contents and validation results; it does not replace the original ZIP or claim that the raw ZIP has been copied into the Git repository.
