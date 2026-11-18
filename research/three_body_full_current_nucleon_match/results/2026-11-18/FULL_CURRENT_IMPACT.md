# Full-current impact on the old W_M-only baseline

**Status:** fixed-speed three-body benchmark completed; natural-xenon halo-fold
with finite-t form factors is still a diagnostic, not the final spectrum.

## 1. What is now numerically established

Workflow run **44243258167** completed the full-current unit/Dirac-trace
job successfully. The independent phase-space component convergence job
reported PASS at the selected 9 benchmarks:
- final Gram Frobenius difference: (1.50\times10^{-8});
- final Lorentz-tensor Frobenius difference: (1.50\times10^{-8});
- active-component difference: (1.57\times10^{-5});
- point-nucleus contraction difference: (1.51\times10^{-8}).

The full-current artifact contains 84 isotope/width benchmark contractions
(7 isotopes × 12 width benchmarks), all with positive total kernels.

For the fixed-speed (E_R=200) keV, (v=776) km/s benchmarks, the
(M+\Phi'') charge correction relative to the pointlike (M) term is
about (-0.384\%). For the (E_R=267) keV near-pole benchmarks it is about
(-0.606\%). These values use the zero-momentum (F_1^V=3),
(F_2^V=-0.552) diagnostic.

The spatial-current contribution is much smaller:
[
\max |R_{\rm spatial}/R_{\rm charge}|
=7.10\times10^{-9}
]
over the 84 contracted rows. The largest values occur in the near-pole
(E_R=267) keV, (g_2=1) benchmark. At (E_R=200) keV the corresponding
maximum is (6.95\times10^{-12}).

Thus, **within the pointlike nucleon-current benchmark, adding
(\Delta,\Sigma',\Sigma'') does not measurably change the rate.**

## 2. The larger correction is finite-(t_N) nucleon structure

The above statement does **not** mean that the old (W_M)-only spectrum is
already complete. The old construction effectively uses
(F_1^V(0)=3) as a pointlike nucleon charge.

Using the central diagnostic finite-(t_N) form-factor model implemented in
`nucleon_vector_form_factors.py` gives a substantially different coherent
charge normalization.

For Xe-131 at (E_R=267) keV, with the AME2020/CODATA-2022 bare nuclear mass
(m_A=121.9099224472) GeV,
[
q_A=0.255146957\ {m GeV},\qquad Q_A^2=0.0651000\ {m GeV}^2.
]
The AFH 2401-node native-validated grid gives, after linear interpolation
between its exact 0.25-MeV nodes,
[
W_{\Phi''}/W_M=19.636056,\qquad
W_{M\Phi''}/W_M=-4.239298.
]

The central finite-(t_N) diagnostic gives
[
F_1^V=2.56389,\qquad
F_2^V=-0.44977,
]
[
c_M=2.54852,\qquad
c_{\Phi''}=0.03073,\qquad
\eta=0.012056.
]
Therefore
[
Q_{\Phi''}=1+2\eta\frac{W_{M\Phi''}}{W_M}
+\eta^2\frac{W_{\Phi''}}{W_M}
=0.900633,
]
so (\Phi'') changes the **finite-(t_N) (M)-only charge term** by
[
\boxed{-9.94\%}.
]

But relative to the old pointlike (F_1^V(0)^2W_M) baseline, the same
central diagnostic changes the coherent charge sector by
[
\boxed{-35.00\%}.
]

This is the important hierarchy:
[
|\delta_{\rm spatial}|\ll
|\delta_{\Phi''}|\ll
|\delta_{F_1(t_N)}|
]
for the present benchmark.

## 3. What this means for the natural-xenon spectrum

We can now separate the calculation into three layers:

| Layer | Physics | Current numerical status |
|---|---|---|
| A | pointlike (W_M)-only | Reproducible baseline |
| B | pointlike (M+\Phi'') | Completed at fixed-speed benchmarks; sub-percent correction at 200--267 keV |
| C | spatial (\Delta,\Sigma',\Sigma'') | Completed at fixed-speed benchmarks; (<7.1\times10^{-9}) of charge |
| D | finite-(t_N) (F_1,F_2) charge | Central diagnostic gives roughly 22% suppression at 200 keV and 28% suppression near 267 keV |
| E | full natural-xenon halo-fold with validated finite-(t_N) form factors | **Pending** |

The dominant unresolved change to the original (W_M)-only spectrum is
therefore **not** the spatial spin/orbital response. It is the finite-(t_N)
nucleon form factor. Near a deep (W_M) cancellation, the native Xe-131
(Phi'') term itself can also become an O(10%) charge-sector correction,
so the provisional O(1%) seven-isotope number must not be extrapolated to
natural xenon.

## 4. Important boundary

The finite-(t_N) numbers above are not yet the final prediction. Bishara
et al. provide the flavor-separated (F_1) slopes and zero-momentum (F_2)
inputs, while the central diagnostic combines these with the isoscalar
electromagnetic z expansion of Borah et al. The strange (F_2(Q^2)) input is
held at its zero-momentum value. A final spectrum therefore still requires
a single validated finite-(Q^2) form-factor prescription for the universal
(u+d+s) current.

Likewise, the seven-isotope AFH spatial-response database used in the fixed
speed contraction remains the Python AFH translation; native Mathematica
pointwise validation is currently complete for the Xe-131
(M,\Phi'',M\Phi'') grid, not for all seven isotopes.

Accordingly, **the complete natural-xenon percentage change is not yet being
declared as a final number**. What is already established is the hierarchy
of corrections and the negligible size of the spatial-current sector in the
tested three-body benchmarks.
