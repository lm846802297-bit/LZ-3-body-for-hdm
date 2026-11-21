# 8.4 数据溯源 / Seven-isotope native AFH provenance

Artifact: `AFH v6.0 seven-isotope eight-response native archive`.

| Item | SHA-256 |
|---|---|
| AFH source `v6/dmformfactor-V6.m` | `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372` |
| Xe-128 CSV | `7c492562fca01cdfd2a185e671755c84b04bf6b5e34cc1a313f8e76b628a8abb` |
| Xe-129 CSV | `80684a3f1201bc312c1c60af3b5b263e1480ab5a05874743a738cce9b86dc532` |
| Xe-130 CSV | `36534761e2b061e4e3cff14d3f3ec0f679f68fa3455f8596e23a654f21cbe44a` |
| Xe-131 CSV | `585ab0f483be0d8131566cefc4cb420c6db7e07bebbcd2b887da568cda2f4ffb` |
| Xe-132 CSV | `7f03e4a14c1e646e624b2d53f8c5ca42f0538c45f4670c524d9a1e39fe8d768e` |
| Xe-134 CSV | `031b30c6b7b0e9e720b155979fc7c9ab37665303e7c9fbf8678bde78f39f3885` |
| Xe-136 CSV | `c00ec4ce6c55fd7fa925a2bf2c3436057a3f54ad31710e1c8f555d7622c7dea4` |
| Native metadata | `05d6e55a8069aba8361c5b4850429c6b8c3a1d06b35798967a998a7815fdb7a6` |
| Python internal validation | `ea1073dcef2ed959b25373e613f1140ef340c2043c16e8e5d044b612e457ef23` |
| Native comparison | `1d3b68ac621e22788a676a9a2f2c97bd433c70883dc30ceb191f69d4d366a030` |

Execution: AFH DMFormFactor v6.0, Wolfram 14.2.0, `source_commit=571e3687b495ced48ef64b5f066b82236fea2b27`,
2,401 uniform q nodes from 0 to 0.6 GeV per isotope, eight `ResponseNuclear[y,index,0,0]`
channels, 16,807 rows total.

**Scope boundary.** `PASS_PROVENANCE_NATIVE_AFH_FULL` validates the seven-isotope
eight-response native database pointwise against the Python AFH-8 reference
(`rows_compared=16807`, `native_afh_validated=true`). It does **not** validate the
rank-resolved spatial multipoles in `../native-spatial-multipoles/`, the three-body
tensor contraction, or a detector-level event rate. No claim about those sectors is
implied by this artifact.

The machine-readable manifest is `sha256_manifest.json`; CI re-hashes every entry and
checks the comparison gate via `verify_native_full_response_provenance.py`.
