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

For the unit-current matching required here, the reported (G_E^s) and (G_M^s) are divided by (e_s=-1/3). In particular,
[
G_{M,mathrm{unit}}^s(0)=rac{-0.017}{-1/3}=+0.051.
]
The electric-radius slope is divided by (e_s), so the quoted (\langle r_E^2\rangle^s) changes sign and scales by 3 when converted to the unit current. The magnetic radius is defined from the normalized slope (-6/G_M(0)\,dG_M/dQ^2), so an overall current rescaling cancels and (\langle r_M^2\rangle^s) is unchanged.

This convention conversion is essential. Directly inserting (-0.017) as (F_2^{s,N}) into the unit-current flavor reconstruction would mix two different current normalizations.

## Adopted implementation

- Primary strange scenario: Sufian 2017 unit-current result.
- Alternative strange scenario: Alexandrou 2020 charge-weighted result converted to unit current.
- The two scenarios are kept separate in all output CSVs and metadata.
- No averaging between them is performed.
- The difference between them is treated as a strange-form-factor input dependence, not as the Ye2020 electromagnetic-fit covariance.

## Alexandrou et al. (2026): continuum-limit physical-point strange form factors

Alexandrou et al., arXiv:2603.26600 (2026), provide a newer calculation using four \(N_f=2+1+1\) ensembles at physical quark masses and a controlled continuum limit. The paper defines the strange current as

\[
j_\mu=e_s\bar s\gamma_\mu s,\qquad e_s=-\frac13,
\]

and explicitly states that the strange charge factor is **not included** in the reported results. Therefore the reported Sachs form factors already correspond to the unit current \(\bar s\gamma_\mu s\); no division by \(-1/3\) is applied.

Their model-averaged continuum-limit results are

\[
\begin{aligned}
\langle r_E^2\rangle_s&=-0.00545(49)(26)\;\mathrm{fm}^2,\\
\langle r_M^2\rangle_s&=-0.01212(280)(72)\;\mathrm{fm}^2,\\
\mu_s&=-0.01792(195)(18).
\end{aligned}
\]

The B postprocessor includes this as `alexandrou2026_continuum_unit_current`. It uses the first-order low-\(Q^2\) slope representation

\[
G_E^s(Q^2)=-\frac{\langle r_E^2\rangle_s}{6}Q^2+O(Q^4),
\qquad
G_M^s(Q^2)=\mu_s\left[1-\frac{\langle r_M^2\rangle_s}{6}Q^2+O(Q^4)\right].
\]

This is a slope-only implementation of the published result, not a numerical reconstruction of the paper's full z-expansion curve. The source uncertainties are recorded in metadata but are not yet propagated through the rate. It is therefore retained as a separate updated cross-check, not substituted silently for the frozen Sufian 2017 historical baseline.

## Magnetic-radius implementation check

For any magnetic Sachs form factor with nonzero \(G_M(0)=\mu\), the radius definition is

\[
\langle r_M^2\rangle=-\frac{6}{G_M(0)}
\left.\frac{dG_M}{dQ^2}\right|_{Q^2=0},
\]

so the low-momentum expansion contains the factor \(\mu\):

\[
G_M(Q^2)=\mu\left(1-\frac{\langle r_M^2\rangle Q^2}{6}+\cdots\right).
\]

The 2020 charge-weighted implementation was corrected to include this normalization factor before converting the full form factor to the unit strange current. A regression test differentiates the implemented form factor and checks that it reproduces the quoted magnetic radius.

## References

- R. S. Sufian et al. (χQCD Collaboration), Phys. Rev. Lett. 118, 042001 (2017), arXiv:1606.07075.
- C. Alexandrou et al. (ETMC), Phys. Rev. D 101, 031501(R) (2020), arXiv:1909.10744.
- C. Alexandrou et al., arXiv:2603.26600 (2026), continuum-limit strange form factors at physical quark masses.
- K. Borah, R. J. Hill, G. Lee, O. Tomalak, Phys. Rev. D 102, 074012 (2020), arXiv:2003.13640.
