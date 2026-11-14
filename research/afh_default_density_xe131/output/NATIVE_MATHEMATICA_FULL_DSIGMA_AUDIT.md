# Native Mathematica–Python audit of the complete Xe-131 differential cross section

**Status: implementation prepared; native Mathematica execution and cross-code comparison are pending.**

The completed 2401-node native AFH comparison validates the nuclear response layer only. It does not validate the three-body integral I6 or the complete differential cross section.

## 1. Fixed benchmark and assumptions

The initial comparison uses the four archived Figure 2 diagnostic benchmarks:

| Label | ms | Delta m |
|---|---:|---:|
| red | 200 keV | 1 MeV |
| green | 300 keV | 1 MeV |
| black | 360 keV | 1 MeV |
| blue | 300 keV | 10 MeV |

Shared inputs: m_chi1 = 1 TeV, m_V = 10 GeV, v = 800 km/s, m_A = 131u = 122.02572741702 GeV, and (g1 g2 gVN)^2 = 10^-8. The benchmark decomposition sets g2 = 1; the coupling product alone does not determine g2.

The primary width is the constant pole width at m_chi2 = m_chi1 + Delta m. It is conditional on Dirac chi states, a real scalar, a pure scalar off-diagonal Yukawa vertex, and chi2 -> chi1 s as the only open decay channel. A zero-width run is available as a separate diagnostic. Neither is the complete vector-plus-scalar self-energy.

The A*u mass convention is retained only to match the archived four-benchmark calculation. It must not be mixed silently with the AME2020 exact-isotope-mass results.

## 2. Integral implemented independently in Wolfram Language

\[
I_6(v,E_R)=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2\,
\sqrt{\lambda_{\rm dim}(W^2)}
\int_{-1}^{1}dz\,\frac{1}{2\pi}
\int_0^{2\pi}d\phi_*\,\mathcal L_{00},
\]
with
\[
\lambda_{\rm dim}(W^2)=
\frac{[W^2-(m_{\chi_1}+m_s)^2]
      [W^2-(m_{\chi_1}-m_s)^2]}{W^4},
\]
\[
W_{\min}^2=(m_{\chi_1}+m_s)^2,
\qquad
W_{\max}^2=m_{\chi_1}^2+
2p_{\chi_1}\sqrt{2m_AE_R+E_R^2}
-2(E_{\chi_1}+m_A)E_R.
\]
The target-rest-frame time component Gamma^0 includes both scalar-emission diagrams and their interference. The initial-spin average 1/2 is included once. The azimuthal weights are divided by 2 pi.

For the full-cross-section audit, the default W^2 mapping is threshold-regularized:
\[
u=\frac{x+1}{2},\qquad
W^2=W_{\min}^2+(W_{\max}^2-W_{\min}^2)u^2,
\qquad
dW^2=2(W_{\max}^2-W_{\min}^2)u\,du.
\]
The dimensionless Kallen factor is evaluated in the stable form
\[
\lambda_{\rm dim}
=\frac{\Delta W^2(4m_{\chi_1}m_s+\Delta W^2)}{W^4},
\qquad \Delta W^2=W^2-W_{\min}^2.
\]
This avoids subtracting nearly equal squared masses at the threshold. The old linear-W^2 mapping remains available only as a diagnostic through \texttt{--w2-mapping linear_w2}; the production default is \texttt{threshold_u2}.

The Wolfram Language runner reconstructs the boosted three-body four-momenta and evaluates the 4x4 Dirac trace. It does not import Python I6 values. It reads only the already archived native AFH response table. The Python comparator independently recomputes the same integral with \texttt{phase_space_convergence.integrate_i6}, using the mapping recorded in the Mathematica CSV.

## 3. Cross-section assembly and factor-four ledger

\[
R_A^{\rm package}(q)=\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}(q),
\qquad
C_0=\frac{A^2}{4R_A^{\rm package}(0)},
\]
\[
R_A^{\rm phys}(q)=4C_0R_A^{\rm package}(q),
\qquad R_A^{\rm phys}(0)=A^2.
\]
C0 removes only the small overall offset from the finite-decimal AFH density-matrix entries; it is not a second isospin factor.

\[
\frac{d\sigma_A}{dE_R}=
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2}
\frac{R_A^{\rm phys}(E_R)}
{(m_V^2+2m_AE_R)^2}
I_6(v,E_R).
\]
The per-nucleon gVN remains in the particle-physics prefactor. Thus the physical response carries the factor four exactly once. A no-factor-four control uses R_A^phys/4; at every open point its cross section must be exactly one quarter of the physical result.

The response uses exact spatial q = sqrt(2 m_A E_R + E_R^2); the mediator propagator uses t = -2 m_A E_R. They are not interchangeable.

## 4. Files and execution

- run_afh_eq6_full_dsigma.wls: native Wolfram Language implementation of I6 and d sigma/dER.
- compare_full_dsigma_mathematica.py: independent Python recomputation using eq6_kernel.py and SciPy PCHIP.
- afh_default_xe131_WM00_mathematica.csv: fixed 2401-node native AFH response input.

Full-grid command from the repository root:

~~~powershell
wolframscript -file research/afh_default_density_xe131/run_afh_eq6_full_dsigma.wls --nw 16 --nz 16 --nphi 8 --w2-mapping threshold_u2 --width-scheme pole
python research/afh_default_density_xe131/compare_full_dsigma_mathematica.py --mathematica-csv research/afh_default_density_xe131/output/full_dsigma_mathematica/mathematica_full_dsigma_xe131.csv --out-csv research/afh_default_density_xe131/output/full_dsigma_mathematica/pointwise_comparison.csv --metadata research/afh_default_density_xe131/output/full_dsigma_mathematica/comparison_metadata.json
~~~

High-order anchor example:

~~~powershell
wolframscript -file research/afh_default_density_xe131/run_afh_eq6_full_dsigma.wls --benchmark green_ms300_dm1 --er-list-kev 200,300,500 --nw 48 --nz 40 --nphi 24 --w2-mapping threshold_u2 --width-scheme pole --out-csv research/afh_default_density_xe131/output/full_dsigma_mathematica/green_high_order.csv
~~~

The Python comparator must be run on each Mathematica output. The full grid uses 16x16x8; high-order anchors assess quadrature convergence separately. Agreement between codes at one order is not itself a convergence test.

## 5. Acceptance criteria

1. R_A^phys = 4 C0 R_A^package passes at all 2401 archived q nodes.
2. Wolfram and Python I6 values agree point by point at identical benchmark, recoil, width prescription and quadrature orders.
3. Full d sigma/dE_R values agree point by point, with the AFH interpolation independently compared.
4. Factor-four response and physical/no-factor-four cross-section ratio residuals are below 2e-12.
5. The chi2 pole clearance remains positive at every open point in the fixed-speed scan.
6. High-order anchors demonstrate quadrature convergence separately.

The comparator defaults to 2e-7 relative tolerance for I6 and d sigma/dE_R, 2e-10 for AFH PCHIP response, and 2e-12 for q, C0, unit conversion, and factor-four identities. It also compares the no-factor-four control against the independently recomputed Python cross section divided by four.

An earlier preflight reported a 4.11e-5 difference between the linear-W^2 kernel and one historical archived I6 value. This is not evidence of an AFH normalization error. The new full audit therefore uses threshold_u2 by default and will re-evaluate that point against a matched high-order reference; the source of the historical-grid difference remains open until the native run is available.

## 6. Scientific status

| Item | Status |
|---|---|
| AFH v6.0 Xe-131 response, native Mathematica vs Python, 2401 q nodes | **PASS** |
| AFH factor-four convention and C0 separation | **PASS at response level** |
| Wolfram Language full I6 implementation | **Prepared; not yet executed** |
| Full d sigma/dE_R, Mathematica vs Python | **Not yet validated** |
| Constant pole width | **Conditional Dirac / scalar-only assumption** |
| Natural-xenon continuous AFH spectrum and LZ likelihood | **Outside this audit** |

No native full-cross-section run, output CSV, or pointwise Mathematica–Python PASS is claimed until the Wolfram runner has completed and the generated artifacts have been compared.


## 7. P0 response-definition reconciliation and P1 recoil-grid plan — 2026-11-15

### P0: response convention now explicit in both manuscript and runner

For the finite-decimal Xe-131 AFH table, the numerical response used by the full-cross-section runner is
\[
R_A^{\rm phys}(q)=4C_0R_{A,\rm package}^{00}(q),\qquad
C_0=\frac{A^2}{4R_{A,\rm package}^{00}(0)}.
\]
The manuscript now states this same convention. For the archived Xe-131 input,
\(R_{A,\rm package}^{00}(0)=4289.895955714993\) and
\(C_0=1.0000825298069378\). The factor four is the AFH isoscalar-to-equal-\(p,n\)
coupling conversion; \(C_0\) is only a \(q\)-independent correction for the
finite decimal precision of the tabulated density matrix. In the exact
unrounded-matrix limit, \(C_0=1\).

The Mathematica four-momentum reconstruction now evaluates
\[
\cos\theta_q=
\frac{2m_{\chi_1}m_s+m_s^2+\Delta W^2+
2(E_{\chi_1}+m_A)E_R}{2p_{\chi_1}Q},
\qquad
\Delta W^2=W^2-W_{\min}^2,
\]
rather than forming \(W^2-m_{\chi_1}^2\) from two large nearly equal
quantities. This is algebraically equivalent to the original expression and
matches the threshold-stable Python construction. No new numerical result is
claimed from this source-level stabilization.

### P1: 5-keV versus 1-keV \(E_R\) grid

The new local PowerShell runner is run_afh_er_grid_convergence.ps1; the
comparison utility is compare_er_grid_convergence.py. Both use the same four
fixed-speed benchmarks, Xe-131 \(m_A=131u\), \(m_{\chi_1}=1\) TeV,
\(m_V=10\) GeV, \(v=800\) km/s, \((g_1g_2g_{VN})^2=10^{-8}\),
\(g_2=1\), constant pole width, threshold-\(u^2\) mapping, and
\((n_W,n_z,n_\phi)=(16,16,8)\).

- Coarse grid: \(E_R=5,10,\ldots,800\) keV (160 points per benchmark).
- Fine grid: \(E_R=5,6,\ldots,800\) keV (796 points per benchmark).
- The AFH 2401-node response table is reused; AFH is not rerun.
- Each Mathematica grid is independently compared point by point with Python
  before the two recoil grids are compared.
- The two grids must agree at every shared 5-keV node. The energy-grid
  comparison then evaluates the integrated fixed-speed \(d\sigma_A/dE_R\)
  area, the peak height and location, and the three AFH response minima
  windows \(85\!-\!120\), \(250\!-\!290\), and \(525\!-\!565\) keV.
- The acceptance thresholds are: common-node \(I_6\) and \(d\sigma/dE_R\)
  relative differences \(\le 2\times10^{-7}\); response interpolation
  differences \(\le 2\times10^{-10}\); \(C_0\) and factor-four identity
  residuals \(\le 2\times10^{-12}\); integrated-area difference
  \(\le 10^{-3}\); peak-height difference \(\le 5\times10^{-3}\).
  Peak and response-minimum locations are reported as diagnostics rather
  than silently forced to agree.
- Near the three AFH response minima, a 1-keV \(E_R\) step maps to
  approximately \(0.773\), \(0.476\), and \(0.334\) MeV in spatial
  momentum \(Q\), respectively. These are larger than the native
  \(0.25\)-MeV \(q\)-grid spacing. Thus 1 keV is the first fine-grid
  comparison, not an assumption that the response minima are fully resolved;
  if their positions/depths remain grid-sensitive, perform a local
  0.5-keV (or finer, if needed) refinement around the affected minimum.

Run from the repository root on the Windows machine with Wolfram Engine and
Python available:

~~~powershell
.\research\afh_default_density_xe131\run_afh_er_grid_convergence.ps1
~~~

The runner writes both native Mathematica CSVs and metadata, both independent
Python pointwise comparison CSVs and metadata, and the final 5-keV/1-keV
summary under
research/afh_default_density_xe131/output/er_grid_convergence_2026-11-15/.

A separate high-order quadrature anchor remains necessary: run the existing
green benchmark at \(E_R=200,300,500\) keV with
\((n_W,n_z,n_\phi)=(48,40,24)\), then compare those values with the
\(16\times16\times8\) results. Recoil-grid convergence and
\(W^2,z,\phi_*\) quadrature convergence are separate acceptance questions.

**Execution status:** source, manuscript normalization, runner and comparison
utility are prepared and committed. The native Mathematica 5-keV and 1-keV
full-grid runs, their Python pointwise comparisons, and the P1 numerical
acceptance remain pending. No PASS is claimed until those local outputs and
their provenance are archived.
