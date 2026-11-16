# LZ 2026 NR full-band parameter-sensitivity and drift audit

Date: 2026-11-16

**Status:** source-level parameter audit and corrected event-local-drift workflow are complete; outputs are archived. Pre-fix band numbers remain historical diagnostics and are superseded. The corrected full-band proxy still does not reproduce the exact collaboration calibration-source geometry or likelihood.

## 1. Scope

This study generates a full-range NR response-band proxy for the observed candidate event using the public NEST EFT2024 configuration candidate pinned at commit 541b6430dae6ea289cf110c99f174a9187f7fdee. It is a response-model cross-check, not a reproduction of the collaboration's calibration band or a likelihood.

The driver is cpp/lz_2026_nr_flat_spectrum_eft2024.cc. It samples:
- true NR recoil energy uniformly over 0.1–330 keV;
- either a uniform active-TPC cylinder (uniform_tpc) or a fixed candidate position (candidate);
- 200,000 events for the uniform-TPC sample and 100,000 for the fixed-position sample, per model family.

The fixed-position diagnostic uses the candidate coordinates (459, 0, 264) mm. The observed point is S1c = 540.07916 phd and S2c = 9267.53 phd, hence log10(S2c/phd) = 3.96696400056. Bands are built in 5-phd S1c bins, with at least 100 events per bin.

The driver uses NEST Parametric S1 and Full S2. It passes the true event position as the reconstructed position, so position correction is idealized. This is not a waveform-level LZ detector simulation.

## 2. Model families and what is isolated

| Configuration | NR mean-yield vector | NR quanta-fluctuation vector | ER mean yields / detector |
|---|---|---|---|
| eft2024 | Public full-precision EFT2024 | Public full-precision EFT2024 | EFT2024 |
| tableS5 | Rounded printed Table S5 | EFT2024 | EFT2024 |
| eftmean_wswidth | EFT2024 | WS2024 vector | EFT2024 |
| eftmean_genericwidth | EFT2024 | Generic NEST vector | EFT2024 |
| ws2024 | WS2024 | WS2024 | WS2024 |
| generic | Generic NEST | Generic NEST | EFT2024 detector overrides |

The historical config names eftmean_wswidth and eftmean_genericwidth are retained for reproducibility. Physically, these are not merely a change of one scalar width: they replace the shared NRERWidthsParam vector. For NR events, only its NR-active entries affect the NR quanta fluctuations; the ER-specific entries are not used by the NR branch.

The tableS5 configuration uses the rounded printed vector
\[
(11.2,1.1,0.052,-0.0533,10.8,0.53,1.4,0.31,2.5,0.50,1.39,1.74,0.0230,0.0289,74.7),
\]
while retaining the EFT2024 detector overrides, ER-yield vector, and NR fluctuation vector. This isolates rounding in the printed NR mean-yield parameters from changes in the fluctuation model.

## 3. Direct NEST source audit: NR fluctuation parameter indices

The pinned src/NEST.cpp implementation of GetQuanta separates NR and ER fluctuation branches. For xenon NR, where the Lindhard factor is below unity:

\[
F_i = p_0 + p_{11}\,\overline N_i,\qquad
F_{\rm ex} = p_1 + p_{12}\,\overline N_{\rm ex},
\]

\[
\omega_{\rm NR}
=\max\left[0,\,
p_2\exp\left(-\frac{1}{2}
\frac{(f_e-p_3)^2}{p_4^2}\right)\right],
\]

and the code applies

\[
\lambda_{\rm Chen}=
\begin{cases}
1+p_2,&p_2<0,\\
1,&p_2\geq0.
\end{cases}
\]

The recombination variance entering the electron fluctuation is

\[
V_{\rm rec}
=\lambda_{\rm Chen}P_{\rm rec}(1-P_{\rm rec})N_i
+\omega_{\rm NR}^2N_i^2.
\]

The NR skew-Gaussian parameter is p5. Therefore the NR-active entries of NRERWidthsParam are indices 0–5, 11, and 12. The ER-only field/charge-fraction and double-Gaussian controls at indices 6–10 and 13–16 do not enter the NR recombination branch.

The key sign difference is:

| Vector | p2 | lambda_Chen | omega_NR |
|---|---:|---:|---|
| EFT2024 | −0.707 | 0.293 | Clamped to zero |
| WS2024 | +0.0383 | 1 | Nonzero |
| Generic NEST | +0.0400 | 1 | Nonzero |

Thus changing the NR fluctuation vector changes more than a Gaussian width. It changes the binomial recombination suppression and the additional non-binomial recombination variance, as well as the ion/exciton Fano terms and skewness. This is a physically significant nuisance-model choice.

## 4. Initial result and bitwise comparison with the corrected driver

The initial full-band run [43660321058](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43660321058) completed with 200,000 uniform-TPC events per family. Its driver evaluated the drift velocity once at the detector centre and reused it for every event.

A source check of the pinned LZ detector header shows that FitEF(x,y,z) returns exactly 96.5 V/cm for every position. The corrected event-local driver therefore evaluates the same drift velocity, 1.33036177945 mm/us, for every event in this detector configuration. A row-by-row comparison of all 10 shared samples between the initial artifact and the corrected local-drift artifact found every common physical output field to be bitwise identical. The old implementation was insufficiently general for a future nonuniform field map, but it did **not** bias the present uniform-field results.

The diagnostic values at 540–545 phd, now independently reproduced by the corrected driver, are:

| Configuration | Uniform-TPC candidate offset |
|---|---:|
| EFT2024 | −1.95 sigma-equivalent |
| EFT2024 means + WS2024 NR fluctuations | −1.63 sigma-equivalent |
| EFT2024 means + generic NR fluctuations | −1.65 sigma-equivalent |
| WS2024 | −5.00 sigma-equivalent |
| Generic NEST | −6.41 sigma-equivalent |

**These values are numerically unchanged by the local-drift correction for the current constant-field detector.** They are still diagnostic-only because the flat true-energy prior and uniform-TPC spatial prior are not the collaboration's calibration priors.

## 5. Local drift-velocity correction

The old implementation calculated
\[
v_d=v_d(E_{\rm centre})
\]
once outside the event loop, then used it for every event's drift time and S1/S2 calls. The pinned LZ detector class currently returns a constant 96.5 V/cm, so this was numerically equivalent to a local evaluation for the present model. The code was nevertheless refactored to calculate from each event's field, so a future nonuniform field map cannot silently reuse a central drift velocity.

The corrected implementation calculates inside the event loop:
\[
v_{d,i}=v_d(E_i),\qquad
d_i=z_{\rm top}-z_i,\qquad
t_{d,i}=d_i/v_{d,i}.
\]

The same local \(v_{d,i}\) is passed to the S1 and S2 response calls. The CSV now stores drift_distance_mm, drift_time_us, and drift_speed_mm_us for every event. The Python summarizer checks
\[
\left|\frac{t_{d,i}v_{d,i}-d_i}{\max(d_i,1\ {\rm mm})}\right|<10^{-9}
\]
for every row and fails the workflow if this closure is violated. It also records the sampled local-field and drift-speed ranges.

The code correction was committed at 9224ba865c51209e96eb968eecc1bfa67d0f6308; the Table S5 branch was added in the same commit. The closure check was added in 438cf179a056c680fad4b201f9070eceb819d488.

## 6. Interpretation limits

1. A uniform true-energy prior over 0.1–330 keV is a diagnostic prior, not the actual D-D or AmBe calibration-neutron spectrum. The NR band can depend on the energy and spatial priors after projecting onto S1c.
2. A uniform active-TPC spatial prior is not the calibration source deployment geometry or the official 4.71-tonne fiducial-volume distribution.
3. The fixed-position sample is a local diagnostic at the candidate coordinates, not a reconstruction-uncertainty convolution.
4. True and reconstructed positions are set equal; position reconstruction smearing and its correlations with S1/S2 are absent.
5. NEST Parametric S1 is not a waveform-level simulation. The separate Parametric-versus-Full S1 cross-check does not supply the full trigger, SS, data-quality, FV, Skin/OD veto, or live-time selection.
6. The public EFT2024 configuration is a strong candidate, not a confirmed copy of the collaboration's exact production build.
7. The 5-phd S1c-bin percentile offset is a diagnostic, not a likelihood-based event significance. The published approximately 1.5-sigma statement must be compared using the collaboration's actual calibration-band construction and event selection.

## 7. Required acceptance before using the result

- [x] Corrected local-drift workflow completes and the per-event kinematic closure passes.
- [x] The rounded Table S5 mean-yield candidate is included in the same corrected run.
- [x] EFT2024 and NR-fluctuation-isolation samples are compared with a deterministic finite-MC bootstrap (the bootstrap output is archived by the follow-up workflow).
- [ ] Replace the flat-energy and uniform-TPC priors with documented D-D/AmBe calibration priors, or retain the present result explicitly as diagnostic-only.
- [ ] Resolve the exact collaboration production NEST/configuration and full analysis-selection provenance before any likelihood use.

## 8. Reproduction references

- [LZ 2026 paper, arXiv:2609.02823](https://arxiv.org/abs/2609.02823)
- [Pinned NEST source, commit 541b643](https://github.com/NESTCollaboration/nest/tree/541b6430dae6ea289cf110c99f174a9187f7fdee)
- [NR full-band driver](../cpp/lz_2026_nr_flat_spectrum_eft2024.cc)
- [Full-band summarizer](../summarize_lz_2026_nr_flat_band_eft2024.py)
- [Workflow](../../../.github/workflows/lz-2026-nr-eFT2024-full-band.yml)
- [NEST release-lineage audit](LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md)


## 9. Corrected full-band results including rounded Table S5

The corrected local-drift and Table S5 run completed successfully:
- [GitHub Actions run 43660830473](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43660830473), commit e6e52637b55eb45e41848a3c295dbeaf6ab92d72.
- Artifact ID: 14139657582.
- ZIP SHA-256: c31eed600f9673641b001d4321cb712b98312d81b592300a71bb0767bfd6ecaf.
- 12 CSV samples: six model families, each with uniform-TPC (200,000 events) and fixed-candidate-position (100,000 events) samples.
- The summary has 90 pairwise band comparisons.
- All rows pass the local drift kinematic closure. The maximum relative closure residual is 1.08e−11. FitEF is exactly 96.5 V/cm for all sampled positions, and the corresponding drift speed is 1.33036177945 mm/us.

The candidate offset in the 540–545 phd bin is:

| Configuration | Uniform-TPC z_eq | Fixed-position z_eq |
|---|---:|---:|
| EFT2024 full precision | −1.9545 | −2.0276 |
| Rounded Table S5 means + EFT2024 fluctuations | −2.3617 | −2.3816 |
| EFT2024 means + WS2024 NR fluctuation vector | −1.6278 | −1.5740 |
| EFT2024 means + generic NR fluctuation vector | −1.6506 | −1.6815 |
| WS2024 | −4.9987 | −5.2900 |
| Generic NEST | −6.4110 | −7.0197 |

Here z_eq = (log10(S2c_observed) − median)/sigma80 and sigma80 = (q90 − q10)/2.5631031311. It is a percentile-width diagnostic, not a likelihood significance.

The rounded Table S5 mean vector moves the candidate from −1.95 to −2.36 sigma-equivalent relative to the full-precision EFT2024 vector. This confirms that rounding the published mean-yield parameters is not harmless for this band comparison. The full-precision public vector should be retained for the executable EFT2024 candidate; the rounded Table S5 vector remains a separate reproducibility alternative.

A separate direct NEST C++ mean-yield cross-check confirms the mechanism. Across
528 comparisons (both vectors, three Xe isotopes, both OldW13eV settings, and
11 energies), the Python port agrees with NEST to better than
\(3.4\times10^{-16}\) scaled absolute difference. At 248 keV, the rounded
Table S5 vector gives 7.4528% fewer photons, 0.3846% more electrons, and
6.9997% fewer total quanta than EFT2024. At 269.9 keV the changes are
−7.5301%, +0.3846%, and −7.1019%, respectively. The high-energy \(p(E)\)
extension is identical; the change comes from the rounded NR normalization,
slope, and charge-yield parameters. See the
[dual-vector NEST cross-check, run 43696267500](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43696267500),
artifact 14154536453. This is a mean-yield validation only; the separate
event-level 2D response remains the relevant test of how these differences
propagate through S1/S2 and the ROI.

The two width-isolation variants move the offset closer to the paper's approximate −1.5-sigma statement. This is not evidence that either alternative is the production model. The candidate event must not be used to tune the NR fluctuation vector; doing so would be circular. The public EFT2024 vector remains the primary public candidate until the exact collaboration production configuration or calibration closure is established.

## 10. Finite-MC uncertainty

A deterministic event bootstrap is implemented in
[bootstrap_lz_2026_nr_full_band_candidate.py](../bootstrap_lz_2026_nr_full_band_candidate.py).
It resamples events within the 540–545 phd S1c bin, uses 2,000 replicas and seed 20261115, and recomputes q10, median, q90, sigma80, and z_eq. Its confidence intervals quantify finite-MC uncertainty only; they do not include uncertainty in the energy prior, spatial prior, NEST configuration, calibration model, or detector response.

The bootstrap-enabled workflow completed successfully:
- [GitHub Actions run 43661274708](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43661274708), commit 0705ffe47c03ef6051973294d3bbe01b6acbbfd0.
- Artifact ID: 14139997390.
- ZIP SHA-256: 1f053db6e3d49863c8b36b6a753d4e4eed0410a8530e73d98eb62d771f4bd967.
- The artifact contains 12 event CSVs, the 90-comparison band summary, and the deterministic bootstrap JSON.

The 95% percentile intervals for the uniform-TPC sample are:

| Configuration | z_eq | Bootstrap 95% interval |
|---|---:|---:|
| EFT2024 full precision | −1.9545 | [−2.0707, −1.8348] |
| Rounded Table S5 means | −2.3617 | [−2.5151, −2.2118] |
| EFT2024 means + WS2024 NR fluctuations | −1.6278 | [−1.7665, −1.5166] |
| EFT2024 means + generic NR fluctuations | −1.6506 | [−1.7668, −1.5685] |
| WS2024 | −4.9987 | [−5.2817, −4.8043] |
| Generic NEST | −6.4110 | [−6.7298, −6.0910] |

For the fixed candidate-position sample:

| Configuration | z_eq | Bootstrap 95% interval |
|---|---:|---:|
| EFT2024 full precision | −2.0276 | [−2.2904, −1.8570] |
| Rounded Table S5 means | −2.3816 | [−2.5514, −2.1658] |
| EFT2024 means + WS2024 NR fluctuations | −1.5740 | [−1.6833, −1.4340] |
| EFT2024 means + generic NR fluctuations | −1.6815 | [−1.8347, −1.5261] |
| WS2024 | −5.2900 | [−5.6130, −4.9140] |
| Generic NEST | −7.0197 | [−7.4520, −6.4819] |

The bootstrap intervals are finite-MC intervals for the percentile offset conditional on this simulated sample design. They do not include model, calibration, source-spectrum, spatial-prior, or detector-systematic uncertainty. The fixed-position EFT2024+WS-width interval includes −1.5, but this is not a justification to choose that fluctuation vector: it is a diagnostic alternative, not a validated production configuration.
