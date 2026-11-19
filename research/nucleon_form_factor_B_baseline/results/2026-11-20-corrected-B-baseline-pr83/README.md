# Corrected finite-nucleon B baseline and AFH-7/Hybrid-9 rate-level outputs

**Archive status:** native output archive; source workflow, artifact digest, extracted payload, run metadata, and every archived file are verified by RUN_MANIFEST.json and SHA256SUMS.

## Provenance

- Source workflow: [run 44584140754](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44584140754), finite nucleon form factors B baseline.
- Source commit: 0b1d1714e461d4c61535c6850805bd8762e32dd0.
- Artifact ID: 14561076256.
- Artifact name: finite-nucleon-form-factor-B-baseline.
- GitHub artifact SHA-256: bd13f797401169a17d6ae5bae9bbbabcec6770226a5b030a407933fcaf22999d.
- Upstream halo input: PR #78 workflow run 44560087038, artifact 14551462445. Its nine extracted native files are byte-identical to the final PR #74 integration rerun archived in the Halo result package.

## Corrected B prescription

The B factor is the finite-nucleon Dirac–Pauli correction multiplied by the finite-size AFH response:

\[
Q_A^2=|\mathbf q_A|^2=2m_AE_R+E_R^2,\qquad t_N=-Q_A^2,
\]
\[
c_M(t_N)=F_1^{uds}(t_N)+\frac{t_N}{8m_N^2}
\left[F_1^{uds}(t_N)+2F_2^{uds}(t_N)\right],
\]
\[
F_M(t_N)=\frac{c_M(t_N)}{3},\qquad
\mathcal C_N(Q_A^2)=|F_M(t_N)|^2.
\]

The finite-size AFH \(W_M(y_A)\) response is retained. The nucleon form factor uses the exact spatial nuclear transfer \(Q_A\); the mediator propagator uses the invariant transfer \(t_A=-2m_AE_R\). These are kept as distinct quantities.

The electromagnetic proton/neutron form factors and coefficient covariance are pinned from Borah, Hill, Lee and Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640, using the GENIE-MC/Generator supplemental distribution at commit e2e04f19e96d395ac646cf3382841646b60fa1b4.

## Corrected strange-current scenarios

Three scenarios are kept separate and are not averaged:

1. **sufian2017_unit_current:** Sufian 2017 unit strange current; frozen magnetic moment because no magnetic radius is supplied by the cited physical-point result.
2. **alexandrou2020_charge_weighted_converted:** Alexandrou 2020 charge-weighted result converted to the unit strange current. Its magnetic expansion uses the normalized form
   \[
   G_M^s(Q^2)=\mu_s\left[1-\frac{\langle r_M^2\rangle_s}{6}Q^2+O(Q^4)\right].
   \]
   A regression test checks the derivative against the published magnetic radius.
3. **alexandrou2026_continuum_unit_current:** continuum-limit physical-point strange form factors, represented by the published low-\(Q^2\) electric and magnetic slopes. This is a slope-only implementation; the full fitted \(z\)-expansion covariance is not reconstructed.

The Borah electromagnetic coefficient covariance is propagated with 3,000 correlated draws using seed 20261119. Strange-lattice uncertainties are recorded but not sampled.

## Seven-isotope B-baseline results

Each scenario contains 208 recoil points and 1,456 isotope-level rows for both baseline and higher-order halo quadrature. The seven AFH isotopes cover natural atom fraction 0.998158; abundances are not renormalized.

| Scenario | Maximum absolute B/A full-rate shift |
|---|---:|
| Sufian 2017 | 56.4346% |
| Alexandrou 2020 converted | 58.2481% |
| Alexandrou 2026 slope-only | 56.3301% |

At the two reference recoil energies:

| \(E_R\) | Sufian 2017 | Alexandrou 2020 converted | Alexandrou 2026 slope-only |
|---:|---:|---:|---:|
| 248 keV | −26.4442% | −27.2648% | −26.3949% |
| 267 keV | −28.6017% | −29.4917% | −28.5483% |

The maximum absolute full-versus-\(I(D)\) discrepancy in the higher-order B natural-xenon grid is 0.3527618%. In the 180–320 keV candidate interval it is at most 0.035510%. The maximum baseline-to-higher-order natural-xenon rate shifts are approximately \(9.89\times10^{-6}\%\) for the full rate and \(1.71\times10^{-5}\%\) for the \(I(D)\) rate.

## Absolute AFH-7/Hybrid-9 spectra

The archive also includes the finite-nucleon correction applied to the committed absolute isotope-resolved three-body kernels:

- 672 natural-xenon spectrum rows per strange-current scenario: four benchmarks × two nuclear-response scenarios × 84 recoil points.
- 3,102 isotope-contribution rows per strange-current scenario.
- AFH-7 uses the seven isotopes with AFH v6.0 default-density responses.
- Hybrid-9 is explicitly AFH-7 plus Helm only for Xe-124 and Xe-126.
- Reconstructing the original A spectrum before applying B closes to \(5.55\times10^{-16}\), against a \(2\times10^{-11}\) tolerance.

## LZ 2026 efficiency-weighted rate-level fold

For each strange-current scenario, the archive contains eight event-yield rows: four benchmarks × AFH-7/Hybrid-9. The fold uses the digitized LZ 2026 Fig. S2 final WIMP-search ROI NR efficiency and its gray envelope, with exposure 2.84 tonne-year. The integral is evaluated analytically for the piecewise-linear spectrum and efficiency, with a 10,000-step dense-trapezoid cross-check.

These are efficiency-weighted rate-level yields. Energy-resolution smearing, event-by-event reconstructed-energy response, two-dimensional S1c/log10(S2c) signal PDFs, background likelihoods, and confidence-level construction are not applied. They are not an official LZ likelihood or a 90% exclusion.

## Files

- source-artifact-pr83.zip: original successful PR #83 workflow artifact.
- extracted/B-baseline/: three strange-current scenarios, baseline halo quadrature.
- extracted/B-highorder/: three scenarios, higher-order halo quadrature.
- extracted/B-quadrature-comparison/: pointwise baseline/high-order comparisons and summaries.
- extracted/B-absolute/: absolute AFH-7/Hybrid-9 spectra and isotope contributions.
- extracted/B-detector/: LZ 2026 efficiency-weighted rate-level event-yield tables and metadata.
- source-code/ and source-inputs/: pinned implementation and input snapshots used by the workflow.
- RUN_MANIFEST.json: source run, commit, artifact ID/digest, upstream halo lineage, calculation summaries, and per-file inventory.
- SHA256SUMS: checksums for the source ZIP, README, code/input snapshots, manifest, and every extracted native file.

## Relationship to the earlier PR #80 archive

The earlier 2026-11-19-finite-nucleon-form-factor-B-baseline archive is retained unchanged as a historical record of the original PR #80 run. Its Sufian 2017 result is unchanged. Its Alexandrou 2020 converted scenario is superseded by this corrected archive because the earlier implementation omitted the overall \(\mu_s\) factor in the magnetic-radius expansion.
