# Full-current impact on the old W_M-only baseline

**Status:** fixed-speed three-body current contraction completed. The matched-\(c_M\)
Xe-131 charge ratios are updated below. The signed spatial-interference
contribution remains provisional pending direct P3 phase validation, and
the natural-xenon halo fold remains gated on native seven-isotope/eight-response
AFH acceptance.

## 1. Three-body current validation

Workflow run **44243258167** completed the full-current Dirac/Pauli contraction
job successfully. The independent phase-space component convergence job
passed at the selected nine stress benchmarks:

- final Gram Frobenius difference: (1.50\times10^{-8});
- final Lorentz-tensor Frobenius difference: (1.50\times10^{-8});
- active-component difference: (1.57\times10^{-5});
- point-nucleus contraction difference: (1.51\times10^{-8}).

The full-current artifact contains 84 isotope/width contractions
(7 isotopes × 12 width benchmarks), all with positive total kernels under
the current candidate \(C_{\Sigma'\Delta}\) sign. The AFH source audit confirms
the response-operator ordering but not the particle-side relative phase, so
the quoted spatial fraction remains provisional until the direct P3
covariant-versus-AFH spherical-multipole comparison.

The maximum spatial-current fraction in those contractions is
[
\boxed{
\max |R_{\rm spatial}/R_{\rm charge}|
=7.10\times10^{-9}
}
]
and occurs in the near-pole (E_R=267) keV, (g_2=1) benchmark.
At (E_R=200) keV the maximum is (6.95\times10^{-12}).

Therefore, **for the tested pointlike nucleon-current benchmark, the
(Delta,Sigma',Sigma'') sector is numerically negligible.**

## 2. Do not mix the provisional seven-isotope result with native Xe-131

The fixed-speed seven-isotope contraction uses the Python AFH translation.
Its pointlike (M+Phi'') charge correction is approximately

- (-0.384%) at (E_R=200) keV;
- (-0.606%) at (E_R=267) keV.

Those are regression outputs, not final natural-xenon predictions.

For Xe-131, the AFH (M,Phi'',MPhi'') response grid has an independent
native Mathematica pointwise validation over all 2401 (q)-nodes, with
maximum scaled differences below (3.8\times10^{-9}),
(9.1\times10^{-10}), and (3.6\times10^{-11}) for the three responses.

The native grid varies rapidly near the (W_M) cancellation, so the exact
(q_A) corresponding to each recoil energy must be used.

## 3. Historical Xe-131 charge-sector normalization diagnostic

**This section records the legacy \(F_1^2\)-normalization calculation. Its
\(-21.48\%\) and \(-34.24\%\) full-charge values are superseded by the
matched-\(c_M\) fixed-speed ratios in the update below.**

Using the AME2020/CODATA-2022 bare Xe-131 nuclear mass
(m_A=121.9099224472) GeV:

### (E_R=200) keV

[
q_A=0.2208257435 {\rm GeV},qquad
Q_A^2=0.0487640090 {\rm GeV}^2.
]

Native AFH interpolation gives
[
\frac{W_{\Phi''}}{W_M}=0.0369557,qquad
\frac{W_{M\Phi''}}{W_M}=-0.1912071.
]

The central finite-(t_N) form-factor diagnostic gives
[
F_1^V=2.66316,qquad F_2^V=-0.46805,
]
[
c_M=2.65122,qquad c_{\Phi''}=0.023883,qquad
eta=0.0090083.
]

Hence
[
Q_{\Phi''}-1=-0.344%
]
relative to the finite-(t_N) (M)-only charge term, while the total charge
sector relative to the old pointlike (F_1^V(0)^2W_M) baseline is
[
\boxed{-21.48\%}.
]

For the pointlike (F_1^V=3,F_2^V=-0.552) benchmark, the explicit
(Phi'') correction alone is only
[
\boxed{-0.335\%}.
]

### (E_R=267) keV: (W_M) cancellation region

[
q_A=0.2551469574 {\rm GeV},qquad
Q_A^2=0.0650999699 {\rm GeV}^2.
]

Native AFH interpolation gives
[
\frac{W_{\Phi''}}{W_M}=19.6361,qquad
\frac{W_{M\Phi''}}{W_M}=-4.23930.
]

The central finite-(t_N) diagnostic gives
[
F_1^V=2.56389,qquad F_2^V=-0.44977,
]
[
c_M=2.54852,qquad c_{\Phi''}=0.030726,qquad
eta=0.0120564.
]

Now
[
Q_{\Phi''}-1=-9.94\%
]
relative to the finite-(t_N) (M)-only charge term.

Even with the pointlike nucleon current, the explicit (Phi'') term is
already
[
\boxed{-9.68\%}
]
relative to pointlike (M)-only.

Including the central finite-(t_N) charge normalization, the total charge
sector becomes
[
\boxed{
\frac{R_{\rm charge}^{\rm finite-t_N}}
{R_{M,\rm pointlike}}-1
=-34.24\%.
}
]

This is a **Xe-131 result at one exact recoil point**, not a natural-xenon
spectrum.

### Updated matched-\(c_M\) fixed-speed Xe-131 ratio

The latest fixed-speed result uses native AFH \(M,\Phi'',M\Phi''\) responses,
the matched Darwin--Foldy charge coefficient
\[
c_M=F_1^V+\frac{t_N(F_1^V+2F_2^V)}{8m_N^2},
\]
the corresponding \(c_{\Phi''}\), and coherent \(M-\Phi''\) interference.
The denominator is the original pointlike \(9W_M\) baseline. For
\(m_{\chi_1}=1\) TeV, \(m_s=300\) keV, \(g_2=1\), and
\(v=776\) km/s:

| \(E_R\) | \(\Delta m\) | Ratio | Change |
|---:|---:|---:|---:|
| 200 keV | 450 keV | 0.7783093394 | -22.1691% |
| 267 keV | 362 keV | 0.6492159107 | -35.0784% |

At these exact points, the earlier \(-21.48\%\) and \(-34.24\%\) values
are legacy \(F_1^2\)-normalization diagnostics. The matched-\(c_M\) results
above supersede them for the coherent finite-\(t_N\) charge ratio. This is a
fixed-speed Xe-131 Coulomb-sector result, not an absolute cross section,
natural-xenon halo average, or complete eight-response prediction. Workflow
[44264272807](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44264272807)
reproduced the ratios with an uploaded artifact.

## 4. Physical hierarchy

The calculation now establishes three separate effects:

| Effect | Size in tested calculation | Status |
|---|---:|---|
| Spatial (Delta,Sigma',Sigma'') | (<7.1\times10^{-9}) of charge | Numerically negligible in fixed-speed benchmarks |
| Pointlike (Phi'') | (-0.335%) at 200 keV; (-9.68%) at 267 keV for native Xe-131 | Strongly recoil-dependent near (W_M) minima |
| Finite-\(t_N\) coherent charge | \(-22.1691\%\) at 200 keV; \(-35.0784\%\) at 267 keV using matched \(c_M\) and coherent \(M+\Phi''\) | Current fixed-speed Xe-131 result; not a halo-folded spectrum |

Thus the main correction to the old (W_M)-only construction is **not**
the spatial nuclear current. The important corrections are the finite-(t_N)
coherent charge and, near a deep (W_M) cancellation, the (Phi'') charge
response.

## 5. What is still required before quoting the final natural-xenon spectrum

The following must still be kept separate:

1. **Native AFH response:** Xe-131 (M,Phi'',MPhi'') is fully pointwise
   validated; the other naturally abundant isotopes still need the same
   native validation if their responses are to support a final spectrum.
2. **Finite-(t_N) form factors:** the present central diagnostic combines
   Bishara (F_1) slopes with the Borah--Hill--Lee--Tomalak isoscalar
   electromagnetic z expansion and holds (F_2^s(Q^2)) at its zero-momentum
   value. A single validated universal (u+d+s) finite-(Q^2) input is still
   needed.
3. **Halo folding:** the final (dR/dE_R) must integrate the exact
   three-body phase-space tensor over the halo speed distribution for every
   isotope.
4. **No extrapolation from the deep minimum:** neither the legacy
   \(-34.24\%\) nor the updated \(-35.0784\%\) fixed-speed Xe-131 point can be
   used as a global spectrum percentage.
5. **Spatial sign:** the candidate \(C_{\Sigma'\Delta}\) sign remains
   provisional until the direct P3 covariant-versus-AFH phase comparison passes.

Therefore the final natural-xenon statement remains:

[
\boxed{
\text{spatial-current correction is negligible, but the complete}
\quad
W_M\to\text{full natural-xenon spectrum}
\quad
\text{is not yet numerically closed.}
}
]
