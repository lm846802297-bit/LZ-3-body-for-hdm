# Repository instructions — LZ three-body dark-matter research

These instructions are mandatory for all agents and contributors. They complement [CONTRIBUTING.md](CONTRIBUTING.md), [research/WORKFLOW.md](research/WORKFLOW.md), and the research-result archival policy.

## 1. Minimal preflight

Before substantive work:

1. Read this file, the root [README](README.md), [CONTRIBUTING.md](CONTRIBUTING.md), [research/WORKFLOW.md](research/WORKFLOW.md), and [research/README.md](research/README.md).
2. Read the relevant topic README, theory note, audit, scripts, tests, and input provenance. Use [the model and three-body amplitude note](research/docs/01_model_and_amplitude.md), [the LZ recast plan](research/docs/02_lz_recast.md), [the cosmology note](research/docs/03_cosmology.md), and [the audit/roadmap](research/docs/04_audit_and_roadmap.md) when relevant.
3. Inspect the latest main SHA, open PRs touching the same paths, and the exact baseline data/code before changing a calculation.
4. Do not infer that a planned task has run. Create a run record only after execution; preserve failed, partial, and blocked attempts honestly.

## 2. Scientific scope and model separation

The central direct-detection process is `chi_1 + A -> chi_1 + A + s`. The repository investigates whether this three-body radiation mechanism can produce a viable xenon recoil spectrum while satisfying detector, cosmological, and other constraints. A high-energy LZ candidate is not a dark-matter discovery; do not write as though the model has already explained it.

Keep model branches separate:

- **Vector–vector:** vector mediator/nuclear vector current and coherent nuclear response, subject to the exact assumptions in the active theory record.
- **Scalar–pseudoscalar:** pseudoscalar nuclear current, momentum/spin response, and its own amplitude and nuclear matrix elements.

These are not interchangeable versions of one formula. Never carry the vector-current amplitude, coherent response, or normalization into the scalar–pseudoscalar branch without a new derivation.

Before a scan, state the fermion nature (Dirac/Majorana), chiral and CP structure, mediator and scalar content, mass hierarchy, coupling conventions, and whether the mediator is a Proca EFT field or a gauge boson of a broken symmetry. Do not silently promote an incompletely specified draft Lagrangian into a complete UV model.

## 3. Three-body amplitude and kinematics

For every amplitude implementation:

1. Derive and document the full three-body phase-space boundaries, including the definitions of (W^2), (W^2_{min}), (W^2_{max}), and all frame-dependent angles.
2. Define (z=cos	heta_*) and (phi_*) with the exact rest frame and axis convention used by the source derivation. If the original convention is incomplete, state and justify the convention adopted; do not infer it from variable names alone.
3. Construct the final-state four-momenta explicitly and verify on-shell conditions, four-momentum conservation, and the phase-space Jacobian.
4. Include both scalar-emission orderings on the dark-matter line. Add the amplitudes coherently and retain their interference; do not add the two diagram cross sections incoherently.
5. Derive spin sums/averages from the Dirac trace and state every initial-state average and final-state sum. Do not duplicate or omit factors such as the initial spin average.
6. Distinguish the dimensionless kinematic lambda in the phase-space expression from the dimensionful Källén function used in decay-width formulas.
7. Check the propagator denominator, mediator momentum transfer, overall dimensions, symmetry factors, and limiting cases independently of the final spectrum.

For an internal `chi_2` propagator, justify the width prescription from its momentum and kinematics. A statement that the physical on-shell pole is outside the integration range does not by itself prove that finite-width effects are negligible near the endpoint. Record the minimum pole detuning and compare finite-width and zero-width results; if the model or open channels change, rederive the width and propagator treatment.

## 4. Nuclear response and natural xenon

A single-isotope, fixed-velocity differential cross section is not a detector recoil spectrum.

- Use isotope-specific nuclear masses and isotope-specific nuclear responses. For natural xenon, sum over the isotopes included in the adopted abundance table; record the abundance source, isotope list, mass fractions, and normalization.
- In the detector rate, use the correct number of target nuclei per detector mass. With isotope mass fraction (x_i), the schematic weighting is (x_i/m_{A_i}), not an unqualified arithmetic average of isotope cross sections.
- Preserve the distinction between microscopic (dsigma_{A_i}/dE_R), the halo-averaged rate, and the detector-level reconstructed spectrum.
- Use the nuclear-response conventions and harmonic-oscillator length prescription specified by the adopted reference. Do not treat the oscillator length as a free fit parameter or tune it to reproduce a plotted minimum. If the reference prescription changes, document the source and quantify the impact.
- Do not replace a finite-momentum nuclear response by its zero-momentum (A^2) limit outside the regime where that approximation is valid.
- Record the nuclear-response implementation, interpolation, units, form-factor normalization, and independent checks against reference values or tables.

## 5. Halo average and detector response

The detector rate requires the laboratory-frame velocity distribution and detector response. State the local dark-matter density, Galactic velocity model, escape speed, laboratory/Earth velocity, time-averaging or annual-modulation convention, and normalization of (f_{m lab}(mathbf v)).

For isotope mass fractions (x_i), the schematic rate per detector mass is

`dR/dE_R = (rho_chi/m_chi) sum_i [x_i/m_{A_i}] integral d^3v f_lab(v) v d sigma_{A_i}/dE_R`.

Verify normalization and units from the precise definition of (x_i), detector mass, and isotope abundance used in code.

When comparing with LZ data, distinguish true recoil energy (E_R) from reconstructed energy (E_{m rec}); differential rate from accepted event counts; exposure/live time from fiducial target mass; efficiency/acceptance from energy-resolution smearing; and signal-region data from sidebands and background assumptions.

Do not normalize a theoretical curve to the candidate event alone and call that a fit. State the likelihood, nuisance parameters, energy windows, treatment of backgrounds, and whether the analysis is a simplified energy-only recast or the official experiment likelihood. Do not label a local significance as global significance or a candidate event as a discovery.

## 6. Cosmology and scalar decays

Use the same model parameters and coupling conventions when connecting direct detection to relic abundance, scalar freeze-out/post-freeze-out evolution, (s) decay, and (Delta N_{m eff}).

Record thermal-history assumptions: equilibrium conditions, distribution functions (MB/FD/BE), chemical potentials/fugacities, initial conditions, included and omitted collision terms, detailed-balance factors, energy and number moments, neutrino-decoupling treatment, and numerical integration tolerances.

Check number/energy conservation identities, equilibrium limits, signs of energy transfer, thresholds, decay widths, and sensitivity to omitted channels. An approximate massless sterile-neutrino treatment or instantaneous active-neutrino decoupling is a model assumption to test and document, not an established fact about an observed particle.

Do not combine cosmological and direct-detection constraints using mismatched benchmark parameters or an unverified coupling translation.

## 7. Data, manuscript, and archival boundaries

- Preserve `paper-source/main_original.tex`, original figures, bibliography, and other original source assets byte-for-byte. Do not overwrite them or silently replace the source archive.
- The working manuscript `paper-source/main.tex` is distinct from the preserved original. A research-code PR must not modify the manuscript unless the task explicitly includes manuscript editing and the diff is separately identified and reviewed.
- Treat figure digitization, data conversion, isotope-abundance updates, and reconstructed-efficiency curves as research inputs: retain the source, extraction method, units, and checksums.
- Follow [research/WORKFLOW.md](research/WORKFLOW.md) and the mandatory calculation-result archival policy. **If files arrive in a ZIP/TAR delivery bundle, extract the bundle first and commit the required extracted native files individually.** Do not commit the delivery bundle as the sole or substitute record of its contents. Retain an original upstream archive only when needed for provenance/reproducibility, with source/version, size, SHA-256, extraction command, and per-file checksums recorded; still commit the extracted files when redistribution is allowed.
- Use Git LFS or durable versioned storage with a manifest for large outputs. Verify remote paths, sizes, counts, and SHA-256 after pushing.

## 8. Validation and completion

Use tests for algebraic limits, kinematic boundaries, four-momentum conservation, trace identities, response normalization, halo normalization, integration convergence, isotope sums, detector convolution, and cosmological conservation laws as applicable.

A plot that resembles a reference figure is not sufficient validation. Do not tune couplings, nuclear lengths, response normalizations, efficiencies, or statistical factors to force agreement. First identify whether a discrepancy comes from conventions, input data, approximations, numerical convergence, or an implementation defect.

At completion, report the exact model branch and assumptions; derivation/code/input revisions and parameter benchmark; tests, convergence, and independent checks actually run; raw cross section, halo-averaged rate, and detector-level result separately; unresolved physics/statistical limitations; and exact GitHub archival status and verified paths.

Use a focused branch and PR. Never describe the LZ candidate as explained or a model as viable unless the full required evidence supports that statement.

## CI is optional; research work must not wait for CI

Continuous integration (CI) is optional supporting infrastructure. It is not a prerequisite, acceptance gate, or merge condition for research work.

- Do not require a CI run to start, continue, or complete a calculation; perform numerical or scientific validation; prepare or archive results; commit or push research files; open or update a pull request; mark a pull request ready for review; or merge a pull request.
- If the calculation can be run directly on an available local machine or an approved compute runner, proceed. Do not pause research solely because GitHub Actions is queued, unavailable, disabled, blocked by account/billing limits, or failing for infrastructure reasons.
- GitHub Actions may still be used when useful as an optional compute, dispatch, or artifact-handoff mechanism. A workflow that actually executes a research calculation is an execution run: record its exact source commit, inputs, settings, environment, logs, and outputs. Its use does not make a separate CI status check mandatory.
- This policy does not waive scientific or numerical validation. Perform the checks appropriate to the claim—such as analytic identities, dimensional and unit checks, limiting cases, independent implementations, convergence, uncertainty estimates, provenance, and output-integrity checks—locally or on an approved runner, and record exactly what was performed. CI neither substitutes for these checks nor adds a mandatory gate.
- If CI is run, report its exact commit SHA and actual result. If it is not run, queued, blocked, cancelled, or failed, record that status truthfully and distinguish infrastructure failure from a scientific or numerical failure. Never describe an unrun check as passed.
- Base review and merge decisions on the actual diff, reproducibility, scientific evidence, scope, and the checks that are genuinely relevant to the change—not on whether a CI badge is green. Do not configure CI status checks as required branch-protection gates under this repository policy. Do not change repository protection settings without explicit authorization.
- CI becomes mandatory for a particular task only when the author explicitly requests it for that task.

