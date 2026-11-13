# Native AFH v6.0 Xe-131 Mathematica audit

**Status: PASS**

## Scope

This run validates the Xe-131 AFH v6.0 default nuclear response obtained from the package's built-in sdgXe131 density matrix:

\[
\texttt{SetIsotope[54,131,"default","default"]},\qquad
W_M^{00}(y)=\texttt{ResponseNuclear[y,1,0,0]}.
\]

It is a response-level native Wolfram calculation and pointwise comparison. It does not calculate the three-body Eq. (6) integral, a complete natural-xenon halo spectrum, or an LZ likelihood.

## Input provenance and environment

- AFH source: v6/dmformfactor-V6.m
- AFH source SHA-256: dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372
- Built-in Xe-131 density matrix: 67 entries
- Density-matrix CSV SHA-256: f656145ba2fb9da741b77faed4c01d0dc457c955fa340928b5dbf9cee9bc5d45
- Runtime: Wolfram 14.0.0, Microsoft Windows 64-bit (December 13, 2023)
- Source delivery mode: the extracted .m source file was supplied directly; the manifest therefore records afhArchiveSha256 = null. The source-file SHA-256 is recorded and checked.
- The local Python executable version was not recorded in the native metadata and is intentionally not inferred here.

## Reproduction

From research/afh_default_density_xe131/ on Windows, with Python dependencies installed and wolframscript available on PATH:

~~~powershell
.\run_native_afh_audit.ps1 -AfhSource "D:\path\to\dmformfactor-V6.m"
~~~

The archived local metadata records the supplied source path as C:\Users\admin\Desktop\3 body HDM\v6\dmformfactor-V6.m. The runner verifies the source and 67-entry matrix hashes, rebuilds the Python reference from that source, runs both native Wolfram scripts, compares the q grids without interpolation, writes the comparison summary and SHA-256 manifest, and retains the extracted output files.

## Grid and comparison settings

- Number of q points: 2401
- q range: 0–0.6 GeV
- Step: 0.00025 GeV = 0.25 MeV
- Python and Mathematica q grids: identical at the exported precision
- Maximum absolute q-grid difference: 0 GeV
- Acceptance: rtol = 2e-8, atol = 2e-10
- Failed points: 0 for every compared response quantity

## Numerical comparison

| Quantity | Maximum absolute difference | Maximum relative difference | Worst q [GeV] |
|---|---:|---:|---:|
| Raw \(W_M^{00}\) | \(1.5916157281\times10^{-12}\) | \(3.5908703\times10^{-9}\) | 0.2565 |
| AFH package response \(4\pi W_M^{00}/(2J_A+1)\) | \(5.0022208598\times10^{-12}\) | \(3.5908703\times10^{-9}\) | 0.2565 |
| Raw physical equal-p/n response | \(2.0008883439\times10^{-11}\) | \(3.5908703\times10^{-9}\) | 0.2565 |
| q=0-normalized physical response | \(2.3646862246\times10^{-11}\) | \(3.5908701\times10^{-9}\) | 0.2565 |

All four comparisons pass the stated tolerance. The largest relative discrepancy, \(3.59\times10^{-9}\), is below the \(2\times10^{-8}\) relative tolerance.

## Factor-four and q=0 normalization contracts

The raw AFH package response and the physical equal-proton/equal-neutron response are stored separately. The output construction checks

\[
R_{\rm equal,pn}^{\rm raw}(q)
=4\,R_{\rm AFH}^{\rm package}(q)
\]

at every q node; the archived CSV columns satisfy this identity exactly at their exported precision, and the Wolfram runner enforces a relative residual below \(10^{-12}\).

At zero momentum, the rounded built-in density-matrix entries give

\[
R_{\rm AFH}^{\rm package}(0)=4289.895955714992,
\qquad
A^2/4=4290.25.
\]

The corresponding raw physical response is

\[
R_{\rm equal,pn}^{\rm raw}(0)=17159.583822859968,
\qquad A^2=17161.
\]

The relative offset is \(-8.2522996331\times10^{-5}\). A separate, small shape normalization

\[
C_0=1.0000825298069378
\]

sets the displayed normalized response to \(R_A(0)=A^2\). This C0 correction is not the factor of four. The factor of four is the AFH isoscalar-coupling conversion; C0 only removes the finite-decimal-precision offset of the tabulated density matrix.

The source-level coupling mapping is documented separately: the AFH setter uses its own isoscalar input convention, while the paper's g_VN is defined per physical nucleon. The native grid comparison validates the raw package response and its numerical translation; it does not by itself replace that source-level derivation or constitute a full DiffCrossSection comparison.

## Response minima

The native Wolfram minimizer independently reports the three Figure-2-region minima:

| q_min [MeV] | E_R,min [keV] | R_A/A^2 |
|---:|---:|---:|
| 157.9357791 | 102.2067248 | \(1.23638155\times10^{-5}\) |
| 256.2718683 | 269.1038991 | \(6.34070237\times10^{-8}\) |
| 365.0665734 | 546.0869099 | \(1.56193996\times10^{-7}\) |

The native 0–0.6 GeV grid also covers the higher-q region; the three-row minimizer table is deliberately restricted to the three Figure-2-region intervals.

**Mass-convention note:** the native WLS file maps q to its display-only E_R column using m_A=131×0.93149410242 GeV. The response itself is tabulated as a function of q. This display conversion must not be substituted for the isotope-specific NIST/AME2020 nuclear mass used in the separate natural-xenon rate calculation.

## Archived files

- ../afh_default_xe131_WM00_mathematica.csv
- ../afh_default_xe131_mathematica_metadata.txt
- afh_native_audit_grid.csv
- python_reference.csv
- afh_native_audit_comparison.csv
- afh_native_audit_minima.csv
- afh_mathematica_python_comparison.json
- afh_native_audit_metadata.txt
- afh_native_audit_manifest.json

The native CSV, Python reference, pointwise comparison, metadata, and manifest are committed individually. A locally generated ZIP is only a convenience bundle, not the canonical archival record.

## Limitations

- This result is for Xe-131 only and the AFH built-in default density matrix.
- It validates the native AFH response against the source-translated Python response on the same 2401-point q grid; it does not validate the complete three-body I6 integration or its continuous-recoil convergence.
- It does not supply the missing Xe-124/Xe-126 AFH matrices or turn the seven-isotope selected-point result into a complete natural-xenon continuous spectrum.
- It is not a halo-folded detector spectrum, a NEST response, a profile likelihood, or an LZ exclusion.
