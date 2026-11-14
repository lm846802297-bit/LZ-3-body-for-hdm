# Natural-xenon AFH inputs

This directory contains immutable inputs and source-derived tables used by the natural-xenon response and halo calculations.

| File or directory | Meaning | Scientific status |
|---|---|---|
| `afh_default_density_matrices/` | Seven AFH v6.0 built-in default-density matrices: Xe-128, 129, 130, 131, 132, 134 and 136 | Source-extracted inputs; Xe-124 and Xe-126 have no AFH v6.0 default matrix |
| `natural_xenon_isotope_weights.csv` | Nine-isotope natural abundances and mass data | Use all nine isotopes for target-number normalization; do not renormalize the seven AFH-supported fraction |
| `afh_response_samples.csv` | Historical 28-point response sample table | PCHIP/interpolated legacy input; diagnostic only for precision work |
| `afh_selected_exact_q_responses.csv` | 56 selected-point responses: seven isotopes, four recoil energies and two nuclear-mass schemes | Direct exact-spatial-q finite-sum values; independently checked with 60-digit mpmath |
| `afh_default_density_matrices/density_matrix_extraction_metadata.json` | Matrix extraction provenance | Retain with the source-derived matrices |

The authoritative upstream source is the preserved `v6/dmformfactor-V6.m` file at the repository root. The response-sample file and direct exact-q table are not interchangeable: the former stores historical PCHIP samples, while the latter stores finite-sum evaluations at the requested exact spatial momentum transfers.

Do not edit source inputs in place. New extractions or recalculations should be versioned separately and accompanied by source provenance and SHA-256 records.
