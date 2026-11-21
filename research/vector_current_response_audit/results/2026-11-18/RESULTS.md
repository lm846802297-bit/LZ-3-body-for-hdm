# Exact four-component vector-current audit

**Status:** reproducible diagnostic; AFH spin/orbital response contraction remains open.

## 1. What was calculated

The existing Eq. (6) implementation evaluates only the temporal mediator vertex
\(\Gamma^0\), and hence only \(L^{00}\). This audit constructs all four
components of the same coherent two-diagram current,

\[
\Gamma^\mu =
\gamma^\mu\frac{\slashed p-\slashed k_s+m_{\chi_2}}{D_{\rm before}}
+
\frac{\slashed p'+\slashed k_s+m_{\chi_2}}{D_{\rm after}}\gamma^\mu,
\qquad \mu=0,1,2,3,
\]

and forms

\[
L^{\mu\nu}=\frac12{\rm Tr}\left[
(\slashed p'+m_{\chi_1})\Gamma^\mu
(\slashed p+m_{\chi_1})\bar\Gamma^\nu
\right].
\]

Both scalar-emission orderings and their interference are retained. The
phase-space integral uses the same Eq. (6) \(\sqrt{\lambda_K}/W^2\) weight,
with threshold-\(u^2\) or endpoint-clustered \(\sin^2\) mapping.

For the coherent elastic comparison, the nuclear current is represented by the
coherent point-charge-current benchmark

\[
J_A^\mu=(P+P')^\mu F_A(q_A^2),\qquad
J_A^\mu/F_A=(2m_A+E_R,\boldsymbol q_A).
\]

The form factor is factored out. This current includes nuclear
centre-of-mass convection, but **not** internal nucleon orbital or
magnetization currents.

## 2. Numerical result

All masses and momenta are in GeV internally. The fixed-speed Xe-131
diagnostics use \(m_{\chi_1}=1\) TeV, \(m_A=131u\),
\(u=0.93149410242\) GeV and \(v=776\) km/s. The supplied 450-keV benchmark
uses \(m_s=300\) keV, \(\Delta m=450\) keV and \(E_R=200\) keV. The
near-pole stress point uses \(m_s=300\) keV, \(\Delta m=362\) keV and
\(E_R=267\) keV.

| Benchmark | \(g_2\) | Pole clearance \(m_{\chi_2}-W_{\max}\) | Conditional \(\Gamma_{\chi_2}\) | \(I_{00}^{\rm pole}/I_{00}^{0}\) | \(r_\chi=\sqrt{(I_{11}+I_{22}+I_{33})/I_{00}}\) (pole) | \(J_A L J_A/(J_A^0)^2L^{00}\) |
|---|---:|---:|---:|---:|---:|---:|
| \(\Delta m=450\) keV, \(E_R=200\) keV | 1 | 102.535 keV | 53.382 keV | 0.951956 | \(2.48632\times10^{-3}\) | 0.999995652 |
| \(\Delta m=1\) MeV, \(E_R=200\) keV | 1 | 652.535 keV | 151.824 keV | 0.988779 | \(2.48666\times10^{-3}\) | 0.999995666 |
| \(\Delta m=362\) keV, \(E_R=267\) keV | 0.1 | 0.828984 keV | 0.322437 keV | 0.987276 | \(2.46793\times10^{-3}\) | 0.999994872 |
| \(\Delta m=362\) keV, \(E_R=267\) keV | 1 | 0.828984 keV | 32.2437 keV | 0.0578622 | \(2.47030\times10^{-3}\) | 0.999994968 |

Here \(r_\chi\) is a target-rest-frame spatial-current norm, not a Lorentz
invariant. It corresponds to a spatial-to-temporal amplitude scale of about
\(2.47\times10^{-3}\), or a squared norm of about \(6.1\times10^{-6}\).

The width scan shows two distinct effects:

- The \(\chi_2\) width can change the *normalization* of the temporal
  three-body kernel substantially. In the deliberately near-pole
  \(g_2=1\) stress point, the pole-width prescription changes \(I_{00}\)
  by about \(-94.2\%\) relative to zero width.
- The relative size of the dark-matter spatial current changes much less:
  the largest shift in this set is about \(9.6\times10^{-4}\) relative
  (0.096%) in \(r_\chi\). Thus the \(\chi_2\) pole and scalar emission do
  not make the spatial DM current comparable to its temporal component
  in these benchmarks.

The coherent point-charge-current contraction differs from the charge-only
contraction by roughly 4.3--5.1 ppm. The pure nuclear-CM spatial-square term
is only \(4.7\)--\(6.6\times10^{-12}\) of the charge term; the leading
few-ppm correction is the charge--spatial interference. This is a result
for the coherent point-charge-current benchmark only.

The zero, pole, and running entries are all retained in
vector_current_response_audit.csv. The running-width prescription is a
diagnostic ansatz, not a full \(\chi_2\) self-energy. The pole width is
conditional on the existing Dirac / real-scalar / pure-scalar /
single-open-channel \(\chi_2\to\chi_1s\) assumptions.

## 3. What this says about spin and orbital responses

The nonrelativistic one-nucleon vector current has the schematic form
\[
J_N^0\simeq 2m_NF_1,\qquad
\frac{\boldsymbol J_N}{J_N^0}\simeq
\frac{\boldsymbol p_N+\boldsymbol p_N'}{2m_N}
+\frac{F_1+F_2}{2m_NF_1}\,
 i\boldsymbol\sigma_N\times\boldsymbol q_A.
\]
The second term is the magnetization current; the first is the convection
current. Using the computed \(r_\chi\simeq2.47\times10^{-3}\):

- For an internal nucleon speed \(v_N=0.1\)--\(0.3\), the
  **per-nucleon kinematic amplitude factor** is
  \(r_\chi v_N\simeq2.5\times10^{-4}\)--\(7.5\times10^{-4}\).
- For a minimal point-Dirac nucleon with \(F_1=1,F_2=0\), the
  magnetization factor is \(r_\chi Q_A/(2m_N)\). It is about
  \(2.9\times10^{-4}\) at 200 keV and \(3.36\times10^{-4}\) at
  267 keV for the Xe-131 mass convention used here.

These are **kinematic factors per nucleon**, not nuclear-response ratios.
They do not include the AFH matrix elements, possible cancellations,
coherence factors, or the baryon-current Pauli form factor. In particular,
the electromagnetic nucleon magnetic moments must not be inserted as if
they were automatically the form factors of the model's universal quark
vector current.

The AFH v6.0 source provides the relevant response channels through
ResponseNuclear[y,2,0,0] (\(\Sigma''\)),
ResponseNuclear[y,3,0,0] (\(\Sigma'\)), and
ResponseNuclear[y,6,0,0] (\(\Delta\)), in addition to
ResponseNuclear[y,1,0,0] (\(M\)). The currently archived Xe-131 and
natural-xenon response grids validate the \(M\) response, not yet the
three-body contraction with \(\Sigma'\), \(\Sigma''\), and \(\Delta\).

This distinction matters especially near a diffraction minimum of
\(W_M^{00}\): even a small absolute spin/orbital contribution can become
relatively visible where the coherent charge response is suppressed.
Therefore this audit does **not** prove that the complete Xe recoil spectrum
is \(W_M^{00}\)-only.

## 4. Acceptance checks

- The new \(\Gamma^0\) component reproduces the existing eq6_kernel.spin_trace
  result to relative precision below \(2\times10^{-13}\) at the regression
  point, with both zero and pole width.
- \(L^{\mu\nu}\) is Hermitian and positive semidefinite within numerical
  tolerance.
- The coherent point-charge current obeys \(q_{A\mu}J_A^\mu=0\).
- The decomposition into charge, spatial-square and charge--spatial
  interference pieces reproduces the full contraction.
- The supplied 450-keV benchmark is stable under quadrature refinement:
  the 24x16x8 result for the pole-width \(I_{00}\) differs from the
  48x32x16 reference by less than \(10^{-10}\) relative.
- The near-pole \(\sin^2\)-mapped \(W^2\) integral is stable under
  \(n_W=32\to48\) at fixed \(n_z=16,n_\phi=8\); see
  quadrature_convergence.csv.

## 5. Conclusions and remaining work

1. The existing \(W_M^{00}\)-only approximation is excellent for the
   **coherent point-nucleus current**: omitted centre-of-mass convection
   changes the result by only a few ppm.
2. The exact three-body dark-matter spatial current is about
   \(2.5\times10^{-3}\) of the temporal current in the scanned benchmarks.
   The \(\chi_2\) width can strongly affect the absolute kernel near a pole,
   but changes this current ratio by at most about \(0.1\%\) in the scan.
3. This does not settle the internal nuclear spin and orbital responses.
   Their AFH multipole matrix elements must be evaluated and contracted with
   the phase-space-dependent \(L^{\mu\nu}\), especially near \(W_M^{00}\)
   minima. Until that is done, retain \(W_M^{00}\) as the baseline but do not
   claim the other responses are negligible.


## 6. Exact-source reproduction evidence

GitHub Actions workflow run 44170287270 executed the committed code at
source revision 28ff13722b7b33ba6145fb7caa3548c365f086e5 using Python 3.13.18
and NumPy 2.3.5.

- Python compilation: passed.
- Unit and regression tests: 8/8 passed.
- Full 12-row width/current scan: completed.
- Independent temporal-integral cross-checks against
  phase_space_convergence.py: passed at zero and pole width.
- Archived-versus-regenerated 12-row numerical comparison: exact agreement
  at the printed CSV precision; maximum relative difference 0.
- The workflow artifact contains the regenerated CSV, metadata, and SHA-256
  file. The archived CSV uses LF line endings so its byte-level SHA-256 is
  reproducible from the script.

This validates the code paths and numerical diagnostics described above.
It does not validate the omitted AFH \(\Sigma'\), \(\Sigma''\), or \(\Delta\)
nuclear matrix elements.
