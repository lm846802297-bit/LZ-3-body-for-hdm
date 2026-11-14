# LZ 2026 public-input audit for the three-body xenon recast

Date: 2026-11-14
Repository branch: research/figure2-p0-4-mainline
Paper: LZ Collaboration, arXiv:2609.02823v1
HEPData DOI: 10.17182/hepdata.182472.v1

## Executive result

The LZ 2026 extended-NR paper exposes enough information to build a substantially better detector-response recast than an efficiency-only fold:

- a 303-point digitization of the final WIMP-search NR efficiency is already archived in this repository;
- the paper states that its tuned NEST v2.4.5 best-fit response parameters are included in the HEPData release;
- the paper publishes the candidate event coordinates and reconstructed recoil energy;
- the paper documents the simultaneous science, prompt-veto, and delayed-veto sample structure and the extended unbinned likelihood.

However, a faithful reproduction of the collaboration likelihood still requires confirming and obtaining the actual signal/background PDF templates and the complete nuisance-parameter constraint information. Public plots and tabulated best-fit NEST parameters are not by themselves equivalent to the BACCARAT PDF templates used in the official fit.

## 1. Verified experimental facts

From arXiv:2609.02823v1:

- Exposure: 2.84 tonne-year.
- Live time: 220 days.
- Fiducial LXe mass: 4.71 +/- 0.08 tonnes.
- WS ROI: S1c = 3--600 phd, S2 > 645 phd, and S2c = 10^2.75--10^4.15 phd.
- NR efficiency averages about 96% from 14 to 250 keV.
- Candidate: S1c = 540.1 phd, S2c = 9268 phd, reconstructed NR energy 248 +/- 23 (stat) +/- 23 (sys) keV.
- The candidate is 1.5 sigma below the modeled NR-band median and 6.7 sigma below the ER-band median at that S1c.
- The collaboration's background-only comparison gives 2.6 sigma global significance after look-elsewhere correction, with maximum local significance 3.4 sigma among the tested models.

These values are paper-level inputs and should be versioned alongside the recast.

## 2. Public detector-response information

The paper identifies NEST v2.4.5 as the tuned detector-response model. The best-fit NEST parameters are stated to be in the HEPData data release, and the Supplemental Material provides the model details.

The repository already contains:
- lz_2026_extended_nr/lz_2026_nr_efficiency_digitized.csv
- lz_2026_extended_nr/lz_2026_nr_efficiency_metadata.json
- lz_2026_extended_nr/rate_level_event_yields/

The digitization metadata records:
- 303 sampled points;
- central final-ROI efficiency and gray uncertainty envelope;
- epsilon(248 keV) = 0.94569;
- lower/upper envelope at 248 keV = 0.88355 / 0.98000;
- gray envelope has no confidence level assigned by LZ and must be treated as a systematic variation, not a confidence interval.

The official paper states that the final NEST response parameters are supplied in the data release. Therefore the next action is to retrieve and version those parameters and check whether the HEPData record contains machine-readable calibration points, efficiency tables, and likelihood-related data.

## 3. What the official detector likelihood actually uses

The LZ analysis does not use only a one-dimensional recoil-energy likelihood.

It constructs signal and background PDFs in:
{S1c, log10(S2c)}

using BACCARAT/GEANT4 simulations with tuned NEST v2.4.5 detector response, with stated exceptions for selected components.

The collaboration simultaneously fits three event samples:
1. science;
2. prompt veto;
3. delayed veto.

The fit is an unbinned extended maximum likelihood. Background component normalizations are nuisance parameters with auxiliary constraints; neutron components are additionally constrained by prompt/delayed veto efficiencies. MSSI, 127Xe, and detector-material gamma components have additional veto-sideband constraints.

Consequently, a faithful recast needs more than the public NR efficiency curve:
- signal NR PDF in S1c/log10(S2c) for this three-body recoil spectrum;
- background PDFs or sufficient public templates/data to reconstruct them;
- science/prompt-veto/delayed-veto event samples;
- auxiliary constraint terms and nuisance correlations;
- exact ROI, FV, and selection definitions.

## 4. Data availability classification

| Input | Current status | Action |
|---|---|---|
| NR efficiency central curve and gray band | Already digitized and archived | Keep as rate-level cross-check |
| NEST v2.4.5 best-fit NR parameters | Paper says available in HEPData | Retrieve machine-readable tables and pin version |
| NR calibration cloud in S1c/log10(S2c) | Published in paper figures | Digitize only for validation, not as substitute for full calibration data |
| Candidate event coordinate | Published: (540.1, 9268) phd | Include in diagnostic plots |
| Candidate reconstructed energy | Published with stat/sys uncertainties | Use only with correct response/energy mapping |
| Background component expected/fitted yields | Published in paper tables | Use as constraints/cross-check |
| Three sample definitions | Published | Implement exact sample structure if templates available |
| Signal/background BACCARAT PDFs | Their use is described; public machine-readable availability not yet verified | Investigate HEPData files and supplementary materials |
| Full nuisance covariance and auxiliary likelihood | Not yet verified in machine-readable release | Do not claim exact official likelihood reproduction until obtained |

## 5. Immediate implementation plan

### P0: Close theory inputs before detector likelihood

The existing width audit shows that the three-body kernel can be sensitive to the independent coupling g2 under the constant pole-width prescription. For example, in the archived diagnostic at ms=300 keV, Delta m=1 MeV, ER=200 keV, v=776 km/s, g2=3 changes I6 by about -45.2% relative to zero width, while the diagnostic running-width ansatz changes it by about -1.83%.

This is not a license to choose running width because it gives a smaller effect. The source manuscript's propagator prescription, Dirac/Majorana nature, allowed decay channels, and independent g2 must be fixed first. The existing running-width result is explicitly diagnostic, not a full fermion self-energy calculation.

### P1: Build a validated NEST response layer

1. Obtain the LZ-tuned NEST v2.4.5 NR parameter table from the HEPData release.
2. Pin the exact NEST release/commit and compile/run configuration.
3. Reproduce mean NR light and charge yields over the analysis recoil-energy range.
4. Reproduce fluctuations and generate conditional S1c/log10(S2c) PDFs.
5. Validate against the published NR calibration band and efficiency curve.
6. Keep detector acceptance separate from the conditional response PDF to prevent double counting.

### P2: Reconstruct or approximate the likelihood transparently

Preferred route: use official machine-readable PDFs/templates and auxiliary likelihood inputs if they are available.

Fallback route: build a clearly labelled approximate recast using the published candidate coordinate, published background yields and uncertainties, published NR efficiency, and reconstructed NEST PDFs. It must not be called the official LZ likelihood or a faithful reproduction.

### P3: Model-specific inference

For the three-body model, generate signal PDFs by folding the predicted true recoil spectrum through the conditional NEST response, then through the analysis selections. Fit the science/prompt-veto/delayed-veto samples where the required information exists. Otherwise report energy-only/rate-level constraints with explicit limitations.

## 6. Candidate event interpretation policy

The 248 keV event is an event of interest / candidate, not a dark-matter discovery. The collaboration reports 2.6 sigma global significance after the look-elsewhere correction. A three-body model should be tested against:
- the candidate's S1c/S2c location;
- the full NR spectrum in the 5.4--269.9 keV accepted window;
- the lower-energy region and higher-energy sidebands;
- background-only and alternative signal hypotheses.

Do not normalize the model to one event and call that a confidence limit. Do not use the high-S1 background expectation of 0.0106 events as the total background over the full ROI; that value refers to a specific projection bin in the paper.

## 7. Key references

- LZ Collaboration, arXiv:2609.02823v1, especially detector/calibration, data-analysis, likelihood, and supplemental NEST sections.
- HEPData record: DOI 10.17182/hepdata.182472.v1.
- NEST v2.4.5 release and LZ tuning details cited by the LZ paper.

## Status

This audit is a public-input availability assessment. It does not claim that the HEPData package has been fully downloaded or that the official likelihood has been reproduced. The existing rate-level event-yield archive remains a useful cross-check, not the final detector-level analysis.
