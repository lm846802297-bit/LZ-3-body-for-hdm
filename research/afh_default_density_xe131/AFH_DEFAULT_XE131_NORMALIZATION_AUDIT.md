# AFH v6.0 Xe-131 default response: source and normalization audit

## 1. Source provenance

Input archive: `v6.zip` uploaded for this calculation.

- ZIP SHA-256: `4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727`
- Source file: `v6/dmformfactor-V6.m`
- Source-file SHA-256: `dc0742f1c50b0a478adab62f2ddef6c82978ee034c1f177e0ed917deab5dd372`
- AFH built-in matrix: `sdgXe131`, 67 entries
- Source selection: `SetIsotope[54,131,"default","default"]`
- AFH oscillator prescription: `b_A[fm] = sqrt(41.467/(45 A^(-1/3)-25 A^(-2/3)))`
- AFH source unit conversion: `Femtometer = 5.0677/GeV`

The parsed 67-entry matrix is preserved in `afh_default_xe131_density_matrix.csv`. The Python runner can also re-parse the official `.m` file and verifies that all parsed entries match the CSV.

## 2. Response calculation

The AFH package defines the M response through `ResponseNuclear[y,1,tau,tau2]`. For Xe-131, the built-in source sets:

- nuclear spin `J_A = 3/2`;
- isospin magnitude `T_iso = |A/2-Z| = 11.5`;
- 16 isoscalar rank-0 density-matrix entries;
- 8 isoscalar rank-2 entries.

The implementation translates the AFH source functions `Lnumber`, `Nodal`, `mjelement`, `BesselElement`, `FF`, and `ResponseNuclear`. For the elastic M response only the even multipoles `J=0,2` survive. The output includes the package's `W_M^{00}` and the normalized physical equal-proton/equal-neutron charge response.

## 3. Factor-of-four convention

The AFH package's isoscalar decomposition uses `c^0=(c^p+c^n)/2` and `c^1=(c^p-c^n)/2`. The source's `Response[]` multiplies isoscalar density-matrix entries by

`Sqrt[2]/Sqrt[2 T_iso+1] * ((a_n+a_p)/2)`.

The `FF` routine constructs the proton/neutron coefficient matrix using one half of the second derivatives of the squared amplitude. `ResponseNuclear[...,0,0]` then takes one quarter of the sum of the four proton/neutron matrix entries. Consequently, the package response has the standard AFH isoscalar zero-momentum limit

`(4 pi/(2 J_A+1)) W_M^{00}(0) = A^2/4`,

not `A^2`.

For the physical equal-nucleon-coupling response used in the manuscript's cross section, the coherent charge amplitude is proportional to `A`. Therefore the response must be four times the AFH isoscalar-normalized package response, or the factor four must be carried elsewhere in the particle/nucleon response prefactor.

This distinction is not a numerical fit. It follows from the package's explicit isospin normalization and is also consistent with the general AFH normalization check that the isoscalar `W_M^{00}` carries an `A/2` charge operator.

## 4. Finite-precision normalization

The built-in density-matrix coefficients are tabulated to finite decimal precision. The direct AFH-source translation gives:

- `R_AFH(0) = 4289.895955714993`;
- `A^2/4 = 4290.25`;
- relative difference `8.2523e-5`.

The equal-pn response is normalized by its computed zero-momentum value:

`R_equal(q) = A^2 * R_AFH(q)/R_AFH(0)`.

This preserves the entire AFH q-dependence and removes only the tiny overall offset caused by the printed density-matrix precision. It gives `R_equal(0)=17161` exactly.

## 5. Numerical result

Default oscillator length:

- `b_A = 2.2923417985218975 fm`;
- `b_A = 11.61690053236942 GeV^-1`.

Refined minima of the physical equal-pn response:

| q_min [MeV] | E_R,min [keV] | R/A^2 |
|---:|---:|---:|
| 157.93578 | 102.20672 | 1.23638e-5 |
| 256.27187 | 269.10390 | 6.34070e-8 |
| 365.06657 | 546.08690 | 1.56194e-7 |
| 499.37189 | 1021.79779 | 1.67063e-8 |

At the three Figure 2 recoil-energy reference points:

| E_R [keV] | q [MeV] | R/A^2 |
|---:|---:|---:|
| 101 | 157.00066 | 1.77914e-5 |
| 267 | 255.26811 | 3.26074e-7 |
| 542 | 363.69793 | 1.83631e-7 |

The three dips in the Figure 2 range are therefore reproduced in location by the AFH default response, without tuning `b_A`.

## 6. Numerical validation

- All 67 density-matrix entries are parsed from the official source.
- The source-parsed matrix matches the archived CSV entry by entry.
- The q=0 AFH package response agrees with `A^2/4` to `8.3e-5`, consistent with finite precision of the printed density matrix.
- The physical equal-pn response is normalized to `A^2` at q=0.
- Selected radial/angular amplitudes agree with an independent 60-digit `mpmath` evaluation of the AFH finite sums at relative/absolute precision better than `2e-11`.
- The script is covered by six regression tests.

## 7. Scope

This is the Xe-131 nuclear response only. It is not yet the full three-body differential cross section, not the four benchmark calculation, not a natural-xenon isotope sum, and not a halo average.

The manuscript currently writes `R_A = 4 pi W_M^{00}/(2J_A+1)` and `R_A(0)=A^2` while citing AFH. If `W_M^{00}` denotes the unmodified AFH package response, these two statements differ by a factor of four. Before using the response in the final cross section, either:

1. redefine `R_A = 16 pi W_M^{00}_AFH/(2J_A+1)` for equal physical proton/neutron couplings; or
2. retain the AFH response convention and carry the compensating factor four explicitly in the coupling/particle-response prefactor.

This convention decision must be made before the full Figure 2 cross-section integration is finalized.

