# LZ 2026 energy-resolved selection, MC uncertainty, and black-tail audit

Date: 2026-11-15  
Branch: \`integration/lz-2026-nest-nr-fullband-20261115\`  
NEST source pin: \`541b6430dae6ea289cf110c99f174a9187f7fdee\`

## 1. Scope and status

This note records the artifact-level follow-up to the energy-resolved Fig. S2 residual-selection bridge. It has three separate goals:

1. distinguish finite NEST response-MC fluctuations from a mismatch between the NEST WS-ROI proxy and the published Fig. S2 cumulative efficiencies;
2. identify which true-recoil-energy intervals dominate the \(m_s=360\) keV (black) benchmark;
3. record the independent-seed 1-keV/5-keV and 1-keV/0.5-keV grid checks.

**Status:** the rate-level bridge and its numerical diagnostics reproduce in CI. The 5-keV black-support point estimates satisfy the proposed 1% rate and 1% two-dimensional TV gates. The 0.5-keV high-tail check also satisfies those point-estimate gates. None of these results closes the official LZ two-dimensional selection response, calibration-source geometry, FV, veto samples, or nuisance covariance. No profile likelihood is authorized by this note.

## 2. Exact meaning of the rate-level bridge

For a true-recoil bin \(i\), define

- \(R_i\): exact integral of the three-body spectrum over the bin;
- \(\epsilon_{\mathrm{WSROI}}^{\mathrm{NEST}}(i)\): event-weighted NEST acceptance after its signed S1/S2 flags and the explicit WS ROI mask;
- \(C_{\mathrm{orange}}(i)\), \(C_{\mathrm{green}}(i)\), and \(C_{\mathrm{black}}(i)\): the published cumulative Fig. S2 efficiencies.

The current diagnostic constructs
\[
R_i^{\mathrm{fact}}
=R_i\,\epsilon_{\mathrm{WSROI}}^{\mathrm{NEST}}(i)
  \frac{C_{\mathrm{green}}(i)}{C_{\mathrm{orange}}(i)}
\]
and compares it with
\[
R_i^{\mathrm{Fig.S2}}=R_i\,C_{\mathrm{black}}(i).
\]
Consequently,
\[
\frac{R_i^{\mathrm{fact}}}{R_i^{\mathrm{Fig.S2}}}
=\frac{\epsilon_{\mathrm{WSROI}}^{\mathrm{NEST}}(i)}
       {C_{\mathrm{black}}(i)/C_{\mathrm{green}}(i)}.
\]

This is a **substitution-closure diagnostic**, not a proof that the numerator and denominator are the same conditional probability. In particular:

- NEST Parametric S1 coincidence is a PMT-occupancy approximation, not waveform-level three-PMT-in-time reconstruction.
- NEST's configured S2 pulse threshold is not the hardware DAQ trigger.
- The Fig. S2 black/green ratio is conditional on the preceding published cumulative stages, including SS and data-analysis cuts.
- The NEST event driver does not model the full official SS/data-analysis, calibration-source, fiducial-volume, Skin/OD, or DAQ response.

Therefore, the mismatch below must not be interpreted as an isolated correction to the official LZ ROI efficiency. It quantifies the failure of the present NEST WS-ROI proxy to substitute for the published conditional ROI factor while retaining the Fig. S2 green/orange factor.

## 3. Artifact-level MC uncertainty result

Source workflow: [run 43706124539](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43706124539)  
Artifact: \`lz-2026-energy-resolved-selection-bridge\`, ID \`14158179257\`.

The artifact was downloaded and inspected. It contains:

- 16 benchmark × nuclear-model × response-family summaries;
- 4,240 per-energy-bin bridge rows;
- 4,240 per-energy-bin weighted-MC diagnostic rows;
- 16 black-benchmark high-energy-band rows.

For fixed sampled event weights \(w_j=dR/dE_R(E_j)\) and response-pass indicators \(I_j\), the weighted acceptance is
\[
\hat\epsilon=\frac{\sum_j w_j I_j}{\sum_j w_j}.
\]
The response-MC plug-in variance is estimated from
\[
\widehat{\mathrm{Var}}(\hat\epsilon)
=\frac{\sum_j w_j^2(I_j-\hat\epsilon)^2}
       {(\sum_jw_j)^2}.
\]
This is a weighted ratio-estimator diagnostic for the NEST/WS-ROI response sample. It is not a complete detector uncertainty and does not include the digitization uncertainty of Fig. S2, model uncertainty, or missing selection migration.

### Integrated black-benchmark results

| Response family | Nuclear response | Factorized vs Fig. S2 final | Relative response-MC SE of factorized rate |
|---|---|---:|---:|
| EFT2024 | GCN | −7.6252% | 0.2002% |
| EFT2024 | JJ55 | −7.5938% | 0.1958% |
| Table S5 | GCN | +13.0271% | 0.1215% |
| Table S5 | JJ55 | +12.7021% | 0.1191% |

The response-MC-only uncertainty is much smaller than the integrated rate mismatch. This rules out ordinary finite NEST response statistics as a sufficient explanation for the observed 7.6–13.0% difference.

The ratio of the rate mismatch to this response-MC standard error is retained in the artifact only as a **scale diagnostic**. It is not a statistical pull, significance, or p-value: the Fig. S2 extraction uncertainty and the unproven event-level SS/DA factorization are not included.

The two replica labels in the original production are disjoint halves of one seeded event stream, not independent-seed productions. Their split-half difference is a stability diagnostic only. The independent-seed checks are recorded separately below.

## 4. Where the black benchmark receives its final rate

The black benchmark has nonzero spectral support beginning near 210 keV. The four bands below are aligned to the 1-keV bridge bins. The final-rate fractions are from the Fig. S2 black cumulative curve and are independent of the NEST response family.

| True recoil band (keV) | GCN fraction of black Fig. S2 final rate | JJ55 fraction |
|---|---:|---:|
| 200.4–230.4 | 16.689% | 16.897% |
| 230.4–245.4 | 28.555% | 29.342% |
| 245.4–260.4 | 10.616% | 10.711% |
| 260.4–269.9 | 44.139% | 43.050% |

Thus the final 9.5-keV interval, 260.4–269.9 keV, carries approximately 43–44% of the black benchmark's Fig. S2 final rate. This is why the high-energy end cannot be represented by a uniform average efficiency.

### NEST WS-ROI substitution versus Fig. S2 conditional ROI

The following entries are \(R^{\mathrm{fact}}/R^{\mathrm{Fig.S2}}-1\), evaluated after integrating within each band. Parentheses show the JJ55 result; the unparenthesized value is GCN.

| True recoil band (keV) | EFT2024 | Table S5 |
|---|---:|---:|
| 200.4–230.4 | −1.691% (−1.693%) | −0.118% (−0.118%) |
| 230.4–245.4 | −6.542% (−6.567%) | −0.820% (−0.824%) |
| 245.4–260.4 | −17.224% (−17.131%) | +1.359% (+1.215%) |
| 260.4–269.9 | −8.261% (−8.237%) | +29.762% (+29.812%) |

This decomposition localizes the model-dependent discrepancy:

- With EFT2024, the NEST WS-ROI acceptance is increasingly below the Fig. S2 conditional ROI factor in the 245.4–260.4 keV band, then remains below it in the final band.
- With Table S5, the 260.4–269.9 keV band is substantially above the Fig. S2 conditional ROI factor. Because this band carries roughly 43–44% of the final black rate, it drives much of the positive integrated mismatch.
- The GCN/JJ55 changes are small compared with the EFT2024/Table S5 response-family change in these bands.

For example, in the 260.4–269.9 keV band the event-weighted NEST WS-ROI acceptance is approximately 0.596 (EFT2024, GCN) or 0.843 (Table S5, GCN), while the Fig. S2 conditional ROI factor is approximately 0.650. This is a diagnostic comparison between two differently conditioned response constructions, not evidence that the official LZ efficiency is wrong.

## 5. Independent-seed recoil-grid checks

### 5.1 Black high-energy tail: 1 keV versus 0.5 keV

Source workflow: [run 43698938527](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43698938527).

- Three independent full productions per grid and per response family.
- 10,000 events per energy stratum per seed.
- True recoil interval: 225.4–269.9 keV.
- 1-keV and 0.5-keV productions use disjoint seed sets.
- Both GCN/JJ55 and NEST/NEST+WS-ROI modes were compared.

| Response family | Maximum rate difference (0.5 vs 1 keV) | Maximum TV distance of mean 2D maps | 1% / 1% point-estimate gate |
|---|---:|---:|---|
| EFT2024 | 0.01862% | 0.84890% | Pass |
| Table S5 | 0.01347% | 0.80383% | Pass |

This supports retaining the 0.5-keV high-energy refinement as a convergence cross-check. Three independent seeds provide a descriptive seed-to-seed stability estimate, not a complete cell-by-cell covariance matrix.

### 5.2 Black signal support: 1 keV versus 5 keV

Source workflow: [run 43700086189](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43700086189).

- Three independent full productions per grid and per response family.
- 16,000 events/keV/seed, i.e. 16,000 events in a full 1-keV bin and 80,000 in a full 5-keV bin.
- True recoil interval: 210.0–269.9 keV, covering the nonzero black-benchmark support.
- GCN/JJ55 and NEST/NEST+WS-ROI modes were included.

| Response family | Maximum accepted-rate difference (5 vs 1 keV) | Maximum TV distance of mean 2D maps | 1% / 1% point-estimate gate |
|---|---:|---:|---|
| EFT2024 | 0.63217% | 0.86485% | Pass |
| Table S5 | 0.31484% | 0.88774% | Pass |

Both families pass the proposed point-estimate thresholds on the black signal-support interval. The rate differences for the NEST+WS-ROI mode are nevertheless about 4.7–5.0 combined seed standard errors in this high-statistics study. This does not invalidate the 1% engineering tolerance, but it means the 5-keV and 1-keV estimators are not statistically indistinguishable at the current event count. The point-estimate gate and the seed-uncertainty diagnostic answer different questions and must both be reported.

The independent-seed result is limited to the black benchmark's 210.0–269.9 keV support. It does not replace the full-range convergence checks for the other benchmarks.

## 6. Recommended grid decision

For the current numerical response-folding task, retain:

- **1 keV** as the reference grid;
- **5 keV** as an accepted computational grid for the black-support comparison under the stated 1% accepted-rate and 1% mean-map TV point-estimate tolerances;
- **0.5 keV** as the high-energy refinement cross-check.

Do not describe this as validation of the full LZ detector response. The 5-keV acceptance is a numerical interpolation/integration decision for the present NEST proxy, not permission to omit detector-response systematics or to use the current proxy as the official signal PDF.

## 7. Remaining work before a physical signal prediction

The next tasks should address the missing conditional response rather than simply increasing the same NEST sample:

1. obtain or reconstruct the joint conditional mapping between true recoil energy, S1c, S2c, DAQ trigger, and the official selection stages;
2. distinguish the NEST S1 coincidence approximation from the official S1 pulse-finding/three-PMT timing requirement;
3. model the DAQ trigger separately from the NEST S2 pulse threshold;
4. add SS reconstruction and data-analysis cuts as conditional migration/acceptance, not as an unqualified scalar factor;
5. implement the 4.71-tonne FV and calibration-source spatial distributions;
6. construct science, prompt-veto, and delayed-veto sample responses;
7. propagate Fig. S2 digitization/envelope and detector nuisance covariance;
8. only after the above, build the final selected two-dimensional signal PDF and profile likelihood.

Until then, the correct deliverable is a reproducible rate-level detector-response diagnostic with explicit missing-response terms—not a final LZ exclusion or discovery sensitivity.
