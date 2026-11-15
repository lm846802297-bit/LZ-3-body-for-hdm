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
