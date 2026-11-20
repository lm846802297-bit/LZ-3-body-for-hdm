# AFH default Xe-131 nuclear response

## Directory map

- `input/`: AFH default density matrix and fixed-speed base cross-section input.
- `audit/`: normalization, momentum-convention, and AME2020 audit reports/scripts.
- `tests/`: Xe-131 response, four-benchmark, and AME2020 regression tests.
- `output/`: response grids, canonical cross sections, native Mathematica audit, and historical diagnostics.
- Study-root Python/Wolfram files remain stable calculation entry points because existing workflows call these paths directly.

## Adopted source input

This stage uses the **built-in AFH/DMFormFactor v6.0 default density matrix** for
Xe-131, not GCN5082 or JJ55.

**Model-provenance clarification:** AFH is the nuclear-response formalism and
package, not a shell-model interaction. The original xenon OBDMEs used by the
AFH work are associated with the Baldridge–Dalton (B&D) shell-model interaction
in the 50–82 major shell. The later shell-model comparison by Abdel Khaleq
et al. (Phys. Rev. D 109, 075036 (2024), Sec. III B and Sec. IV B) explicitly
identifies the original Fitzpatrick/Anand–Fitzpatrick–Haxton calculations as
using B&D. The precise terminology is therefore **AFH v6.0 formalism/default
OBDMEs with B&D underlying shell-model provenance**; AFH itself should not be
called an interaction.

GCN5082 and the archived JJ55-labelled input remain separate sensitivity
alternatives only. They are not mixed into the AFH mainline. For the exact
scope and comparison rules, see
[NUCLEAR_STRUCTURE_BASELINE_POLICY.md](NUCLEAR_STRUCTURE_BASELINE_POLICY.md).

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
`input/afh_default_xe131_density_matrix.csv`. The Python runner can optionally
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
`audit/AFH_DEFAULT_XE131_NORMALIZATION_AUDIT.md`.

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
`output/nuclear_response_dip_check.csv`, and `output/afh_default_xe131_WM00.png`.

## Reproduction

Python dependencies: NumPy, SciPy, SymPy, mpmath. From this directory:

```bash
python run_afh_default_xe131.py --outdir output
```

To verify the extracted matrix against the official AFH source as well:

```bash
python run_afh_default_xe131.py \
  --afh-package /path/to/dmformfactor-V6.m \
  --density-matrix-csv input/afh_default_xe131_density_matrix.csv \
  --outdir output
```

Run regression tests with:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

For a native AFH Mathematica calculation, use
`run_afh_default_xe131.wls`; by default it loads the committed official source
from `v6/dmformfactor-V6.m`. Set `DMFormFactorPath` to use another verified
copy of the AFH v6.0 source.

For an independent native Mathematica/Python comparison, use the one-command
Windows PowerShell runner below. It accepts either the original AFH v6.0 ZIP
archive or the extracted `dmformfactor-V6.m` file:

```powershell
.\run_native_afh_audit.ps1 -AfhSource "D:\path\to\v6.zip"
```

The runner verifies the supplied ZIP SHA-256
(`4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`) or
source-file SHA-256
(`dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`),
checks the 67-entry Xe-131 density-matrix CSV, regenerates the Python
reference from that exact source, runs both native Wolfram scripts, compares
all 2401 q nodes without interpolation, and writes a SHA-256 manifest.

Required on the Windows machine: Python with the repository requirements,
Wolfram Engine or Mathematica with `wolframscript` on `PATH`, and the
either the original AFH v6.0 ZIP or its extracted dmformfactor-V6.m source file. The direct 2401-point Mathematica response export and its execution metadata are written to
`output/native_exports/`. The independent Python/Wolfram pointwise comparison,
minima, Wolfram version, source hashes, CSV hashes, and
`afh_native_audit_manifest.json` are written to `output/native_audit/`.
These are separate records: the direct native export is not the comparison grid.
The runner bundles both directories into the local convenience archive
`output/afh-native-audit-results.zip`. The canonical repository record is the
individually committed content under `output/native_exports/` and
`output/native_audit/`, not the ZIP bundle.

A successful Python GitHub Actions run is **not** a substitute for this native
Wolfram execution. The native audit is considered complete only when the
manifest reports `status = PASS` and the comparison JSON reports
`"passed": true`.

## Completed native Mathematica audit (2026-11-13)

The local Windows/Wolfram run is now archived and reports **PASS**:

- Wolfram 14.0.0, Windows 64-bit; official AFH v6.0 source SHA-256 dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372.
- 2401 q nodes from 0 to 0.6 GeV in 0.25 MeV steps; Mathematica and Python grids are identical, with no interpolation.
- Raw \(W_M^{00}\), package response, physical equal-p/n response, and q=0-normalized response all pass at rtol=2e-8, atol=2e-10; maximum relative difference is \(3.59087\times10^{-9}\) at \(q=0.2565\) GeV.
- The factor-four response mapping is checked at every q node. The separate q=0 shape-normalization factor is \(1.0000825298069378\), correcting the \(8.2523\times10^{-5}\) finite-density-matrix offset; it is not another factor of four.
- Full details and the native SHA-256 manifest are in output/native_audit/NATIVE_MATHEMATICA_AUDIT.md and output/native_audit/afh_native_audit_manifest.json.

The 2401-node native Mathematica/Python comparison validates the Xe-131 AFH response layer. The separate native Wolfram full Eq. (6) calculation has now also completed: see the 652-row native output and corrected Mathematica/Python comparison archive below. The Python-only v=800 km/s fixed-speed calculation remains a separate internal cross-check.

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
only as a small-recoil approximation. The natural-xenon 28-point response
archive uses exact spatial q and is consistent with the exact three-body kinematics; it is only a historical 28-row selected-sample file. The full 16,807-row seven-isotope response grid is now committed separately at `../afh_default_density_natural_xenon_halo/results/full_afh_v6_default_7_isotope_response/`. Numerical differences in the NR approximation are documented in

research/docs/appendices/09G_recoil_momentum_convention_audit.md.

## Scope and connection to the three-body calculation

The AFH default Xe-131 nuclear response is archived here. The four fixed-speed
benchmark response substitutions are archived in
`output/four_benchmarks_AFH_GCN_JJ55_corrected.csv` and
`output/four_benchmarks_AFH_GCN_JJ55_wide_audit.csv`. They use the
existing 5 keV-grid Eq. (6) integral and replace only the nuclear response;
they are not a fresh independent recomputation of all 640 three-body
integrals.

The research calculation adopts
`R_A = 16 pi W_M00_AFH/(2 J_A+1)` for the physical equal-proton/equal-neutron
response, giving `R_A(0)=A^2`; the factor four is applied exactly once in the
nuclear response. The manuscript file `paper-source/main.tex` is deliberately
not modified by this research-integration change. Any manuscript synchronization
must be reviewed and merged separately. The source-level code-convention
check is documented in `audit/AFH_COUPLING_NORMALIZATION_MAPPING.md`.

The early selected-point natural-xenon isotope sum and halo velocity fold are
implemented separately in
`../afh_default_density_natural_xenon_halo/`. The selected-point AME2020
mass-scheme result remains distinct from the later AFH-7/Hybrid-9 full-range
84-point grid-sampled spectra, which use the committed AFH default response
grids and high-order quadrature checks.

A separate seven-isotope AME2020 direct exact-q selected-point fold is archived
at `../afh_default_density_natural_xenon_halo/results/AME2020_DIRECT_EXACT_Q_RECALCULATION_2026-11-12.md`
and `../afh_default_density_natural_xenon_halo/results/ame2020_direct_exactq_fold/`.
It supersedes the older Xe-131-only PCHIP hybrid for selected-point mass-scheme
comparison, but it is not a full 84-point AME2020 spectrum.

The provenance metadata distinguishes the original 16,807-row seven-isotope
response grid from the historical 28-row selected-sample file; the full grid
is now committed at
`../afh_default_density_natural_xenon_halo/results/full_afh_v6_default_7_isotope_response/`.
The Xe-131 response table has an archived native Mathematica/Wolfram 14.0.0
output and a 2401-point Python comparison (PASS). This response-level PASS
does not by itself validate the full Eq. (6) three-body integral.

The GCN/JJ55 files from `dmscatter` remain separate nuclear-structure
calculations and are not relabeled or substituted for AFH default.




## Mathematica/Python full differential-cross-section comparison

The code-level crosswalk, matched inputs, phase-space measure, spin trace,
AFH factor-four placement, acceptance tolerances, and run procedure are
documented in
[MATHEMATICA_PYTHON_FULL_DSIGMA_CROSSCHECK_REVIEW.md](output/MATHEMATICA_PYTHON_FULL_DSIGMA_CROSSCHECK_REVIEW.md).

Before committing to the full 652-row native run, a reduced smoke test can
be performed on Windows:

~~~powershell
.\run_native_full_dsigma_windows.ps1 -OutputDirectory "$env:TEMP\lz-xe131-smoke" -Benchmark "green_ms300_dm1" -ERListKeV "200" -NW 8 -NZ 8 -NPhi 4 -RequireFullGrid:$false
~~~

The explicit -ERListKeV "200" argument is an exact recoil-grid override,
so this command checks only 200 keV. It validates code execution and cross-code
agreement at the same low quadrature order, not numerical convergence. To
check the four explicit anchors, pass -ERListKeV "101,200,267,542".
The normal default remains the complete 652-row grid at \(16\times16\times8\).

## AME2020/CODATA2022 nuclear-mass update

The current mainline-based AME2020 study is documented in
[AME2020_CODATA2022_MASS_RECALC.md](audit/AME2020_CODATA2022_MASS_RECALC.md).
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
not a full AME2020 natural-xenon prediction. The full seven-isotope AFH default response grids are now archived, and a separate exact-q AME2020 selected-point fold is complete. A full 84-point AME2020 grid-sampled spectrum remains uncomputed; it must reevaluate each isotope's exact spatial q and rate kernel using AME2020 nuclear masses at every recoil point, then perform the abundance-weighted halo fold.

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


## Full Eq. (6) differential-cross-section status

The native AFH response layer is validated: the archived Wolfram 14.0.0 run compares all 2,401 Xe-131 \(q\) nodes against the Python translation, with maximum relative difference \(3.59\times10^{-9}\).

Separately, the Python-only v=800 km/s fixed-speed Xe-131 full Eq. (6) calculation has completed 652 rows (500 open, 152 closed) and 16 high-order anchors. Its maximum \(I_6\) relative difference is \(1.66367\times10^{-11}\), the AFH factor-four mapping residual is \(3.55679\times10^{-16}\), and the physical/no-factor-four ratio residual is zero. The workflow [run 43591097068](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43591097068) archived artifact [14112736343](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43591097068).

The Python-only calculation is an end-to-end factor-four PASS within the Python implementation under the conditional Dirac / real-scalar / pure-scalar / single-channel pole-width assumptions. It is not a natural-xenon halo fold.

The native Wolfram runner `run_afh_eq6_full_dsigma.wls` reads the already archived AFH-native 2,401-node response table and independently recomputes \(I_6\). The Python comparator `compare_full_dsigma_mathematica.py` independently recomputes \(I_6\) and compares the AFH response, full \(d\sigma_A/dE_R\), no-factor-four control, momentum, mediator denominator and unit conversion.
The completed full-grid output is archived in `output/full_dsigma_mathematica/`: 652 rows (500 open, 152 closed), Wolfram 14.2.0, four benchmarks, fixed 800 km/s, `threshold_u2`, pole width and 16×16×8 quadrature. Both implementations use the same fixed native AFH response input. The comparison JSON reports PASS: maximum I6, dσ and converted cross-section differences are (1.34\times10^{-12}); AFH interpolation is (3.36\times10^{-16}); Mathematica/Python unit-conversion identity residuals are (3.35\times10^{-16})/0; and the factor-four ratio residual is 0.

On Windows, use `run_native_full_dsigma_windows.ps1` from the repository root after installing the requirements and ensuring `wolframscript` is on `PATH`. Mathematica and the independent Python integrator both use the same fixed native AFH response input; the source-translated Python AFH response remains a separate 2401-node audit. The wrapper checks the fixed 800 km/s / pole-width / threshold-\(u^2\) assumptions and quadrature metadata; it then runs the native integrator and Python comparator. After PASS it writes the native and comparison CSV/JSON files, `full_dsigma_sha256_manifest.json`, and `SHA256SUMS.txt`, including source/input hashes, the exact benchmark/recoil grid, and Wolfram/Python runtime versions.
The wrapper's full provenance manifest is generated in its selected run-local output directory. In the committed archive, `SHA256SUMS.txt` contains 14 repository-relative checksums for source/input files and the full-grid outputs; `green_high_order_SHA256SUMS.txt` separately covers the four Green high-order artifacts. CI verifies both checksum lists from the repository root.

High-order anchors are a separate quadrature-convergence check. For a focused comparison, use a distinct output directory, one benchmark, 48x40x24, and `-RequireFullGrid $false`; the wrapper still compares every row in that subset. Do not infer quadrature convergence from cross-code agreement at one order.

**Current result: PASS for the P1-MMA cross-code gate.** The full 652-row comparison and 48x40x24 anchors at 200, 300, and 500 keV pass. Tolerances are 2e-7 for I6/dσ and converted cross-code dσ, 2e-10 for AFH interpolation using the shared fixed native table, and 2e-12 for per-code conversion identities, factor-four relations, and kinematic identities. The high-order anchors differ from the 16x16x8 values at those same energies by at most (6.70\times10^{-12}). The broader result remains fixed-speed Xe-131 under conditional width assumptions; it does not establish a natural-xenon halo fold or LZ likelihood.


## Python-first full differential-cross-section stage (2026-11-14)

The full Xe-131 Python calculation is now separated from the final native
Mathematica comparison. Run:

~~~bash
python research/afh_default_density_xe131/run_python_full_dsigma_xe131.py \
  --outdir research/afh_default_density_xe131/output/python_full_dsigma \
  --nw 16 --nz 16 --nphi 8 --anchor-order 48 40 24
~~~

This evaluates the complete fixed-speed \(d\sigma_A/dE_R\) over the 5--800 keV
grid for all four Figure-2 benchmarks, with high-order anchors. It uses the
existing 2401-node Python AFH response table, so it does not recalculate the
nuclear response or invoke Mathematica. The physical response is
\(R_A^{\rm phys}=4C_0R_A^{\rm package}\); the cross-section prefactor retains
the per-nucleon coupling and does not apply another factor four. A
no-factor-four control must give exactly one quarter of the physical cross
section.

The machine-readable normalization and numerical boundaries are documented
in audit/PYTHON_FULL_DSIGMA_FACTOR4_AUDIT.md. GitHub Actions runs the
Python-only full-grid calculation and uploads its CSV/metadata/anchor archive.
The Python-only full-grid calculation described above and the subsequent native Wolfram 14.2.0 full-grid execution with independent Python pointwise comparison both completed on 2026-11-16. The strict shared-input comparator and separate high-order anchor comparison report `PASS`; see `output/full_dsigma_mathematica/` and `output/MATHEMATICA_PYTHON_FULL_DSIGMA_CROSSCHECK_REVIEW.md`. The result remains fixed-speed Xe-131 under the stated conditional width assumptions.

The native Wolfram runner and Python comparator both read the archived native
response from output/native_exports/afh_default_xe131_WM00_mathematica.csv.
The independent source-translated AFH table is checked separately.


## Native Mathematica vs Python full-cross-section comparison

The native Wolfram Language integrator and independent Python comparator have completed the full 652-row pointwise comparison. The commands below reproduce the archived fixed-speed Xe-131 calculation; they do not produce a natural-xenon halo fold or detector-level likelihood.

On Windows, from a PowerShell session at the repository root, run:

~~~powershell
python -m pip install -r research/afh_default_density_xe131/requirements.txt
powershell -ExecutionPolicy Bypass -File research/afh_default_density_xe131/run_native_full_dsigma_windows.ps1
~~~

This requires Mathematica or Wolfram Engine with wolframscript available on
PATH. The wrapper uses the same archived native AFH response table in both
implementations, validates the fixed 800 km/s / pole-width / threshold-\(u^2\)
assumptions and quadrature metadata, runs the Wolfram I6 integration, and
invokes the independent Python comparator. It requires the complete 652-row
grid and checks kinematics, I6, nuclear response, physical/no-factor-four
rates, and each implementation's unit-conversion identity.
The default output is written under the system temporary directory, not into
the source tree.

The Wolfram and Python default recoil grids now both contain the regular
5--800 keV grid plus the explicit 101, 200, 267 and 542 keV anchors. The
comparison uses 2e-7 for I6, d sigma/dER and the converted cross-code rate;
2e-10 for PCHIP interpolation from the shared native AFH table; and 2e-12 for
each code's unit-conversion identity, factor-four mapping, q and C0. The
independent source-translated AFH comparison retains its separate 2e-8 tolerance.

A successful run writes:
- mathematica_full_dsigma_xe131.csv and its metadata;
- mathematica_python_full_dsigma_comparison.csv;
- mathematica_python_full_dsigma_comparison.json.
- `full_dsigma_sha256_manifest.json` and `SHA256SUMS.txt`, covering the native/Python CSVs, metadata, AFH response inputs, the source files used by the run, and the recorded Wolfram/Python runtime versions.

For a separate high-order anchor check, use a distinct output directory and
disable the full-grid requirement:

~~~powershell
powershell -ExecutionPolicy Bypass -File research/afh_default_density_xe131/run_native_full_dsigma_windows.ps1 -OutputDirectory "$env:TEMP\lz-xe131-highorder" -Benchmark "green_ms300_dm1" -ERListKeV "200,300,500" -NW 48 -NZ 40 -NPhi 24 -RequireFullGrid $false
~~~

This is a subset comparison, separate from the 652-row full-grid acceptance.
An explicit recoil list is used exactly, without inserting standard grid
anchors. The 200, 300, and 500 keV 48x40x24 run and pointwise Python comparison
both report PASS; the largest change from 16x16x8 at those same energies is
\(6.70\times10^{-12}\) in I6 and the cross section.
**Acceptance status (2026-11-16):** the native Mathematica/Python full-cross-section gate is complete. The committed comparator JSON reports `PASS`, and the scientific result is classified `PASS_WITH_NOTES` because the width prescription and fixed-speed Xe-131 scope remain conditional. The CSV, metadata, row-level comparison and SHA-256 archive have been reviewed.


## Historical Xe-131 I6 mapping and quadrature audit

The archived green benchmark I6 point at \(v=776\) km/s and zero width has
now been compared against the legacy Eq. (6) kernel and four independent
W2 mappings. The legacy kernel reproduces the historical archive exactly;
the independent linear-W2 mapping agrees within \(5.42\times10^{-11}\).
At the historical \(40\times32\times20\) order, threshold-\(u^2\) is lower
by \(2.14\)--\(2.23\times10^{-6}\), but its \(48\times40\times24\) and
\(64\times48\times32\) results agree within \(1.40\times10^{-11}\).

This is an I6-only diagnostic and does not recompute AFH or establish the
full Mathematica/Python \(d\sigma_A/dE_R\) comparison. See
[the full mapping audit](output/HISTORICAL_I6_MAPPING_AUDIT.md) and the
[archived CSV/metadata/checksums](output/historical_i6_mapping_audit/).



## Frozen full Eq. (6) archive source provenance

The native full-differential-cross-section archive under
`output/full_dsigma_mathematica/` is a frozen 2026-11-16 result. Its
`SHA256SUMS.txt` intentionally records the phase-space implementation used
for that historical calculation, rather than the actively developed version
of `phase_space_convergence.py`.

The archived source snapshot is pinned at commit
`8f73c26d89605300b6539d6ca2cbd3ab5ceffcbe`. The read-only validation workflow
checks the immutable output files in the current checkout and separately
checks the historical phase-space source hash
`7396b06fb2ea4bc4f857463ea63c48cc60d118ce286a12915cbb7a7a387217b7` from
that commit. This preserves the original archive provenance while allowing
later numerical-method improvements to the shared integration module.
