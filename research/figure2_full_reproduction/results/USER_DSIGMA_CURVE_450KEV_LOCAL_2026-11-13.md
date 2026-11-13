# Fixed-speed Xe-131 dσ/dE_R: local result record (2026-11-13)

## Benchmark and scope

- mχ1 = 1 TeV; Δm = 450 keV; mχ2 = 1 TeV + 450 keV
- ms = 300 keV; mV = 10 GeV; v = 776 km/s
- (g1 g2 gVN)^2 = 1; zero-width prescription
- Xe-131 with mA = 131 u = 122.02572741702 GeV (A*u approximation, not AME2020)
- 105 fixed-speed recoil points: 130–650 keV in 5 keV steps
- AFH GCN and JJ55 response tables; exact spatial q = sqrt(2 mA ER + ER^2)

This is a single-isotope, fixed-speed cross-section diagnostic. It is not a natural-xenon halo fold, detector-level LZ prediction, event-rate calculation, or exclusion.

## Numerical results

The global maximum on the 5-keV scan is at ER = 175 keV:

| Response | max dσ/dER [cm²/keV] |
|---|---:|
| GCN | 1.874622684e-32 |
| JJ55 | 1.985254401e-32 |

A 1-keV local refinement gives the following sampled interior minima (not claimed as exact continuous minimizers):

| Response | First dip | Second dip |
|---|---:|---:|
| GCN | 269 keV: 1.717618811e-36 | 551 keV: 9.427717286e-37 |
| JJ55 | 270 keV: 1.676281693e-37 | 555 keV: 3.732300740e-38 |

The two response models share the same Eq. (6) kernel; the differences in the deep dips are nuclear-response effects.

## Validation

- All 105 grid points are kinematically open; 655 keV is closed.
- q spans 0.1781199204–0.3982886744 GeV, within the response tables' 0–0.6 GeV range.
- Each response table has 2,401 nodes with Δq = 0.25 MeV.
- R_A(0) = 17160.9875693 versus A² = 17161 (relative difference 7.24e-7).
- Independent SciPy PCHIP check at ten anchors: max absolute difference 3.553e-15; max relative difference 4.929e-14.
- Eq. (6) quadrature (20,16,12) versus (24,20,16), ten anchors: maximum relative change 7.346e-6.
- The χ2 s-channel pole is closed throughout the scan; minimum clearance is 85.663520 keV.
- Sampled four-momentum closure residual: ≤2.416e-13 GeV; sampled mass-shell/K² residual: ≤4.657e-10 GeV².

## Source provenance

- Eq. (6) kernel blob: `7c796b48c3f3c2cb9079ddbf1e632cc0b9ce207c`
- Response loader blob: `12b0f7c3f9408e2a58721e599f7fe1172def2848`
- GCN response blob: `2bbdcd8ae055803975cbcd18bb657c078e0f06a7`
- JJ55 response blob: `d35455e01f005941a84983a517e2440e26e0d0a7`

## Native local archive

The local archive contains the 105-point CSV, 1-keV minima refinement CSV, quadrature-convergence CSV, metadata JSON, validation report, and SHA256SUMS. All five listed file checksums were revalidated after correcting the minima table in the report. The native data archive still needs to be added to this branch before this PR is promoted from Draft.
