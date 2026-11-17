# AFH spatial-response first numerical audit: Xe-129 and Xe-131

## Status and scope

This is a first source-translated numerical audit of the AFH v6.0 nuclear responses for the isoscalar convention \`ResponseNuclear[y,i,0,0]\`. It computes the AFH \`M\` and \`SigmaPrime\` nuclear responses for Xe-129 and Xe-131 at selected spatial momentum transfers. It also audits the AFH \`DeltaJ\` source definition.

It is **not** a completed physical vector-current calculation. In particular, it does not yet include the baryon-current Pauli form factors, the matching coefficients multiplying the nonrelativistic operators, the three-body dark-matter tensor, or a halo fold. The literal \`DeltaJ\` source path has a parity-selection inconsistency described below; its zero output must not be interpreted as a physical prediction.

## AFH source mapping

The official source \`v6/dmformfactor-V6.m\` defines:

- \`SigmaPJ\` through \`SigmaPrime\` and \`MJLSigma\`;
- \`DeltaJ\` through \`DeltaPrime\` and \`MJLDivQ\`;
- response index 3 as \`SigmaPJ\`;
- response index 6 as \`DeltaJ\`;
- response index 8 as the \`SigmaPJ\)-\`DeltaJ\` interference.

The Python implementation follows the source definitions of the oscillator radial sums, 3-j, 6-j and 9-j symbols, parity wrappers, and the AFH isoscalar coefficient. The two input matrices are the committed AFH default density matrices (39 entries for Xe-129 and 67 for Xe-131).

## First numerical results

The table gives the AFH package-normalized isoscalar responses. The physical equal-proton/equal-neutron normalization factor of four has **not** been applied; it would multiply both \(W_M\) and \(W_{\Sigma'}\) by four and therefore does not change the ratios shown.

| Isotope | \(q_A\) [GeV] | \(W_M^{00}\) | \(W_{\Sigma'}^{00}\) | \(W_{\Sigma'}^{00}/W_M^{00}\) |
|---|---:|---:|---:|---:|
| Xe-129 | 0 | 662.0513 | 0.0208089 | \(3.1431\\times10^{-5}\) |
| Xe-129 | 0.158 | \(7.2230\\times10^{-3}\) | \(2.9452\\times10^{-6}\) | \(4.0775\\times10^{-4}\) |
| Xe-129 | 0.256 | \(5.8389\\times10^{-4}\) | \(9.2210\\times10^{-5}\) | 0.15792 |
| Xe-129 | 0.365 | \(1.8307\\times10^{-5}\) | \(6.7948\\times10^{-7}\) | 0.03712 |
| Xe-131 | 0 | 1365.5163 | 0.0147078 | \(1.0771\\times10^{-5}\) |
| Xe-131 | 0.158 | \(1.4174\\times10^{-2}\) | \(8.5512\\times10^{-4}\) | 0.06033 |
| Xe-131 | 0.256 | \(1.9904\\times10^{-4}\) | \(7.9205\\times10^{-5}\) | 0.39793 |
| Xe-131 | 0.365 | \(1.1205\\times10^{-4}\) | \(1.7000\\times10^{-4}\) | 1.51717 |

The Xe-131 response contains both \(L=1\) and \(L=3\) contributions to \(W_{\Sigma'}\). At \(q_A=0.158\) GeV, the two contributions are approximately \(3.0663\\times10^{-4}\) and \(5.4849\\times10^{-4}\), respectively. At \(q_A=0.256\) GeV they are approximately \(2.3713\\times10^{-6}\) and \(7.6834\\times10^{-5}\). At \(q_A=0.365\) GeV they are approximately \(8.6317\\times10^{-5}\) and \(8.3688\\times10^{-5}\).

### Interpretation

At \(q_A=0\), the spin response is very small compared with the coherent charge response in this AFH isoscalar benchmark. That alone does not establish that it is negligible in the three-body rate.

Near the diffraction minima of \(W_M\), the ratio \(W_{\Sigma'}/W_M\) becomes much larger. For Xe-131 at \(q_A=0.365\) GeV, the bare nuclear response ratio exceeds one. This is a warning that a \(W_M\)-only approximation can fail locally near charge-response minima if the three-body tensor and single-nucleon matching coefficients do not suppress the transverse response sufficiently.

The table is a comparison of nuclear response functions, not a percentage correction to \(d\sigma/dE_R\). The latter requires the correct coefficient multiplying \(\Sigma'\), including the \(q/(2m_N)\) and the baryon-current magnetic form factor, followed by the full tensor contraction.

## Critical AFH \`DeltaJ\` parity inconsistency

The source defines:

\[
\mathrm{PhysicalConditionsAbnormal}:
(-1)^{\ell+\ell'+L+1}=+1,
\]
so its \`DeltaJ\` wrapper permits \(\ell+\ell'+L\) odd.

But the internal \`MJLDivQsummand1/2\` terms contain 3-j symbols with angular momenta \((\ell',L\pm1,\ell\pm1)\). Their all-zero magnetic projection requires the sum of these three angular momenta to be even. Modulo two, each term therefore requires \(\ell+\ell'+L\) even.

Thus the source wrapper and the internal 3-j selection rule are mutually incompatible: the literal \`DeltaJ\` matrix element vanishes for all transitions selected by that wrapper. The new code records this contradiction explicitly. It does not silently change the parity wrapper to force a nonzero answer.

This needs a native AFH/Wolfram check and comparison with the published AFH operator conventions before deciding whether it is a package-source typo, a convention misunderstanding, or a translation issue. Until resolved, neither \(W_\Delta\) nor \(W_{\Sigma'\Delta}\) is considered calculated.

## Physical matching caveat for the current model

For the universal quark-vector benchmark, \(F_1^p(0)=F_1^n(0)\) is fixed by equal baryon charge. The Pauli form factors \(F_2^{p,n}(0)\), and hence the magnetic form factors \(G_M^{p,n}=F_1^{p,n}+F_2^{p,n}\), are not fixed by the equality of the Dirac charges. They must be matched to the baryon-number current (or to the specified UV current), not borrowed without justification from the electromagnetic current.

Therefore the charge-response equality \(g_p=g_n\) does not imply equal or known coefficients for the magnetization current.

## Reproduction

From the repository root:

\`\`\`bash
python research/afh_default_density_xe131/run_afh_spatial_response_audit.py --outdir /tmp/afh-spatial-audit
python -m unittest research/afh_default_density_xe131/tests/test_afh_spatial_response_audit.py -v
\`\`\`

The selected-q CSV and JSON metadata record the exact inputs, AFH isoscalar convention, and the \`DeltaJ\` parity blocker.

## Required next validation

1. Run the native Wolfram AFH package for Xe-129 and Xe-131 at the same \(q_A\) points and export response indices 1, 3, 6 and 8.
2. Compare Python and Wolfram \(W_M\) and \(W_{\Sigma'}\) point by point before any normalization adjustment.
3. Resolve the \`DeltaJ\` parity contradiction against the original AFH documentation/source provenance.
4. Only after that, match the physical baryon-current \(F_1^{p,n}(Q^2)\), \(F_2^{p,n}(Q^2)\), construct the three-body particle tensor, and calculate the complete contraction.
