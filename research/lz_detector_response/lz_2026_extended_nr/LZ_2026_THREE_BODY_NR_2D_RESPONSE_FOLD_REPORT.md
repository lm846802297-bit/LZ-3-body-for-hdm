# LZ 2026 three-body signal folded through the NR 2D detector response

**Status:** first end-to-end pre-selection fold completed successfully in GitHub Actions. This connects the existing natural-xenon three-body recoil spectra to an event-level NEST NR response. It is not an official LZ likelihood, a post-selection PDF, or an exclusion result.

## 1. Inputs reused (no duplicate nuclear/halo calculation)

The fold reuses the archived continuous natural-xenon spectra:
`research/figure2_full_reproduction/results/natural_xenon_continuous_spectrum/<benchmark>/natural_xenon_continuous_spectrum.csv`.

These spectra already include:
- isotope-by-isotope natural-xenon abundance weighting for the seven available isotopes (Xe-128, 129, 130, 131, 132, 134, 136);
- NIST nuclear-mass prescription and exact spatial momentum transfer;
- truncated SHM halo folding with (v_0=220\,\mathrm{km/s}), (v_E=232\,\mathrm{km/s}), (v_{esc}=544\,\mathrm{km/s});
- the archived GCN and JJ55 nuclear response models;
- the original conditional pole-width benchmark setup.

Xe-124 and Xe-126 response inputs remain unavailable in this continuous GCN/JJ55 data set; the isotope amount fraction retained is 0.998158, without renormalizing the available isotopes.

Four existing benchmarks were folded:
- red: (m_s=200\,\mathrm{keV},\Delta m=1\,\mathrm{MeV});
- green: (m_s=300\,\mathrm{keV},\Delta m=1\,\mathrm{MeV});
- black: (m_s=360\,\mathrm{keV},\Delta m=1\,\mathrm{MeV});
- blue: (m_s=300\,\mathrm{keV},\Delta m=10\,\mathrm{MeV}).

Common rate benchmark inputs are (m_\chi=1\,\mathrm{TeV}), (m_V=10\,\mathrm{GeV}), ((g_1g_2g_{VN})^2=10^{-8}), (g_2=1), and (ho_\chi=0.3\,\mathrm{GeV/cm^3}), as recorded in the source metadata. The coupling normalization is the pre-existing benchmark normalization, not a fit.

## 2. NEST response samples

The response was regenerated on the exact LZ high-efficiency ROI:
[
5.4\leq E_R\leq269.9\;\mathrm{keV}.
]

For each of four response families, 200,000 events were simulated with:
- pinned NEST source commit `541b6430dae6ea289cf110c99f174a9187f7fdee`;
- the public `LZ_Detector_2024` detector class;
- uniform true recoil energy over the exact ROI;
- uniform active-TPC cylinder volume as the spatial prior;
- NEST `FullCalculation -> GetS1 -> GetS2` event path;
- corrected observables `s1[5]` and `s2[7]).

Response families are kept distinct:
1. `eft2024`: LZ EFT2024 NR mean yields and EFT2024 NR fluctuation vector;
2. `tableS5`: rounded Table S5 NR mean-yield vector with EFT2024 NR fluctuation vector;
3. `ws2024`: WS2024 detector-class NR means and NR widths;
4. `generic`: generic NEST NR means and widths, with EFT2024 detector overrides.

The response grid is 10 keV in true energy, 10 phd in (S1_c), and 0.02 dex in (log_{10}S2_c).

**Spatial-prior limitation:** uniform active-TPC volume is a transparent detector-volume proxy. It is not the D-D/AmBe calibration-source distribution, nor a collaboration-derived event-position prior. The fold is therefore a detector-response candidate, not a reproduction of the exact calibration geometry.

## 3. Probability convention and convolution

For energy bin (k), the response generator records (N_{gen,k}), the number of generated events, and (N_{ij,k}), the number in positive reconstructed cell ((i,j)). We define the cell probability without renormalizing away events with non-positive observables:
[
P_{ij,k}=\frac{N_{ij,k}}{N_{gen,k}},\qquad
P_{+,k}=\sum_{ij}P_{ij,k}\leq1.
]

The rate in each true-energy bin is integrated from the piecewise-linear pre-detector recoil spectrum. The cell intensity is
[
R_{ij}=\sum_k
\left[\int_{E_k\cap[5.4,269.9]}^{E_{k+1}}
\frac{dR_{3b}}{dE_R}\,dE_R\right]P_{ij,k}.
]
The implementation integrates the rate exactly for its piecewise-linear interpolation on each clipped bin. The response is represented by the Monte Carlo average within each 10-keV energy bin; it is not an exact continuous-energy response function.

The output is a **pre-selection observable intensity** in events/(kg day) per 10-phd by 0.02-dex cell. A conditional shape given positive (S1_c,S2_c) is obtained by dividing all cell intensities by their sum.

### Efficiency is intentionally not applied to the 2D shape

The existing scalar LZ final-ROI efficiency curve is an energy-only efficiency. It does not specify how accepted events migrate among ((S1_c,\log_{10}S2_c)) cells. It is therefore not multiplied into this 2D PDF. The earlier rate-level efficiency-weighted event-yield calculation remains a separate selected-count diagnostic. Multiplying that scalar efficiency into a shape that already included the relevant selection would risk double counting; using it here as a cell-independent factor would not reconstruct the selected 2D distribution.

## 4. Numerical acceptance

- GitHub Actions workflow: [run 43645345194](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43645345194), conclusion: success.
- Head commit: `2bf912d9ac3c8355e9e8a3747f9fc9c86eb69532`.
- Artifact: `lz-2026-three-body-nr-2d-response-fold`, artifact ID `14133509039`.
- Artifact SHA-256: `525e4156df371deff962d9676d50e08a9edfe00a6f67c2504681ab9f139659be`.
- Numerical unit tests: 4 passed (piecewise-linear integral, ramp integral, partial ROI bins, and no-renormalization of positive-observable probability).
- Folded combinations: 4 benchmarks × 2 nuclear response models × 4 NEST response families = 32.
- Maximum cell-sum closure error: below (2.7\times10^{-16}), well below the (5\times10^{-12}) acceptance threshold.

For all benchmark spectra in this ROI, the rate-weighted positive-(S1_c,S2_c) fraction is 1 to the displayed precision. The bins below 30 keV, where the response sample has a small non-positive-observable fraction, carry zero rate in these benchmark spectra. This is a property of these four rate spectra, not a general assertion that NEST has unit detection probability.

## 5. Pre-selection expected counts and GCN/JJ55 comparison

Using the existing (2.84\,\mathrm{tonne\,year}=1{,}037{,}310\,\mathrm{kg\,day}) exposure, the unweighted pre-selection counts are:

| Benchmark | GCN | JJ55 | JJ55/GCN − 1 |
|---|---:|---:|---:|
| red | 0.353697 | 0.362225 | +2.41% |
| green | 0.00159681 | 0.00165418 | +3.59% |
| black | (3.72274\times10^{-9}) | (3.74021\times10^{-9}) | +0.469% |
| blue | (1.30720\times10^{-5}) | (1.35414\times10^{-5}) | +3.59% |

These are expected counts before detector efficiency, analysis cuts, and likelihood treatment. They are not observed counts or confidence limits.

For comparison only, the previously archived energy-only efficiency fold gives central selected-window expectations:
- red: 0.337978 (GCN), 0.346125 (JJ55);
- green: 0.00152452 (GCN), 0.00157927 (JJ55);
- black: (2.85274\times10^{-9}) (GCN), (2.87945\times10^{-9}) (JJ55);
- blue: (1.24803\times10^{-5}) (GCN), (1.29283\times10^{-5}) (JJ55).

The second list is retained as a separate scalar-efficiency calculation; it is not used to renormalize the 2D cell intensities.

## 6. Response-family shape comparison

The integrated theoretical rate is independent of the NEST response-family choice. The response choice changes the distribution across observable cells. To quantify this, we normalized each folded 2D cell map to unit sum and computed the total-variation distance
[
D_{TV}(P,Q)=\frac12\sum_{ij}|P_{ij}-Q_{ij}|.
]

Across the four benchmarks and both nuclear response models, relative to EFT2024:
- Table S5 mean yields + EFT2024 widths: (D_{TV}=0.162\text{--}0.249);
- WS2024: (D_{TV}=0.606\text{--}0.927);
- Generic NEST: (D_{TV}=0.806\text{--}0.992).

These are distances between coarse-binned, pre-selection response shapes, not statistical significances or nuisance-parameter constraints. They show why the four parameter families must remain separate rather than being treated as interchangeable.

A visualization for the red benchmark with GCN nuclear response and EFT2024 detector response is stored as `lz_three_body_eft2024_nr_2d_signal_red_gcn.png` in the conversation output.

## 7. Files and reproducibility

- Driver: `research/lz_detector_response/cpp/lz_2026_nr_full_calibration_band.cc` (now accepts explicit energy minimum and maximum).
- Fold implementation: `research/lz_detector_response/fold_lz_2026_three_body_2d_response.py`.
- Tests: `research/lz_detector_response/tests/test_lz_2026_three_body_2d_response.py`.
- Workflow: `.github/workflows/lz-2026-three-body-2d-response-fold.yml`.
- Artifact contains the four 200k-event response CSVs, `fold_summary.json`, `response_validity_by_energy.json`, and `signal_2d_intensity.csv`.

## 8. What this result does and does not establish

Established:
1. The existing pre-detector natural-xenon three-body spectra can be folded numerically through the event-level NEST NR response.
2. The cell intensities close to the independently computed rate weighted by the positive-observable probability.
3. GCN/JJ55 alter the integrated rate at the few-percent level for these benchmarks, while the NEST response family changes the observable 2D shape substantially.
4. The EFT2024 response is the primary public LZ-specific candidate; Table S5, WS2024, and Generic remain explicit alternatives.

Not established:
1. The exact collaboration production NEST configuration or calibration-source spatial distribution.
2. A full post-selection (P(S1_c,\log_{10}S2_c)) including S1 coincidence, trigger, data-quality, fiducial and analysis selections.
3. Position-dependent nuisance covariance and calibration parameter correlations.
4. ER/background PDFs, the candidate-event likelihood, a profile likelihood, or a confidence interval.

## 9. Next validation gates

1. Replace the uniform-volume response prior with the actual spatial distribution or position-weighted response maps used for the 2026 analysis.
2. Generate a response conditional on true energy with finer energy bins (5 keV and selected 1-keV checks near rapid spectral features) and quantify response-MC covariance.
3. Recover the full selected-event response, including S1 coincidence and relevant S2/trigger/data-quality selections; only then combine the selected 2D PDF with the published efficiency without double counting.
4. Propagate NEST nuisance parameters and calibration covariance.
5. Construct ER and background distributions before any likelihood analysis.
