# Native AFH rank-resolved spatial multipoles

Native Wolfram AFH v6.0 evaluation of the abnormal-parity `DeltaJ` and
`SigmaPJ` OBDME amplitudes for Xe-129 and Xe-131.

## Contents

- `afh_v6_xe129_xe131_spatial_multipoles_native.csv`: 2401 uniform momentum
  nodes (`q = 0` to `0.6 GeV`, step `0.00025 GeV`) for every isoscalar
  rank in the AFH default density matrix. Rows: `9604`
  (Xe-129 rank 1: 2401; Xe-131 ranks 1,2,3: 7203).
- `afh_v6_spatial_multipoles_q0.csv`: the four `q=0` rows, evaluated as the
  analytic `Limit[y -> 0]` of the native `DeltaJ` and `SigmaPJ` OBDME sums.
  The main CSV includes these rows; keeping them separate documents the
  removable `0/0` treatment.
- `native_spatial_multipole_metadata.txt`: source hash, grid, rank map, and
  normalization.
- `spatial_multipoles_validation.json`: structural validation (`rows=9604`,
  rank map, y consistency, zero imaginary residual).

## Columns

`A`, `q_GeV`, `y`, `multipole_J`,
`M_Delta_J_native`, `M_SigmaPrime_J_native`,
`Im_M_Delta_J_native`, `Im_M_SigmaPrime_J_native`.

The amplitudes use the raw AFH isoscalar package convention
(`tau1=tau2=0`) and the isoscalar factor `Sqrt[2/(2 TIso+1)]`. No physical
equal-proton/neutron factor-four rescaling is applied.

## Reproduce

```bash
export AFH_SOURCE_COMMIT="$(git rev-parse HEAD)"
wolframscript -file research/afh_full_response_database/run_afh_spatial_multipoles_native.wls
wolframscript -file research/afh_full_response_database/run_afh_spatial_multipoles_q0.wls
python research/afh_full_response_database/merge_afh_spatial_multipoles_q0.py \
  --main-csv research/afh_full_response_database/output/native-spatial-multipoles/afh_v6_xe129_xe131_spatial_multipoles_native.csv \
  --q0-csv research/afh_full_response_database/output/native-spatial-multipoles/afh_v6_spatial_multipoles_q0.csv \
  --out-csv research/afh_full_response_database/output/native-spatial-multipoles/afh_v6_xe129_xe131_spatial_multipoles_native.csv \
  --metadata research/afh_full_response_database/output/native-spatial-multipoles/native_spatial_multipole_metadata.txt
python research/afh_full_response_database/validate_afh_spatial_multipoles_native.py \
  --csv research/afh_full_response_database/output/native-spatial-multipoles/afh_v6_xe129_xe131_spatial_multipoles_native.csv \
  --metadata research/afh_full_response_database/output/native-spatial-multipoles/native_spatial_multipole_metadata.txt \
  --out-json research/afh_full_response_database/output/native-spatial-multipoles/spatial_multipoles_validation.json
```

Running the first command in place overwrites the merged CSV with the raw
2400-row `q>0` export; the merge step restores the four `q=0` limit rows.

## Scope boundary

This archive validates the native rank-resolved `DeltaJ`/`SigmaPJ` amplitudes,
not the `P3-B` Python multipole archive, the complete three-body tensor
contraction, or a detector-level rate. The separate
`compare_p3_spatial_multipoles_native.py` gate performs the P3 cross-check when
the P3 response/multipole archive is available.
