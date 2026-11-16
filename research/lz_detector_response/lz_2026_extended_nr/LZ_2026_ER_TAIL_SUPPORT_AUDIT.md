# LZ 2026 ER candidate-tail support audit

Date: 2026-11-16

**Status:** empirical support audit, corrected event-local drift, and 2,000-replica bootstrap rerun are complete (successful workflow 43662363556). This is a diagnostic of the public EFT2024 candidate, not an official LZ ER likelihood; the empirical ER PDF still has zero support in the candidate's 2D cell.

## 1. Why this audit is necessary

The ER full-band pilot reports a candidate displacement of approximately 6.7 sigma-equivalent below the median in the 540–545 phd S1c bin. That number is obtained from the central 10–90% width:
\[
\sigma_{80}=\frac{q_{90}-q_{10}}{2.5631031311},\qquad
z_{80}=\frac{\log_{10}S2_{c,\rm obs}-q_{50}}{\sigma_{80}}.
\]

This is a useful band-location diagnostic. It is not an empirical tail probability, and it does not establish the ER likelihood density at the observed candidate.

## 2. Event-level support in the candidate bin

Observed event:
\[
S1_c=540.07916\ {\rm phd},\quad
S2_c=9267.53\ {\rm phd},\quad
\log_{10}(S2_c/{\rm phd})=3.96696400056.
\]

The previous ER event artifact contains 200,000 events per uniform-TPC model and 100,000 per fixed-position model. Directly reading the CSVs gives:

| Model | Position prior | Events in 540–545 phd | Minimum S2c (phd) | Minimum / observed S2c | Events with S2c at or below candidate |
|---|---|---:|---:|---:|---:|
| EFT2024, m6 = −1 | Uniform TPC | 631 | 29,595.4 | 3.193 | 0 |
| Table S3, m6 = 0 | Uniform TPC | 677 | 31,052.1 | 3.351 | 0 |
| Generic NEST | Uniform TPC | 700 | 37,448.7 | 4.041 | 0 |
| EFT2024, m6 = −1 | Fixed candidate position | 330 | 28,665.1 | 3.093 | 0 |
| Table S3, m6 = 0 | Fixed candidate position | 317 | 28,370.7 | 3.061 | 0 |
| Generic NEST | Fixed candidate position | 364 | 39,865.0 | 4.302 | 0 |

There are also zero events in the 10-phd by 0.02-dex 2D histogram cell containing the candidate:
\[
540\leq S1_c<550\ {\rm phd},\qquad
3.96\leq\log_{10}(S2_c/{\rm phd})<3.98.
\]

For zero events in a sample of size \(n\), the one-sided exact 95% binomial upper bound is
\[
p_{95}=1-0.05^{1/n}.
\]
For the uniform-TPC samples this is 0.474% (EFT2024), 0.442% (Table S3), and 0.427% (generic). For the fixed-position samples it is 0.904%, 0.941%, and 0.820%, respectively. These are only Monte Carlo upper bounds conditional on the chosen energy and position priors; they are not estimates of the physical ER leakage probability.

## 3. Bootstrap uncertainty of the band displacement

The 2,000-replica event bootstrap uses seed 20261115 and resamples the positive-observable events in the 540–545 phd S1c bin. The 95% percentile intervals for the central-band offset are:

| Model | Position prior | z80 | Bootstrap 95% interval |
|---|---|---:|---:|
| EFT2024, m6 = −1 | Uniform TPC | −6.6850 | [−7.2028, −6.0795] |
| Table S3, m6 = 0 | Uniform TPC | −6.3104 | [−6.7990, −5.9305] |
| Generic NEST | Uniform TPC | −9.9702 | [−10.5041, −9.2095] |
| EFT2024, m6 = −1 | Fixed candidate position | −6.5441 | [−7.2230, −6.0287] |
| Table S3, m6 = 0 | Fixed candidate position | −6.3655 | [−7.2303, −5.9648] |
| Generic NEST | Fixed candidate position | −9.9494 | [−10.8569, −9.3617] |

These intervals quantify finite-MC uncertainty in the percentile offset only. They do not include the ER yield model, fluctuation-model, calibration-source, spatial-prior, detector, or background-model uncertainties.

## 4. Interpretation

1. The EFT2024 ER candidate's central-band displacement is robustly around 6.5–6.7 sigma-equivalent in these two proxy priors, close to the paper's quoted approximately 6.7-sigma separation.
2. The empirical ER 2D histogram has no support in the candidate's 540–550 phd by 3.96–3.98 dex cell. The observed event lies below the minimum simulated S2c in its 540–545 phd S1c bin by a factor of about 3.1–3.2 for EFT2024.
3. Therefore the current sparse empirical ER PDF assigns zero probability to the candidate cell. It cannot be used directly as a likelihood density at the observed point.
4. The quoted 6.7 sigma-equivalent displacement must not be converted to a Gaussian tail probability or a likelihood ratio without validating the far ER tail. The 10–90% band does not constrain a tail this far below the simulated minimum.
5. More ordinary Monte Carlo is inefficient for a tail at this distance. A likelihood-ready ER model needs a validated parametric tail, importance sampling or dedicated tail generation, and calibration constraints on that tail.
6. The flat true-ER-energy prior (0.1–300 keV) and uniform active-TPC position prior are proxies, not the collaboration's calibration-source energy/spatial distributions. The HEPData table archive does not contain the calibration event cloud or exact production NEST configuration.

## 5. Reproduction and current workflow

- Previous ER band/2D run: [43642038888](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43642038888).
- Previous artifact ID: 14132651289.
- Previous artifact SHA-256: f1a903a68c75f9c787549a64bb69c0d8b661ef0d777ffa2a769b19aee9666c69.
- The updated ER driver calculates drift velocity event by event from the local field and stores drift distance/time/speed. The summarizer enforces relative kinematic closure below 1e−9.
- Corrected event-local drift and bootstrap run: [43662363556](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43662363556), successful.
- Corrected artifact ID: 14140966494.
- Corrected artifact SHA-256: a2a138d262245e811c94b8bc41d76f4af16c53196d1a12adea044bf66a9f7bc1.
- The artifact contains six event CSVs, the conditional 2D PDFs, the band summary, and the 2,000-replica bootstrap/tail-support JSON.
- All 200,000/100,000 event samples pass the local drift kinematic closure. The maximum relative residual is 1.0581e−11; the field is constant at 96.5 V/cm and the drift speed at 1.33036177945 mm/us.
- All common physical event columns in the six corrected CSVs are bitwise identical to the earlier pilot artifact. The new files additionally store local drift distance/time/speed.
- The corrected bootstrap reproduces the values and 95% intervals in Section 3.

The full ER response study is in
[LZ_2026_NR_ER_FULL_RESPONSE_CANDIDATE_REPORT.md](LZ_2026_NR_ER_FULL_RESPONSE_CANDIDATE_REPORT.md).
