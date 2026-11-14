# AFH natural-xenon isotope coverage and the Xe-124/Xe-126 input gap

## 1. Scope and decision

The AFH v6.0 default xenon implementation does **not** provide a nine-isotope natural-xenon response. Its SetIsotope default dispatch contains density matrices for

\[
A\in\{128,129,130,131,132,134,136\},
\]

and does not contain sdgXe124 or sdgXe126. The source does list the ground-state spins of \(^{124}\mathrm{Xe}\) and \(^{126}\mathrm{Xe}\) as zero, but a spin assignment is not a density matrix and does not determine the finite-\(q\) response.

The scientifically clean baseline is therefore:

1. compute the complete continuous AFH v6.0 response for the seven supported isotopes;
2. preserve the natural abundances without renormalizing those seven isotopes to unity;
3. report the missing \(^{124}\mathrm{Xe}\) and \(^{126}\mathrm{Xe}\) fractions explicitly;
4. evaluate a separately labelled Helm fallback for those two isotopes as a *hybrid model*, never as AFH data.

No density-matrix entries are to be extrapolated from \(A=128\) or \(130\), and no synthetic sdgXe124 or sdgXe126 array is to be inserted into the AFH source.

## 2. Source-level audit

The committed AFH v6.0 source is v6/dmformfactor-V6.m.

- IsotopicSpins contains \((Z,A,J)=(54,124,0)\) and \((54,126,0)\).
- The SetIsotope default branch has explicit assignments for Xe-128, Xe-129, Xe-130, Xe-131, Xe-132, Xe-134, and Xe-136.
- There is no sdgXe124 or sdgXe126 density-matrix array and no matching SetDMmatrixLength dispatch.
- The seven supported matrix lengths are 21, 39, 21, 67, 21, 21, and 21 entries, respectively.

Thus, the absence is an AFH v6.0 input-coverage limitation, not a missing spin lookup.

## 3. Natural abundance and coherent zero-momentum accounting

Using the isotope fractions archived in input/natural_xenon_isotope_weights.csv:

| Isotope | Natural atom fraction | AFH v6.0 default matrix |
|---|---:|---|
| Xe-124 | 0.000952 (0.0952%) | unavailable |
| Xe-126 | 0.000890 (0.0890%) | unavailable |
| Xe-128 | 0.019102 | available |
| Xe-129 | 0.264006 | available |
| Xe-130 | 0.040710 | available |
| Xe-131 | 0.212324 | available |
| Xe-132 | 0.269086 | available |
| Xe-134 | 0.104357 | available |
| Xe-136 | 0.088573 | available |

The two unsupported isotopes account for

\[
f_{124}+f_{126}=0.001842=0.1842\%
\]

of natural xenon atoms. The seven AFH-supported isotopes therefore cover 99.8158% of the atom fraction.

For an isoscalar coherent response normalized as \(R_A(0)=A^2\), the missing zero-momentum abundance-weighted coherent share is

\[
\delta_{A^2}(0)=
\frac{\sum_{A=124,126} f_A A^2}
     {\sum_{A\in\mathrm{natural\ Xe}} f_A A^2}
=1.6660\times10^{-3},
\]

so the seven-isotope set accounts for 99.8334% of this *zero-momentum coherent normalization*.

This \(A^2\)-weighted number is **not** a universal bound on the differential event-rate error at every recoil energy. At finite recoil, each isotope has its own exact spatial momentum \(q_A=\sqrt{2m_AE_R+E_R^2}\), minimum speed \(v_{\min,A}\), and halo support. Near a kinematic endpoint, isotope-dependent \(v_{\min}\) can change relative contributions. The rate-level impact must therefore be calculated with the isotope-specific masses and halo integral rather than inferred from abundance alone.

## 4. What the nuclear-response literature does and does not supply

### 4.1 Vietze et al. (2015): scalar-isoscalar xenon structure factors

L. Vietze, P. Klos, J. Menéndez, W. C. Haxton, and A. Schwenk, *Nuclear structure aspects of spin-independent WIMP scattering off xenon*, Phys. Rev. D **91**, 043520 (2015), DOI: [10.1103/PhysRevD.91.043520](https://doi.org/10.1103/PhysRevD.91.043520).

The paper calculates leading scalar one-body spin-independent structure factors for the seven isotopes Xe-128, 129, 130, 131, 132, 134, and 136. Its Table II gives fit coefficients for precisely that set; it does not provide Xe-124 or Xe-126 density matrices. The paper finds good agreement with Helm at low momentum transfer, while noting that at higher momentum transfer the Helm curve lies somewhat above the shell-model result and its second minimum is shifted.

This is directly relevant to the leading coherent M-type response, but it is not an AFH v6.0 completion for Xe-124/Xe-126.

### 4.2 Abdel Khaleq et al. (2024): shell-model interaction dependence

R. Abdel Khaleq, G. Busoni, C. Simenel, and A. E. Stuchbery, *Impact of shell model interactions on nuclear responses to WIMP elastic scattering*, Phys. Rev. D **109**, 075036 (2024), DOI: [10.1103/PhysRevD.109.075036](https://doi.org/10.1103/PhysRevD.109.075036), arXiv: [2311.15764](https://arxiv.org/abs/2311.15764).

This NuShellX study also lists Xe-128, 129, 130, 131, 132, 134, and 136, not Xe-124 or Xe-126. It reports that the leading standard spin-independent response is only weakly sensitive to the shell-model interaction compared with several other response channels. It therefore supports a phenomenological scalar-response cross-check, but does not provide the two missing isotope matrices.

## 5. Helm fallback: definition and limits

For a separately labelled hybrid estimate, use the standard Helm scalar-isoscalar response

\[
R_A^{\mathrm{Helm}}(q)=A^2 F_{\mathrm{Helm}}^2(q),
\]

\[
F_{\mathrm{Helm}}(q)=
3\,\frac{j_1(qr_n)}{qr_n}
\exp\!\left[-\frac{(qs)^2}{2}\right],
\]

\[
r_n^2=c^2+\frac{7}{3}\pi^2a^2-5s^2,\qquad
c=(1.23A^{1/3}-0.60)\,\mathrm{fm},
\quad a=0.52\,\mathrm{fm},\quad s=1.0\,\mathrm{fm}.
\]

Here \(q\) in the Bessel argument is converted to \(\mathrm{fm}^{-1}\) using \(\hbar c=0.1973269804\,\mathrm{GeV\,fm}\). The response is normalized so that \(R_A^{\mathrm{Helm}}(0)=A^2\).

The Helm curve is a phenomenological nuclear-density model. It must be stored in a separate column or file with an explicit Helm label. It must not be mixed into an AFH-only table or used to claim a nine-isotope AFH result.

For the supported isotopes, compare Helm and AFH on the same exact-\(q\) grid before assigning a model-spread uncertainty to the missing isotopes. In particular, do not infer that a low-\(q\) agreement guarantees agreement around a high-\(q\) diffraction minimum.

## 6. Required numerical comparison

After the seven-isotope AFH continuous grid is generated and validated:

1. compute the strict seven-isotope AFH natural-xenon spectrum using the original natural atom fractions;
2. compute a nine-isotope hybrid spectrum with Helm only for Xe-124 and Xe-126;
3. compute a conservative missing-isotope envelope by replacing their Helm response with the coherent upper normalization \(R_A(q)=A^2\), while preserving their isotope-specific masses and \(v_{\min}\);
4. compare strict-AFH and hybrid spectra over the actual recoil-energy grid and each benchmark halo/kinematic setup;
5. report both absolute rate changes and relative changes, especially near any response minimum or kinematic endpoint.

The envelope in item 3 is a deliberately conservative coherent-response diagnostic, not an alternative nuclear calculation.

## 7. Reporting vocabulary

Use these labels consistently:

- **AFH-7**: seven supported isotopes, all using AFH v6.0 default density matrices; natural abundances are not renormalized.
- **Hybrid-9 (AFH-7 + Helm-2)**: AFH for the seven supported isotopes and Helm for Xe-124/Xe-126.
- **Helm-9**: Helm for all nine naturally occurring isotopes, used only as a separate model comparison.

Do not call AFH-7 or Hybrid-9 a “complete nine-isotope AFH calculation.”
