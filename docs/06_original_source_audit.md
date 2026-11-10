# Audit against the original LaTeX source

## Source of truth

The authoritative manuscript source is \`paper-source/main.tex\`, supplied in \`3body_for_HDM.zip\` on 2026-11-11. The earlier five-page extracted research summary is useful as a secondary note, but it is not a substitute for the actual TeX source. Where they differ, follow the TeX source and record the discrepancy.

## Model content actually present in main.tex

### Vector–vector branch

The source defines two heavy fermions \(\chi_1,\chi_2\), a massive \(U(1)_X\) vector \(V_\mu\), and a sub-MeV scalar \(s\), with
\[
\mathcal L_{\rm int}
=g_1V^\mu\bar\chi_2\gamma_\mu\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+g_{Vq}V^\mu\sum_q\bar q\gamma_\mu q,
\]
and uses \(g_{VN}=3g_{Vq}\). The \(2\to3\) differential cross section, two radiation diagrams, their interference, the coherent nuclear response, and the \(W^2\) integration limits are written only for this vector–vector branch.

The source imposes \(W_{\max}<m_{\chi_2}\) over accessible halo phase space to exclude on-shell \(\chi_2\) production. It inserts a pole width only in the propagator with invariant \(W^2=(p'+k)^2\). The manuscript does not yet provide the explicit \(\chi_2\to\chi_1s\) width formula or a finite-width/zero-width comparison.

### Scalar–pseudoscalar branch

The source also lists
\[
\mathcal L_{\rm int}
=g_1\phi\bar\chi_2\chi_1
+g_2s\bar\chi_2\chi_1+\mathrm{h.c.}
+i g_{\phi N}\phi\sum_{N=p,n}\bar N\gamma^5N.
\]
However, it does not derive the corresponding \(2\to3\) amplitude, nuclear response, differential cross section, or parameter scan. The vector–vector cross section must not be silently assigned to this branch.

The source does not state whether \(\chi_{1,2}\) are Dirac or Majorana fields, nor does it specify the chiral/CP structure beyond the displayed bilinears. These are open model-definition questions.

## Cosmology: important correction to the earlier summary

The actual source retains only
\[
VV\leftrightarrow ss,\qquad Vs\leftrightarrow Vs,
\]
together with \(s\leftrightarrow N_sN_s\) decay and inverse decay. It explicitly sets
\[
C_0=C_{\rm pair},\qquad Q_0=Q_{\rm pair}+Q_{\rm elastic}.
\]

It explicitly neglects:
- heavy-catalyzed conversion \(Vh\leftrightarrow sh\);
- the net scalar source from \(\chi_2\) decays and inverse decays;
- excited-state regeneration through heavy-particle collisions and scattering with the SM bath.

The source states that this omission makes little difference to the benchmark \(\Delta N_{\rm eff}\), but the underlying benchmark inputs and a reproducible numerical comparison are not included in the manuscript source. This is a claim to be independently tested, not a validated conclusion.

The source initializes \(T_s=T_f\), \(n_s=n_s^{\rm eq}(T_f)\), and \(n_{N_s}=\rho_{N_s}=0\). It uses MB moment closure, instantaneous active-neutrino decoupling at \(2\) MeV, and reports \(\Delta N_{\rm eff}\simeq0.043\) in the MB treatment versus \(0.046\) in a separate quantum-equilibrium thermodynamic check. It also says the active-neutrino reheating effect in the presence of dark radiation is not recalculated precisely.

## Manuscript incompleteness visible in the source

- \`Introduction\` is empty.
- The direct-detection section contains internal task notes (“2-3 scattering Feynman diagram”, “Er -- Events benchmark”, “Parameter scan 2D”).
- Captions for the event-rate spectrum and parameter-contour figures still say “Feynman diagrams”.
- The loop-induced \(2\to2\) subsection is only a heading.
- The relic-abundance section contains TODO prose rather than a calculation.
- The constraints section is only a placeholder.
- The conclusion contains “change V to Scalar ...”.
- The supplementary section contains TODO text and the post-freeze-out equations.
- A comment requests a reference for vector decays into mesons.
- The source has no complete benchmark table, no complete relic-abundance computation, and no LZ detector-level likelihood/efficiency/background treatment.

## Mechanical source checks

- All six \`\\cite\` keys in \`main.tex\` have matching entries in \`ref.bib\`.
- All seven \`\\includegraphics\` references resolve to figure files in the supplied ZIP.
- A local \`pdflatex -interaction=nonstopmode -halt-on-error main.tex\` pass succeeds and writes a five-page PDF. The local runtime lacks \`bibtex\`, so the citation-resolution and final multi-pass build remain unverified.

## Consequence for the research plan

The first decision is still to choose which model is the paper's main branch. The existing cross section and plotted direct-detection spectra belong to vector–vector. The scalar–pseudoscalar interaction is currently only a second Lagrangian ansatz. Cosmology should be described using the truncated collision/source set actually present in \`main.tex\`; any restoration of omitted heavy-catalyzed or \(\chi_2\)-decay sources must be a separately derived and tested extension.
