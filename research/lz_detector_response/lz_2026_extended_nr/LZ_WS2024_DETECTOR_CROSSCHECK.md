# LZ WS2024 NEST detector-class cross-check against the 2026 paper

**Status:** strong candidate detector baseline for an NR-only pilot; not yet certified as the exact 2026 analysis configuration.

## 1. Source

Pinned source:
- Repository: https://github.com/NESTCollaboration/nest
- Commit: `423b9745a5bfbb0402514f1d7955e67445de0810`
- File: [`include/Detectors/LZ_WS2024.hh`](https://github.com/NESTCollaboration/nest/blob/423b9745a5bfbb0402514f1d7955e67445de0810/include/Detectors/LZ_WS2024.hh)

The file identifies itself as the LZ SR3/WS2024 detector input and says its response/yield vectors were adjusted to match tritium and D-D calibration data. It recommends NEST v2.4.0. The 2026 paper instead states that its final detector response uses NEST v2.4.5, so the detector class is a candidate input, not proof of exact 2026 provenance.

## 2. Direct detector settings in the source

| Setting | LZ_WS2024 value |
|---|---:|
| (g_1) | 0.1122 phd/photon |
| Gas gain (g_{1,gas}) | 0.076404 phd/gas photon |
| Double-photoelectron probability | 0.214 |
| Raw S2 threshold (before lifetime correction) | 783 phe |
| Gas field | 8.301178 kV/cm |
| Gas gap | 8 mm |
| Temperature | 175.9 K |
| Pressure | 1.86 bar |
| Drift field, `FitEF` | 96.5 V/cm |
| Electron lifetime | 9000 μs |
| `OldW13eV` | true |
| Top drift | 1461 mm |
| Anode | 1469 mm |

The detector class includes analytic position-dependent `FitS1` and `FitS2` corrections. These are not a substitute for confirming whether the 2026 analysis used exactly the same spatial-response maps.

## 3. Recompute (g_2) from the NEST source formula

Using the pinned `CalculateG2` implementation and the detector-class settings:

- Xenon gas density from the source Van der Waals equation: (0.01719893\,\mathrm{g/cm^3}).
- Liquid extraction field after the dielectric conversion: (4.49278\,\mathrm{kV/cm}).
- Extraction efficiency: (0.726195).
- Electroluminescence yield: (613.1904) gas photons per extracted electron.
- Single-electron size: (46.8502\,\mathrm{phd/electron}).
- Resulting (g_2=34.0224\,\mathrm{phd/electron}).

Comparison with the 2026 paper:

| Quantity | NEST WS2024 class / recomputed | 2026 paper | Difference |
|---|---:|---:|---:|
| (g_1) | 0.1122 | (0.110\pm0.002) | +1.10 (sigma) |
| (g_2) | 34.0224 | (34.5\pm1.1) | -0.43 (sigma) |
| Raw S2 threshold (before lifetime correction) | (783/(1+0.214)=644.98\,\mathrm{phd}) | 645 phd | -0.02 phd |
| Drift field | 96.5 V/cm | Table S3 reference: 97 V/cm | -0.5 V/cm |

The close agreement in (g_2) and the raw-threshold conversion are useful consistency checks. The 644.98 phd value is not the threshold boundary on corrected S2c, because NEST applies the threshold before lifetime and position corrections. These checks do not alone establish that the full detector response is identical.

## 4. What can be reused for an NR-only candidate simulation

The public detector class exposes `get_nr_er_width_params()`. Its NR-relevant entries are:
[
(0,1,2,3,4,5,11,12)
=(0.404,0.393,0.0383,0.497,0.1906,2.220,0,0).
]

The 2026 Table S5 15-entry NR mean-yield vector can be passed explicitly to `FullCalculation`, overriding the older 12-entry mean-yield vector stored in the detector class. This gives a well-motivated candidate combination:
- 2026 Table S5 mean NR yields;
- LZ WS2024 tuned NR fluctuation settings;
- LZ WS2024 detector response as the candidate geometry/gain model.

## 5. Important limitations

1. The detector header recommends NEST v2.4.0, whereas the 2026 paper states NEST v2.4.5.
2. The 2026 paper's Table S5 replaces the old mean-yield vector; it must be supplied explicitly.
3. The 2026 paper introduces a double-skewed-Gaussian ER fluctuation model in Table S4. The 13-element WS2024 width vector does not encode that full ER model; it is therefore not suitable by itself for reproducing ER calibration/background PDFs.
4. The WS2024 detector class's analytic spatial corrections have not been proven identical to the final 2026 spatial response.
5. The HEPData ZIP contains observed science/veto samples and limit tables, not calibration event samples or a detector configuration.

## 6. Recommended interpretation

Use this detector class and its tuned NR width entries as the **primary candidate for an NR-only event-level pilot**, and run the generic NEST NR-width defaults as a controlled comparison. Do not call either output an exact LZ 2026 response reproduction until the 2026 NEST configuration/resource or collaboration confirmation is obtained and the calibration-band checks are passed.

Relevant 2026 paper statements:
- (g_1=0.110\pm0.002), (g_2=34.5\pm1.1), calibration channels, and NEST v2.4.5 are given in the main detector section.
- Table S3 references 97 V/cm.
- Table S4 gives the final double-skewed-Gaussian ER fluctuation parameters.
- Table S5 gives the 15-parameter NR mean light-/charge-yield model.


## 7. Important distinction: raw S2 threshold versus corrected S2c

The 644.98 phd value above is only the detector's configured threshold (783 phe) converted to phd by removing the double-photoelectron factor. NEST's GetS2 implementation tests the threshold against the **raw pulse area in phe**, then forms the reported S2c by applying the electron-lifetime correction and position correction. Therefore 644.98 phd is not the threshold boundary on the corrected S2c observable.

For the pilot's reference-depth position, the spatial correction is unity and the drift time is the detector's (dt_{cntr}=525\,\mu\mathrm{s}). With the WS2024 electron lifetime (9000\,\mu\mathrm{s}), the corresponding threshold boundary in corrected S2c is

[
S2c_{\rm threshold}
=\frac{783}{1+0.214}\exp\left(\frac{525}{9000}\right)
=683.72\,\mathrm{phd}.
]

The 645 phd comparison to the paper must therefore be interpreted as a raw-threshold conversion only. Whether the paper's quoted 645 phd is defined before or after the same lifetime correction must be checked against its precise observable definition; do not identify it automatically with the corrected S2c cut. The event driver preserves NEST's sign-based threshold flag and records both the raw-threshold phd equivalent and the reference-depth corrected-S2c threshold.
