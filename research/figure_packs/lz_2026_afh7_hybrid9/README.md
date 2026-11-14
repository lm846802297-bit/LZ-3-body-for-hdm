# LZ 3-body HDM — scientific figure pack

This directory records the provenance and scientific interpretation of the 13-figure atlas generated for PR #29.

## Deliverables

The companion figure pack contains 13 PNG figures, a landscape PDF atlas, a figure index, and a JSON manifest. The binary files were generated and checksum-verified in the working session. **This PR metadata commit does not contain the PNG/PDF/ZIP bytes**; the GitHub connector available for this session can create text files and Git blobs but does not provide a direct local-binary upload path. The binary pack therefore remains attached to the ChatGPT conversation rather than being represented as repository files.

## Figure index

| Figure | File | Scientific content |
|---|---|---|
| 01 | `Fig01_Tree_level_diagrams.png` | Schematic tree-level orderings for scalar emission on the \(\chi_1\leftrightarrow\chi_2\) line; schematic only, not an amplitude derivation |
| 02 | `Fig02_Xe131_fixed_speed_benchmarks.png` | Corrected Xe-131 fixed-speed benchmark comparing AFH, GCN and JJ55 |
| 03 | `Fig03_Natural_xenon_halo_spectra.png` | Natural-xenon halo-folded AFH-7 and Hybrid-9 spectra |
| 04 | `Fig04_Xe131_AFH_physical_normalization.png` | AFH raw and physical response, with the factor-four convention |
| 05 | `Fig05_Three_body_phase_space_I6.png` | Three-body phase-space integral \(I_6(E_R)\) for four benchmarks |
| 06 | `Fig06_LZ_2026_NR_efficiency.png` | Digitized one-dimensional LZ 2026 final-ROI NR efficiency and gray envelope |
| 07 | `Fig07_LZ_AFH7_Hybrid9_expected_yields.png` | Efficiency-weighted rate-level expected yields |
| 08 | `Fig08_High_energy_tail_fraction.png` | Accepted-rate fraction in the 225–269.9 keV recoil interval |
| 09 | `Fig09_Natural_xenon_isotope_abundance.png` | Natural xenon abundances and AFH default-density coverage |
| 10 | `Fig10_Quadrature_convergence_audit.png` | Benchmark- and isotope-level quadrature convergence |
| 11 | `Fig11_AFH_vs_Helm_isotope_response_difference.png` | AFH-versus-Helm normalized response differences for seven supported isotopes |
| 12 | `Fig12_Exact_q_vs_NR_approximation.png` | Exact spatial momentum transfer versus the NR approximation |
| 13 | `Fig13_Halo_cutoff_vs_untruncated_MB.png` | Truncated-SHM endpoint versus an untruncated Maxwell–Boltzmann tail diagnostic |

## Interpretation and limitations

- Figure 02 is a single-isotope fixed-speed diagnostic at \(v_\chi=800\,\mathrm{km/s}\). This exceeds the adopted truncated-SHM endpoint, \(v_{\max}=776\,\mathrm{km/s}\), so it is not a halo-supported event prediction.
- Figure 03 uses the archived natural-xenon halo-folded spectra. AFH-7 uses the seven isotopes with official AFH v6.0 default density matrices; Hybrid-9 uses Helm only for Xe-124 and Xe-126. No abundance renormalization is applied, and Hybrid-9 is not a full AFH-9 result.
- Figure 04 uses \(R_A^{\mathrm{phys}}=4 C_A R_{\mathrm{raw}}\). The factor 4 is physical and is included once; \(C_A=1.0000825298069376\) only removes the finite-decimal \(q=0\) normalization offset for Xe-131.
- Figure 06's gray envelope is a digitized detector-systematic range, not a confidence interval assigned by LZ.
- Figure 07 is a one-dimensional efficiency-folded rate-level estimate at 2.84 tonne-year over 5.4–269.9 keV. It is not a detector-level likelihood or an exclusion.
- Figure 08 is an unsmeared recoil-energy diagnostic, not a reconstructed-energy likelihood-window probability.
- Figure 10 records numerical quadrature checks; it does not establish completeness of the physical model.
- The original manuscript confidence-level contour figures are intentionally not recreated: the full two-dimensional signal PDF, background likelihood, nuisance covariance, and profile-likelihood construction are not available in this workstream.

## Reproducibility record

See `figure_manifest.json` for file sizes, SHA-256 digests, source branch, and scope flags. `SHA256SUMS.txt` contains the same digests in standard checksum-file format.
