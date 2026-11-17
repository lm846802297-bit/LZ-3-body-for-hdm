# AFH isotope-response equivalence audit

This module audits the equal-proton/equal-neutron **physical charge response** for the seven xenon isotopes with AFH v6.0 default-density matrices.

## Scope

- Zero-momentum coherent normalization, including the AFH v6.0 isoscalar factor-of-four convention.
- Point-by-point reconstruction of the archived response from the stored even-multipole amplitudes.
- Isotope-to-isotope shape differences at common recoil energies, using the direct exact-spatial-`q` AFH-7 response comparison archive.
- First local response minimum on the archived 0.25 MeV momentum grid in the stated (80\text{--}220\,\mathrm{MeV}) interval.
- The Xe-131 rank-2 contribution to the charge (M) response.

This is a nuclear-response audit, not a recalculation of the three-body phase-space integral, a detector simulation, or an LZ likelihood.

## Inputs

The runner reads, without modifying:

- `research/afh_default_density_natural_xenon_halo/results/full_afh_v6_default_7_isotope_response/afh_default_xe{A}_response_2401.csv`
- `research/afh_default_density_natural_xenon_halo/results/afh7_hybrid9_continuous_2026-11-14/afh_hybrid9_response_model_comparison.csv`

The first archive contains the seven AFH default-density response grids (2,401 nodes each). The second contains 84 recoil points per isotope with direct finite-sum evaluation at each isotope's exact spatial momentum.

## Run

From the repository root:

```bash
python research/afh_isotope_response_equivalence/run_afh_isotope_response_equivalence.py
python -m unittest discover -s research/afh_isotope_response_equivalence/tests -p 'test_*.py' -v
```

Outputs are written to `research/afh_isotope_response_equivalence/results/`:

- `zero_momentum_normalization.csv`
- `multipole_reconstruction.csv`
- `selected_recoil_shape_comparison.csv`
- `first_local_minima_grid.csv`
- `xe131_rank2_fraction.csv`
- `summary.json`

## Important interpretation

1. AFH v6.0's raw isoscalar package response has (4\pi W_M^{00}/(2J_A+1)\simeq A^2/4). For a physical per-nucleon coupling (g_p=g_n=g_N), the response multiplying (g_N^2) must approach (A^2). The factor four is included once.
2. The response reconstruction from stored multipole amplitudes is an internal algebraic closure check. It is not an independent nuclear-structure calculation.
3. Xe-131 has (J_A=3/2), allowing the elastic even multipoles (L=0,2). The rank-2 term is still part of the charge (M) response, not a spin-dependent (Sigma') or (Sigma'') response.
4. The seven-isotope AFH set covers natural atom fraction 0.998158. Xe-124 and Xe-126 have no AFH v6.0 default-density matrices in this archive; this audit does not silently replace them with AFH results.
5. A local minimum found on the 0.25 MeV grid is a grid-local minimum, not a continuously optimized zero. Do not interpret large ratios near a deep diffraction minimum as large absolute rates.

See `docs/AFH_ISOTOPE_RESPONSE_EQUIVALENCE.md` for the physics derivation and numerical results.


## Vector-current matching boundary

See [quark-to-nucleon vector-current matching and spatial-current scope](docs/QUARK_TO_NUCLEON_VECTOR_CURRENT_MATCHING.md) for the derivation of the current flavor-universal benchmark `g_p=g_n=3 g_Vq`, the finite-`Q^2` form-factor caveat, and the explicit distinction between the completed charge-response audit and the still-pending `Delta`/`Sigma'` nuclear-current calculation.
