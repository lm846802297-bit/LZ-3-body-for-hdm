# VV nucleon-current matching and Xe-131 Phi-double-prime response audit

## Question and scope

This study adds the AFH default-density Xe-131 responses
\(W_{\Phi''}^{00}\) and \(W_{M\Phi''}^{00}\) alongside the existing
\(W_M^{00}\) baseline. It asks whether the spin-orbit response remains
nonzero where the existing coherent mass response has deep minima.

A first three-body **charge-sector** matching is now derived: the exact
radiative time current multiplies both \(M\) and \(\Phi''\), so it cancels
from their relative correction at fixed recoil. The zero-momentum form-factor
benchmark gives the first numerical \(M+\Phi''\) correction. This is not yet
the complete three-body rate: finite-\(t\) flavour form factors and the
spatial-current \(\Sigma'\), \(\Sigma''\), and \(\Delta\) sectors remain open.

## Status

**AFH response grid reproduced; charge-sector benchmark implemented; native
Mathematica cross-check passed.** The 2401-point Python response grid,
selected minima, regression tests, native Mathematica export, pointwise
comparison, and run manifest are archived. The new
`phi_charge_response_match.py` evaluates the \(M+\Phi''\) charge-sector
correction using explicitly labelled zero-momentum form-factor anchors.
This is a controlled benchmark, not yet a finite-\(t\), all-current prediction
for the LZ recoil spectrum.

## Model branch and assumptions

- Vector-vector branch only: \(V_\mu\bar\chi_2\gamma^\mu\chi_1\) and a
  universal light-quark vector current.
- Equal proton and neutron vector charges at \(t=0\):
  \(F_1^{V,p}(0)=F_1^{V,n}(0)=3\), for the universal \(u+d+s\) number
  current (the strange vector charge vanishes at zero momentum transfer).
- Isoscalar AFH component only: \((\tau_1,\tau_2)=(0,0)\).
- AFH/DMFormFactor v6.0 built-in Xe-131 default density matrix; 67 entries.
- Default oscillator length: \(b_A=2.2923417985218975\,\mathrm{fm}\).
- Response variable: \(y=(b_Aq_A/2)^2\), where \(q_A\) is the spatial
  nuclear momentum transfer.
- Grid: 0--0.6 GeV in 0.25 MeV steps.
- The exact equal-p/n AFH factor-four conversion is applied once. Raw
  physical responses are reported separately from the legacy mass-response
  shape normalization.

The nucleon Pauli form factor is not assigned a constant by fiat. Its
flavour content, sign convention, and \(t\)-dependence are discussed in
the theory note.

## Files

- afh_vv_phi_xe131.py: vectorized AFH v6.0 Python translation for \(M\),
  \(\Phi''\), and \(M\)-\(\Phi''\) interference.
- run_native_phi_xe131.wls: native Mathematica export using
  ResponseNuclear indices 1, 4, and 7.
- compare_native_phi_xe131.py: exact-grid Python/Mathematica comparison;
  interpolation is explicitly forbidden.
- verify_phi_mpmath.py: 60-digit independent special-function spot-check at
  the four archived minima.
- phi_charge_response_match.py: coefficient-level (M+Phi'') charge-sector
  matching and 2401-point correction scan; default form factors are
  zero-momentum anchors only.
- tests/test_phi_charge_response_match.py: charge-coefficient, reference
  point, positivity, and Cauchy--Schwarz regression checks.
- tests/: regression checks for the 67-entry matrix, oscillator length,
  archived \(M\)-response minima, selected \(\Phi''\) ratios, and the
  Cauchy--Schwarz response inequality.
- output/: full 2401-point response grid, selected minima, native comparison
  when run, and run_manifest.json.
- theory/VV_NUCLEON_CURRENT_AND_PHI_RESPONSE.md: physical derivation,
  normalization, results, and matching caveats.
- audit/NUMERICAL_AUDIT.md: calculation procedure and numerical results.

## Reproduction

From the repository root:

~~~bash
python research/afh_vv_phi_xe131/afh_vv_phi_xe131.py
python research/afh_vv_phi_xe131/phi_charge_response_match.py \
  --grid research/afh_vv_phi_xe131/output/afh_vv_phi_xe131_full_grid.csv \
  --selected research/afh_vv_phi_xe131/output/afh_vv_phi_xe131_selected_points.csv \
  --outdir research/afh_vv_phi_xe131/output/
python -m unittest discover -s research/afh_vv_phi_xe131/tests -v
python research/afh_vv_phi_xe131/verify_phi_mpmath.py
~~~

This reads the already archived input matrix, minima, and canonical
\(W_M^{00}\) grid from research/afh_default_density_xe131/.

For native AFH execution on a machine with Wolfram Engine/Mathematica:

~~~bash
wolframscript -file research/afh_vv_phi_xe131/run_native_phi_xe131.wls
python research/afh_vv_phi_xe131/compare_native_phi_xe131.py \
  --python-csv research/afh_vv_phi_xe131/output/afh_vv_phi_xe131_full_grid.csv \
  --mathematica-csv research/afh_vv_phi_xe131/output/native_mathematica/afh_vv_phi_xe131_native.csv \
  --output research/afh_vv_phi_xe131/output/native_mathematica/comparison.json
~~~

Python dependencies: NumPy, SciPy, SymPy, and mpmath. The native export
additionally requires Wolfram Engine/Mathematica and wolframscript.

## Results and interpretation boundary

Recoil energies below use the AME2020 Xe-131 neutral-atom mass converted to
the bare nuclear mass using CODATA-2022 constants. At the second mass-response
minimum, \(q_A=256.271867617\) MeV and \(E_R=269.3595249\) keV, the exact AFH
responses give
\[
W_{\Phi''}/W_M=115.8894642,\qquad
W_{M\Phi''}/W_M=-1.46248999.
\]
Using the zero-momentum diagnostic inputs \(F_1^V(0)=3\),
\(F_2^V(0)=-0.552\), and \(m_N=0.938918\) GeV gives
\[
\eta=c_{\Phi''}/c_M=0.01184042,\qquad
Q_{\Phi''}=0.9816142.
\]
Thus the \(\Phi''\) addition changes the same nonrelativistically normalized
\(M\)-only charge response by \(-1.839\%\), not by a factor of 115.9.
Including the \(t_N/(8m_N^2)\) correction to the \(M\) coefficient gives
a combined \(-2.991\%\) change relative to \(F_1^V(0)^2W_M\) at this point.

The 2401-point diagnostic grid shows a rapid local variation around the
deep \(W_M\) cancellation: the sampled \(Q_{\Phi''}-1\) ranges from
\(-13.61\%\) at \(q_A=255.75\) MeV (\(E_R=268.2636\) keV) to
\(+11.50\%\) at \(q_A=256.75\) MeV (\(E_R=270.3656\) keV). These are local ratios to a very small \(W_M\)
baseline, not global event-rate changes. The signed interference changes
rapidly across the minimum, while the combined charge response remains
nonnegative.

The form factors in this benchmark are held fixed at their \(t=0\) values.
A final prediction requires finite-\(t\), flavour-separated
\(F_1^{V,N}(t_N)\) and \(F_2^{V,N}(t_N)\). The current calculation also
contains only the \(M+\Phi''\) vector-charge sector. The spatial-current
contraction can generate \(\Sigma'\), \(\Sigma''\), and \(\Delta\), which
must be matched independently.

The current AFH result is Xe-131 only. No natural-xenon isotope sum,
halo fold, detector convolution, or manuscript modification is part of
this study.
## Provenance

- AFH package: v6/dmformfactor-V6.m, SHA-256
  dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372.
- Density matrix: research/afh_default_density_xe131/input/afh_default_xe131_density_matrix.csv,
  SHA-256 f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45.
- Existing mass-response baseline and its native Mathematica/Python audit are
  retained unchanged under research/afh_default_density_xe131/.

## Next step

1. Supply finite-\(t\), flavour-separated \(F_1^{V,N}(t_N)\) and
   \(F_2^{V,N}(t_N)\) in the fixed \(q_A\) convention.
2. Complete the spatial-current Pauli reduction and match the resulting
   \(\Sigma'\), \(\Sigma''\), and \(\Delta\) coefficients to AFH.
3. Repeat the AFH response calculation for the other naturally abundant
   xenon isotopes before producing the full natural-xenon spectrum.
4. Preserve the current \(W_M\)-only natural-xenon result as the baseline;
   do not label the Xe-131 charge-sector benchmark as a complete prediction.
