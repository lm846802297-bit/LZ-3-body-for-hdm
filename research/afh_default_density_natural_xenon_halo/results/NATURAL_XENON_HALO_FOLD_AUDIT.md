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

## Exact-spatial-q reproduction acceptance

The default exact_spatial calculation was rerun and compared against the archived selected-point halo-fold tables. The archived samples use the same exact spatial AFH momentum, so this is a direct numerical reproduction rather than a change of response convention.

- Workflow run: [43044583357](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43044583357), PASS.
- 98 isotope-contribution rows and 14 total-rate rows compared.
- Comparison tolerance: \(5\times10^{-8}\) relative.
- Maximum relative difference in any isotope contribution: \(4.32\times10^{-10}\).
- Maximum relative difference in the 14 total rates: \(2.67\times10^{-12}\).
- The NR approximation guard was also checked: the code refuses to reuse exact-q response values under nr_approx.

Machine-readable comparison summary: results/exact_spatial_reproduction_comparison.json. The full recomputed output and metadata are retained in the CI artifact named afh-natural-xenon-exact-spatial-reproduction.

This confirms that the exact AFH spatial-q baseline is reproducible. The NR-q option remains a separate small-recoil approximation; it is not required to repair or regenerate the existing selected-point rates.
