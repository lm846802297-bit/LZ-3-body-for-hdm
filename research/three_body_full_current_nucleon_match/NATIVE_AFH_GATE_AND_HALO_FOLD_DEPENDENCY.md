# Native AFH gate and charge-sector halo-fold dependency

**Updated: 2026-11-18**

## 1. Acceptance state

The native AFH database is a hard input gate for the charge-sector halo
engine. The following states must remain distinct:

| Layer | Evidence | State |
|---|---|---|
| Seven-isotope, eight-response Python database | LZ repository workflow run 44244699196; artifact 14400843100 | PASS, Python internal validation |
| Seven-isotope, eight-response native Wolfram comparison | Private control workflow run 44222502400, attempt 2 | QUEUED; no artifact |
| Charge-sector halo engine | Requires a validated native artifact | Ready only after native gate closes |
| Full three-body AFH multipole rate | Requires the complete tensor-to-multipole projection | Not yet complete |

The Python result has 16,807 rows: seven isotopes times 2,401 q points.
Its internal positivity, normalization, and interference checks do not
constitute native Wolfram validation.

The native job is in the private repository
lm846802297-bit/research-compute-control, workflow
xe131-afh-spatial-native.yml, job native-afh-eight-response, run
44222502400 attempt 2. It targets the self-hosted labels
Windows, X64, and research-gpu. The latest observed job state is
queued, and the run has no uploaded artifact. Therefore the native gate
must remain OPEN until the runner executes and the pointwise comparator
reports PASS.

## 2. Pinned native source

The control workflow pins the LZ research checkout to:

dcefbeb7ad705b6c03f2b4689200eb1d9252e67b

The expected native package is AFH DMFormFactor v6.0. The native comparison
must cover the exact isotope set

[128, 129, 130, 131, 132, 134, 136]

and all eight AFH response indices:

| Index | Response |
|---:|---|
| 1 | M |
| 2 | SigmaDoublePrime |
| 3 | SigmaPrime |
| 4 | PhiPP |
| 5 | PhiTildePrime |
| 6 | Delta |
| 7 | signed M-PhiPP |
| 8 | signed SigmaPrime-Delta |

The expected q grid is 2,401 points per isotope from 0 to 0.6 GeV in
0.00025 GeV steps. The expected total is exactly 16,807 pointwise rows.

## 3. Native artifact layout

The private control workflow uploads the artifact root with this structure:

- native/afh_v6_xe128_eight_response_native.csv through Xe-136;
- native/native_metadata.txt;
- native-comparison.json;
- run_manifest.json;
- SHA256SUMS.txt.

The halo engine must receive the extracted artifact root, not merely the
native/ subdirectory. The comparison and provenance manifests live at the
artifact root, while the seven Wolfram CSV exports live under native/.

## 4. Hardening applied to the charge-sector engine

The engine's native gate must verify all of the following before reading
response values:

1. native-comparison.json says status=PASS,
   native_afh_validated=true, and rows_compared=16807.
2. Python rows and native rows are both 16,807; each of the seven isotopes
   has 2,401 expected points.
3. All eight response names appear in the pointwise comparison maxima and
   the failure list is empty.
4. The comparison tolerances are no looser than
   rtol=5e-7, atol=2e-12, and imaginary residual 2e-12.
5. run_manifest.json identifies the expected LZ repository, pinned source
   commit, AFH v6.0 package, isotope set, response-index map, q grid,
   Wolfram/Python versions, and control run identity.
6. The native metadata file and all seven native isotope CSVs exist.
7. SHA-256 entries for the comparison, run manifest, metadata, and seven
   native CSVs match SHA256SUMS.txt.
8. Every isotope CSV has exactly 2,401 rows, the correct isotope identity,
   the canonical q grid, finite values for all eight responses, and
   negligible imaginary residuals for all eight channels.

The engine retains only M, Phi'', and signed M-Phi'' for its current
charge-density-sector fold, but validates the full eight-response native
artifact before accepting it. This prevents a three-channel subset or a
Python-only archive from accidentally satisfying the native AFH gate.

## 5. What a native PASS does and does not mean

A successful native AFH run validates the nuclear response database against
AFH v6.0 ResponseNuclear outputs. It does not validate the three-body
particle-side multipole coefficients, the complete
L_mu_nu^(3) W_A^(mu nu) contraction, the halo integral, or the
detector response.

The charge-sector halo engine remains a diagnostic using integrated
L_00^(3) and M + Phi'' + M-Phi''. It is not the final full-current
natural-xenon spectrum.

The complete calculation remains blocked on the independent tensor-to-AFH
multipole projection audit:
AFH_THREE_BODY_TENSOR_PROJECTION_AUDIT.md.

## 6. Exact-q test correction

The exact_qA_GeV regression test now uses the full isotope mass
121.90971983538435 GeV. The previous expected q values were calculated
with the rounded mass 121.909719835 GeV. The test expectations are updated
to the exact mass-shell values; the kinematic formula itself is unchanged.
