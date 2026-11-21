# 8.3 数据溯源 / Data provenance

Artifact: `121-node native Xe-131 charge-response export near the W_M diffraction minimum`.

| Item | SHA-256 |
|---|---|
| AFH source `v6/dmformfactor-V6.m` | `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372` |
| Dense CSV `xe131_dense_charge_response_dip_native.csv` | `d3a6b418ec5565850884ea44ffceb2e2c0a3684c0a8ec13744c54b65a5141b14` |
| Dense metadata `xe131_dense_charge_response_dip_metadata.txt` | `865a67afe87923ba82babdfca4204830d416d241bb447ca301fb68634d77cc7d` |
| Validation JSON `xe131_dense_charge_dip_validation.json` | `b93c851ac8af0a6b0797fca31d4a8293d1e6bf7162d7bb935709fcf8dd1d7eb0` |
| Coarse native reference `afh_default_xe131_M_PhiPP_native.csv` | `b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff` |

Execution: AFH DMFormFactor v6.0, Wolfram 14.2.0, `source_commit=3b0dd39a58ee6ce9e91ab748bcbecf11edcf2356`, q = 0.2545–0.2575 GeV, step 0.000025 GeV.

**Scope boundary.** The `PASS_NATIVE_XE131_DENSE_CHARGE_DIP` result validates only the three Xe-131 charge responses
\(W_M\), \(W_{\Phi''}\) and \(W_{M\Phi''}\) at the 121 dense nodes, including 13 overlap nodes against the
2,401-node native coarse export, with zero imaginary residual. It does **not** validate the remaining
spatial AFH multipoles, the complete seven-isotope / eight-response native database, or the three-body
tensor contraction. No claim about those sectors is implied by this artifact.

The machine-readable manifest is `sha256_manifest.json`; CI re-hashes every entry and checks the
validation scope via `verify_xe131_dense_charge_dip_provenance.py`.
