# AFH isospin-response normalization and the physical nucleon coupling

## Purpose

This note fixes the coupling convention before inserting the AFH default Xe-131 response into the three-body cross section. It distinguishes the package's isospin response entry from the coherent response multiplying a coupling defined per nucleon.

## 1. What the AFH v6 source actually computes

In `dmformfactor-V6.m`, the source defines the one-body isospin decomposition in the internal `Response[]` expression (around source lines 963--966). For the isoscalar part, the nucleon coefficients enter through

```text
(an + ap)/2
```

The `FF` routine forms second derivatives with respect to the proton/neutron coefficients and includes a factor 1/2. The `ResponseNuclear[y,1,0,0]` branch then returns one quarter of the sum of the four proton/neutron matrix entries (source around lines 981--1002).

For the built-in Xe-131 density matrix, the direct source translation gives

```text
R_AFH,00(0) = 4 pi/(2 J_A+1) W_M,AFH^{00}(0)
             = 4289.895955714993
A^2/4       = 4290.25
relative difference = 8.2522996e-5
```

The small difference is consistent with the finite decimal precision of the tabulated density-matrix coefficients. The important convention is that the package's individual isoscalar response entry is normalized to approximately A^2/4.

## 2. Mapping to a coupling defined per nucleon

The manuscript defines (g_{VN}) by equal physical proton and neutron couplings,

[
g_p=g_n=g_{VN}.
]

For this physical interaction, the coherent nuclear amplitude at zero momentum is

[
mathcal M_A(0) propto Zg_p+(A-Z)g_n=A g_{VN},
]

so the coherent response multiplying (g_{VN}^2) must obey

[
mathcal R_A^{m phys}(0)=A^2.
]

The AFH package's isoscalar coefficient convention must therefore be mapped consistently. Its setter `SetCoeffsNonrel[op,c,0]` sets (c_p=c_n=c/2), as can be seen in the source implementation around lines 1087--1138. Thus a per-nucleon coupling (g_{VN}) corresponds to the AFH isoscalar input (c_0=2g_{VN}) in that interface.

The contraction (c_0^2 W_M^{00}) then gives

[
(2g_{VN})^2,W_{M,m AFH}^{00}
= g_{VN}^2,[4W_{M,m AFH}^{00}].
]

Accordingly, if the cross-section prefactor is written with (g_{VN}^2), the physical response is

[
oxed{
mathcal R_A^{m phys}(E_R)
=rac{16pi}{2J_A+1}W_{M,m AFH}^{00}(y)
}
]

or, equivalently, retain (4pi W_{M,m AFH}^{00}/(2J_A+1)) and explicitly use the AFH isoscalar coefficient (2g_{VN}) in the amplitude-level coupling contraction.

## 3. What must not be done

- Do not use the raw AFH (W_M^{00}) with a per-nucleon (g_{VN}) and simultaneously assert (mathcal R_A(0)=A^2).
- Do not multiply by four twice: once in (mathcal R_A) and again in the coupling.
- Do not change (g_{VN}=3g_{Vq}); this is a separate quark-to-nucleon matching relation.
- Do not alter the AFH density matrix or (b_A) to fix a normalization convention.
- Do not edit the manuscript formula until the exact definition of the (g_{VN}) factor in the Eq. (6) amplitude derivation is checked against this mapping.

## 4. Numerical normalization used for the response shape

The source's rounded density matrix gives a small zero-momentum offset. For plotting and shape-only nuclear-response insertion, the archived response is normalized by its own computed zero-momentum value:

[
mathcal R_A^{m phys}(q)
=A^2,rac{mathcal R_{A,m AFH}^{00}(q)}
{mathcal R_{A,m AFH}^{00}(0)}.
]

This is a single overall normalization correction of (8.2523	imes10^{-5}); it does not move the response minima or alter the (q)-dependence. The raw package response and the normalized physical response are both retained in the CSV.

## 5. Verification status

- The official uploaded AFH v6 source archive was parsed and its 67 Xe-131 density-matrix entries were checked against the archived CSV.
- The source-to-Python implementation was rerun against the supplied package and reproduced the archived response values.
- All six Python regression tests pass.
- The Mathematica/Wolfram native runner is committed, but has not yet been executed because no Wolfram kernel is installed in the current execution environment. This is still an independent validation task; Python source translation tests are not represented as a native Mathematica run.
