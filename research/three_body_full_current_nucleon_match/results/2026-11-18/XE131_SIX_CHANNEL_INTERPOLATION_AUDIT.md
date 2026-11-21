# Xe-131 six-channel response interpolation audit

> **Baseline clarification (2026-11-19):** The interpolation-stability checks remain useful for the AFH response grid, but this artifact predates the adopted B normalization. Its ratio denominator and form-factor prescription must not be treated as the current B production baseline; rerun the recoil scan with Bishara B and report B/A, C/B, and C/A separately.

**Status: PASS_LOCAL_INTERPOLATION_STABILITY_DIAGNOSTIC.**  
**Scientific promotion:** not a native dense-q AFH validation.  
**Source scan:** [workflow 44307471788](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44307471788), artifact 14430267797.  
**Source commit used by that run:** \`f5e22bcb0f1a3d215724168397737a505b945824\`.

## 1. Why this audit was added

The six-channel fixed-speed Xe-131 scan showed a narrow recoil feature around
\[
E_R\simeq 268\text{--}270~\mathrm{keV},\qquad q_A\simeq0.256~\mathrm{GeV}.
\]
The native AFH charge response \(W_M\) has a diffraction minimum in this
region, while the signed \(W_{M\Phi''}\) response crosses zero nearby.
The scan originally used PCHIP interpolation on a 2,401-node response grid
with \(\Delta q_A=0.00025~\mathrm{GeV}=0.25~\mathrm{MeV}\).

A PCHIP-versus-linear comparison alone is not an adequate interpolation
error estimate near a response minimum or a signed zero crossing. This
audit therefore compares PCHIP against local Chebyshev polynomial
interpolants constructed from the same archived AFH grid.

## 2. Inputs and provenance

| Item | Value |
|---|---|
| Fixed-speed scan workflow | 44307471788 |
| Scan artifact | 14430267797 |
| Scan CSV SHA-256 | \`50cbb459f91ae0b72361e7b626ad7da8d27ebc824f4974e2ac9e1c61e003c28c\` |
| Response-grid CSV SHA-256 | \`74ee7ca4897a22c5b5b55fdabb3c009d2947819a098df2d006ca44730c209806\` |
| Scan metadata SHA-256 | \`0e594d518d74df82fa44b29f5112843f7a48ebd38c7c4240664ff3b453e22af3\` |
| Recoil scan rows | 140 |
| AFH response grid | 2,401 points, \(0\le q_A\le0.6~\mathrm{GeV}\) |
| Response-grid spacing | \(0.00025~\mathrm{GeV}\) |
| Channels | \(M,\Phi'',M\Phi'',\Delta,\Sigma',\Sigma'\Delta\) |

The particle-side phase-space tensors are not reintegrated in this audit.
The coefficients multiplying the six nuclear responses are reconstructed
from the archived per-channel kernel terms and the corresponding archived
PCHIP response values, then held fixed while the response interpolation is
changed.

The three charge responses come from the provenance-pinned native Xe-131
AFH archive. The three spatial responses are source-translated P3-B Python
outputs and remain marked
\`PROVISIONAL_SOURCE_TRANSLATED_AFH_SPATIAL_RESPONSES\`; they are not
native-Wolfram validated.

## 3. Interpolation method

For each of the 140 recoil-scan momentum transfers, the audit evaluates:

- PCHIP on the original 2,401-point response grid;
- a degree-8 local Chebyshev polynomial using the 11 nearest q nodes;
- a degree-10 local Chebyshev polynomial using the 13 nearest q nodes.

The local coordinate is rescaled by the largest selected-node distance
from the target q before fitting. The degree-8/degree-10 comparison is an
internal stability diagnostic for the local polynomial approximation.
It is not an independent AFH calculation and cannot replace a denser
native \`ResponseNuclear\` evaluation.

The script also propagates the alternative responses through the same
six-channel particle-side coefficients and independently checks positivity
of the diagonal responses and both response-level Cauchy--Schwarz bounds.

## 4. Results

### 4.1 PCHIP versus local degree-10 interpolation

| Response | Maximum absolute difference | Maximum relative difference* |
|---|---:|---:|
| \(W_M\) | \(1.89759\times10^{-5}\) | \(1.68466\%\) |
| \(W_{\Phi''}\) | \(1.88338\times10^{-6}\) | \(0.00993\%\) |
| \(W_{M\Phi''}\) | \(9.28707\times10^{-7}\) | \(0.07404\%\) |
| \(W_\Delta\) | \(7.53513\times10^{-11}\) | \(7.22\times10^{-7}\) |
| \(W_{\Sigma'}\) | \(1.40709\times10^{-9}\) | \(1.99\times10^{-6}\) |
| \(W_{\Sigma'\Delta}\) | \(1.88981\times10^{-9}\) | \(1.33\times10^{-6}\) |

\*The relative-difference denominator is floored at \(10^{-12}\) times
the maximum absolute value of the corresponding response on the full grid,
so signed zero crossings do not produce meaningless divergences.

The largest \(W_M\) difference occurs at
\[
E_R=269.5~\mathrm{keV},\qquad
q_A=0.2563384708~\mathrm{GeV}.
\]
At this point,
\[
W_M^{\rm PCHIP}=1.1263953\times10^{-3},\qquad
W_M^{\rm Cheb10}=1.1074193\times10^{-3}.
\]
PCHIP is about \(1.71\%\) above the local degree-10 estimate.

### 4.2 Degree-8 versus degree-10 stability

The local degree-8 and degree-10 interpolants agree extremely well over
the 140 scan q values. The maximum absolute differences are:

| Response | \(\max|W^{(8)}-W^{(10)}|\) |
|---|---:|
| \(W_M\) | \(1.39\times10^{-13}\) |
| \(W_{\Phi''}\) | \(2.00\times10^{-15}\) |
| \(W_{M\Phi''}\) | \(1.78\times10^{-14}\) |
| \(W_\Delta\) | \(2.60\times10^{-17}\) |
| \(W_{\Sigma'}\) | \(3.47\times10^{-17}\) |
| \(W_{\Sigma'\Delta}\) | \(2.52\times10^{-17}\) |

The high-order local interpolation also preserves positive diagonal
responses and satisfies both
\[
|W_{M\Phi''}|\le\sqrt{W_MW_{\Phi''}},\qquad
|W_{\Sigma'\Delta}|\le\sqrt{W_\Delta W_{\Sigma'}}.
\]
The maximum positive Cauchy--Schwarz excess is zero at the stored
floating-point precision.

### 4.3 Effect on the contracted kernels

| Quantity | Maximum relative PCHIP-to-Cheb10 change |
|---|---:|
| Charge-sector kernel | \(1.65891\%\) |
| Spatial-current kernel | \(5.92\times10^{-7}\) |
| Full six-channel kernel | \(1.65891\%\) |
| Full / pointlike-\(M\) ratio | \(0.11821\%\) |

The largest absolute-kernel shift occurs at the near-pole benchmark,
\[
\Delta m=362~\mathrm{keV},\quad E_R=269.5~\mathrm{keV},
\]
where the degree-10 local response interpolation changes the full
charge-dominated kernel by \(1.6589\%\). The spatial kernel changes by
less than one part per million in this interpolation comparison.

The full/pointlike-\(M\) ratio is less sensitive because the \(W_M\)
dependence partly cancels between numerator and denominator. Its largest
relative change is \(0.1182\%\), at \(E_R=269.0~\mathrm{keV}\).

The maximum spatial-to-charge ratio itself is also stable at the scale
relevant here: PCHIP gives \(3.20868\times10^{-8}\), while the local
Chebyshev degree-10 responses give \(3.24854\times10^{-8}\), both at the
near-pole \(E_R=269.0~\mathrm{keV}\) running-width point. Thus the updated
interpolation estimate remains about 32 ppb; it does not change the
charge-dominance conclusion.

The earlier PCHIP-versus-linear comparison gave a maximum full-kernel
difference of \(4.73\%\) near \(E_R=268.5~\mathrm{keV}\). Linear
interpolation is therefore not adopted as the preferred interpolation
in the diffraction-minimum region. The \(22.45\%\) relative PCHIP/linear
difference reported for \(W_{M\Phi''}\) occurs close to its zero crossing
and should not be interpreted as a \(22.45\%\) uncertainty in the total
cross section.

## 5. Interpretation

The six-channel result remains qualitatively stable: the transverse
spatial-current contribution is tiny compared with the coherent charge
sector in this fixed-speed Xe-131 scan. The more relevant numerical issue
is the interpolation of the coherent charge response near the \(W_M\)
diffraction minimum.

The local degree-8/degree-10 agreement strongly supports the stability of
the local polynomial reconstruction from the archived grid, but it is
still an interpolation-only check. Since the two polynomial orders use
the same coarse response samples, this cannot establish the exact native
AFH response between grid nodes. The PCHIP-versus-Chebyshev spread should
be retained as an interpolation diagnostic, not silently absorbed into a
final error bar.

## 6. Required next calculation: dense native Xe-131 charge response

The next numerical gate is a direct native Wolfram evaluation of
\[
\mathrm{ResponseNuclear}[y,i,0,0],\qquad i=1,4,7,
\]
corresponding to \(M,\Phi'',M\Phi''\), for Xe-131 on
\[
0.2545\le q_A\le0.2575~\mathrm{GeV},
\qquad \Delta q_A=0.000025~\mathrm{GeV}.
\]
This is 121 q nodes and is ten times finer than the current grid.

The dense native values should be merged with the existing coarse native
grid, preserving the raw AFH package convention and applying the physical
equal-\(p=n\) factor four exactly once. Then rerun the fixed-speed
six-channel contraction around the dip, with the same phase-space tensor
and the same fixed benchmark parameters. Only that direct dense-q
calculation can close the interpolation question.

## 7. Reproducibility

The reusable audit implementation is
\`audit_xe131_six_channel_interpolation.py\`, with regression tests in
\`test_audit_xe131_six_channel_interpolation.py\`. The six-channel
workflow now runs this audit after generating the recoil scan and uploads
the audit CSV and JSON alongside the original response grid and kernel
table.

The audit's status is deliberately limited to
\`PASS_LOCAL_INTERPOLATION_STABILITY_DIAGNOSTIC\`. It does not promote
\`native_afh_validated\`, does not close the native spatial-response gate,
and does not validate the bound-nucleus covariant/q-frame/AFH amplitude
identity or a halo-integrated event rate.


## 8. Dense native export implementation status

The next calculation is now prepared in draft
[PR #63](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/pull/63).
It adds the Wolfram v6.0 exporter, metadata/hash validator, and unit tests.
The private control workflow
[xe131-afh-spatial-native.yml](https://github.com/lm846802297-bit/research-compute-control/blob/main/.github/workflows/xe131-afh-spatial-native.yml)
has also been updated. Its default source commit is
\`5afc500a3102b857dd16e29432db8e6e068d65d1\`, and its P3-B input is pinned
to run 44317358790 / artifact 14431903885.

The updated native workflow will:
1. run the seven-isotope/eight-response native export;
2. evaluate the 121-point dense Xe-131 \(M,\Phi'',M\Phi''\) grid;
3. compare all 13 overlapping q nodes with the coarse native Xe-131 export;
4. record the dense CSV, metadata, validation, and SHA-256 values in the
   run manifest and uploaded artifact;
5. continue with the Xe-129/Xe-131 native spatial multipole comparison.

The previously queued control run 44306907993 was dispatched before this
workflow update and therefore does **not** contain the dense export step.
A fresh manual workflow dispatch is required. The Windows self-hosted
runner with labels \`Windows\`, \`X64\`, and \`research-gpu\` must be online.
No native dense-q PASS is claimed yet.
