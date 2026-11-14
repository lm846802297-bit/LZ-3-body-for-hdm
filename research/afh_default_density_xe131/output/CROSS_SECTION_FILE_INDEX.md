# Canonical AFH Xe-131 four-benchmark cross-section files

This is the single canonical filename index for the fixed-speed Xe-131
four-benchmark differential cross sections. When citing these files from
elsewhere in the repository, use the repository-root paths shown below;
do not shorten them to a bare \`output/...\` path.

## Canonical outputs

| Purpose | Repository-root path | Local file |
|---|---|---|
| Long-form comparison (AFH default, GCN, JJ55; 1,920 rows) | \`research/afh_default_density_xe131/output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv\` | [corrected long-form CSV](figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv) |
| Wide-form AFH/GCN/JJ55 audit (640 recoil rows) | \`research/afh_default_density_xe131/output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv\` | [wide-form audit CSV](figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv) |
| Current response/interpolation/row-count metadata | \`research/afh_default_density_xe131/output/four_benchmark_metadata.json\` | [metadata JSON](four_benchmark_metadata.json) |
| Detailed cross-section reconstruction and assumptions | \`research/afh_default_density_xe131/output/FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md\` | [cross-section audit](FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md) |

The long-form CSV is the canonical machine-readable table for downstream
plots, tables and comparisons. The wide-form CSV is an audit view of the same
corrected AFH result alongside GCN and JJ55. Both use the exact spatial
momentum
\[
q=\sqrt{2m_AE_R+E_R^2}
\]
for the AFH response and the physical equal-proton/equal-neutron response
normalized to \(R_A(0)=A^2\), with the finite-decimal normalization correction
applied only as the q-independent factor \(C_A\).

## Superseded historical file

The historical file
\`research/afh_default_density_xe131/output/figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv\`
is retained for provenance only and is **superseded**. Its AFH response
column was copied from the GCN response rather than populated from the AFH
response table. Do not use it for plots, rate calculations, tables, or
manuscript results.

The historical filename is intentionally not deleted so old commits and
research notes remain auditable. New code and documentation must point to
the corrected long-form CSV (or the wide-form audit file where its layout is
explicitly needed). The historical filename should appear only in this
index, the audit trail, or a clearly labelled superseded-file note.

## Downstream rate-level products are different data products

The LZ efficiency-weighted AFH-7/Hybrid-9 event yields are not cross-section
tables and must not be cited as substitutes for the files above. They are
derived from continuous natural-xenon spectra and the LZ 2026 one-dimensional
efficiency curve. Their repository-root archive is
\`research/lz_detector_response/lz_2026_extended_nr/afh7_hybrid9_rate_level_yields/\`.

## Scope

These are fixed \(v=800\;\mathrm{km\,s^{-1}}\), Xe-131 differential
cross-section diagnostics. They reuse the archived \(I_6(E_R)\) kernel grid;
they are not a fresh independent three-body integration, a natural-xenon
halo fold, or a detector-level likelihood.
