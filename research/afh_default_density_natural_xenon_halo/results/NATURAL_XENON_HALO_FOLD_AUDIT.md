# AFH default-density natural-xenon halo fold

## Observable and formula

The isotope-specific cross section is evaluated first:

\[
\frac{d\sigma_A}{dE_R} =
\frac{m_A (g_1g_2g_{VN})^2 R_A(E_R)}
{256\pi^3 p_{\chi_1}^2(m_V^2+2m_AE_R)^2}\,I_6.
\]

The natural-xenon differential rate is then

\[
\frac{dR}{dE_R} =
N_T\frac{\rho_\chi}{m_{\chi_1}}c
\sum_A x_A\int_{v_{\min,A}}^{v_{\max}}dv\,
f_{\rm lab}(v)\frac{v}{c}\frac{d\sigma_A}{dE_R}(v),
\quad
N_T=\frac{N_{\rm Av}1000}{\bar M_{\rm Xe}}.
\]

Each isotope has its own nuclear mass, AFH response and three-body threshold.
The abundance sum is not approximated by one average nuclear mass.

## Fixed inputs

- AFH: Anand–Fitzpatrick–Haxton, PRC 89 (2014) 065501, arXiv:1308.6288; DMFormFactor v6.0 built-in sdgXeA default densities.
- AFH default oscillator length:
  \(b_A=\sqrt{41.467/(45A^{-1/3}-25A^{-2/3})}\,\mathrm{fm}\).
- Available isotopes: Xe-128, 129, 130, 131, 132, 134, 136.
- NIST natural atom-fraction coverage: 0.998158. Xe-124 and Xe-126 (combined 0.001842) are omitted because the supplied AFH v6.0 response set has no corresponding built-in density matrices. Available abundances are not renormalized.
- Nuclear mass: \([M_{\rm atom}(A)-54m_e]u\), neglecting the small electronic binding energy. Target number per kg uses the NIST abundance-weighted mean atomic mass 131.2927614479 g/mol.
- \(m_{\chi_1}=1\) TeV, \(m_V=10\) GeV, \(g_2=1\), \((g_1g_2g_{VN})^2=10^{-8}\), \(\rho_\chi=0.3\) GeV/cm³.
- Pole width for \(\chi_2\to\chi_1s\), conditional on Dirac fermions, a real scalar, a pure scalar off-diagonal Yukawa and no other open channels.

## AFH spatial momentum and the non-relativistic recoil approximation

The AFH response functions are functions of

\[
y=\left(\frac{q b_A}{2}\right)^2,
\]

where \(q\) is the magnitude of the **spatial momentum transfer**. This is the definition used by the AFH formalism; see Fitzpatrick et al., JCAP 02 (2013) 004, arXiv:1203.3542, Sec. 4 and Sec. 7.

For a nucleus initially at rest, the exact mass-shell relation is

\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q),\qquad P'^2=P^2=m_A^2,
\]

which gives

\[
\boxed{q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}}.
\]

Therefore the exact AFH response argument used in this three-body calculation is

\[
\boxed{y_{\rm exact}=\frac{b_A^2}{4}(2m_AE_R+E_R^2)}.
\]

The familiar expression

\[
y_{\rm NR}=\frac{b_A^2m_AE_R}{2}
\]

follows from the small-recoil approximation \(E_R\ll m_A\), or \(q_{\rm NR}=\sqrt{2m_AE_R}\). We retain it as a controlled approximation, not as a mandatory replacement for the exact spatial momentum.

**The 28 archived AFH response samples use exact spatial q.** They are therefore the appropriate samples for the exact three-body mass-shell kinematics; they are not an erroneous or obsolete response set.

The q difference is very small: 0.032–0.409 keV across the 28 natural-xenon samples (0.20–1.14 ppm). Nevertheless, the AFH response can have a steep slope near its diffraction minima. On the 2401-point Xe-131 AFH grid, replacing exact q by q_NR changes the response at the four selected recoil points by a few to about 213 ppm for the NIST nuclear-mass convention. For the fixed-speed Figure-2 benchmark mass \(M_A=131u\), the corresponding NR-approximation response shifts are approximately 21.2, 5.48, 225.0 and 89.7 ppm at 101, 200, 267 and 542 keV, respectively.

These are response-level comparisons, not empirical corrections to the halo rate. The adopted calculation retains exact q.

Machine-readable comparisons:

- results/natural_xenon_q_convention_audit.csv: all 28 natural-xenon samples;
- results/xe131_afh_response_shift_NR_vs_exact.csv: Xe-131 with the NIST nuclear mass;
- results/xe131_fixed_benchmark_q_comparison.csv: Xe-131 with the fixed benchmark mass \(M_A=131u\);
- results/q_convention_audit_summary.json: machine-readable summary.

The exact invariant momentum transfer entering a mediator propagator is a separate object:

\[
t=(P'-P)^2=-2m_AE_R.
\]

Thus a propagator denominator \(m_V^2-t=m_V^2+2m_AE_R\) is compatible with exact spatial q; it must not be confused with \(q_{\rm exact}^2\).

The exact spatial q is used in the AFH response interpolation, the three-body phase-space construction, \(W_{\max}\), and \(v_{\min}\). The NR relation remains available only as a documented approximation.

## Halo prescriptions

1. Truncated SHM baseline: \(v_0=220\), \(v_E=232\), \(v_{\rm esc}=544\) km/s; \(v_{\max,\rm lab}=776\) km/s.
2. Untruncated boosted Maxwell–Boltzmann: same \(v_0,v_E\), integrated to 1600 km/s. This is a tail-sensitivity diagnostic, not the adopted physical default.

Both speed PDFs integrate to unity numerically.

## Numerical convergence

- Eq. (6) kernel: \(8\times8\times4\).
- Speed integral: 32-point Gauss–Legendre.
- Six representative kernel checks: \(8\times8\times4\) versus \(16\times16\times8\); maximum relative difference \(2.19\times10^{-4}\).
- Five representative speed checks: 32 versus 64 nodes; maximum relative difference \(3.31\times10^{-6}\).
- Preliminary \(4\times4\times2\) results differ from final \(8\times8\times4\) rates by 0.12–0.15% at open points and are not used as final values.

## Reproduction of the archived legacy exact-q rates

The q-separation refactor was checked by rerunning the complete selected-point halo fold with the explicit legacy option. The default manuscript-NR mode was separately verified to reject the archived exact-q response samples.

- Workflow run: [43040078335](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43040078335), PASS.
- 98 isotope-contribution rows and 14 total-rate rows compared.
- Comparison tolerance: \(5\times10^{-8}\) relative.
- Maximum relative difference in any isotope contribution: \(4.32\times10^{-10}\).
- Maximum relative difference in the 14 total rates: \(2.67\times10^{-12}\).

Machine-readable comparison summary: results/legacy_exact_reproduction_comparison.json. The full recomputed output and metadata are retained in the CI artifact named afh-natural-xenon-legacy-exact-reproduction.

This verifies that the new explicit q-convention handling preserves the old exact-q archive when legacy_exact is selected. It does not validate manuscript-NR samples or provide corrected NR-q rates.

## Results at \(E_R=101\) keV

Rates in events/(kg day keV), before detector response:

| Benchmark | Truncated SHM | Untruncated MB tail diagnostic |
|---|---:|---:|
| Red: \(m_s=200\) keV, \(\Delta m=1\) MeV | \(5.2810\times10^{-11}\) | \(8.6009\times10^{-11}\) |
| Green: \(m_s=300\) keV, \(\Delta m=1\) MeV | \(2.5995\times10^{-22}\) | \(1.3837\times10^{-12}\) |
| Black: \(m_s=360\) keV, \(\Delta m=1\) MeV | 0 (closed) | \(6.2236\times10^{-14}\) |
| Blue: \(m_s=300\) keV, \(\Delta m=10\) MeV | \(2.1675\times10^{-24}\) | \(1.1079\times10^{-14}\) |

At 101 keV, the isotope-specific minimum-speed ranges are:
- Red: 588.3–605.0 km/s; all seven available isotopes are open.
- Green/Blue: 775.8–798.3 km/s; only Xe-136 is open under the truncated SHM.
- Black: 888.3–914.2 km/s; no available isotope is open under the truncated SHM.

For Green/Blue, Xe-136 has \(v_{\min}=775.806\) km/s, only 0.194 km/s below the truncated-SHM endpoint. This explains the very small SHM rates at 101 keV. The untruncated MB diagnostic includes speeds above 776 km/s and consequently gives nonzero contributions from the other isotopes.

## Green benchmark at selected recoil energies

For \(m_s=300\) keV and \(\Delta m=1\) MeV:

| \(E_R\) [keV] | Truncated SHM | Untruncated MB tail diagnostic |
|---:|---:|---:|
| 101 | \(2.5995\times10^{-22}\) | \(1.3837\times10^{-12}\) |
| 200 | \(1.8136\times10^{-11}\) | \(1.6461\times10^{-10}\) |
| 267 | \(2.7271\times10^{-13}\) | \(1.7872\times10^{-12}\) |
| 542 | \(1.4561\times10^{-15}\) | \(8.1709\times10^{-14}\) |

These are selected points, not a continuous recoil spectrum. No \(b_A\) parameter is fitted to the dips.

## Interpretation and limits

- \(v=800\) km/s lies above the truncated-SHM endpoint 776 km/s. It is not a supported speed in this halo model. A fixed-speed \(d\sigma_A/dE_R\) curve and a halo-folded \(dR/dE_R\) are different observables.
- The untruncated MB result is a tail diagnostic; it is not treated as an equally preferred halo model.
- Xe-124 and Xe-126 are omitted without renormalization. Their missing rate is not assumed to equal exactly 0.1842% of the total.
- No detector efficiency, resolution, exposure, cuts, backgrounds, likelihood or annual modulation are included.
- Native Mathematica re-execution of AFH v6.0 remains pending. The response samples are from the source-translated AFH v6.0 built-in density-matrix table.
