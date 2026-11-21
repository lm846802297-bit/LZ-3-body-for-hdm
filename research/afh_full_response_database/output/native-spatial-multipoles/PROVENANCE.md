# 8.5 数据溯源 / Native spatial multipoles provenance

Artifact: `native AFH v6.0 rank-resolved DeltaJ and SigmaPJ multipoles for Xe-129 and Xe-131`.

| Item | SHA-256 |
|---|---|
| AFH source `v6/dmformfactor-V6.m` | `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372` |
| Native multipole CSV | `5b02bd1b8db73b450e328a27dba5e0b2434487c6861579dc3d7da3b3e0938c17` |
| Native metadata | `9750d8fb2b25c3b78428c190f11b505e42aada07bbbb432227e0dfe345e65fb2` |
| q=0 limit rows | `2acc740c748c889dbe4932d5e97bb3d9e1888d5e433e894e849403ae41165304` |
| Validation JSON | `d022b70c42ec0c83c38a113cf870a66c658a2aefb3169941d9a2a0c16cc3c605` |
| P3 native crosscheck JSON | `58e98e72c3b9d0196b90fb428478c249ffc8d28904168d5b87c2cb0558546dbe` |

Execution: AFH DMFormFactor v6.0, Wolfram 14.2.0,
`source_commit=571e3687b495ced48ef64b5f066b82236fea2b27`. The main grid is
2,401 uniform q nodes from 0 to 0.6 GeV per isotope. The four `q=0` rows are
the analytic `Limit[y -> 0]` of the native `DeltaJ` and `SigmaPJ` OBDME sums,
because the native abnormal-parity amplitudes are `0/0` at the origin.

**Scope boundary.** `PASS_NATIVE_AFH_SPATIAL_MULTIPOLES` validates 9,604 native
rank-resolved amplitude rows: Xe-129 rank 1 (2,401) and Xe-131 ranks 1,2,3
(7,203), with zero imaginary residual and the expected q grid/rank map.
`PASS_NATIVE_AFH_SPATIAL_MULTIPOLE_CROSSCHECK` additionally compares the native
archive with the P3-B Python archive over 16,807 total-response rows and the
same 9,604 rank rows. It does **not** validate the complete three-body tensor
contraction or a detector-level rate.

The machine-readable manifest is `sha256_manifest.json`; CI re-hashes every entry
and checks `rows=9604`, the rank map, the q=0 analytic-limit declaration, and the
committed P3 crosscheck status.
