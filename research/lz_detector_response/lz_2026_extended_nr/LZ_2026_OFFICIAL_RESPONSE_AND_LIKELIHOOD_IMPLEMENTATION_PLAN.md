# LZ 2026 official response and likelihood: implementation plan

**Date:** 2026-11-20  
**Scope:** formal-B three-body signal prediction in the LZ extended-NR search  
**Status:** formal-B/Halo baseline frozen; rate-level three-sample signal partition implemented; official event-level response and likelihood remain in progress.

## 1. Frozen signal inputs

The accepted formal nucleon baseline is
\[
F_1^{V,N}(t_N),\qquad F_2^{V,N}(t_N),\qquad W_M(y_A),
\]
with the accepted PR #93 high-order Halo integration and the PR #96 formal-B reweight. The permanent archive is:

research/lz_detector_response/results/2026-11-20-formal-B-highorder-and-NEST/

It contains:
- the accepted seven-isotope and natural-xenon high-order Halo comparison;
- the three-strange-current formal-B reweight of that exact high-order source;
- the four-benchmark event-weighted NEST output;
- the original source ZIPs, run/artifact provenance, and a top-level SHA256SUMS.

The seven-isotope AFH set covers 99.8158% of natural-xenon atom abundance. Xe-124 and Xe-126 are absent from AFH-7 and are not renormalized. Hybrid-9 adds Helm only for those two isotopes; it must remain a separately labelled fallback scenario.

The PR #87 production benchmark (four recoil benchmarks, AFH-7 and Hybrid-9) is distinct from the PR #86 seven-isotope Full-versus-I(D_NR) approximation scan. They are not merged into one benchmark definition.

## 2. What is already calculated at detector level

### 2.1 Official one-dimensional efficiency

The central final-WIMP-search-ROI efficiency from LZ 2026 Supplemental Fig. S2 is already digitized and folded into the formal-B detector rate-yield tables in the PR #87 source artifact:
- input artifact: run 44662497177, artifact 14596147908;
- source artifact SHA-256: f5c1d8d791bffff3159a6e279e5a0e68b705bf07466be6b489ba9a49e29ce7ac;
- three strange-current alternatives;
- four signal benchmarks;
- AFH-7 and Hybrid-9;
- 24 rate-level rows in total.

The input yields use the 2.84 tonne-year exposure (220 live days × 4.71 t), the 5.4–269.9 keV search interval, and the published Fig. S2 final cumulative efficiency. They do not include energy-resolution smearing, a two-dimensional signal PDF, a background likelihood, or an exclusion construction.

The Fig. S2 efficiency stages are trigger, S1 threshold, SS reconstruction and data-analysis cuts, and the final WS ROI. The final curve crosses 50% at 269.9 keV. The rate-level B yields must be treated as already efficiency-folded; do not multiply Fig. S2 into them again.

### 2.2 Three-sample signal-rate partition

The published random-coincidence losses for unrelated TPC signals are 0.01% into the prompt-veto sample and 2.86% into the delayed-veto sample. With prompt and delayed classes treated as mutually exclusive, the central signal fractions are
\[
p_{\rm prompt}=10^{-4},\qquad
p_{\rm delayed}=0.0286,\qquad
p_{\rm science}=1-p_{\rm prompt}-p_{\rm delayed}=0.9713.
\]

The script partition_lz_2026_signal_samples.py applies these fractions to the 24 Fig. S2-folded formal-B rate-yield rows. It writes science, prompt-veto, and delayed-veto expected signal counts, while preserving the pre-veto total and the 225–269.9 keV candidate-slice diagnostic. The calculation checks that the three sample yields sum exactly to the input rate-level yield.

This is a rate-level migration calculation only. It does not create sample-specific S1c/log10(S2c) PDFs or apply an event-level Skin/OD simulation. The published best-fit signal yields in Supplemental Tables S1 and S2 provide a cross-check: for the representative L_s10, 1000 GeV model, the prompt signal yield is approximately 10^-4 of the science yield and the delayed yield is approximately 3.1×10^-2 of the science yield. These are rounded, fit-specific reference values; the partition uses the central random-coincidence fractions.

### 2.3 Existing event-weighted NEST result

The archived NEST fold contains 192 comparisons, 25,440 energy-bin diagnostics, and 120,000 nonzero two-dimensional cells. Its maximum raw-rate closure is \(7.77\times10^{-16}\). The replica rate and 2D-map differences are retained as diagnostics.

The native manifest explicitly records formal_pass = null and DIAGNOSTIC_ONLY_NO_PREDECLARED_TOLERANCE. Therefore this output is not an accepted official LZ response. In particular, it currently:
- samples a uniform active-TPC volume proxy rather than the 4.71 t fiducial volume;
- uses a parametric S1-coincidence proxy and S2 threshold, not the full waveform-level SS reconstruction and official analysis cuts;
- applies a software WS-ROI mask but not the full official selection chain;
- has no prompt/delayed Skin/OD event-level migration;
- has no background model or likelihood.

The raw C++ response sample contains x_mm, y_mm, z_mm, and local field columns, but the current Python reader discards the position columns. Retaining them is the next implementation step for spatial-response work.

## 3. Official LZ selection inputs

The controlling source is the LZ Collaboration paper, arXiv:2609.02823v1, including its Supplemental Material.

### 3.1 Fiducial volume

The official mass is \(4.71\pm0.08\) tonnes for the 220 live-day analysis. The upper FV boundary is 12.8 cm below the gate and the lower boundary is 9.0 cm above the cathode. The radial contour is depth- and azimuth-dependent and is selected to keep the expected wall-background count below \((1.0\pm0.5)\times10^{-4}\) events. The minimum stand-off is 8.0 cm from the true wall and 6.0 cm from the reconstructed wall; the mean distances are 10.7 cm and 7.2 cm, respectively, and the maximum distances near the bottom are 18.2 cm and 10.4 cm.

Original source reference: Fig. 3, PDF p. 4. The figure displays the smallest and largest radial extents, not a machine-readable azimuth-dependent FV map. The public HEPData archive reviewed in HEPDATA_V1_ARCHIVE_AUDIT.md does not supply the full position-dependent FV surface.

Implementation consequence:
1. Do not apply another 4.71/7 volume factor to rate-level results already normalized to the 4.71 t exposure.
2. For event-level response, condition the spatial event distribution on the FV.
3. Retain the true and reconstructed positions separately. The official cut is defined in reconstructed coordinates, while the generator currently supplies true x,y,z and no complete position-reconstruction kernel.
4. Until the collaboration's exact map and reconstruction kernel are available, implement inner/nominal/outer FV envelopes from the published Fig. 3 extents and label them as a geometry bracket, not as the official FV.

### 3.2 Prompt and delayed vetoes

The published event categories are:
- **Science:** no signal in either veto system.
- **Prompt veto:** Skin signal >2.5 phd within ±0.25 μs of TPC S1, or OD signal >4.5 phd within ±0.3 μs.
- **Delayed veto:** Skin >300 keV or OD >200 keV within 600 μs of TPC S1, excluding the prompt-veto window.

The background tagging nuisance parameters used by the official fit include
\[
\lambda_{DN}=0.87\pm0.02,\quad
\lambda_{PN}=0.050\pm0.010,\quad
\lambda_{PG}=0.88\pm0.02,\quad
\lambda_{\rm MSSI}=0.94\pm0.02.
\]
The neutron rate is constrained by the prompt and delayed veto samples rather than a direct Gaussian rate constraint. MSSI, 127Xe/125Xe, and detector gamma backgrounds also receive veto-sideband constraints.

The three-sample signal partition is already implemented at rate level. The next step is to propagate the same signal response shape into the three samples with the published signal migration fractions, while keeping the background-specific tag efficiencies as separate nuisance parameters.

### 3.3 Energy and observable response

The official signal and background PDFs are built in
\[
\left(S1_c,\log_{10}S2_c\right)
\]
using BACCARAT/GEANT4 event simulation and tuned NEST v2.4.5. The LZ 2026 paper reports \(g_1=0.110\pm0.002\) phd/photon and \(g_2=34.5\pm1.1\) phd/electron. The high-energy NR response is tuned with both D-D calibration data (0–74 keV NR) and AmBe calibration data (0–330 keV NR). NEST v2.4.5 modifies the NR charge-yield power law above E0, as described by Supplemental Eq. (5) and Table S5.

Original source references: Fig. 2, PDF p. 3; Supplemental Tables S3–S5, PDF pp. 16–17.

Do not add a separate Gaussian smearing directly to ER on top of the NEST response. The detector response is the conditional distribution in corrected S1/S2 observables, including quanta and detector fluctuations. If a reconstructed-energy spectrum is required, derive it from the S1c,S2c response and the experiment's energy estimator.

The Fig. S2 final cumulative efficiency and the event-level 2D response are separate audited objects. The current NEST map already applies its own S1-coincidence proxy, S2 threshold, and WS-ROI mask. Multiplying the entire Fig. S2 final curve into that map would double-count overlapping selection stages. The residual SS/data-analysis factor can only be applied to the 2D map after a conditional-response closure test.

## 4. Official background model and likelihood

The LZ 2026 likelihood is an unbinned extended maximum likelihood in the three samples, with event coordinates in (S1c, log10(S2c)):
\[
\mathcal L(\theta)=
\prod_{i=0}^{2}
\left[
\operatorname{Pois}(N_i\mid\mu_{\mathrm{tot},i})
\prod_{e=1}^{N_i}
\frac{
\mu_{\mathrm{sig},i}(\boldsymbol\lambda)f_{\mathrm{sig},i}(\mathbf x_e)
+\sum_b\mu_{b,i}(\boldsymbol\lambda)f_{b,i}(\mathbf x_e)
}{
\mu_{\mathrm{tot},i}
}
\right]
\prod_k g_k(\phi_k\mid\nu_{\phi_k}).
\]

The paper reports the following post-fit total counts and observed sample sizes (the component pre-fit expectations are listed separately in Table I and Supplemental Tables S1–S2):
| Sample | Post-fit total counts | Observed events |
|---|---:|---:|
| Science | \(1713\pm39\) | 1710 |
| Prompt veto | \(69.4\pm11.7\) | 66 |
| Delayed veto | \(50.4\pm2.0\) | 55 |

The science-sample component rates are given in Table I; prompt and delayed component rates and tag efficiencies are given in Supplemental Tables S1 and S2. Gaussian constraints are applied to background normalizations except detector neutrons, which are constrained by veto tagging. The MSSI, 127Xe/125Xe, and detector gamma components also use veto-sideband information.

The collaboration constructs the component PDFs using BACCARAT/GEANT4 plus tuned NEST v2.4.5; 83mKr is taken from calibration data and accidentals are generated from isolated S1/S2 populations. The public HEPData archive contains the released event samples and numerical tables, but the repository's HEPData audit did not find the full component PDF templates, their nuisance covariance, or the full position-dependent FV/reconstruction maps.

Therefore:
- We can implement the published three-sample likelihood structure and all public rate/tag constraints.
- We must not substitute a KDE of the observed data for the missing component PDFs and call it the official likelihood.
- Until the BACCARAT component templates and nuisance covariance are available or independently rebuilt, any likelihood made from reconstructed approximate PDFs must be labelled a public-data recast, not an LZ likelihood reproduction.

## 5. Work sequence

1. **Complete the rate-level sample partition.** Run the independent workflow for all 24 formal-B rows, verify exact sample-sum closure and SHA-256, and archive the output.
2. **Build the FV spatial bridge.** Retain x,y,z and field in the event reader; implement the Fig. 3 radial envelopes and z cuts; add true-to-reconstructed position smearing; normalize the conditional response inside the 4.71 t FV.
3. **Build the official-observable signal response.** Use the tuned NEST v2.4.5 NR model and position corrections to generate \(p(S1_c,\log_{10}S2_c\mid E_R,\mathbf x)\). Apply the SS/data-analysis and WS ROI selections with a conditional efficiency factor, validated against Fig. S2 without double counting.
4. **Construct the three signal samples.** Use the published random-coincidence signal fractions and retain common observable PDFs with sample-specific normalizations unless a response study demonstrates a sample-shape difference.
5. **Build background components.** Reconstruct or obtain BACCARAT/GEANT4 templates, accidental templates, and nuisance covariance. Implement the Gaussian constraints and veto-tag constraints from Tables I, S1, and S2.
6. **Validate the likelihood.** Reproduce the published sample counts, background-only fit, and representative L_s10 benchmark fit before inserting the three-body B signal.
7. **Produce the final prediction.** Report signal expectations, local test statistics, confidence intervals, and exclusion contours only after the signal PDFs, background templates, and nuisance model are validated.

## 6. Source references

- LZ Collaboration, “Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment,” arXiv:2609.02823v1 (2026): Fig. 3 (PDF p. 4), Fig. 4 (PDF p. 5), Table I (PDF p. 7), Supplemental Fig. S2 and Eq. (3) (PDF p. 14), Supplemental Tables S1–S2 (PDF pp. 15–16), Supplemental Tables S3–S5 (PDF pp. 16–17).
- LZ Collaboration, “Dark Matter Search Results from 4.2 Tonne-Years of Exposure of the LUX-ZEPLIN (LZ) Experiment,” arXiv:2410.17036v3 (2025): previous analysis selections and detector-position response.
- LZ_2026_SELECTION_STAGE_RATE_LEVEL_CLOSURE.md: previous GCN/JJ55 rate-level Fig. S2 closure; historical benchmark, not the current formal-B source.
- LZ_2026_B_BASELINE_NEST_EVENT_WEIGHTED_FOLD.md: current event-weighted NEST diagnostic and explicit scope.
- HEPDATA_V1_ARCHIVE_AUDIT.md: audit of public data-release contents.
- partition_lz_2026_signal_samples.py: current formal-B rate-level sample-partition implementation.
