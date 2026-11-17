# Three-body VV charge-sector contraction: M + Phi''

**Status:** reproducible charge-sector diagnostic; full four-current AFH contraction remains open.

## Purpose

This study connects the existing three-body dark-matter current audit (PR #53)
to the AFH Xe-131 M, Phi'', and M-Phi'' response calculation (PR #54). It
performs an amplitude-level contraction of the Coulomb/charge multipole
sector rather than multiplying response ratios by hand.

The result is deliberately narrower than the full nuclear tensor contraction:
it uses T3^0 and the AFH charge multipoles M and Phi''. Spatial components
T3^i, Sigma', Sigma'', and Delta are not yet included.

## Formula

With the AFH vector-charge multipole convention,
\[
\mathcal M_{JM}^{(V,C)} =
F_1^V M_{JM}+
\frac{q_A^2}{4m_N^2}(F_1^V+2F_2^V)
\left(\Phi''_{JM}-\frac12 M_{JM}\right).
\]

Define r2=F2^V/F1^V and
\[
\eta=\frac{q_A^2}{4m_N^2}(1+2r_2),\quad
C_M/F_1^V=1-\eta/2,\quad C_{\Phi''}/F_1^V=\eta.
\]

The charge-sector contraction is
\[
\mathcal W_C^{(3)}\propto I_{00}
\left[
C_M^2W_M^{00}
+2C_MC_{\Phi''}W_{M\Phi''}^{00}
+C_{\Phi''}^2W_{\Phi''}^{00}
\right].
\]

The ratio to the F1^2 W_M^00 baseline is
\[
R_C=(1-\eta/2)^2+
2(1-\eta/2)\eta\frac{W_{M\Phi''}^{00}}{W_M^{00}}+
\eta^2\frac{W_{\Phi''}^{00}}{W_M^{00}}.
\]

The common AFH isoscalar normalization cancels in this ratio. Do not apply
the equal-proton/equal-neutron factor of four a second time.

## Inputs and provenance

- PR #53 three-body scan: research/vector_current_response_audit/results/2026-11-18/vector_current_response_audit.csv.
- PR #54 AFH response grid: input/afh_vv_phi_xe131_full_grid_pr54_snapshot.csv.
- PR #54 exact AFH minima: input/afh_vv_phi_xe131_selected_points_pr54_snapshot.csv.
- PR #54 source manifest snapshot: input/pr54_run_manifest_snapshot.json.
- AFH response mapping: M uses ResponseNuclear[...,1,0,0], Phi'' uses
  ResponseNuclear[...,4,0,0], and M-Phi'' uses ResponseNuclear[...,7,0,0].

The AFH grid contains 2401 points from q_A=0 to 0.6 GeV at 0.25-MeV
spacing. Three-body benchmark momenta are evaluated with local polynomial
interpolation; exact AFH minima use the separately archived exact-point file.

## F2/F1 sensitivity

The finite-t model-specific F2^V(t)/F1^V(t) is not fixed in the current
project. Therefore the code reports four explicit scenarios:
F2/F1=0, -0.14, -0.15, -0.17. The nonzero values are low-q sensitivity
benchmarks, not a fitted finite-t model or a substitution of electromagnetic
magnetic moments.

## Reproduction

Python 3.12+; standard library only.

~~~bash
python -m unittest discover \
  -s research/three_body_phi_charge_contraction \
  -p 'test_*.py' -v

python research/three_body_phi_charge_contraction/phi_charge_contraction.py \
  --outdir /tmp/three-body-phi-charge-contraction
~~~

The GitHub Actions workflow runs the tests and produces the full 2401-point
contraction grid, the 12-row three-body benchmark contraction, and the exact
AFH-minimum comparison as an artifact.

## Interpretation boundary

- R_C is a charge-sector response ratio, not a full d sigma/dER.
- The chi2 width changes I00, but at fixed q_A it cancels in R_C, because
  the same T3^0 multiplies both charge multipoles.
- This does not imply that width effects cancel in the spatial-current
  Sigma', Sigma'', or Delta sectors.
- The PR #54 native Mathematica cross-check of the Phi'' implementation is
  still pending. The interference sign and normalization remain provisional
  until that independent check passes.
- No mediator propagator, absolute cross section, halo fold, natural-xenon
  isotope sum, detector response, or likelihood is included.
