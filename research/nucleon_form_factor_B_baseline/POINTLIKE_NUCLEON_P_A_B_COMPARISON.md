# Pointlike-nucleon P versus zero-transfer A and finite-form-factor B

**Status:** The isotope-resolved P/A/B central spectra and LZ rate-level detector folds have been calculated from the archived AFH-7/Hybrid-9 three-body halo kernels. The formal one-body impulse convention is used throughout this comparison:
\[
t_N=t_A=-2m_AE_R.
\]
The exact spatial transfer
\[
Q_A^2=2m_AE_R+E_R^2
\]
is retained separately for the AFH Fourier variable. It is not used as the nucleon form-factor argument.

## 1. Baseline definitions

All three baselines use the same three-body phase-space integral, halo distribution, isotope abundances, mediator propagator, and finite-size AFH nuclear response. Only the single-nucleon current is changed.

### P: pointlike Dirac nucleon

\[
\boxed{\widehat F_1^N=1,\qquad \widehat F_2^N=0.}
\]
Using the formal charge matching,
\[
\widehat c_M^{P}
=\widehat F_1^N+
\frac{t_N}{8m_N^2}
\left(\widehat F_1^N+2\widehat F_2^N\right)
=1-\frac{2m_AE_R}{8m_N^2}.
\]
The pointlike approximation therefore removes the nucleon Pauli and finite-size form factors while retaining the kinematic recoil term in the matched Dirac current.

### A: zero-transfer nucleon-current reference

\[
\boxed{
\widehat F_1^N(0)=1,\qquad
\widehat F_2^N(0)=-0.184,\qquad t_N=0.
}
\]
Consequently \(\widehat c_M^A=1\). This is the existing zero-transfer reference spectrum. It is not a point nucleus: the finite-size AFH \(W_M^{\rm phys}(y_A)\) response remains in the calculation.

### B: finite nucleon Dirac–Pauli form factors

\[
\widehat F_{1,2}^N(t_N)=\frac{F_{1,2}^{uds,N}(t_N)}{3},
\qquad
\widehat c_M^B(t_N)
=\widehat F_1^N(t_N)
+\frac{t_N}{8m_N^2}
\left[\widehat F_1^N(t_N)+2\widehat F_2^N(t_N)\right].
\]
The finite-\(t_N\) form factors use the Borah et al. (2020) proton/neutron low-\(Q^2\) \(z\)-expansion and the three separately retained unit-strange-current inputs:
Sufian 2017, Alexandrou 2020 converted to the unit current, and Alexandrou 2026 continuum-limit slope-only.

The isotope-level multipliers are
\[
\mathcal C_P=|\widehat c_M^P|^2,\qquad
\mathcal C_A=1,\qquad
\mathcal C_B=|\widehat c_M^B|^2.
\]

## 2. Momentum-transfer and normalization conventions

For each isotope,
\[
q_A^\mu=P_A'^\mu-P_A^\mu,\qquad
t_A=q_A^2=-2m_AE_R,
\]
\[
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2.
\]
The adopted impulse prescription is
\[
\boxed{q_N^\mu=q_A^\mu,\qquad t_N=t_A=-2m_AE_R.}
\]

Thus:

- \(t_N\) enters \(F_1^N,F_2^N\) and \(\widehat c_M\);
- \(Q_A^2\) enters the AFH variable \(y_A=b_A^2Q_A^2/4\);
- the mediator denominator is \((m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2\).

The raw universal \(u+d+s\) form factors are divided by three because the external coupling convention already uses \(g_{VN}=3g_{Vq}\). The AFH raw-to-physical factor of four is applied only in the physical AFH response. The P/A/B comparison does not replace \(W_M^{\rm phys}\) by a point-nucleus response.

## 3. Numerical setup

- Dark matter mass: \(m_{\chi_1}=1\) TeV.
- Mediator mass: \(m_V=10\) GeV.
- Reference coupling product squared: \(10^{-8}\).
- \(g_2=1\); conditional pole-width prescription inherited from the accepted source scan.
- Halo: truncated SHM with \(v_0=220\), \(v_E=232\), \(v_{\rm esc}=544\) km/s.
- Natural xenon: seven AFH isotopes (Xe-128, 129, 130, 131, 132, 134, 136), with natural abundances not renormalized.
- AFH-7 omits Xe-124 and Xe-126. Hybrid-9 adds the explicitly labelled Helm fallback for those two isotopes.
- Recoil grid: the archived 84-point, 5--800 keV spectrum.
- Detector: LZ 2026 Fig. S2 central final-WIMP-search-ROI NR efficiency.
- ROI: 5.4--269.9 keV.
- Exposure: 2.84 tonne-year.
- Detector integration: exact analytic integration of the piecewise-linear recoil spectrum times the piecewise-linear efficiency over the union of their knots.

The A spectrum is reconstructed from the isotope-level kernels and required to close against the archived natural-xenon A spectrum at relative tolerance \(2\times10^{-11}\) before P and B are accepted.

## 4. AFH-7 detector-level results

Central expected events for the Sufian-2017 unit-strange-current B input:

| Benchmark | A: zero-transfer | P: pointlike Dirac | B: finite form factors | P/A | B/A | B/P |
|---|---:|---:|---:|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.3172783 | 0.3142066 | 0.2662628 | 0.990319 | 0.839209 | 0.847413 |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.397899\times10^{-3}\) | \(1.379657\times10^{-3}\) | \(1.102673\times10^{-3}\) | 0.986951 | 0.788807 | 0.799237 |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.858492\times10^{-9}\) | \(2.807575\times10^{-9}\) | \(2.074125\times10^{-9}\) | 0.982188 | 0.725601 | 0.738760 |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(1.144298\times10^{-5}\) | \(1.129372\times10^{-5}\) | \(9.027337\times10^{-6}\) | 0.986957 | 0.788898 | 0.799323 |

The pointlike Dirac recoil term lowers the event yield relative to A by approximately 0.97--1.78%. The finite nucleon form factors then produce a substantially larger additional suppression. For the Sufian input, B is 15.3--26.1% below P, or 16.1--27.4% below A.

## 5. Strange-current input dependence of B

The A and P predictions are independent of the strange-current choice. The B detector yields for the three inputs are:

| Benchmark | Sufian 2017 | Alexandrou 2020 converted | Alexandrou 2026 slope-only |
|---|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.2662628 | 0.2646968 | 0.2663577 |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.102673\times10^{-3}\) | \(1.093571\times10^{-3}\) | \(1.103222\times10^{-3}\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.074125\times10^{-9}\) | \(2.049750\times10^{-9}\) | \(2.075587\times10^{-9}\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(9.027337\times10^{-6}\) | \(8.952866\times10^{-6}\) | \(9.031834\times10^{-6}\) |

The three strange-current inputs remain separate; they are not averaged.

## 6. Hybrid-9 detector-level cross-check

For the Sufian-2017 input, the Hybrid-9 event yields are:

| Benchmark | A | P | B | P/A | B/A | B/P |
|---|---:|---:|---:|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 0.3180931 | 0.3150126 | 0.2669322 | 0.990316 | 0.839164 | 0.847370 |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | \(1.400488\times10^{-3}\) | \(1.382210\times10^{-3}\) | \(1.104690\times10^{-3}\) | 0.986949 | 0.788789 | 0.799220 |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | \(2.858492\times10^{-9}\) | \(2.807575\times10^{-9}\) | \(2.074125\times10^{-9}\) | 0.982188 | 0.725601 | 0.738760 |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | \(1.146423\times10^{-5}\) | \(1.131469\times10^{-5}\) | \(9.043902\times10^{-6}\) | 0.986956 | 0.788880 | 0.799306 |

The Xe-124/Xe-126 Helm contribution changes the first, second, and fourth benchmarks slightly. It does not change the seven AFH isotope contributions.

## 7. Size of the transfer-convention correction

The permanent PR85 archive records the earlier static diagnostic \(t_N=-Q_A^2\). The formal impulse prescription used here is \(t_N=t_A=-2m_AE_R\). Re-evaluating the Borah form factors with the formal transfer changes the four AFH-7 Sufian detector yields by only about \(1.1\times10^{-5}\%\) to \(3.1\times10^{-5}\%\).

This numerical closeness does not make the two prescriptions interchangeable. The formal B production path uses \(t_N=t_A\); the old PR85 archive is preserved as a historical static-transfer diagnostic and is not overwritten.

## 8. Interpretation

1. The pointlike Dirac nucleon correction is small but nonzero, at the percent level in the detector-integrated yields.
2. The finite nucleon form factors are the dominant single-nucleon correction, reducing the B yield by roughly 15--26% relative to P for the primary Sufian input.
3. The AFH finite-size nuclear response remains present in P, A, and B. “Pointlike nucleon” does not mean “pointlike nucleus.”
4. The three-body phase-space and halo kernels are reused without re-integration. The changes arise only from the isotope-level single-nucleon current multiplier.
5. These are rate-level expected event counts. Energy-resolution smearing, event-level S1c/\(\log_{10}S2_c\) PDFs, background likelihood, and confidence-level exclusion are not included.

## 9. Reproducibility

Run the comparison with:

~~~bash
python research/nucleon_form_factor_B_baseline/compare_pointlike_A_B_nucleon_baselines.py \
  --source-dir research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14 \
  --efficiency-csv research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv \
  --out-dir results/pointlike-A-P-B \
  --roi-min-keV 5.4 --roi-max-keV 269.9 --exposure-tonne-year 2.84
~~~

The program writes:
- pointlike_A_B_natural_xenon_spectrum.csv
- pointlike_A_B_isotope_contributions.csv
- pointlike_A_B_detector_yields.csv
- metadata.json
- SHA256SUMS.txt

The workflow .github/workflows/pointlike-nucleon-A-P-B.yml runs the complete regression suite and uploads the numerical outputs as the pointlike-A-P-B-natural-xenon-and-LZ artifact.


### Completed GitHub validation

The pull-request workflow completed successfully:

- P/A/B regression suite: **17 tests passed**.
- A-spectrum reconstruction: maximum relative difference \(5.5511\times10^{-16}\), against the required \(2\times10^{-11}\) tolerance.
- Output rows: 2,016 natural-xenon spectrum rows, 18,144 isotope-contribution rows, and 24 detector-yield rows.
- All four files in the artifact SHA-256 manifest passed checksum verification.

The B values were also independently recalculated by the existing B-baseline workflow after changing its form-factor argument to \(-t_N=2m_AE_R\). Its LZ detector yields agree with the B column in the P/A/B artifact exactly at stored precision for all four benchmarks and both AFH-7/Hybrid-9 scenarios.

- P/A/B workflow: [run 44653142263](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44653142263)
- P/A/B numerical artifact: [download artifact 14590934148](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44653142263/artifacts/14590934148)
- Independent B-baseline workflow: [run 44653142064](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44653142064)
- Repository layout and benchmark-manifest check: [run 44653142113](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44653142113)

The uploaded P/A/B artifact ZIP SHA-256 is:

\[
\texttt{85685c9cb9684d0ad7290e937e5d4b4cd2b505a6f5b93050c08ffbd977d21fac}.
\]
