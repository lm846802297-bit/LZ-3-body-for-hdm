> **Historical / legacy diagnostic — not the adopted B baseline.**
>
> The numerical values below were produced with the earlier raw-flavor
> normalization, alternate isoscalar-z-expansion form factors, static
> transfer prescription \(t_N=-Q_A^2\), and the legacy \(9W_M\)
> denominator. They are preserved unchanged for provenance. The label
> “pointlike” in the historical text should be read as the raw-current
> reference, not as a point nucleus: the AFH \(W_M\) response is finite-size.
> The adopted B calculation uses \(t_N=t_A=-2m_AE_R\), effective
> \(\widehat F_i=F_i^{uds}/3\), and reports A/B/C separately. See
> [FORM_FACTOR_BASELINE_COMPARISON.md](FORM_FACTOR_BASELINE_COMPARISON.md)
> and the new B-baseline result record when its rerun passes CI.
>
> No CSV, numerical value, workflow ID, or artifact hash in this historical
> record has been overwritten.

# Xe-131 fixed-speed charge-sector differential cross-section ratio

**Status:** PASS — workflow 44262472992, commit
a25efe7025f2cc0d530685291146248fb24f64aa.

## 1. Scope and benchmark

This is a fixed-speed Xe-131 ratio, not an absolute cross section or halo
average. The benchmark is:

| Parameter | Value |
|---|---:|
| \(m_{\chi_1}\) | 1000 GeV |
| \(m_s\) | 300 keV |
| \(v_\chi\) | 776 km/s |
| \(g_2\) | 1 |
| Target | Xe-131 |
| Width schemes | pole, running |

The benchmark-specific mass splitting is 450 keV at \(E_R=200\) keV and
362 keV at \(E_R=267\) keV.

The numerator includes native AFH v6.0 \(M,\Phi'',M\Phi''\) responses,
finite-\(t_N\) Dirac--Pauli coefficients \(c_M,c_{\Phi''}\), and the signed
interference. The denominator is the original pointlike \(9W_M\) baseline:
\[
\mathcal Q(E_R)=
\frac{(d\sigma/dE_R)_{\rm finite-t_N,\ M+\Phi''}}
     {(d\sigma/dE_R)_{\rm pointlike,\ M}}.
\]

## 2. Numerical result

| \(E_R\) | \(\Delta m\) | \(\mathcal Q(E_R)\) | Relative change |
|---:|---:|---:|---:|
| 200 keV | 450 keV | 0.7783093394 | -22.1691% |
| 267 keV | 362 keV | 0.6492159107 | -35.0784% |

The result is identical for pole/running width choices within numerical
precision: the ratio max-minus-min is \(2.22\times10^{-16}\) at 200 keV
and \(1.11\times10^{-16}\) at 267 keV. The absolute \(d\sigma/dE_R\)
would still depend on the width through the common phase-space factor.

## 3. Matched charge coefficients and AFH response ratios

| Quantity | 200 keV | 267 keV |
|---|---:|---:|
| \(q_A\) (GeV) | 0.220825559966 | 0.255146745386 |
| \(F_1^V(t_N)\) | 2.66316341 | 2.56388626 |
| \(F_2^V(t_N)\) | -0.46805344 | -0.44977451 |
| \(c_M\) | 2.65122188 | 2.54852325 |
| \(c_{\Phi''}\) | 0.02388306 | 0.03072600 |
| \(W_{\Phi''}/W_M\) | 0.03695594 | 19.84506258 |
| \(W_{M\Phi''}/W_M\) | -0.19120930 | -4.28296439 |
| \(Q_{\Phi''}\), relative to finite-\(t_N\) M-only | 0.99655805 | 0.89961039 |
| finite-\(t_N\) M-only / pointlike M | 0.78099749 | 0.72166342 |
| full coherent charge ratio | 0.77830934 | 0.64921591 |

The coherent charge kernel is
\[
K_{\rm ch}=L_C^{(3)}
\left[c_M^2W_M+2c_Mc_{\Phi''}W_{M\Phi''}
+c_{\Phi''}^2W_{\Phi''}\right].
\]
The interference is negative at both recoil points and is especially
important near the \(W_M\) cancellation region at 267 keV.

## 4. Reconciliation with the historical percentages

The earlier \(-21.48\%\) and \(-34.24\%\) values are legacy
\(F_1^2\)-normalization diagnostics, not the final \(c_M\)-matched
coherent ratio. On the updated exact-q points, the legacy \(F_1^2\)
ratios are \(-21.4664\%\) and \(-34.2933\%\).

The current calculation uses the Darwin--Foldy matched coefficient
\[
c_M=F_1^V+\frac{t_N(F_1^V+2F_2^V)}{8m_N^2},
\]
rather than replacing \(c_M\) by \(F_1^V\), and retains the
\(M-\Phi''\) interference. This accounts for the main shift to
\(-22.1691\%\) and \(-35.0784\%\). The small difference between the
historical values and same-q legacy values also reflects the updated
Xe-131 mass/q input.

The adopted mass convention is
\[
m_A=(m_{\rm atom}-Z m_e)u,
\]
using \(m_{\rm atom}=130.90508406\,u\), which gives
\(m_A=121.90971983538435\) GeV. This convention does not add a separate
electronic binding-energy correction; it is recorded explicitly so that
later mass updates can be compared consistently.

## 5. Continuity and phase-space checks

The calculation uses the conditional continuity-reduced Coulomb weight
\[
L_C=L_{00}-\frac{E_R}{Q_A}(L_{03}+L_{30})
+\left(\frac{E_R}{Q_A}\right)^2L_{33}.
\]
The point-nucleus direct/reduced identity is a kinematic and metric
convention check; it does not prove the many-body one-body current is
dynamically conserved.

| \(E_R\) | Width | \(L_C/L_{00}-1\) | Medium/high \(L_C\) difference |
|---:|---|---:|---:|
| 200 keV | pole | \(-4.35056\times10^{-6}\) | \(1.9021\times10^{-10}\) |
| 200 keV | running | \(-4.35098\times10^{-6}\) | \(1.9804\times10^{-10}\) |
| 267 keV | pole | \(-5.03498\times10^{-6}\) | \(4.7227\times10^{-10}\) |
| 267 keV | running | \(-5.03395\times10^{-6}\) | \(3.0465\times10^{-10}\) |

The common \(L_C\) factor cancels from the ratio. It does not cancel from
an absolute differential cross section.

## 6. Provenance

- Workflow: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44262472992
- Artifact ID: 14408816831
- Artifact name: xe131-fixed-speed-charge-sector-dsigma-ratio
- Artifact SHA-256: 3d63f0d4896946129e1692ee0915da9b6d791323f65da85d0ee242bc1ae498bd
- Native AFH archive commit: e6d9dee3527cab200ee6b21198d577b987282fac
- Original Wolfram export commit: 54e1ff10bba0cbffe7acc6af428014415c708475
- Native CSV canonical-LF SHA-256:
  b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff
- Metadata canonical-LF SHA-256:
  ad8231ec92c71faf12631534871e192bc3000601514c2a369fc84d963bfa9887
- Validation canonical-LF SHA-256:
  6d199ac9fd4d7fdace93292d1dded1c98d9f49c2836244ee9d2e3ddd334e8333

## 7. Explicit limitations

This result is only the fixed-speed Xe-131 Coulomb-sector ratio. It does
not include native AFH \(\Delta,\Sigma',\Sigma''\) transverse multipoles,
the complete eight-response three-body contraction, halo velocity
integration, natural-xenon isotope summation, detector response, or an
absolute coupling-normalized rate. The seven-isotope/eight-response native
Wolfram gate remains a separate pending task.


## 8. Independent rerun after archive hash-chain repair

The same calculation was rerun after the Xe-131 metadata/validation
checksum repair and the final archive provenance pin. Workflow
44264272807 completed SUCCESS and reproduced the same ratios:

| \(E_R\) | \(\mathcal Q(E_R)\) | Relative change |
|---:|---:|---:|
| 200 keV | 0.778309339441481 | -22.1690660559% |
| 267 keV | 0.649215910707624 | -35.0784089292% |

The width-scheme ratio spreads are \(2.22\times10^{-16}\) and
\(1.11\times10^{-16}\), respectively. The rerun's native-input provenance
records the explicit policy “UTF-8 text normalized to LF before SHA-256”,
the unchanged native CSV canonical-LF hash
b1b65708cd103058c3bcaea50bf65550d5671a88e97000b94f2536fbc60a59ff,
metadata hash
ad8231ec92c71faf12631534871e192bc3000601514c2a369fc84d963bfa9887,
and validation hash
6d199ac9fd4d7fdace93292d1dded1c98d9f49c2836244ee9d2e3ddd334e8333.

- Workflow: https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/44264272807
- Artifact ID: 14408938287
- Artifact SHA-256: b1e2e7db3241e88f7230de4f17213d652fb5de1dd696378a68b54e916460abe1

This rerun changes no physics input or response data; it independently
confirms the previous numerical result with the repaired provenance chain.
