# Three-body vector-current and nuclear-response audit

**Status:** reproducible diagnostic; full AFH spin/orbital contraction remains exploratory.

## 1. Research question and scope

This study tests whether the \(W_M^{00}\)-only treatment is justified after
retaining all four Lorentz components of the three-body dark-matter current.

It separates three questions:

1. Does the vector-current magnetization term couple to the dark-matter
   spatial current strongly enough to require the nuclear spin responses
   \(\Sigma'\) and \(\Sigma''\)?
2. Does the nucleon convection current generate a relevant orbital
   \(\Delta\) response?
3. Do the virtual \(\chi_2\) propagator and scalar-emission diagrams change
   the ratio of the dark-matter spatial and temporal currents?

The Python calculation completes the exact four-component dark-matter
current, the coherent point-charge-current comparison, and the
propagator-width scan. It does **not** yet contract the three-body tensor with
the AFH \(\Sigma'\), \(\Sigma''\), and \(\Delta\) nuclear multipoles.

## 2. Model and conventions

- Natural units; metric \((+---)\); all masses and momenta in GeV.
- The two scalar-emission diagrams are kept coherently:
  \[
  \Gamma^\mu=
  \gamma^\mu\frac{\slashed p-\slashed k_s+m_{\chi_2}}{D_{\rm before}}
  +\frac{\slashed p'+\slashed k_s+m_{\chi_2}}{D_{\rm after}}\gamma^\mu.
  \]
- The dark-matter tensor is
  \[
  L^{\mu\nu}=\frac12\operatorname{Tr}
  [(\slashed p'+m_{\chi_1})\Gamma^\mu
   (\slashed p+m_{\chi_1})\bar\Gamma^\nu].
  \]
- For the coherent point-nucleus comparison,
  \(J_A^\mu=(P+P')^\mu F_A(q_A^2)\), with \(F_A\) factored out.
  This is a coherent point-charge current representative, not the full vector current of spinful Xe-131. It includes centre-of-mass
  convection, not internal nuclear orbital or magnetization currents.
- The scalar width is the existing conditional Dirac / real-scalar /
  pure-scalar / single-open-channel \(\chi_2\to\chi_1s\) width. The
  running-width option is a diagnostic Breit-Wigner ansatz, not the full
  \(\chi_2\) self-energy; the vector-sector contribution remains unspecified.
- Fixed-speed Xe-131 benchmark mass convention: \(m_A=131u\), with
  \(u=0.93149410242\) GeV; \(m_{\chi_1}=1\) TeV and \(v=776\) km/s.
- No halo integral, isotope-abundance fold, detector response, or likelihood
  is included.

## 3. Inputs and provenance

| Input | Source / version | SHA / identity |
|---|---|---|
| Eq. (6) baseline kernel | Main-branch research/three_body_calculation_and_validation/eq6_kernel.py at baseline commit c0cd9a566b570a8f317abfdd20fc7fcdfdde298e | Git blob 68a9f6b3767728898b97494382234f77fc063c79 |
| AFH nuclear-response definitions | v6/dmformfactor-V6.m, AFH DMFormFactor v6.0 | Repository source; response IDs 1, 2, 3, 6 |
| Three-body benchmark inputs | Existing repository benchmark conventions | Explicitly recorded in results/2026-11-18/metadata.json |

No new external nuclear data or fitted parameters are introduced.

## 4. Code map

| Purpose | Path |
|---|---|
| Full four-component current tensor, point-current contraction, width scan | vector_current_response_audit.py |
| Unit and regression tests | test_vector_current_response_audit.py |
| Numerical results and interpretation | results/2026-11-18/RESULTS.md |
| Machine-readable 12-row scan | results/2026-11-18/vector_current_response_audit.csv |
| Quadrature refinement | results/2026-11-18/quadrature_convergence.csv |
| Run provenance and checksums | results/2026-11-18/run_manifest.json, SHA256SUMS.txt |

## 5. Environment and reproduction

- Python 3.12 or later.
- Dependency: NumPy.
- The script imports the existing Eq. (6) kernel from
  research/three_body_calculation_and_validation/.

From the repository root:

~~~bash
python -m unittest discover \
  -s research/vector_current_response_audit \
  -p 'test_*.py' -v

python research/vector_current_response_audit/vector_current_response_audit.py \
  --outdir research/vector_current_response_audit/results/2026-11-18
~~~

The benchmark scan is deterministic; there are no random seeds.

## 6. Validation

The regression tests cover:

- equality of the new \(\Gamma^0\) trace with the legacy Eq. (6) temporal
  spin trace, with zero and pole width;
- Hermiticity and positive semidefiniteness of \(L^{\mu\nu}\);
- conservation of the coherent point-charge current;
- exact decomposition of charge, spatial-square, and interference pieces;
- closed-phase-space handling;
- stability of the spatial/temporal ratio when the \(\chi_2\) width changes.

The archived quadrature checks compare the 450-keV pole-width result through
48x32x16, the 1-MeV result through 32x24x12, and the near-pole \(W^2\)
integration using the endpoint-clustered \(\sin^2\) map. The near-pole scan
uses a separate \(n_W\) refinement at fixed \(n_z=16,n_\phi=8\).

The initial numerical archive was assembled with a standalone mirror of the
baseline Eq. (6) kernel API. The PR workflow subsequently reran the committed
script against the exact repository source at commit
28ff13722b7b33ba6145fb7caa3548c365f086e5: all 8 tests passed, the full
12-row calculation completed, and the regenerated numerical table agreed
exactly with the archived table (maximum relative difference 0; workflow
run 44169485507). Software checks validate only the implemented current
tensor and coherent point-charge comparison, not the omitted AFH internal
nuclear responses.

## 7. Results

The main numerical conclusions are in
results/2026-11-18/RESULTS.md.

Across the scanned benchmarks, the target-rest-frame spatial-to-temporal
dark-matter current norm is approximately \(2.47\times10^{-3}\). The exact
coherent point-charge-current contraction differs from the charge-only result by
about 4--5 ppm. The \(\chi_2\) width can strongly alter the absolute
three-body kernel near the pole while changing the spatial/temporal current
ratio by at most about 0.1% in this scan.

For the nuclear responses, AFH v6.0 defines:
- ResponseNuclear[y,1,0,0]: \(W_M\);
- ResponseNuclear[y,2,0,0]: \(W_{\Sigma''}\);
- ResponseNuclear[y,3,0,0]: \(W_{\Sigma'}\);
- ResponseNuclear[y,6,0,0]: \(W_\Delta\).

The existing archived AFH response validation covers \(W_M\), not yet the
three-body contraction with the other response channels. This matters near
a minimum of \(W_M\), where a subleading absolute contribution may become
relatively important.

## 8. Assumptions and limitations

- The coherent point-charge-current calculation is not the internal nuclear
  convection or magnetization current.
- The per-nucleon estimates \(r_\chi v_N\) and
  \(r_\chi Q_A/(2m_N)\) are kinematic amplitude factors only. They are not
  nuclear-response ratios and do not include AFH matrix elements or
  coherence/cancellation factors.
- \(F_2\) for the model's universal quark/baryon vector current is not
  specified. The quoted minimal magnetization estimate uses a point-Dirac
  nucleon with \(F_1=1,F_2=0\); electromagnetic nucleon magnetic moments
  must not be substituted without a matching calculation.
- The spin responses are relevant only for isotopes with nonzero ground-state
  spin, notably \(^{129}\mathrm{Xe}\) (\(J=1/2\)) and
  \(^{131}\mathrm{Xe}\) (\(J=3/2\)). The even-even xenon isotopes have
  \(J=0\), but this fact alone is not a numerical evaluation of all orbital
  multipoles.
- The AFH response grids presently used by the project validate \(W_M\);
  no numerical \(\Sigma'\), \(\Sigma''\), or \(\Delta\) contraction is
  claimed here.
- The scalar-only \(\chi_2\) width omits the unspecified vector-sector
  self-energy contribution.
- Results are fixed-speed, single-isotope diagnostics, not natural-xenon
  halo-folded spectra or detector-level LZ predictions.

## 9. History and next steps

- Baseline main commit: c0cd9a566b570a8f317abfdd20fc7fcdfdde298e.
- The original Eq. (6) kernel is not modified.
- No manuscript source under paper-source/ is modified.
- Next step: export and validate the AFH \(\Sigma'\), \(\Sigma''\), and
  \(\Delta\) response grids for all seven isotopes with default matrices,
  then derive the phase-space-dependent nonrelativistic coefficient map
  needed to contract those responses with \(L^{\mu\nu}\). Pay particular
  attention to recoil energies where \(W_M^{00}\) has a deep minimum.
