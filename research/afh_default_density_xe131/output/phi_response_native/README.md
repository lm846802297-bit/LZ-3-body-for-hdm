# Native Xe-131 M / Phi'' AFH response export

**Archived — response-level PASS**

This directory contains the completed native Wolfram AFH v6.0 export for
Xe-131 and the corresponding Python acceptance summary.

| File | Contents |
|---|---|
| afh_default_xe131_M_PhiPP_native.csv | 2,401 rows; raw AFH \(W_M^{00}\), \(W_{\Phi''}^{00}\), \(W_{M\Phi''}^{00}\), raw and physical response conventions |
| afh_default_xe131_M_PhiPP_metadata.json | AFH source and density-matrix SHA-256, Wolfram version, exact q grid, oscillator length and normalization |
| afh_default_xe131_M_PhiPP_validation.json | Python validation summary; status PASS |
| sha256_manifest.json | SHA-256 digests of the three files above |

The export uses Xe-131 \((A,Z,J_A)=(131,54,3/2)\), the built-in
sdgXe131 density matrix (67 entries), and 2,401 points from 0 to 0.6 GeV
in 0.25 MeV steps. The physical equal-p/n mapping
\(R_X^{\rm phys}=4R_X^{\rm raw}\) is applied once to all three responses.

The validator checks the grid, \(y=(q_Ab_A/2)^2\), response conversion,
factor-four bookkeeping, diagonal positivity, imaginary residuals,
Cauchy-Schwarz consistency, q=0 charge normalization, and CSV provenance.
It does not independently recalculate the AFH matrix elements or contract
the response with the full three-body tensor.

See the detailed audit record
(../../audit/AFH_PHI_RESPONSE_XE131_NATIVE_PLAN.md) for numerical findings
and limitations.
