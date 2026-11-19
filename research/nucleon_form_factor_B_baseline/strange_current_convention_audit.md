# Strange nucleon form-factor current-convention audit

## Matching convention required by the DM quark current

The model interaction uses a unit quark vector current,
[
J_q^mu=ar qgamma^mu q,
]
so the flavor form factors (F_i^{q/N}) in
[
langle N'|ar qgamma^mu q|Nangle
=ar u_N'left[F_1^{q/N}gamma^mu+
rac{iF_2^{q/N}}{2m_N}sigma^{mu
u}q_
uight]u_N
]
must be defined for the unit current, not for the electromagnetic charge-weighted current (e_qar qgamma^mu q).

The isospin reconstruction used in this project is
[
F_i^{uds,N}=3left(F_i^{mathrm{EM},p}
+F_i^{mathrm{EM},n}+F_i^{s,N,mathrm{unit}}ight).
]
Therefore, a strange form factor that already contains (e_s=-1/3) must be divided by (e_s) before it enters this equation.

## Sufian et al. (2017): unit strange current

Sufian et al., Phys. Rev. Lett. 118, 042001 (2017), arXiv:1606.07075, explicitly calculate the matrix element of (ar sgamma_mu s) (their Eqs. (2)--(4) and discussion around the disconnected insertion). They quote
[
G_M^s(0)=-0.064(14)(09),qquad
langle r_E^2angle_s=-0.0043(16)(14) mathrm{fm}^2.
]
These are used directly as unit-current inputs. No extra factor of (-1/3) is applied.

For the primary benchmark, (G_E^s(Q^2)) is retained to first order using the quoted electric radius, while (G_M^s(Q^2)) is held at (G_M^s(0)). The cited result does not provide a magnetic radius in the paper's quoted physical-point result, so the frozen magnetic moment is explicitly a leading low-(Q^2) benchmark.

## Alexandrou et al. (2020): charge-weighted strange electromagnetic current

Alexandrou et al., Phys. Rev. D 101, 031501(R) (2020), arXiv:1909.10744, define
[
j_mu^s=e_sar sgamma_mu s,qquad e_s=-rac13
]
in their Eq. (2). Their Fig. 2 caption explicitly states that the strange charge factor (e_s=-1/3) is included. The reported values
[
mu_s=-0.017(4),quad
langle r_E^2angle_s=-0.0048(6) mathrm{fm}^2,quad
langle r_M^2angle_s=-0.015(9) mathrm{fm}^2
]
therefore belong to that charge-weighted current convention.

For the unit-current matching required here, the reported (G_E^s), (G_M^s), and their slopes are divided by (e_s=-1/3). In particular,
[
G_{M,mathrm{unit}}^s(0)=rac{-0.017}{-1/3}=+0.051.
]
The radii also change sign under this conversion because the complete form factor and its derivative are divided by (e_s).

This convention conversion is essential. Directly inserting (-0.017) as (F_2^{s,N}) into the unit-current flavor reconstruction would mix two different current normalizations.

## Adopted implementation

- Primary strange scenario: Sufian 2017 unit-current result.
- Alternative strange scenario: Alexandrou 2020 charge-weighted result converted to unit current.
- The two scenarios are kept separate in all output CSVs and metadata.
- No averaging between them is performed.
- The difference between them is treated as a strange-form-factor input dependence, not as the Ye2020 electromagnetic-fit covariance.

## References

- R. S. Sufian et al. (χQCD Collaboration), Phys. Rev. Lett. 118, 042001 (2017), arXiv:1606.07075.
- C. Alexandrou et al. (ETMC), Phys. Rev. D 101, 031501(R) (2020), arXiv:1909.10744.
- K. Borah, R. J. Hill, G. Lee, O. Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640.
