# LZ 2026 rate-level selection-stage closure for the four three-body benchmarks

Date: 2026-11-15

**Status:** independent rate-level integration reproduced the stored Fig. S2 efficiency-weighted yields to floating-point precision. This does not create a two-dimensional selected signal PDF.

## 1. Method

The 303-point vector-extracted Fig. S2 final cumulative efficiency curve was multiplied by each benchmark's piecewise-linear differential recoil spectrum. The integral was evaluated exactly on the union of the spectrum and efficiency knots. On each subinterval, both functions are linear, so their product is quadratic and its integral is analytic.

For each benchmark and nuclear-response choice,

\[
R_{\rm raw}=\int_{5.4}^{269.9} r(E)\,dE,
\qquad
R_{\rm final}=\int_{5.4}^{269.9}r(E)\epsilon_{\rm Fig.\,S2}^{\rm final}(E)\,dE.
\]

The expected event count uses the repository's 2.84 tonne-year exposure,
\(1{,}037{,}310\ {\rm kg\,day}\). The independently calculated
\(R_{\rm final}\times\mathcal E\) matches
`expected_events_in_high_efficiency_window` in
`lz_2026_rate_level_event_yields.csv` to floating-point
precision for all eight benchmark/nuclear-response rows (maximum relative
difference \(2.22\times10^{-16}\)).

## 2. Fig. S2 stage anchors over the benchmark signal support

The four benchmark spectra have first nonzero recoil energies of 35, 101,
210, and 101 keV. Over the complete 35–269.9 keV range, the vector-extracted
Fig. S2 curves give:

| Cumulative stage | Minimum | Maximum |
|---|---:|---:|
| S2 trigger | 100.000% | 100.000% |
| S2 trigger + S1 threshold | 100.000% | 100.000% |
| Trigger + S1 + SS/data-analysis cuts | 95.5038% | 95.5830% |
| Final, including WS ROI | 49.8820% | 95.5830% |

Therefore, for the support of these four benchmarks, the published
one-dimensional efficiency curve has unit trigger and S1-threshold
acceptance. The principal pre-ROI loss is the approximately 4.4% SS/data-
analysis stage. The upper S1c ROI then causes a strong energy-dependent
loss near the high-energy endpoint.

Useful anchor values:

| True NR energy | Trigger | + S1 threshold | + SS/data analysis | + WS ROI | ROI conditional factor |
|---:|---:|---:|---:|---:|---:|
| 35 keV | 100.000% | 100.000% | 95.5038% | 95.5038% | 100.000% |
| 101 keV | 100.000% | 100.000% | 95.5783% | 95.5783% | 100.000% |
| 210 keV | 100.000% | 100.000% | 95.5811% | 95.5811% | 100.000% |
| 248 keV | 100.000% | 100.000% | 95.5793% | 94.5688% | 98.9427% |
| 269.9 keV | 100.000% | 100.000% | 95.5796% | 49.8820% | 52.1889% |

This shows why the black \(m_s=360\) keV benchmark needs particular care:
its spectrum extends into the region where the upper S1c ROI becomes
strongly inefficient. The other three benchmark spectra have rate-weighted
final efficiencies close to the approximately 95.6% SS/data-analysis
plateau, with negligible additional loss from the upper ROI in their
rate-weighted totals.

## 3. Rate-level expected counts

| Benchmark | Nuclear response | Raw rate (events/kg/day) | Fig. S2-weighted rate (events/kg/day) | Expected events in 2.84 t-y | Final/raw efficiency |
|---|---|---:|---:|---:|---:|
| red \(m_s=200\) keV, \(\Delta m=1\) MeV | GCN | \(3.40976\times10^{-7}\) | \(3.25822\times10^{-7}\) | 0.337978 | 95.5557% |
| red \(m_s=200\) keV, \(\Delta m=1\) MeV | JJ55 | \(3.49197\times10^{-7}\) | \(3.33676\times10^{-7}\) | 0.346125 | 95.5550% |
| green \(m_s=300\) keV, \(\Delta m=1\) MeV | GCN | \(1.53938\times10^{-9}\) | \(1.46969\times10^{-9}\) | \(1.52452\times10^{-3}\) | 95.4728% |
| green \(m_s=300\) keV, \(\Delta m=1\) MeV | JJ55 | \(1.59468\times10^{-9}\) | \(1.52247\times10^{-9}\) | \(1.57927\times10^{-3}\) | 95.4716% |
| black \(m_s=360\) keV, \(\Delta m=1\) MeV | GCN | \(3.58884\times10^{-15}\) | \(2.75013\times10^{-15}\) | \(2.85274\times10^{-9}\) | 76.6301% |
| black \(m_s=360\) keV, \(\Delta m=1\) MeV | JJ55 | \(3.60568\times10^{-15}\) | \(2.77589\times10^{-15}\) | \(2.87945\times10^{-9}\) | 76.9864% |
| blue \(m_s=300\) keV, \(\Delta m=10\) MeV | GCN | \(1.26019\times10^{-11}\) | \(1.20315\times10^{-11}\) | \(1.24803\times10^{-5}\) | 95.4736% |
| blue \(m_s=300\) keV, \(\Delta m=10\) MeV | JJ55 | \(1.30544\times10^{-11}\) | \(1.24633\times10^{-11}\) | \(1.29283\times10^{-5}\) | 95.4723% |

For red, green, and blue, the rate-weighted final efficiency is about
95.47–95.56%, consistent with the SS/data-analysis plateau because the
benchmark spectra receive negligible integrated loss from the upper S1c
boundary. For black, the final efficiency falls to 76.63–76.99%; the
additional loss is caused by the high-energy WS ROI acceptance.

## 4. What this does and does not validate

Validated:
- The Fig. S2 final cumulative efficiency curve is integrated consistently
  with the benchmark-specific differential spectra.
- The rate-level expected event counts in the stored CSV are independently
  reproduced.
- The trigger and S1-threshold cumulative curves are unity over the
  signal-support region of these four benchmark spectra.
- The SS/data-analysis stage is approximately 95.5–95.6% over this region.
- The upper S1c ROI is a major additional efficiency effect for the black
  high-energy benchmark.

Not validated:
- The one-dimensional efficiency curve does not determine the
  \((S1_c,\log_{10}S2_c)\) migration kernel.
- It does not prove that the current NEST response-family 2D map has the
  same response, calibration priors, position correction, or selection
  correlations as the collaboration's BACCARAT/GEANT4 signal PDFs.
- It does not supply the science/prompt-veto/delayed-veto signal partition,
  full waveform-level SS reconstruction, FV mask, or background likelihood.

Do not multiply this rate-level efficiency into the existing
NEST/WS-ROI two-dimensional intensity. Keep the rate-level yield and
two-dimensional response as separate audited objects until their
two-dimensional selection closure is established.

## 5. Sources and reproducibility

- [LZ 2026 extended-NR paper, arXiv:2609.02823](https://arxiv.org/abs/2609.02823), Supplemental Fig. S2.
- [LZ WS2024 analysis, arXiv:2410.17036](https://arxiv.org/abs/2410.17036), trigger, S1/SS reconstruction, analysis cuts, FV, veto, and live-time selections.
- [Rate-level event-yield table](rate_level_event_yields/lz_2026_rate_level_event_yields.csv).
- [Digitized final efficiency curve](lz_2026_nr_efficiency_digitized.csv).
- [Event-weighted 2D response-fold audit](LZ_2026_THREE_BODY_EVENT_WEIGHTED_FOLD_AUDIT.md).


## 6. Reproducible implementation

The exact integration is implemented in
[summarize_lz_2026_selection_stage_rates.py](../summarize_lz_2026_selection_stage_rates.py)
and covered by
[unit tests](../tests/test_lz_2026_selection_stage_rates.py). The lightweight
workflow
[lz-2026-selection-stage-rate-audit.yml](../../../.github/workflows/lz-2026-selection-stage-rate-audit.yml)
re-extracts the four vector curves from the paper PDF, runs the tests, and
checks raw-rate and final expected-count closure for all eight
benchmark/nuclear-response combinations. It does not rebuild NEST or rerun
the expensive event-level response Monte Carlo.

The stored digitized final-efficiency curve reproduces the archived rate-level
expected yields with maximum relative difference \(2.22\times10^{-16}\).
The lightweight CI independently re-extracts the vector curves from the
current arXiv PDF; that fresh extraction differs from the stored curve at the
last digits and gives a maximum final-yield relative difference
\(7.02\times10^{-10}\), for the very small black-GCN expected count. The
workflow therefore uses a documented \(10^{-8}\) closure tolerance. This is
a PDF vector-extraction/rounding reproducibility difference, not a response
or physics-model discrepancy; the raw-rate closure remains at floating-point
precision.


## 7. Latest reproducible CI result and spectrum-weighted stage factors

The lightweight audit completed successfully:
- [GitHub Actions run 43681260816](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43681260816).
- Artifact ID: `14148377892`.
- ZIP SHA-256: `53fa87cc4b2fdb3361e73fd65d847992b2ea2c96996891d7cfd6c10850b136b5`.
- Five output files; 123,090 bytes.
- Eight benchmark/nuclear-response rows.
- Maximum raw-rate relative closure: 0.
- Maximum final expected-count relative closure against the archived rate-level table: \(7.0113\times10^{-10}\), passing the documented \(10^{-8}\) tolerance.

The CI output gives the spectrum-weighted conditional stage factors:

| Benchmark | Nuclear response | SS + data-analysis given S1 | WS ROI given SS + data-analysis | Total final efficiency |
|---|---|---:|---:|---:|
| red, \(m_s=200\) keV | GCN | 95.5780% | 99.9767% | 95.5557% |
| red, \(m_s=200\) keV | JJ55 | 95.5780% | 99.9760% | 95.5550% |
| green, \(m_s=300\) keV | GCN | 95.5783% | 99.8896% | 95.4728% |
| green, \(m_s=300\) keV | JJ55 | 95.5783% | 99.8883% | 95.4716% |
| black, \(m_s=360\) keV | GCN | 95.5790% | 80.1746% | 76.6301% |
| black, \(m_s=360\) keV | JJ55 | 95.5790% | 80.5474% | 76.9864% |
| blue, \(m_s=300\) keV, \(\Delta m=10\) MeV | GCN | 95.5783% | 99.8904% | 95.4736% |
| blue, \(m_s=300\) keV, \(\Delta m=10\) MeV | JJ55 | 95.5783% | 99.8892% | 95.4723% |

The trigger and S1-threshold conditional factors are exactly 100% for all
eight benchmark/nuclear-response rows. The black benchmark's additional
upper-ROI loss is about 19.5–19.8% of the events that survive the
SS/data-analysis stage; the other three benchmarks lose only about
0.02–0.11% at that stage.

The artifact contains the re-extracted Fig. S2 curves and the full JSON/CSV
stage-yield table. The stored-curve calculation in Section 3 remains the
archived rate-level reference; the fresh extraction is independently
reproducible within the stated \(10^{-8}\) tolerance.


### Integration-PR reproduction

The same lightweight workflow was run from the clean integration branch used by PR #41:
- [GitHub Actions run 43682717319](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43682717319), successful.
- Artifact ID: 14149346224.
- ZIP SHA-256: `5fdacaed77cde4a65db56801997f75e8171b6a4bb3d7ba0218be7d708cfbba0e`.
- Eight rows reproduced; maximum raw-rate closure 0 and maximum final-yield relative closure \(7.0113\times10^{-10}\), unchanged from the mainline run.

This confirms the audit scripts, spectrum inputs, and reference yield table are present and reproducible in the integration snapshot, not only on the research branch.


The integration-branch CI was then extended to run the high-energy 0.5-keV,
event-weighted-fold, and selection-rate unit tests together. The expanded
audit passed:
- [GitHub Actions run 43682860360](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43682860360).
- Artifact ID: 14149540926.
- ZIP SHA-256: `0167a2c74e179215584b573097dce28dc8ea12672ecebd826d7d98362634af27`.
- The three targeted test modules, fresh Fig. S2 vector extraction, and all
  eight rate-level closures passed in the same workflow.
