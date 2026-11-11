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
GitHub Actions artifact named afh-xe131-mpmath-full-grid-validation. This is an
independent high-precision check of the Python finite-sum translation; it is
not a native Mathematica execution.

Run it with:

~~~bash
python verify_afh_mpmath_full_grid.py \
  --response-csv output/afh_default_xe131_WM00.csv \
  --outdir output/mpmath_full_grid
~~~

## Recoil-momentum convention

For a fixed recoil energy, the manuscript's current response definition
\(y=b_A^2m_AE_R/2\) corresponds to
\(q_{\rm resp}^{\rm NR}=\sqrt{2m_AE_R}\). The exact three-body kinematics
continues to use
\(q_{\rm kin}^{\rm exact}=\sqrt{2m_AE_R+E_R^2}\). The fixed-speed response
substitution uses the former; the exact momentum remains in the kinematic
boundary. The natural-xenon archived response samples currently use exact q
and are explicitly marked legacy pending their seven-isotope regeneration.
See research/docs/appendices/09G_recoil_momentum_convention_audit.md.

## Scope and connection to the three-body calculation

The AFH default Xe-131 nuclear response is archived here. The four fixed-speed
benchmark response substitutions are archived in
`output/figure2_four_benchmarks_AFH_GCN_JJ55_corrected.csv` and
`output/figure2_four_benchmarks_AFH_GCN_JJ55_wide_audit.csv`. They use the
existing 5 keV-grid Eq. (6) integral and replace only the nuclear response;
they are not a fresh independent recomputation of all 640 three-body
integrals.

The manuscript source `paper-source/main.tex` now explicitly uses
`R_A = 16 pi W_M00_AFH/(2 J_A+1)` for the raw AFH v6.0 response and the
physical equal-proton/equal-neutron coupling. This gives `R_A(0)=A^2`.
The factor four is applied exactly once, in the nuclear response. The
independent historical code-convention check is documented in
`AFH_COUPLING_NORMALIZATION_MAPPING.md`.

The natural-xenon isotope sum and halo velocity integration remain separate
follow-up calculations. The AFH native Mathematica execution also remains
pending; the current AFH numerical table is from the source-translated Python
implementation.

The GCN/JJ55 files from `dmscatter` remain separate nuclear-structure
calculations and are not relabeled or substituted for AFH default.

