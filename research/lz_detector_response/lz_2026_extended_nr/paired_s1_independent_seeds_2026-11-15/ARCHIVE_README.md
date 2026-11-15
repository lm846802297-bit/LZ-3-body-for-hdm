# Paired S1 independent-seed 2D response archive

- Production run: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43721276233
- Production artifact: 14164652993
- Production artifact ZIP SHA-256: 26964920be1e89470075848e55c4ba488494f9ddc4e0421add4d07421227c62c
- Binning audit (archived first pass): https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43722459713
- Binning audit artifact: 14165305118
- Binning audit artifact ZIP SHA-256: 3b4a6ff0155422796d7045e068148f9fc334913cbbfbf06e7c97d36d384237a7
- Binning audit reproducibility rerun: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43722824029
- Reproducibility-rerun artifact: 14165550612
- Reproducibility-rerun ZIP SHA-256: 93f0b14355590c9aba8daec602cf21c44a8a818875e9a50257217b0587375bde
- The three native CSV/JSON payloads are byte-identical between the two binning-audit artifacts; only ZIP packaging metadata changes the whole-archive digest.
- Source commit for the NEST production: f1b4bf615e2c59192f31bd355b98595c4502b3b1
- Pinned NEST commit: 541b6430dae6ea289cf110c99f174a9187f7fdee
- Seeds: 20261117, 40261117, 60261117; 470,000 events per seed.

The archive commits all per-seed fold maps, rate summaries, split-half summaries,
ensemble maps, metadata, and exact binning-stability summaries. The three raw
event CSVs (about 367 MB uncompressed total) remain in the production artifact;
raw_event_artifact_SHA256SUMS.txt preserves their individual checksums.
The original ZIP digest above verifies the downloaded artifact as a whole.
