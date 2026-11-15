# Black 360-keV paired S1 upper-tail audit

**Status:** completed ten-independent-seed diagnostic; not an official LZ detector response or likelihood input.

The detailed methodology, numerical results, ten-threshold S1 tail scan, energy-resolved migration, independent S2-window closure, and limitations are in [REPORT.md](./REPORT.md).

## Main result

For the black \(m_s=360\ \mathrm{keV}\) benchmark over \(E_R=205\)--\(269.9\ \mathrm{keV}\), the Full S1 response shifts the upper S1 quantiles upward by roughly 1--2 phd. The S1 ROI efficiency changes by -0.5983% (GCN) and -0.5881% (JJ55), relative to Parametric. The effect is driven by net migration across the 600-phd S1 upper boundary.

All 1.3 million raw events in this black support pass the S1 coincidence and S2 threshold/ROI requirements. Thus the WS-ROI acceptance equals the S1 [3,600]-phd acceptance for this support.

## Provenance

- Source production: [run 43750948249](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43750948249), artifact 14176882910.
- Audit: [run 43762406779](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43762406779), artifact 14181285817.
- Audit ZIP SHA-256: fb1b06d77d9d4c58dd837ab9e657edbcc9e593856fbad6f30c70b1b4866bbe0d.
- Source production ZIP SHA-256: 606397d9eac594008630a18b97f1e72fbbfa1d157e34779de7ce5fd0fe5b8cb5.

The audit reuses the immutable ten-seed paired Parametric/Full S1 event production. It does not regenerate NEST events or change the detector configuration. Event weights close to the original exact per-bin integrated rates with a maximum relative residual of \(6.33\times10^{-15}\).

## Files

- **REPORT.md:** full audit report and interpretation.
- **black_s1_upper_tail_summary.csv:** 12 energy-band/model summary rows; nested values are JSON strings.
- **black_s1_upper_tail_per_seed.csv:** 120 seed-level rows.
- **black_s1_upper_tail_thresholds.csv:** 1,200 threshold rows.
- **black_s1_upper_tail_metadata.json:** canonical structured metadata and summary.
- **SHA256SUMS:** file checksums.

The audit is an EFT2024 NEST proxy diagnostic. It is not the official LZ waveform-level selected PDF and does not include DAQ, SS/DA, official FV, Skin/OD, live-time, or their covariance. No final likelihood or exclusion result is authorized by this study.
