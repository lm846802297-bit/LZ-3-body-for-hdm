# Numerical audit: AFH Xe-131 \(M\), \(\Phi''\), and interference

## Run identity

- Study: research/afh_vv_phi_xe131/
- AFH source: v6/dmformfactor-V6.m
- Source SHA-256: dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372
- Density-matrix SHA-256: f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45
- Matrix rows: 67; isoscalar normal-parity entries: rank 0 = 16, rank 2 = 8
- Oscillator length: 2.2923417985218975 fm
- Grid: 2401 points, 0--0.6 GeV, 0.00025 GeV spacing
- Reproduction workflow environment (GitHub Actions): Python 3.13.18, NumPy 2.5.5, SciPy 1.18.1, SymPy 1.14.0; the exact mpmath version is recorded in run_manifest.json.

## Procedure

1. Read the unmodified 67-entry Xe-131 AFH density matrix already archived in
   research/afh_default_density_xe131/input/.
2. Translate AFH v6.0 MJE, PhiPPJ, BesselElement,
   BesselElementMinus, and BesselElementPlus definitions into Python.
3. Precompute Wigner 3j/6j/9j recoupling coefficients and evaluate the
   q-dependent hypergeometric sums on the 2401-point grid.
4. Assemble W_M, W_PhiPP, and W_MPhiPP in the AFH isoscalar convention.
5. Convert the isoscalar response to equal physical proton/neutron couplings
   by multiplying by four exactly once.
6. Check the four existing mass-response minima, Cauchy--Schwarz at every
   grid node, and high-precision mpmath spot checks.
7. Provide a native Mathematica runner and exact-grid comparator. The native
   execution remains pending until it is run on a Wolfram installation.

## Regression and numerical checks

| Check | Result |
|---|---|
| 67-entry input matrix and rank inventory | PASS |
| AFH default \(b_A\) | PASS |
| Four archived \(M\)-response rank-0/rank-2 amplitudes | PASS |
| Nonzero \(W_{\Phi''}(q=0)\) | PASS |
| \(q_A=256.272\) MeV response ratios | PASS |
| Cauchy--Schwarz over all 2401 points | PASS |
| 60-digit mpmath spot-check at four minima | PASS; max relative amplitude difference \(2.13\times10^{-15}\) |
| Native Mathematica/Python pointwise comparison | PENDING |
| (M+Phi'') vector-charge coefficient matching | PASS as a zero-(t) benchmark |
| Finite-(t) flavour-separated form factors | PENDING |
| Spatial-current (Sigma'), (Sigma''), and (Delta) matching | PENDING |

The full-grid Cauchy--Schwarz maximum is
\(0.9999998601592628\), at \(q_A=470.75\) MeV. This is a normalized
correlation and is expected to be no larger than one.

## Selected-point results

Raw equal-p/n physical response divided by \(A^2\):

| \(q_A\) (MeV) | \(W_{\Phi''}/W_M\) | \(W_{M\Phi''}/W_M\) | \(|W_{M\Phi''}|/\sqrt{W_MW_{\Phi''}}\) |
|---:|---:|---:|---:|
| 157.935778 | 13.5676847 | +0.3313747 | 0.0899635 |
| 256.271868 | 115.8894642 | -1.4624900 | 0.1358535 |
| 365.066569 | 2.2555441 | +0.3599774 | 0.2396898 |
| 499.371886 | 0.69015695 | -0.0882541 | 0.1062334 |

The full numerical values and all 2401 grid points are in
output/afh_vv_phi_xe131_full_grid.csv; the four minima are in
output/afh_vv_phi_xe131_selected_points.csv.

## First charge-sector matching result

The separate script
\`phi_charge_response_match.py\` applies the nonrelativistic vector-charge
expansion of Hoferichter, Menéndez, and Schwenk, PRD 102, 074018 (2020),
Eq. (41), and matches its spin-orbit term to the AFH \(\Phi''\) operator
of Anand, Fitzpatrick, and Haxton, PRC 89, 065501 (2014), Eq. (51).

With \(q_A=k'-k\), \(t_A=-q_A^2\), and the AFH Fourier convention
\(\boldsymbol q_{\rm AFH}=-\boldsymbol q_A\), the coefficients are
\[
c_M=F_1^V(t_A)+\frac{t_A}{8m_N^2}
       [F_1^V(t_A)+2F_2^V(t_A)],
\]
\[
c_{\Phi''}=\frac{q_A^2}{4m_N^2}
       [F_1^V(t_A)+2F_2^V(t_A)].
\]
The three-body charge amplitude factorizes as
\[
\mathcal M_{M+\Phi''}^{(3)}
=\mathcal T_3^0[c_M M+c_{\Phi''}\Phi''].
\]
Thus the common spin-averaged three-body phase-space integral of
\(\mathcal T_3^0\) cancels from the relative \(M+\Phi''\) correction.
This is a charge-sector matching result; it does not include the spatial
current or the \(\Sigma'\), \(\Sigma''\), and \(\Delta\) responses.

For the diagnostic anchors \(F_1^V(0)=3\), \(F_2^V(0)=-0.552\), and
\(m_N=0.938918\) GeV, at the second \(W_M\) minimum:
\[
q_A=256.271867617\ {\rm MeV},\quad
E_R=269.1038976\ {\rm keV},\quad
\eta=c_{\Phi''}/c_M=0.01184042.
\]
Using the exact selected-point AFH responses gives
\[
Q_{\Phi''}
=1+2\eta\frac{W_{M\Phi''}}{W_M}
+\eta^2\frac{W_{\Phi''}}{W_M}
=0.9816142.
\]
This is a \(-1.839\%\) change relative to the same relativistically
corrected \(M\)-only charge response. Including the \(t_A/(8m_N^2)\)
correction to \(c_M\), the combined result is \(-2.991\%\) relative to
\(F_1^V(0)^2W_M\) at this selected point.

Across the 2401-node grid, the sampled \(Q_{\Phi''}-1\) varies locally
from \(-13.61\%\) at \(q_A=255.75\) MeV to \(+11.50\%\) at
\(q_A=256.75\) MeV. These extrema occur in the deep \(W_M\) cancellation
region and are ratios to a very small \(W_M\) denominator; they must not
be described as a global rate change. The matched charge response is
checked to remain nonnegative.

The default \(F_1,F_2\) are held at their zero-momentum values in this
diagnostic. Finite-\(t\) flavour-separated form factors are still required
for a quantitative spectrum.

## Normalization audit

For Xe-131, \(J_A=3/2\), so the equal-p/n physical conversion factor is

\[
4\times\frac{4\pi}{2J_A+1}=4\pi.
\]

The raw mass response at q=0 gives
\(R_M(0)/A^2=0.9999174770036694\). The legacy mass-only shape normalization
multiplies by 1.0000825298069376 to enforce exactly \(A^2\). That small
mass-only correction is not imposed on the \(\Phi''\) or mixed response.
Both raw physical and shape-comparison columns are retained in the CSV.

## Scientific interpretation

The \(\Phi''\) nuclear response does not share the deep suppression of the
second \(W_M\) minimum. Therefore a response-level \(W_M\)-only audit is not
sufficient to prove that spin-orbit nuclear structure is negligible.

The new result is a matched **charge-sector** correction, not a complete
three-body cross-section prediction. The common \(\mathcal T_3^0\) factor
cancels only in the relative \(M+\Phi''\) charge-sector ratio. Finite-\(t\)
form factors and the spatial-current \(\Sigma'\), \(\Sigma''\), and
\(\Delta\) sectors remain to be calculated.

## Reproduction commands

~~~bash
python research/afh_vv_phi_xe131/afh_vv_phi_xe131.py
python research/afh_vv_phi_xe131/phi_charge_response_match.py \
  --grid research/afh_vv_phi_xe131/output/afh_vv_phi_xe131_full_grid.csv \
  --selected research/afh_vv_phi_xe131/output/afh_vv_phi_xe131_selected_points.csv \
  --outdir research/afh_vv_phi_xe131/output/
python -m unittest discover -s research/afh_vv_phi_xe131/tests -v
python research/afh_vv_phi_xe131/verify_phi_mpmath.py
~~~

Native Mathematica execution and comparison commands are in the study README.
