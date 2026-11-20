# B baseline: finite nucleon form factors × finite-size AFH charge response

## Adopted definition

The project baseline is

\[
\boxed{F_1(t_N),\quad F_2(t_N),\quad W_M(y_A)}
\]

with nucleon structure and nuclear finite-size structure kept as distinct ingredients.

For a target isotope with recoil energy \(E_R\),

\[
Q_A^2\equiv |\mathbf q_A|^2=2m_AE_R+E_R^2,
\qquad
t_N=t_A=-2m_AE_R.
\]

The same calculation also keeps the invariant transfer in the mediator propagator separate:

\[
t_A=q_A^2=-2m_AE_R,
\qquad
\frac{1}{(m_V^2-t_A)^2}
=\frac{1}{(m_V^2+2m_AE_R)^2}.
\]

Thus \(Q_A^2\) is used for the AFH spatial momentum only. The nucleon form factors use \(-t_N=2m_AE_R\), with the formal impulse identification \(t_N=t_A\); the same invariant \(t_A\) enters the mediator propagator.

For universal unit \(u,d,s\) vector coupling, the flavor sum is reconstructed as

\[
F_i^{uds,N}(t_N)
=
3\left[
F_i^{\mathrm{EM},p}(t_N)
+F_i^{\mathrm{EM},n}(t_N)
+F_i^{s,N,\mathrm{unit}}(t_N)
\right].
\]

The charge-like NR coefficient used by this B rate-level implementation is

\[
c_M(t_N)=F_1^{uds,N}(t_N)
+\frac{t_N}{8m_N^2}
\left[F_1^{uds,N}(t_N)+2F_2^{uds,N}(t_N)\right].
\]

Since the equal-coupling pointlike normalization is \(c_M(0)=3\), define

\[
F_M(t_N)=\frac{c_M(t_N)}{3},
\qquad
\mathcal C_N(t_N)=|F_M(t_N)|^2.
\]

Each isotope's already-computed three-body rate contribution is multiplied by \(\mathcal C_N\), then the natural-xenon sum is reconstructed. The finite-size AFH \(W_M(y_A)\) response is retained unchanged; it is not replaced by a point-nucleus response.

## Electromagnetic proton and neutron inputs

The electromagnetic input is the separate proton and neutron low-\(Q^2\) \(z\)-expansion of Borah, Hill, Lee and Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640. The pinned coefficients and free-coefficient covariance matrices are under data/borah2020/.

The source data are the GENIE-MC/Generator distribution of the Borah et al. supplemental data:

- config/ZExpELFormFactorModel.xml
- data/covariances/FormFactor/Vector/ELZExpFF.dat
- pinned source commit: e2e04f19e96d395ac646cf3382841646b60fa1b4

The four free coefficients of each Sachs form factor are completed by the \(G(0)\) normalization and four \(Q^4\) asymptotic sum rules, following GENIE's Q4limit implementation. The full Sachs form factors are converted using

\[
F_1=\frac{G_E+\tau G_M}{1+\tau},
\qquad
F_2=\frac{G_M-G_E}{1+\tau},
\qquad
\tau=\frac{Q^2}{4m_N^2}.
\]

The electromagnetic coefficient covariance is propagated using correlated Monte Carlo draws. It is kept distinct from the strange-current scenario dependence.

## Strange-current scenarios

Three separately labelled strange-current inputs are implemented. Their current conventions are documented in strange_current_convention_audit.md.

1. sufian2017_unit_current — historical primary benchmark. This is already the unit-current matrix element \(\bar s\gamma^\mu s\), with \(G_M^s(0)=-0.064\) and \(\langle r_E^2\rangle_s=-0.0043\,\mathrm{fm}^2\). The magnetic form factor is frozen at zero momentum because the cited physical-point result does not provide a magnetic radius.
2. alexandrou2020_charge_weighted_converted — Alexandrou et al. (2020). The published charge-weighted form factors are divided by \(e_s=-1/3\) to convert to the unit strange current. The magnetic-radius expansion includes its \(G_M^s(0)=\mu_s\) normalization.
3. alexandrou2026_continuum_unit_current — Alexandrou et al., arXiv:2603.26600 (2026). The reported form factors already use the unit-current convention. The current implementation uses the published electric and magnetic slopes as a low-\(Q^2\) expansion; it is not a reconstruction of the full \(z\)-expansion.

The three scenarios are calculated separately and never averaged. The 2026 source uncertainties are recorded in metadata but are not yet sampled.

## Applying B to the halo/isotope artifact

This postprocessor uses the isotope-level CSV from the seven-isotope halo workflow. It does not rerun the three-body phase-space integration.

    python research/nucleon_form_factor_B_baseline/apply_nucleon_form_factors_B.py \
      --input-dir path/to/halo-seven-isotope-highorder \
      --out-dir results/nucleon-form-factor-B \
      --draws 3000

## Applying B to the archived absolute AFH-7/Hybrid-9 spectra

The absolute-spectrum postprocessor reconstructs the archived leading-order P0 spectrum from the isotope-resolved three-body kernels before applying B. It requires the reconstructed P0 spectrum to close against the archived natural-xenon P0 spectrum at relative tolerance \(2\times10^{-11}\).

    for model in sufian2017_unit_current alexandrou2020_charge_weighted_converted alexandrou2026_continuum_unit_current; do
      python research/nucleon_form_factor_B_baseline/apply_B_to_afh_hybrid9_continuous_spectrum.py \
        --source-dir research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14 \
        --out-dir results/B-absolute/$model \
        --strange-model $model --draws 3000
    done

It writes:

- afh_hybrid9_B_natural_xenon_spectrum.csv
- afh_hybrid9_B_isotope_contributions.csv
- metadata.json
- SHA256SUMS.txt

The isotope output records \(Q_A^2\), \(t_N\), \(t_A\), \(c_M\), \(F_M\), and the individual P0/B rate contributions. The metadata records the exact source-file hashes and the electromagnetic covariance sampling seed.

## LZ 2026 efficiency fold

The B spectra can be passed directly to the existing rate-level LZ efficiency fold:

    python research/three_body_calculation_and_validation/fold_lz_2026_afh_hybrid9_rate_level.py \
      --spectrum-csv results/B-absolute/sufian2017_unit_current/afh_hybrid9_B_natural_xenon_spectrum.csv \
      --spectrum-metadata results/B-absolute/sufian2017_unit_current/metadata.json \
      --efficiency-csv research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv \
      --out-dir results/B-detector/sufian2017_unit_current \
      --exposure-tonne-year 2.84 --integration-steps 10000

This applies the digitized LZ 2026 Fig. S2 final-WIMP-search-ROI NR efficiency over \(5.4\)–\(269.9\) keV and reports efficiency-weighted expected event yields for AFH-7 and Hybrid-9.

The detector fold reports the central B event yield. The separate covariance propagator applies the same 3000 correlated Borah coefficient draws to every isotope and recoil energy, then integrates each draw through the LZ central efficiency curve. It writes the p16, median and p84 detector event yields and checks the central event yield against the existing detector fold. The strange-lattice uncertainties and the LZ gray efficiency envelope are not sampled or combined with the electromagnetic covariance. The gray envelope has no confidence level assigned by LZ.

    python research/nucleon_form_factor_B_baseline/propagate_B_covariance_to_lz_yields.py \
      --source-dir research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14 \
      --b-spectrum-dir results/B-absolute/sufian2017_unit_current \
      --detector-yield-csv results/B-detector/sufian2017_unit_current/lz_2026_afh7_hybrid9_rate_level_event_yields.csv \
      --efficiency-csv research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv \
      --out-dir results/B-detector-covariance/sufian2017_unit_current \
      --strange-model sufian2017_unit_current --draws 3000

## P0 versus P: pointlike Dirac nucleon precision levels

P0 and P use the same pointlike Dirac form factors, \(\widehat F_1=1\) and \(\widehat F_2=0\). Their difference is the matching order:

\[
\widehat c_M^{P0}=F_M^{P0}=1,\qquad
\widehat c_M^P=F_M^P=1+\frac{t_N}{8m_N^2}
=1-\frac{Q_N^2}{8m_N^2},\qquad c_M^{\rm raw}=3\widehat c_M.
\]

P0 is the archived leading-order charge-only spectrum. P retains the finite-transfer correction in the current M-only charge matching prescription. Both retain the same finite-size AFH \(W_M\), three-body/halo kernels and isotope sum. Thus P0 is the leading-order approximation to P, not a different nucleon-structure model.

The detailed derivation, momentum-transfer definitions, fixed-isotope rate ratio, natural-xenon folding, Xe-131 numerical check and detector-level comparison are recorded in [P0_VS_P_POINTLIKE_DIRAC_BASELINES.md](P0_VS_P_POINTLIKE_DIRAC_BASELINES.md). The full four-level P0/P/A0/B numerical comparison remains in [POINTLIKE_NUCLEON_P_A_B_COMPARISON.md](POINTLIKE_NUCLEON_P_A_B_COMPARISON.md).

## Four-level P0/P/A0/B nucleon-current comparison

The original PR85 source spectrum labelled A is the leading-order charge-only reference P0:
\[
\widehat F_1=1,\qquad \widehat F_2=0,\qquad \widehat c_M=F_M=1 \ (c_M^{\rm raw}=3).
\]
It is not the zero-transfer Dirac–Pauli approximation.

The four comparisons are:

- P0: archived leading-order charge-only rate, \(\widehat c_M=F_M=1\) (raw \(c_M^{\rm raw}=3\)).
- P: pointlike Dirac nucleon, \(\widehat F_1=1\), \(\widehat F_2=0\), retaining the finite-transfer recoil matching term.
- A0: freeze \(\widehat F_1(0)=1\) and the model-specific \(\widehat F_2(0)\), while retaining the actual recoil matching term.
- B: finite-momentum Borah proton/neutron Dirac–Pauli form factors plus the selected unit-strange-current input.

All four retain the same finite-size AFH \(W_M(y_A)\) response and the same three-body/halo kernels. The formal impulse prescription is \(t_N=t_A=-2m_AE_R\); \(Q_A^2=2m_AE_R+E_R^2\) remains the AFH spatial Fourier variable.

See [POINTLIKE_NUCLEON_P_A_B_COMPARISON.md](POINTLIKE_NUCLEON_P_A_B_COMPARISON.md) for the formulas, detector-level event yields, three strange-current scenarios, AFH-7/Hybrid-9 comparison, and numerical interpretation.

Run the calculation with:

~~~bash
python research/nucleon_form_factor_B_baseline/compare_pointlike_A_B_nucleon_baselines.py \
  --source-dir research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14 \
  --efficiency-csv research/lz_detector_response/lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv \
  --out-dir results/nucleon-P0-P-A0-B
~~~

The workflow [.github/workflows/pointlike-nucleon-A-P-B.yml](../../.github/workflows/pointlike-nucleon-A-P-B.yml) runs the regression suite and uploads the four-baseline spectra and detector yields.

## Validation and scope

Regression tests cover zero-momentum normalization, Sachs-to-Dirac/Pauli conversion, the \(z\)-expansion sum rules, covariance properties, strange-current conventions, magnetic-radius normalization, exact P0-spectrum closure, model-dependent \(\widehat F_2(0)\) inputs, four-level P0/P/A0/B spectra, isotope-level B multiplication, and natural-xenon resummation.

This stage includes finite nucleon \(F_1,F_2\), the finite-size AFH \(W_M\) response, the three-body/halo spectrum, and the LZ NR efficiency fold. It does not include additional AFH responses such as \(W_{\Phi''}\) or \(W_{M\Phi''}\), energy-resolution smearing, S1c/\(\log_{10}S2_c\) signal PDFs, background likelihood, or a confidence-level exclusion.


## Permanent numerical archive

The current PR85 result has a permanent native-output archive at [results/2026-11-20-B-baseline-PR85/README.md](results/2026-11-20-B-baseline-PR85/README.md). It contains the original pinned Actions artifact, all extracted CSV/JSON outputs, source-code and source-input snapshots, the run manifest, and a SHA-256 checksum list.

The archive workflow [44593911420](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44593911420) passed artifact identity/digest verification, extraction checks, B-baseline and detector-scope validations, correlated-covariance checks, and the complete archive checksum self-check. The archived source calculation is pinned to commit f6a01b7735c2373848510657826503484dd118d5.
