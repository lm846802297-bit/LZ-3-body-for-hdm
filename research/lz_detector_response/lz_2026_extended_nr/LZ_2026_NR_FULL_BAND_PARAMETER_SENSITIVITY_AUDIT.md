# LZ 2026 NR full-band parameter-sensitivity and drift audit

Date: 2026-11-15

**Status:** source-level parameter audit complete; corrected local-drift workflow is running. Pre-fix band numbers are retained only as historical diagnostics and are superseded.

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

## 4. Pre-fix result: historical only, not valid for final interpretation

The initial full-band run [43660321058](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43660321058) completed with 200,000 uniform-TPC events per family. It used one drift velocity evaluated at the detector centre for every event, despite evaluating a position-dependent electric field for each event.

Its diagnostic values at 540–545 phd were:

| Configuration | Uniform-TPC candidate offset |
|---|---:|
| EFT2024 | −1.95 sigma-equivalent |
| EFT2024 means + WS2024 NR fluctuations | −1.63 sigma-equivalent |
| EFT2024 means + generic NR fluctuations | −1.65 sigma-equivalent |
| WS2024 | −5.00 sigma-equivalent |
| Generic NEST | −6.41 sigma-equivalent |

**These values are superseded.** They are retained here only to document why the local-drift correction was made. They must not be used as the final candidate-band comparison.

## 5. Local drift-velocity correction

The old implementation calculated
\[
v_d=v_d(E_{\rm centre})
\]
once outside the event loop, then used it for every event's drift time and S1/S2 calls. This is inconsistent with the local field map \(E_i=E(x_i,y_i,z_i)\).

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

- Corrected local-drift workflow completes and the per-event kinematic closure passes.
- The rounded Table S5 mean-yield candidate is included in the same corrected run.
- The EFT2024 and NR-fluctuation-isolation samples are compared with bootstrap or independent-seed uncertainty.
- The energy and spatial prior are either replaced with documented calibration priors or explicitly retained as diagnostic-only.
- The result is not promoted to a likelihood until the official calibration/selection provenance is resolved.

## 8. Reproduction references

- [LZ 2026 paper, arXiv:2609.02823](https://arxiv.org/abs/2609.02823)
- [Pinned NEST source, commit 541b643](https://github.com/NESTCollaboration/nest/tree/541b6430dae6ea289cf110c99f174a9187f7fdee)
- [NR full-band driver](../cpp/lz_2026_nr_flat_spectrum_eft2024.cc)
- [Full-band summarizer](../summarize_lz_2026_nr_flat_band_eft2024.py)
- [Workflow](../../../.github/workflows/lz-2026-nr-eFT2024-full-band.yml)
- [NEST release-lineage audit](LZ_2026_NEST_RELEASE_LINEAGE_AUDIT.md)
