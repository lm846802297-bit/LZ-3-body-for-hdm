# Repository-wide physics, variable-naming and historical-result audit

**Date:** 2026-11-19  
**Repository:** lm846802297-bit/LZ-3-body-for-hdm  
**Scope:** default main, P3/P4 base branch, and open provisional P4 branch (PR #67).

## 1. Executive conclusion

The repository contains three physically distinct layers. They must never be collapsed into one generic “form factor” label.

1. **Single-nucleon Dirac–Pauli form factors:** \(F_1^{V,N}(t_N)\), \(F_2^{V,N}(t_N)\), or their effective-coupling-basis versions \(\widehat F_1^N,\widehat F_2^N\). These describe the quark-current matrix element inside one proton or neutron.
2. **Finite-size nuclear response:** \(W_M^{\rm phys}(y_A)\), with \(y_A=b_A^2Q_A^2/4\). This describes the coherent spatial distribution of nucleons in the whole nucleus.
3. **Other AFH nuclear responses:** \(W_{\Phi''},W_\Delta,W_{\Sigma'},W_{\Sigma''},\ldots\), plus allowed interference responses. These describe distinct nuclear multipole/operator channels.

Therefore:
- \(F_1,F_2\) are **nucleon form factors**, not nuclear form factors.
- \(W_M(y_A)\) is a **finite-size AFH nuclear response**, not a point-nucleus response.
- \(W_M(0)\), \(A^2\), and a point-target current contraction are not substitutes for finite-\(q_A\) AFH response.
- “Point-nucleus” contractions may remain as algebraic kinematic diagnostics; they must not be confused with the physical AFH response.

The adopted production baseline is B:
\[
\frac{d\sigma_B}{dE_R}
=\mathcal P_3 L_C^{(3)}
\widehat c_M(t_N)^2W_M^{\rm phys}(y_A),
\]
with no \(\Phi''\), \(\Delta\), \(\Sigma'\), \(\Sigma''\), or interference response added to B.

## 2. Canonical variable dictionary

| Symbol / code field | Canonical meaning | Must not mean |
|---|---|---|
| F1V_quark_sum, F2V_quark_sum | Raw universal u+d+s single-nucleon form factors | Nuclear response |
| F1N_effective, F2N_effective | Effective nucleon form factors \(\widehat F_i=F_i^{uds}/3\) in the external \(g_{VN}\) basis | Raw flavor sum |
| \(t_N\) | Nucleon-current invariant transfer | Spatial momentum squared |
| \(q_A^\mu,Q_A^2=|\mathbf q_A|^2\) | Nuclear four-transfer and spatial magnitude | Nucleon invariant transfer |
| \(t_A=q_A^2\) | Nuclear Lorentz-invariant transfer | \(-Q_A^2\) |
| \(W_M(y_A)\) | Finite-size AFH nuclear M response | Point-nucleus response or nucleon form factor |
| \(F_A(q_A)\) | Reserve for a scalar coherent whole-nucleus form factor in the manuscript | \(F_1^N,F_2^N\) |
| point_nucleus_contractions | Idealized point-target tensor/current identity for a convention check | Physical AFH \(W_M\) evaluation |

For the formal one-body impulse prescription:
\[
q_N^\mu=q_A^\mu,\quad
t_N=t_A=-2m_AE_R,\quad Q_N^2=-t_N=2m_AE_R.
\]
The exact spatial nuclear momentum is instead
\[
Q_A^2=2m_AE_R+E_R^2,\quad y_A=b_A^2Q_A^2/4.
\]
In the q-aligned frame and metric \((+---)\), formal B uses
\[
q_A^\mu=(E_R,0,0,Q_A),\qquad q_N^\mu=q_A^\mu.
\]
Here \(q_N^\mu\) denotes the external four-momentum flowing through the
one-body nucleon-current vertex. For a free on-shell impulse benchmark it
can be represented as \(k_N'^\mu-k_N^\mu\); for a bound nucleus the B
prescription assigns the external nuclear transfer to the one-body current
and does not reconstruct each nucleon's microscopic off-shell momentum
change. The static diagnostic instead assigns
\(q_{N,\rm static}^\mu=(0,0,0,Q_A)\), giving
\(t_{N,\rm static}=-Q_A^2\); it is a distinct low-energy approximation
and must not enter formal B production. B/P4 outputs serialize
\texttt{qA\_four\_vector\_GeV}, \texttt{qN\_four\_vector\_GeV},
\texttt{tA\_GeV2}, and \texttt{tN\_GeV2} separately.

The mediator propagator uses
\[
(m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2,
\]
not \((m_V^2+Q_A^2)^2\).

## 3. Independent normalization ledgers

Two factors are independent and each must be applied exactly once.

### 3.1 Quark-to-effective-nucleon coupling

For the universal u+d+s current:
\[
g_{VN}=3g_{Vq},\quad
F_1^{uds,N}(t_N)=3+8.392t_N+O(t_N^2),\quad
F_2^{uds,N}(t_N)=-0.552+O(t_N).
\]
When the public rate prefactor already contains \((g_1g_2g_{VN})^2\), current coefficients must use
\[
\widehat F_i^N=F_i^{uds,N}/3,\quad
\widehat F_1(0)=1,\quad\widehat F_2(0)=-0.184.
\]
Using raw \(F_i^{uds}\) in those coefficients duplicates the factor three and makes an absolute rate too large by nine. The adopted B truncation uses the available first-order Dirac slope and the available leading constant Pauli term; it does not invent an \(F_2(t_N)\) slope.

### 3.2 AFH raw-to-physical response normalization

The AFH v6.0 raw isoscalar response has zero-momentum normalization \(A^2/4\); the physical equal-proton/equal-neutron response has normalization \(A^2\). The response conversion is \(R_{\rm phys}=4C_0(A)R_{\rm raw}\), where \(C_0(A)=A^2/[4R_{M,\rm raw}(0)]\) corrects finite-decimal OBDME normalization. The factor four and \(C_0\) are each applied once. They are independent of the quark-to-nucleon factor three. The native Xe-131 loader now derives and applies \(C_0(131)\) from the raw q=0 M response; the seven-isotope native loader does the same per isotope. The Xe-131 six-channel scan compares this native \(C_0\) with P3-B and no longer multiplies the charge responses a second time.

For Xe-131, the pinned native charge CSV gives
\(C_0(131)=1.0000825298069376\), which matches the P3-B spatial
artifact metadata exactly at the stored precision. The six-channel scan
now checks this equality before combining charge and spatial responses.

Do not add a second Helm factor on top of AFH \(W_M(y_A)\).

## 4. Confirmed findings and fixes made on the research branches

### P0 — PR #67 propagator invariant (corrected in P4 branch)

The previous provisional P4 code used \((m_V^2+Q_A^2)^2\) in the mediator denominator. This substitutes the spatial transfer for the Lorentz invariant. It has been changed to a dedicated denominator helper implementing \((m_V^2-t_A)^2=(m_V^2+2m_AE_R)^2\), and the exact mass-shell relation \(E_R^2-Q_A^2=-2m_AE_R\) is checked.

### P0 — PR #67 factor-nine absolute normalization (corrected in P4 branch)

The previous pointlike_M reference was \(F_1(0)^2L_CW_M=9L_CW_M\). This was not pointlike nuclear structure: it retained finite-size AFH \(W_M\). It also used raw quark-summed \(F_1(0)=3,F_2(0)=-0.552\) while the external coupling product was already in the \(g_{VN}=3g_{Vq}\) basis.

The P4 branch now divides the raw flavor sum by three before constructing coefficients and exposes explicit A/B/C fields:
- A: q=0 effective nucleon current times finite-size \(W_M\);
- B: finite-\(t_N\) effective nucleon current times the same \(W_M\), M only;
- C: B plus \(\Phi''\) and signed M-\(\Phi''\) interference.

Plot labels, isotope rows, total-rate fields, workflow comparison keys, and P4 documentation were changed to A/B/C. The old pointlike_M field is not emitted by the corrected P4 path.

### P0 — AFH common OBDME normalization C0 (corrected in P4 branch)

The native Xe-131 and seven-isotope loaders now derive
\(C_0(A)=A^2/[4R_{M,\rm raw}(0)]\) from the raw AFH M response, apply
the same factor once to every response channel after the independent
factor four, and enforce \(R_M^{\rm phys}(0)=A^2\). The Xe-131
six-channel scan compares the native and P3-B C0 values and no longer
applies C0 twice to the charge sector. The Xe-131 fixed-speed and absolute
benchmark paths inherit the corrected native loader.

### P0 — PR #67 formal nucleon transfer (corrected in P4 branch)

The previous P4 code evaluated bishara_linear at \(Q_A^2\), i.e. the static \(t_N=-Q_A^2\) diagnostic. The corrected production path passes \(t_N=t_A=-2m_AE_R\) into form-factor and current-coefficient routines. The static prescription is no longer the production path.

### P1 — Effective-nucleon labels in AFH coefficient extraction (corrected on P3/P4 branches)

The P3 coefficient routine defaults were already \(\widehat F_1=1,\widehat F_2=-0.184\), but serialized fields were named F1V/F2V, which could be mistaken for the raw universal quark sum. They were renamed F1N_effective/F2N_effective (and corresponding input names), and the P3-C consumer now reads those explicit keys. The nucleon form-factor module also exposes RAW_F1_UDS0/RAW_F2_UDS0; the older F1V0/F2V0 names remain only as documented backward-compatible raw aliases. Regression examples now use effective values. The README spatial Eq. (107) coefficients were made consistent: every coefficient uses the same hatted effective nucleon form factors, rather than mixing raw \(F_1^V\) with hatted \(F_1,F_2\).

### P1 — P4 plotting and workflow labels (corrected in P4 branch)

The P4 plot and workflows now run bishara_linear as the adopted B prescription. A is generated as the internal q=0 reference in the same run; it is not selected as the P4 production form-factor input. The ratio plot distinguishes B/A, C/B, C/A, and provisional D-candidate comparisons.

## 5. Historical result classification

| Historical item | Correct interpretation | Permitted reuse |
|---|---|---|
| Original Mathematica AFH rate engine | Constant effective coupling times finite-size AFH \(W_M(y_A)\); A-like reference, with no explicit finite-\(t_N\) Dirac–Pauli insertion in the recorded production path | Historical A reference and provenance cross-check; not B |
| Old \(9W_M\) denominator / pointlike_M label | Finite-size AFH \(W_M\) multiplied by raw \(F_1^{uds}(0)^2=9\); not a point nucleus and over-normalized absolutely with external \(g_{VN}\) | Ratios may survive if numerator and denominator share the same factor-nine convention; absolute rates must be recomputed |
| Fixed-speed ratios 0.77830934 and 0.64921591 | Historical C/A ratios using earlier raw-current normalization and earlier form-factor prescription; not C/B | Dimensionless historical comparison only; not an absolute rate or adopted B result |
| Full-recoil ratios 0.99655805 and 0.89961039 | C/B charge-response correction at fixed finite-\(t_N\) nucleon-current prescription | Ratio-only diagnostic with original form-factor and interpolation provenance |
| Old \(F_1^2\) corrections -21.5% and -34.2% | Legacy simplified charge-kernel normalization diagnostics | Historical comparison only; superseded by matched-\(c_M\) calculations |
| Provisional seven-isotope P4 spectra before correction | Used raw q=0 form factor, wrong propagator invariant, and static \(t_N\) prescription | Do not use as B; recompute |
| Point-nucleus tensor-contraction residuals | Algebraic point-target convention/continuity checks | Valid as kinematic checks; not nuclear-response calculations |

Ratios must always state their denominator:
\[
B/A=\text{nucleon form-factor correction},\quad
C/B=\text{additional AFH charge-response correction},\quad
C/A=\text{combined change}.
\]
The historical 0.778/0.649 values are not interchangeable with 0.9966/0.8996.

## 6. Manuscript nomenclature and formula cross-check (2026-11-19)

The current `paper-source/main.tex` was reopened and checked against the
adopted B convention.

A separate conversation-uploaded `main.tex` was also inspected. It is a
different, longer manuscript version and is **not** the same file as the
repository's `paper-source/main.tex`. The uploaded version still uses
\(m_N\) as the nuclear mass in the recoil section, reuses \(m_N\) for the
generic point-target derivation, calls the whole-nucleus shape \(F_N(q)\),
and writes the raw AFH response while asserting \(A^2\) normalization
without the \(4C_0(A)\) conversion. It has not been copied over the
repository manuscript because that would risk replacing its newer B-aligned
content with a divergent draft. The authoritative manuscript source must
be confirmed before merging those two versions. The earlier audit statements about an overloaded
\(F_N\), nuclear \(m_N\), and an unconverted raw AFH response are stale
for the current branch; the manuscript already contains the corresponding
corrections:

1. **Whole-nucleus form factor:** the appendix uses \(F_A(q_A)\) for the
   normalized whole-nucleus density amplitude, with \(F_A(0)=1\). It
   explicitly distinguishes this object from the AFH response
   \(W_M^{\mathrm{phys}}\) and from the single-nucleon
   \(F_{1,2}^{V,N}(t_N)\).
2. **Mass symbols:** the manuscript uses \(m_A\) for the nucleus,
   \(m_N\) for the free nucleon in the Dirac--Pauli charge coefficient,
   and \(m_T\) for a generic pointlike Dirac target in the appendix,
   setting \(m_T=m_A\) when that target is the nucleus. No current
   occurrence uses \(m_N\) as the nuclear mass.
3. **AFH normalization:** the manuscript defines
   \(W_M^{00,\mathrm{phys}}=4C_0(A)W_M^{00,\mathrm{raw}}\), then
   defines \(\mathcal R_A=4\pi W_M^{00,\mathrm{phys}}/(2J_A+1)\).
   The zero-momentum normalization is therefore
   \(\mathcal R_A(0)=A^2\), with factor four and \(C_0\) included
   once in the physical response.
4. **Momentum variables:** the manuscript distinguishes
   \(Q_A^2=2m_AE_R+E_R^2\), \(t_A=-2m_AE_R\), and the formal
   impulse prescription \(t_N=t_A\). It uses exact
   \(y_A=b_A^2Q_A^2/4\) in the AFH response.
5. **Mediator mass notation:** the main model introduces the vector
   mediator as \(A'_\mu\), while the current-matching and appendix
   formulas use \(V_\mu\). The manuscript now states
   \(m_V\equiv m_{A'}\) at the direct-detection matching section.
6. **Historical A versus B:** the Mathematica rate engine and its
   archived outputs remain A-like if they use the constant nucleon
   coupling without the finite-\(t_N\) Dirac--Pauli insertion. They
   must not be relabelled as B. A separate Mathematica B implementation
   or pointwise comparison with the Python B result remains a future
   cross-check.

A small editorial defect in the introductory recoil derivation was also
fixed in this branch: an extra period before “We write the invariant mass”
was removed, and the leading recoil expressions now use \(q_A\)
consistently instead of an unindexed \(q\). The heavy-mediator comparison
now states its spatial-transfer limit using \(Q_A^2\).

## 7. Validation status and next gates

- P3/P4 branch edits above were made through the GitHub connector.
- No new GitHub Actions run was returned for the latest P4 branch commit during this audit. Therefore the edits are **not yet claimed to pass Python compilation or unit tests**.
- PR #67 remains provisional. Native AFH provenance, the P3-C full covariant-to-AFH nuclear-amplitude gate, and the local Mathematica comparison remain independent requirements.
- Run the corrected P4 workflow with bishara_linear and Pole width; archive fresh JSON/CSV/plots with hashes. Do not reuse pre-correction spectra.
- Before promoting an absolute rate, verify the public prefactor, \(g_{VN}\) normalization, AFH factor four, isotope abundances, and exact A/B/C fields in output metadata.

## 8. Final naming rule

Use **nucleon form factor** only for \(F_1^{V,N},F_2^{V,N}\); use **nuclear form factor** (preferably \(F_A\)) only for a coherent whole-nucleus scalar form factor; use **AFH nuclear response** for \(W_M,W_{\Phi''},W_\Delta,\ldots\). Never call finite-size \(W_M(y_A)\) a point-nucleus response.
