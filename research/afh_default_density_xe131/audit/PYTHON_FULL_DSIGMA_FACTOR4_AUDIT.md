# Python-only Xe-131 full differential-cross-section and factor-four audit

## Status and ordering

This is the Python-first stage of the full Eq. (6) cross-section validation. It
does **not** invoke Mathematica or Wolfram. The native Mathematica full
cross-section calculation remains the final independent cross-code check and
must not block this Python calculation, the normalization audit, or the
natural-xenon halo work.

The runner is:

- **run_python_full_dsigma_xe131.py**
- regression tests: **tests/test_python_full_dsigma_xe131.py**
- response input: **output/afh_default_xe131_WM00.csv**
- output: **output/python_full_dsigma/**

The response input is the existing 2401-node AFH v6.0 source-translated Python
table. It is not recalculated by this runner. The AFH response layer already
has its separate native Mathematica/Python 2401-node audit.

## Differential cross section

For the fixed-speed Xe-131 Figure-2 benchmark, the Python calculation uses

\[
\frac{d\sigma_A}{dE_R}
=
\frac{m_A(g_1g_2g_{VN})^2}
{256\pi^3p_{\chi_1}^2(m_V^2+2m_AE_R)^2}
R_A^{\rm phys}(q)\,I_6(v,E_R),
\]

with

\[
I_6=
\int_{W_{\min}^2}^{W_{\max}^2}dW^2\,
\sqrt{\lambda_{\rm dim}(W^2)}
\int_{-1}^{1}dz\,
\frac{1}{2\pi}\int_0^{2\pi}d\phi_*\,
\mathcal L_{00}.
\]

The Python implementation uses phase_space_convergence.integrate_i6, the
threshold-regularized \(W^2=W_{\min}^2+\Delta W^2u^2\) mapping, and the
existing Dirac spin-trace implementation. The spin average is already
included once in eq6_kernel.spin_trace; the azimuthal average is already
included once in integrate_i6.

The four archived benchmark parameter sets are retained. The primary
fixed-speed comparison uses \(m_{\chi_1}=1\) TeV, \(m_A=131u\),
\(m_V=10\) GeV, \(v=800\) km/s,
\((g_1g_2g_{VN})^2=10^{-8}\), and \(g_2=1\) to factorize the conditional
pole-width prescription. The width assumes Dirac fermions, a real scalar,
a pure scalar off-diagonal Yukawa, and \(\chi_2\to\chi_1s\) as the only open
decay channel. It is not a complete vector-plus-scalar self-energy.

## AFH normalization and factor-four ledger

The AFH package response is

\[
R_A^{\rm package}(q)=
\frac{4\pi}{2J_A+1}W_{M,\rm AFH}^{00}(q),
\qquad
R_A^{\rm package}(0)\simeq\frac{A^2}{4}.
\]

The small \(q=0\) offset is caused by the finite-decimal AFH density-matrix
entries. Define only the corresponding shape-normalization correction

\[
C_0=\frac{A^2}{4R_A^{\rm package}(0)}
\simeq 1.00008252980694.
\]

For equal physical proton and neutron couplings, the coherent charge is \(A\),
so the physical response is

\[
\boxed{R_A^{\rm phys}(q)=4C_0R_A^{\rm package}(q)},
\qquad
R_A^{\rm phys}(0)=A^2.
\]

The implementation checks this identity at all 2401 AFH grid nodes and at
every interpolated recoil point. **The factor four appears here once.** The
cross-section prefactor retains the per-nucleon coupling \(g_{VN}\); it does
not contain another factor four.

A control calculation uses \(R_A^{\rm phys}/4\) with every other input fixed.
It must satisfy

\[
\frac{(d\sigma_A/dE_R)_{\rm phys}}
     {(d\sigma_A/dE_R)_{\rm no\ factor\ four}}=4
\]

at every kinematically open point. This control is an algebraic ledger, not a
fit to another calculation.

## Momentum and unit conventions

The AFH response uses the exact spatial momentum

\[
q_{\rm spatial}=\sqrt{2m_AE_R+E_R^2}.
\]

The mediator propagator uses the invariant transfer

\[
t=(P'-P)^2=-2m_AE_R,
\qquad
(m_V^2-t)^2=(m_V^2+2m_AE_R)^2.
\]

These are distinct quantities and are kept distinct in the runner.

The output reports \(d\sigma/dE_R\) in GeV\(^{-3}\) and converts it to
cm\(^2\)/keV with

\[
1\ {\rm GeV}^{-3}
\longrightarrow
0.3893793721\times10^{-33}\ {\rm cm}^2/{\rm keV}.
\]

No identical-particle \(1/2!\) factor is present because the final \(\chi_1\)
and scalar \(s\) are distinguishable.

## Numerical checks

The runner performs:

1. AFH response-grid integrity and \(R_A^{\rm phys}=4C_0R_A^{\rm package}\)
   checks at all 2401 q nodes.
2. Full Python \(I_6\) and \(d\sigma_A/dE_R\) evaluation over the 5--800 keV
   recoil grid, with the selected Figure-2 recoil points inserted explicitly.
3. A physical/no-factor-four cross-section ratio check.
4. A GeV\(^{-3}\) to cm\(^2\)/keV conversion check.
5. Exact zero checks for kinematically closed points and positive pole
   clearance for open points.
6. High-order \(I_6\) anchors at 101, 200, 267 and 542 keV for all four
   benchmarks. The default anchor order is \(48\times40\times24\), compared
   against the production \(16\times16\times8\) grid.

The acceptance threshold for the high-order anchor comparison is configurable
and defaults to \(10^{-3}\). A failed anchor check must be investigated; do not
rescale the rate to force agreement.

## Reproduction

From the repository root:

~~~bash
python research/afh_default_density_xe131/run_python_full_dsigma_xe131.py \
  --outdir research/afh_default_density_xe131/output/python_full_dsigma \
  --nw 16 --nz 16 --nphi 8 \
  --anchor-order 48 40 24
~~~

For a fast smoke calculation:

~~~bash
python research/afh_default_density_xe131/run_python_full_dsigma_xe131.py \
  --er-list-kev 101,200,267,542,1300 \
  --nw 4 --nz 4 --nphi 4 --skip-anchor-checks \
  --outdir /tmp/xe131-python-dsigma-smoke
~~~

The runner writes the full differential-cross-section CSV, a machine-readable
metadata JSON, and a separate high-order anchor CSV. GitHub Actions uploads
these files as a reproducible artifact; it does not commit generated numerical
outputs to main.

## Boundaries

- This is a fixed-speed Xe-131 differential cross section, not a halo fold.
- It uses PCHIP interpolation of the existing 2401-node Python AFH response
  grid. The response grid itself has a separate native Mathematica/Python
  validation; selected off-grid direct finite-sum response checks are a
  distinct accuracy diagnostic.
- This does not replace the already completed natural-xenon continuous
  spectrum or its high-order halo-fold convergence audit.
- It does not validate the complete detector-level LZ likelihood.
- The final Mathematica full \(d\sigma_A/dE_R\) run and pointwise comparison
  remain deferred until the Python calculation and all non-Mathematica work
  are complete.


## Completed Python run (2026-11-14)

GitHub Actions run 43591097068 completed successfully. The archived artifact is
named python-xe131-full-dsigma-factor4-audit (artifact ID 14112736343).

Measured results:

| Quantity | Result |
|---|---:|
| Differential-cross-section rows | 652 |
| Kinematically open rows | 500 |
| Kinematically closed rows | 152 |
| High-order anchor comparisons | 16 |
| Maximum \(I_6\) relative difference, 16x16x8 vs 48x40x24 | \(1.663669202400797\times10^{-11}\) |
| Maximum AFH factor-four mapping residual | \(3.556786241889844\times10^{-16}\) |
| Physical/no-factor-four algebraic ratio residual | 0 |
| Unit-conversion algebraic residual | 0 |
| \(C_0\) | 1.0000825298069376 |
| Physical response at \(q=0\) | 17161 = \(131^2\) |

The zero residuals in the physical/no-factor-four ratio and unit-conversion
checks are algebraic assembly checks: the control uses the same prefactor and
\(I_6\), replacing only \(R_A^{\rm phys}\) by \(R_A^{\rm phys}/4\). They verify
that the implementation applies the factor four once and does not introduce
another factor in the prefactor; they are not independent cross-code tests.

SHA-256:
- AFH response input: 1b936abf07f54a669ae0680fe230ca7d858297f579ba3113bbbc55c3e76ed83c
- Differential-cross-section CSV: cca2ef09696cd7896674088b742e1c4a062b02b4033ab06c6a4f0d708264e44b
- High-order anchor CSV: c83da70e2fe45de2c0b32d0b4969c729de7d1893989926090998542bf7a3bf08

The run metadata explicitly records that Mathematica/Wolfram was not invoked.
The independent native Mathematica full-cross-section comparison remains
pending and must be completed before this audit is promoted to a full
cross-code validation.


For reference, the fixed-speed spectra have the following grid maxima. These
are numerical outputs for the stated \(v=800\) km/s benchmark and are not
halo-averaged rates or detector event counts.

| Benchmark | Open \(E_R\) range (keV) | Maximum \(d\sigma_A/dE_R\) (GeV\(^{-3}\)) | Grid location (keV) |
|---|---:|---:|---:|
| red, \(m_s=200\) keV, \(\Delta m=1\) MeV | 35--800 | \(9.62585\times10^{-7}\) | 50 |
| green, \(m_s=300\) keV, \(\Delta m=1\) MeV | 100--750 | \(4.39465\times10^{-8}\) | 170 |
| black, \(m_s=360\) keV, \(\Delta m=1\) MeV | 190--550 | \(1.40708\times10^{-9}\) | 355 |
| blue, \(m_s=300\) keV, \(\Delta m=10\) MeV | 100--750 | \(3.50707\times10^{-10}\) | 170 |
