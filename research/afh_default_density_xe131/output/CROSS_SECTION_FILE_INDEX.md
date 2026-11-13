# Canonical AFH Xe-131 four-benchmark cross-section files

This index is the single file-name reference for the fixed-speed Xe-131
four-benchmark comparison.

## Canonical outputs

| Purpose | Canonical file |
|---|---|
| Long-form comparison (AFH default, GCN, JJ55; 1,920 rows) | output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv |
| Wide-form AFH/GCN/JJ55 audit (640 recoil rows) | output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv |
| Current response/interpolation/row-count metadata | output/four_benchmark_metadata.json |
| Detailed cross-section reconstruction and assumptions | output/FOUR_BENCHMARK_CROSS_SECTION_AUDIT.md |

The long-form CSV is the canonical machine-readable table for downstream
plots and comparisons. The wide-form CSV is an audit view of the same
corrected AFH result alongside GCN and JJ55. Both use the exact spatial
momentum
\[
q=\sqrt{2m_AE_R+E_R^2}
\]
for the AFH response and the physical equal-proton/equal-neutron response
normalized to \(R_A(0)=A^2\).

## Superseded historical file

output/figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv is retained for
provenance only and is **superseded**. Its AFH response column was copied
from the GCN response rather than populated from the AFH response table.
Do not use it for plots, rate calculations, tables, or manuscript results.

The historical filename is intentionally not deleted so old commits and
research notes remain auditable. New code and documentation must point to
output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv (or the wide-form
audit file where its layout is explicitly needed).

## Scope

These are fixed \(v=800\;\mathrm{km\,s^{-1}}\), Xe-131 differential
cross-section diagnostics. They reuse the archived \(I_6(E_R)\) kernel grid;
they are not a fresh independent three-body integration, a natural-xenon
halo fold, or a detector-level likelihood.
