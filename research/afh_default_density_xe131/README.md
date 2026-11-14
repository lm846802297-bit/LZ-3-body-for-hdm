# AFH default Xe-131 nuclear response

## Adopted source input

This stage uses the **built-in AFH/DMFormFactor v6.0 default density matrix** for
Xe-131, not GCN5082 or JJ55.

Official source archive supplied for this calculation:
- ZIP SHA-256: `4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`
- source: `v6/dmformfactor-V6.m`
- source-file SHA-256: `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`

The AFH source contains the 67-entry `sdgXe131` matrix and selects it with:

```mathematica
SetIsotope[54,131,"default","default"]
```

The AFH default oscillator prescription is

```text
b_A[fm] = sqrt(41.467/(45 A^(-1/3)-25 A^(-2/3)))
```

and the source's unit conversion is `Femtometer = 5.0677/GeV`. For Xe-131,
`b_A = 2.2923417985218975 fm`.

The extracted 67-entry matrix is preserved in
`afh_default_xe131_density_matrix.csv`. The Python runner can optionally
re-parse the official `.m` file and verify that the archived matrix matches
all source entries.

## AFH response and isospin normalization

The selected AFH response is

```mathematica
ResponseNuclear[y,1,0,0]
```

which returns the AFH package's isoscalar `W_M^{00}(y)`.

**Important: the AFH package's isoscalar convention has a factor of four
relative to a response normalized to the physical equal-proton/equal-neutron
coherent charge `A^2`.** With the AFH output as-is,

```text
(4 pi/(2 J_A+1)) W_M^{00}(0) = A^2/4
```

For the equal physical nucleon coupling used in the three-body cross section,
the coherent response is four times this AFH isoscalar-normalized quantity.
The built-in density-matrix coefficients are rounded, so the physical response
is normalized by its computed q=0 value:

```text
R_equal(q) = A^2 * R_AFH(q)/R_AFH(0)
```

This preserves the AFH q-dependence and removes only the small overall
finite-precision offset. The source-based derivation and manuscript
normalization issue are documented in
`AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md`.

## Numerical result

The full 0--0.6 GeV momentum-transfer grid (0.25 MeV spacing) is in
`output/afh_default_xe131_WM00.csv`. The three Figure 2 dip locations are
reproduced without adjusting `b_A`:

| AFH default minimum | q [MeV] | E_R [keV] | R/A^2 |
|---|---:|---:|---:|
| 1 | 157.93578 | 102.20672 | 1.23638e-5 |
| 2 | 256.27187 | 269.10390 | 6.34070e-8 |
| 3 | 365.06657 | 546.08690 | 1.56194e-7 |

A fourth minimum appears at approximately 1.022 MeV recoil, outside the
three-dip Figure 2 region.

See `output/RESULTS.md`, `output/metadata.json`, `output/minima.csv`,
`output/figure2_dip_check.csv`, and `output/afh_default_xe131_WM00.png`.

## Reproduction

Python dependencies: NumPy, SciPy, SymPy, mpmath. From this directory:

```bash
python run_afh_default_xe131.py --outdir output
```

To verify the extracted matrix against the official AFH source as well:

```bash
python run_afh_default_xe131.py \
  --afh-package /path/to/dmformfactor-V6.m \
  --density-matrix-csv afh_default_xe131_density_matrix.csv \
  --outdir output
```

Run regression tests with:

```bash
python -m unittest test_afh_default_xe131.py
```

For a native AFH Mathematica calculation, use
`run_afh_default_xe131.wls` with the official package file in this directory
or set `DMFormFactorPath`.

## Independent full-grid mpmath validation

The CI workflow now evaluates the AFH finite sums independently with 60-digit
mpmath arithmetic at all 2401 momentum-grid nodes. The reference calculation
groups the finite BesselElement sums by hypergeometric parameter and does not
call SciPy's hyp1f1 implementation.

Latest completed full-grid check:

| Metric | Result |
|---|---:|
| q nodes | 2401 |
| Maximum absolute amplitude difference | \(3.98\times10^{-14}\) |
| Maximum relative amplitude difference where reference amplitude exceeds \(10^{-10}\) | \(8.83\times10^{-13}\) |
| Maximum absolute response difference divided by \(A^2\) | \(1.22\times10^{-15}\) |
| Status | PASS |

The machine-readable 2401-row comparison and JSON summary are uploaded as the
GitHub Actions artifact named afh-xe131-mpmath-full-grid-validation. The compact
summary is also committed as output/mpmath_full_grid_summary.json. This is an
independent high-precision check of the Python finite-sum translation; it is
not a native Mathematica execution.

Run it with:

~~~bash
python verify_afh_mpmath_full_grid.py \
  --response-csv output/afh_default_xe131_WM00.csv \
  --outdir output/mpmath_full_grid
~~~

## Recoil-momentum convention

AFH defines the nuclear response variable as \(y=(q b_A/2)^2\), where \(q\) is
the spatial momentum transfer. For a nucleus initially at rest, exact
mass-shell kinematics gives

\[
q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}.
\]

This exact spatial q is used for the response interpolation and the three-body
kinematic boundary. The common \(q_{\rm NR}=\sqrt{2m_AE_R}\) relation is retained
only as a small-recoil approximation. The AFH-7/Hybrid-9 continuous-spectrum archive evaluates the seven supported
isotope responses at exact spatial q and is consistent with the exact
three-body kinematics. The earlier 28-point selected-sample archive remains
available as a historical cross-check. Numerical differences in the NR approximation are documented in
research/docs/appendices/09G_recoil_momentum_convention_audit.md.

## Scope and connection to the three-body calculation

The AFH default Xe-131 nuclear response is archived here. The four fixed-speed
benchmark response substitutions are archived in
`output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv` and
`output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv`. They use the
existing 5 keV-grid Eq. (6) integral and replace only the nuclear response;
they are not a fresh independent recomputation of all 640 three-body
integrals.

The manuscript source `paper-source/main.tex` now explicitly uses
`R_A = C_A 16 pi W_M00_AFH/(2 J_A+1)` for the raw AFH v6.0 response and the
physical equal-proton/equal-neutron coupling, with `C_A` fixed by the q=0
sum rule. This gives `R_A(0)=A^2`; the factor four is applied exactly once.
The independent historical code-convention check is documented in
`AFH_COUPLING_NORMALIZATION_MAPPING.md`.

The selected-point natural-xenon isotope sum and halo velocity fold are
implemented separately in
`../afh_default_density_natural_xenon_halo/`. That calculation uses 28
selected AFH samples (seven isotopes x four recoil energies), not seven
complete 2401-point response grids. The provenance metadata now explicitly
distinguishes the original 16,807-row source input from the committed
28-row selected-sample file; the original all-isotope input itself is not
currently committed. The AFH native Mathematica execution also remains
pending; the current AFH numerical table is from the source-translated Python
implementation.

The GCN/JJ55 files from `dmscatter` remain separate nuclear-structure
calculations and are not relabeled or substituted for AFH default.



## AME2020/CODATA2022 nuclear-mass update

The current mainline-based AME2020 study is documented in
[AME2020_CODATA2022_MASS_RECALC.md](AME2020_CODATA2022_MASS_RECALC.md).
It adds a third nuclear-mass prescription alongside the historical \(A u\)
and NIST nuclear-mass schemes:

\[
M_N=M_{\rm atom}^{\rm AME2020}-54m_e+B_e(54),
\]

using unrounded AME2020 atomic masses and CODATA-2022 constants.

The Xe-131 partial halo fold uses the exact AFH spatial momentum
\(q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}\) as its baseline. The
\(q_{\rm NR}=\sqrt{2m_AE_R}\) result is retained only as an approximation
diagnostic. The calculation and its numerical outputs are archived under
`output/ame2020_exact_spatial_xe131_partial/`.

A separate Xe-131-only hybrid diagnostic replaces the Xe-131 term in the
existing NIST natural-xenon selected-point sum with the AME2020 result while
leaving the other six isotope terms at their NIST baseline. It is explicitly
not a full AME2020 natural-xenon prediction. Updating the full seven-isotope
sum requires the original all-isotope AFH response input or regeneration of
the six other full response grids from the AFH v6.0 source archive.

The exact-spatial-q calculation, mass-scheme comparison, and Xe-131-only
hybrid diagnostic passed in
[GitHub Actions run 43188435890](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43188435890).
The archived numerical tables and input SHA-256 records are under
`output/ame2020_exact_spatial_xe131_partial/`. The hybrid changes the
natural-xenon selected-point total by at most 7.87 ppm when only the Xe-131
term is replaced; this must not be interpreted as the complete
seven-isotope AME2020 correction.

## Subsequent exact-q interpolation audit (2026-11-12)

The AME2020 partial-rate tables above were generated by interpolating the
2401-node Xe-131 response grid with PCHIP. A later seven-isotope audit compared
that interpolation with direct finite-sum evaluation at the selected exact
spatial momenta and an independent 60-digit mpmath calculation.

For Xe-131, the direct exact-q response differs from the 2401-node PCHIP value
by up to \(3.185\times10^{-4}\) at 267 keV. The direct finite-sum and
60-digit mpmath values agree to approximately \(6\times10^{-14}\) or better
at the selected Xe-131 points.

This is a response-interpolation issue, not a change to the AME2020 nuclear
mass conversion or to the exact spatial-q definition. It is nevertheless
large enough to be comparable to the previously quoted NIST-to-AME2020
rate shift at 267 keV. Therefore:

- the AME2020 atomic and nuclear mass values and their unit tests remain valid;
- the previous Xe-131 PCHIP-based partial rates are retained as historical
  reproducible outputs, but are **provisional** as precision rates;
- the previously quoted Xe-131-only natural-xenon hybrid shift (at most
  7.87 ppm) is also provisional;
- these rate-level results must be recomputed using the direct exact-q
  response table or a separately validated refined/adaptive response grid.

The detailed seven-isotope diagnosis is in
`../afh_default_density_natural_xenon_halo/audit/AFH_RESPONSE_INTERPOLATION_AUDIT.md`.
Do not use the PCHIP-based values above as the final AME2020 rate prediction
until that recomputation is complete.


## Canonical four-benchmark cross-section files

See [output/CROSS_SECTION_FILE_INDEX.md](output/CROSS_SECTION_FILE_INDEX.md) for the single canonical file-name mapping. The current long-form result is `output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv`; the matching wide audit is `output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv`. The historical `output/figure2_four_benchmarks_dsigma_AFH_GCN_JJ55.csv` is retained only for provenance and is superseded because its AFH response column was copied from GCN. It must not be used in downstream plots or calculations.


## Native Mathematica comparison against the Python full grid

The repository now includes
`validate_afh_mathematica_vs_python.wls`. Unlike the older
`run_afh_default_xe131.wls`, this harness explicitly compares the native
Wolfram-kernel result against the archived Python CSV at all 2,401 momentum
nodes.

From the repository root on a machine with Mathematica / Wolfram Engine and
`wolframscript` installed:

```powershell
wolframscript -file research/afh_default_density_xe131/validate_afh_mathematica_vs_python.wls
```

The default paths load `v6/dmformfactor-V6.m` and compare against
`output/afh_default_xe131_WM00.csv`. Optional environment variables
`DMFormFactorPath`, `AFHPythonReferenceCSV`, and `AFHMathematicaOutDir`
override the package, reference CSV, and output directory.

The script calls the official `SetIsotope[54,131,"default","default"]` and
`ResponseNuclear[y,1,0,0]` functions in the Wolfram kernel, then writes a
2,401-row pointwise comparison CSV and a JSON metadata summary. It checks the
AFH package's (A^2/4) zero-momentum convention, the physical equal-(p,n)
(R_A(0)=A^2) normalization, the q grid, the finite-precision factor (C_A),
and the maximum full-grid response difference.

**Execution status:** the harness is committed, but it has not yet been
executed in a native Wolfram kernel. The Python/60-digit mpmath validation is
not a substitute for this native Mathematica run. Do not mark the native
comparison PASS until the generated CSV and metadata JSON are inspected and
archived.

See also the Phase II report:
[09H — high-energy tail nuclear-model sensitivity](../docs/appendices/09H_high_energy_tail_nuclear_model_sensitivity.md).
