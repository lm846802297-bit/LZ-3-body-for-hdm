# Exploratory three-body Phi'' charge-projection stress test

**Status: exploratory only. This is not an accepted VV-to-AFH matching or a physical recoil-rate correction.**

This study combines the existing three-body temporal kernel from PR #53 with
the AFH Xe-131 M, Phi'', and M-Phi'' response data from PR #54 under an
explicit trial coefficient map. It asks how sensitive the rate could be to
the spin-orbit response if that map were applicable.

The trial map is
\[
C_M/F_1=1-\eta/2,\qquad C_{\Phi''}/F_1=\eta,\qquad
\eta=\frac{q_A^2}{4m_N^2}(1+2F_2/F_1).
\]
It gives
\[
R_C^{\rm trial}=(1-\eta/2)^2+
2(1-\eta/2)\eta\frac{W_{M\Phi''}}{W_M}
+\eta^2\frac{W_{\Phi''}}{W_M}.
\]

**Important:** the isolated charge projection is not the full amplitude
\(\mathcal T_3^\mu J^N_\mu\). The spatial-current terms can combine with,
modify, or cancel charge-piece spin-orbit terms when the full nonrelativistic
operator basis is constructed. Therefore the numerical values below are
sensitivity diagnostics only. In particular, the -12.79% value at 267 keV
must not be quoted as the predicted change in the physical three-body rate.

## Inputs

- PR #53 three-body scan:
  research/vector_current_response_audit/results/2026-11-18/vector_current_response_audit.csv.
- PR #54 AFH response grid:
  input/afh_vv_phi_xe131_full_grid_pr54_snapshot.csv.
- PR #54 exact AFH minima:
  input/afh_vv_phi_xe131_selected_points_pr54_snapshot.csv.
- PR #54 source manifest snapshot:
  input/pr54_run_manifest_snapshot.json.

The AFH grid has 2401 points from q_A=0 to 0.6 GeV at 0.25-MeV spacing.
Three-body benchmark momenta use local polynomial interpolation; exact AFH
minima use the separate exact-point file.

## Sensitivity scenarios

The finite-t model-specific F2/F1 is not fixed. The code reports
F2/F1=0,-0.14,-0.15,-0.17 as explicit sensitivity cases. These are not a
finite-t form-factor fit.

## Reproduction

Python 3.12+; standard library only.

~~~bash
python -m unittest discover \
  -s research/three_body_phi_charge_contraction \
  -p 'test_*.py' -v

python research/three_body_phi_charge_contraction/phi_charge_contraction.py \
  --outdir /tmp/three-body-phi-charge-contraction
~~~

The workflow uploads the 2401-point grid, the benchmark table, and the
exact-AFH-minimum table. Passing tests validates the interpolation and
arithmetic implementation, not the physical matching.

## Next required step

Construct the spin-resolved 2x2 matrix \(\mathcal T_3^\mu\), verify its
spin trace against the existing \(L^{\mu\nu}\), derive its Ward contraction,
and only then contract the complete current with the Dirac-Pauli nucleon
current. The physical coefficients of M, Phi'', Sigma', Sigma'', Delta,
and their interferences must come from that full reduction.
