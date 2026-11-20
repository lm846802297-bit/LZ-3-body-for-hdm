# Four-level nucleon-current comparison: P0, P, A0 and B

**Status:** The four-level comparison has been numerically reconstructed from the archived isotope-resolved three-body/halo kernels and the LZ 2026 NR efficiency. The central calculation keeps the same AFH finite-size \(W_M\) response, mediator propagator, three-body phase-space integrals, halo distribution and isotope abundances in all four baselines.

The original PR85 source spectrum was labelled A. Its actual content is the leading-order charge-only baseline P0, not the zero-transfer Dirac–Pauli approximation A0. This distinction is now explicit in the calculation and output metadata.

> **P0/P distinction:** P0 and P share the same pointlike Dirac form factors, \(\widehat F_1=1,\widehat F_2=0\). P0 uses the leading-order coefficient \(c_M=1\), while P retains \(c_M=1+t_N/(8m_N^2)\). Their difference is the retained matching order, not a difference in nucleon structure. The detailed derivation and numerical P0/P validation are documented in [P0_VS_P_POINTLIKE_DIRAC_BASELINES.md](P0_VS_P_POINTLIKE_DIRAC_BASELINES.md).

## 1. Four baseline definitions

Use the normalized flavor-current form factors
\[
\widehat F_i^N(t_N)=\frac{F_i^{uds,N}(t_N)}{3},
\]
because the external coupling convention already uses \(g_{VN}=3g_{Vq}\).

The formal impulse prescription used for this comparison is
\[
q_N^\mu=q_A^\mu,\qquad
t_N=t_A=-2m_AE_R.
\]
The exact spatial momentum remains
\[
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2,
\]
and is used separately in the AFH Fourier variable \(y_A=b_A^2Q_A^2/4\).

### P0: archived leading-order charge-only baseline

\[
\boxed{
\widehat F_1=1,\qquad \widehat F_2=0,\qquad
\widehat c_M^{P0}=1.
}
\]
This is the archived source rate. The source CSV's legacy column named rate_events_kg_day_keV is interpreted as P0. It contains the leading-order charge-only M response and does not include the finite-\(t_N\) recoil matching correction.

### P: pointlike Dirac nucleon

\[
\boxed{
\widehat F_1=1,\qquad \widehat F_2=0.
}
\]
Retaining the finite-transfer charge matching term gives
\[
\boxed{
\widehat c_M^P
=1+\frac{t_N}{8m_N^2}
=1-\frac{2m_AE_R}{8m_N^2}.
}
\]
The difference P/P0 isolates the relativistic recoil correction of a pointlike Dirac nucleon.

### A0: zero-momentum nucleon form factors

Freeze the Dirac and Pauli form factors at their zero-transfer values:
\[
\boxed{
\widehat F_1^{A0}(t_N)=\widehat F_1(0)=1,\qquad
\widehat F_2^{A0}(t_N)=\widehat F_2(0).
}
\]
The actual nonzero transfer remains in the matching coefficient:
\[
\boxed{
\widehat c_M^{A0}
=1+\frac{t_N}{8m_N^2}
\left[1+2\widehat F_2(0)\right].
}
\]
A0 therefore retains the static Pauli magnetic moment while freezing the form-factor momentum dependence.

### B: finite-momentum nucleon form factors

\[
\widehat F_{1,2}^{B}(t_N)
=\frac{F_{1,2}^{uds,N}(t_N)}{3},
\]
\[
\boxed{
\widehat c_M^{B}(t_N)
=\widehat F_1^B(t_N)
+\frac{t_N}{8m_N^2}
\left[\widehat F_1^B(t_N)+2\widehat F_2^B(t_N)\right].
}
\]
The proton and neutron electromagnetic Sachs form factors use the Borah et al. (2020) low-\(Q^2\) \(z\)-expansion. The strange unit-current input is kept as three separate scenarios: Sufian 2017, Alexandrou 2020 converted to the unit current, and Alexandrou 2026 continuum-limit slope-only.

All four baselines retain the same finite-size AFH \(W_M(y_A)\). P is pointlike at the single-nucleon level, not at the nuclear level.

## 2. Zero-transfer Pauli inputs

The zero-transfer values are reconstructed from the pinned Borah electromagnetic normalizations and each strange-current input:
\[
\widehat F_2(0)
=F_2^{\mathrm{EM},p}(0)
+F_2^{\mathrm{EM},n}(0)
+F_2^{s,\mathrm{unit}}(0).
\]

The results are:

| Strange-current input | \(\widehat F_2(0)\) |
|---|---:|
| Sufian 2017 | \(-0.1868323435\) |
| Alexandrou 2020 converted to unit current | \(-0.0718323435\) |
| Alexandrou 2026 continuum unit current | \(-0.1407523435\) |

For example, Sufian 2017 gives
\[
(2.7928473508-1)
+(-1.9156796943)
+(-0.064)
=-0.1868323435.
\]

The previous fixed value \(-0.184\) is not used in A0. It does not match the current Borah-2020 electromagnetic normalization and Sufian unit-current input.

## 3. Numerical setup

- Dark matter mass: \(m_{\chi_1}=1\) TeV.
- Mediator mass: \(m_V=10\) GeV.
- Reference coupling product squared: \(10^{-8}\).
- \(g_2=1\), with the archived conditional pole-width prescription.
- Truncated SHM: \(v_0=220\), \(v_E=232\), \(v_{\rm esc}=544\) km/s.
- Natural xenon with unrenormalized natural isotope abundances.
- AFH-7: Xe-128, 129, 130, 131, 132, 134 and 136.
- Hybrid-9: AFH-7 plus the separately labelled Helm fallback for Xe-124 and Xe-126.
- Recoil grid: 84 archived points from 5 to 800 keV.
- LZ 2026 Fig. S2 central final-WIMP-search-ROI NR efficiency.
- ROI: 5.4–269.9 keV.
- Exposure: 2.84 tonne-year.
- Detector integration: exact analytic integration of the piecewise-linear recoil spectrum times the piecewise-linear efficiency over the union of their knots.

The P0 spectrum is reconstructed from the isotope-level kernels and required to close against the archived source spectrum at relative tolerance \(2\times10^{-11}\). The B result is independently generated by the B postprocessor using the same formal \(t_N=t_A\) convention.

## 4. AFH-7 detector-level results

Central expected events for the Sufian 2017 strange-current input:

| Benchmark | P0: leading order | P: pointlike Dirac | A0: frozen \(F_i(0)\) | B: finite \(F_i(t_N)\) |
|---|---:|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.3172783 | 0.3142066 | 0.3153524 | 0.2662628 |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.397899\times10^{-3}\) | \(1.379657\times10^{-3}\) | \(1.386459\times10^{-3}\) | \(1.102673\times10^{-3}\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.858492\times10^{-9}\) | \(2.807575\times10^{-9}\) | \(2.826547\times10^{-9}\) | \(2.074125\times10^{-9}\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(1.144298\times10^{-5}\) | \(1.129372\times10^{-5}\) | \(1.134938\times10^{-5}\) | \(9.027337\times10^{-6}\) |

### 4.1 Separate size of the three effects

| Benchmark | P/P0 − 1 | A0/P − 1 | B/A0 − 1 |
|---|---:|---:|---:|
| 200 keV, 1 MeV | \(-0.9681\%\) | \(+0.3647\%\) | \(-15.5666\%\) |
| 300 keV, 1 MeV | \(-1.3050\%\) | \(+0.4930\%\) | \(-20.4684\%\) |
| 360 keV, 1 MeV | \(-1.7812\%\) | \(+0.6757\%\) | \(-26.6198\%\) |
| 300 keV, 10 MeV | \(-1.3043\%\) | \(+0.4928\%\) | \(-20.4596\%\) |

Thus:

1. The pointlike Dirac recoil correction reduces the yield by approximately 0.97–1.78%.
2. The static Pauli magnetic moment raises the yield relative to P by approximately 0.36–0.68%.
3. Finite-momentum nucleon structure produces the dominant additional suppression, approximately 15.6–26.6% relative to A0.

### 4.2 A0 and B dependence on the strange-current input

A0 yields:

| Benchmark | Sufian 2017 | Alexandrou 2020 converted | Alexandrou 2026 |
|---|---:|---:|---:|
| 200 keV, 1 MeV | 0.3153524 | 0.3146468 | 0.3150696 |
| 300 keV, 1 MeV | \(1.386459\times10^{-3}\) | \(1.382270\times10^{-3}\) | \(1.384780\times10^{-3}\) |
| 360 keV, 1 MeV | \(2.826547\times10^{-9}\) | \(2.814862\times10^{-9}\) | \(2.821862\times10^{-9}\) |
| 300 keV, 10 MeV | \(1.134938\times10^{-5}\) | \(1.131511\times10^{-5}\) | \(1.133564\times10^{-5}\) |

B yields:

| Benchmark | Sufian 2017 | Alexandrou 2020 converted | Alexandrou 2026 |
|---|---:|---:|---:|
| 200 keV, 1 MeV | 0.2662628 | 0.2646968 | 0.2663577 |
| 300 keV, 1 MeV | \(1.102673\times10^{-3}\) | \(1.093571\times10^{-3}\) | \(1.103222\times10^{-3}\) |
| 360 keV, 1 MeV | \(2.074125\times10^{-9}\) | \(2.049750\times10^{-9}\) | \(2.075588\times10^{-9}\) |
| 300 keV, 10 MeV | \(9.027337\times10^{-6}\) | \(8.952866\times10^{-6}\) | \(9.031834\times10^{-6}\) |

The strange-current scenarios remain separate; no averaging is performed.

### 4.3 Correct interpretation of the historical B/A ratio

The historical PR85 ratio labelled B/A used the archived leading-order charge-only spectrum. Its correct four-level name is
\[
\boxed{B/P0,}
\]
not \(B/A0\).

For the Sufian input, the detector-integrated ratios are:

| Benchmark | B/P0 | B/P | B/A0 |
|---|---:|---:|---:|
| 200 keV, 1 MeV | 0.839209 | 0.847413 | 0.844334 |
| 300 keV, 1 MeV | 0.788807 | 0.799237 | 0.795316 |
| 360 keV, 1 MeV | 0.725601 | 0.738760 | 0.733802 |
| 300 keV, 10 MeV | 0.788898 | 0.799323 | 0.795404 |

The old PR85 archive remains immutable as a historical record. Its legacy A label is mapped to P0 in the current code, metadata and documentation.

## 5. Hybrid-9 cross-check

For the Sufian 2017 input, the Hybrid-9 expected events are:

| Benchmark | P0 | P | A0 | B |
|---|---:|---:|---:|---:|
| 200 keV, 1 MeV | 0.3180931 | 0.3150126 | 0.3161617 | 0.2669322 |
| 300 keV, 1 MeV | \(1.400488\times10^{-3}\) | \(1.382210\times10^{-3}\) | \(1.389026\times10^{-3}\) | \(1.104690\times10^{-3}\) |
| 360 keV, 1 MeV | \(2.858492\times10^{-9}\) | \(2.807575\times10^{-9}\) | \(2.826547\times10^{-9}\) | \(2.074125\times10^{-9}\) |
| 300 keV, 10 MeV | \(1.146423\times10^{-5}\) | \(1.131469\times10^{-5}\) | \(1.137045\times10^{-5}\) | \(9.043902\times10^{-6}\) |

The Xe-124/Xe-126 Helm fallback changes the Hybrid-9 total slightly. It does not change any of the seven AFH isotope contributions.

## 6. Momentum-transfer and normalization audit

For each isotope:
\[
t_A=q_A^2=-2m_AE_R,\qquad
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2.
\]
The adopted formal impulse prescription is
\[
\boxed{t_N=t_A=-2m_AE_R.}
\]

The calculation keeps the variables separate:

- \(t_N\): argument of the nucleon form factors and the \(c_M\) matching coefficient.
- \(Q_A^2\): spatial momentum in the AFH Fourier variable \(y_A=b_A^2Q_A^2/4\).
- \(t_A\): invariant momentum transfer in the mediator propagator \((m_V^2-t_A)^{-2}\).

The earlier PR85 static-nucleon prescription \(t_N=-Q_A^2\) is retained only as a historical diagnostic. It is not mixed into the formal-impulse P0/P/A0/B production path.

## 7. Interpretation and scope

- P0, P, A0 and B all use the same finite-size AFH \(W_M\) response. Pointlike nucleon does not mean pointlike nucleus.
- P/P0 isolates the pointlike Dirac recoil matching correction.
- A0/P isolates the static Pauli magnetic-moment contribution.
- B/A0 isolates the finite-momentum nucleon form-factor dependence.
- The three-body phase-space and halo kernels are reused without re-integration.
- These are rate-level expected event counts. Energy-resolution smearing, event-level S1c/\(\log_{10}S2_c\) PDFs, background likelihood and confidence-level exclusion are not included.
- Additional AFH responses such as \(W_{\Phi''}\) and \(W_{M\Phi''}\) remain outside this M-only comparison.

## 8. Reproducibility

Run:
~~~bash
python research/nucleon_form_factor_B_baseline/compare_pointlike_A_B_nucleon_baselines.py \
  --source-dir research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14 \
  --efficiency-csv research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv \
  --out-dir results/nucleon-P0-P-A0-B \
  --roi-min-keV 5.4 --roi-max-keV 269.9 --exposure-tonne-year 2.84
~~~

The program writes:
- nucleon_P0_P_A0_B_natural_xenon_spectrum.csv
- nucleon_P0_P_A0_B_isotope_contributions.csv
- nucleon_P0_P_A0_B_detector_yields.csv
- metadata.json
- SHA256SUMS.txt

The workflow .github/workflows/pointlike-nucleon-A-P-B.yml runs the regression suite and uploads the four-level numerical outputs.
