# AME2020/CODATA-2022 nuclear masses and exact-spatial AFH Xe-131 rate

**Status:** reproducible Xe-131 isotope partial calculation; full AME2020 natural-xenon sum not yet available.

## 1. Scope and relation to the natural-xenon baseline

This study replaces the legacy xenon nuclear-mass prescriptions with unrounded
AME2020 atomic masses and CODATA-2022 constants, then recomputes the Xe-131
isotope contribution to the halo-folded three-body rate using the full
2401-point AFH v6.0 Xe-131 response curve.

The AFH response is evaluated at the **exact spatial momentum transfer**
\[
q_{\rm AFH}=q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}.
\]
The non-relativistic approximation
\[
q_{\rm NR}=\sqrt{2m_AE_R}
\]
is retained only as a sensitivity diagnostic. It is not the baseline.

The scope must be distinguished from the already validated natural-xenon
selected-point calculation on main:

- The main natural-xenon result uses NIST nuclear masses and 28 selected
  AFH response samples: seven isotopes at four recoil energies. It covers
  natural abundance fraction 0.998158 without renormalizing the available
  isotopes, and reproduces its archived tables with maximum total-rate
  relative difference \(2.67\times10^{-12}\).
- The AME2020 calculation below uses the full Xe-131 AFH response curve and
  recomputes the response at the AME2020 nuclear mass. It is therefore a
  Xe-131 partial contribution per kg of natural xenon, not the all-isotope
  AME2020 prediction.
- The 28 selected response samples were generated at the NIST-mass q values.
  They cannot be reused at the AME2020 q values by simply changing the mass
  metadata. The natural-xenon runner deliberately rejects that mismatch.

The rate is before detector efficiency, energy resolution, exposure, cuts,
backgrounds, and likelihood. It is not an LZ event-yield or exclusion result.

## 2. AME2020 atomic-to-nuclear mass conversion

AME2020 tabulates neutral-atom masses. The nuclear mass is
\[
\boxed{
m_Ac^2=M_{\rm atom}(A,Z)c^2-Zm_ec^2+B_e(Z)
}
\]
with the AME2020 approximate total electronic binding energy
\[
B_e(Z)=14.4381Z^{2.39}
      +1.55468\times10^{-6}Z^{5.35}\ {\rm eV}.
\]
For xenon, \(Z=54\):
\[
B_e(54)=202378.277717\ {\rm eV}
       =202.378277717\ {\rm keV}.
\]

The implementation uses the unrounded atomic masses in the official AME2020
mass_1.mas20 table and CODATA-2022 constants:
\[
uc^2=931.49410372\ {\rm MeV},\qquad
m_ec^2=0.51099895069\ {\rm MeV},
\]
\[
m_e=5.485799090441\times10^{-4}u.
\]

The AME2020 electronic-binding expression is an approximate correction;
its precision is not asserted to match the precision of the measured atomic
masses. No additional uncertainty is invented for it.

### 2.1 Nine natural-xenon isotopes

The isotope abundances are the NIST natural atom fractions. The AME2020
atomic masses are the unrounded mass_1.mas20 values.

| Isotope | Natural atom fraction | AME2020 atomic mass [u] | AME2020 nuclear mass [GeV] |
|---|---:|---:|---:|
| Xe-124 | 0.000952 | 123.905885174 | 115.390209890729 |
| Xe-126 | 0.000890 | 125.904297422 | 117.251719116542 |
| Xe-128 | 0.019102 | 127.90353075341 | 119.113993176711 |
| Xe-129 | 0.264006 | 128.90478085742 | 120.046651744946 |
| Xe-130 | 0.040710 | 129.903509346 | 120.976961443275 |
| Xe-131 | 0.212324 | 130.90508412808 | 121.909922447217 |
| Xe-132 | 0.269086 | 131.90415508346 | 122.840551151352 |
| Xe-134 | 0.104357 | 133.905393030 | 124.704692498694 |
| Xe-136 | 0.088573 | 135.907214474 | 126.569377370481 |

Three mass prescriptions are kept distinct:

1. **A_u:** historical \(m_A=A\,u\), retained for exact reproduction of
   older fixed-mass calculations.
2. **nist_nuclear:** NIST neutral-atom isotope mass minus 54 electron rest
   masses, with the historical CODATA-2018 constants and no electronic
   binding correction.
3. **ame2020_nuclear:** unrounded AME2020 neutral-atom mass minus 54 electron
   masses plus \(B_e(54)\), with CODATA-2022 constants.

For Xe-131:
\[
m_A^{\rm AME2020}=121.909922447217\ {\rm GeV},
\]
\[
m_A^{\rm NIST}=121.909719835384\ {\rm GeV},\qquad
m_A^{A u}=122.025727417020\ {\rm GeV}.
\]
The AME2020 mass is about \(202.612\) keV above the NIST nuclear-mass
conversion; the \(A u\) approximation is about \(115.805\) MeV above the
AME2020 mass.

### 2.2 Isotope-dependent threshold example

For \(m_{\chi_1}=1\) TeV, \(m_s=300\) keV,
\(\Delta m=1\) MeV, and \(E_R=101\) keV, the AME2020 masses give:

| Isotope | \(v_{\min}\) [km/s] |
|---|---:|
| Xe-124 | 810.299895 |
| Xe-126 | 804.208208 |
| Xe-128 | 798.260345 |
| Xe-129 | 795.334767 |
| Xe-130 | 792.451024 |
| Xe-131 | 789.592969 |
| Xe-132 | 786.775240 |
| Xe-134 | 781.228229 |
| Xe-136 | 775.805285 |

The truncated-SHM endpoint is \(v_{\max}=v_{\rm esc}+v_E=776\) km/s,
so only Xe-136 is open at this particular recoil point. The open-isotope
set changes with \(E_R\); this threshold table is not a statement that
Xe-136 dominates the integrated spectrum at all recoil energies.

## 3. Exact AFH spatial momentum versus the NR recoil approximation

The AFH response variable is
\[
y=\left(\frac{q b_A}{2}\right)^2,
\]
where \(q=|\mathbf q|\) is the magnitude of the **spatial momentum transfer**.
For a target nucleus initially at rest,
\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q),\qquad P'^2=P^2=m_A^2.
\]
The exact mass-shell relation gives
\[
\boxed{q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}},
\qquad
\boxed{y_{\rm exact}=\frac{b_A^2}{4}(2m_AE_R+E_R^2)}.
\]
Expanding for \(E_R\ll m_A\) gives the approximation
\[
q_{\rm NR}=\sqrt{2m_AE_R},\qquad
y_{\rm NR}=\frac{b_A^2m_AE_R}{2}.
\]

The adopted convention is therefore:

| Quantity | Baseline | Diagnostic |
|---|---|---|
| AFH response momentum | \(q_{\rm exact}\) | \(q_{\rm NR}\) |
| Three-body kinematics | exact mass shell | exact mass shell |
| \(v_{\min}\) and phase-space limits | exact | exact |
| Purpose | physical result | small-recoil approximation sensitivity |

Changing only the response-q interpolation must not change \(v_{\min}\),
the three-body phase-space support, or the halo distribution.

The propagator uses a different invariant:
\[
t=(P'-P)^2=-2m_AE_R,\qquad
m_V^2-t=m_V^2+2m_AE_R.
\]
It is incorrect to replace this invariant by \(q_{\rm exact}^2\):
\[
q_{\rm exact}^2=2m_AE_R+E_R^2\ne -t.
\]

### 3.1 Xe-131 response-level comparison

For the AME2020 Xe-131 mass, PCHIP interpolation of the full 2401-point
AFH response gives:

| \(E_R\) [keV] | \(q_{\rm exact}\) [GeV] | \(q_{\rm NR}\) [GeV] | \(R_A(q_{\rm exact})\) | \(R_A(q_{\rm NR})\) | NR vs exact [ppm] |
|---:|---:|---:|---:|---:|---:|
| 101 | 0.156926143569 | 0.156926111066 | 0.320979635189 | 0.320986807329 | +22.344 |
| 200 | 0.220825743470 | 0.220825652900 | 9.62844388981 | 9.62849643886 | +5.458 |
| 267 | 0.255146957410 | 0.255146817709 | 0.00676540962832 | 0.00676684899246 | +212.708 |
| 542 | 0.363525308193 | 0.363524904144 | 0.00328013662691 | 0.00328045596122 | +97.344 |

The response difference is amplified near the AFH diffraction minimum around
267 keV. The maximum selected-point shift in the table is about 213 ppm.
This is a response-interpolation sensitivity, not a universal multiplicative
correction to the full rate.

The AFH default oscillator length \(b_A\) is unchanged and is not fitted to
the Figure-2 minima.

## 4. Xe-131 partial halo-folded rate

For one kg of natural xenon, the Xe-131 target contribution is
\[
\frac{dR_{131}}{dE_R}
=
N_T\,\xi_{131}\,\frac{\rho_\chi}{m_{\chi_1}}c
\int_{v_{\min,131}}^{v_{\max}}dv\,
f_{\rm lab}(v)\frac{v}{c}
\frac{d\sigma_{131}}{dE_R}(v),
\]
where
\[
N_T=\frac{N_{\rm Av}1000}{\bar M_{\rm Xe}},\qquad
\xi_{131}=0.212324,\qquad
\bar M_{\rm Xe}=131.2927614479\ {\rm g/mol}.
\]
The one-dimensional lab-frame speed PDF is normalized to unity. The baseline
truncated SHM inputs are
\[
v_0=220\ {\rm km/s},\quad v_E=232\ {\rm km/s},\quad
v_{\rm esc}=544\ {\rm km/s},\quad v_{\max}=776\ {\rm km/s}.
\]
An untruncated boosted Maxwell-Boltzmann distribution integrated to
1600 km/s is retained only as a high-speed-tail diagnostic.

The isotope mass enters consistently through:
- the exact AFH response momentum \(q_{\rm exact}\);
- the exact three-body threshold \(v_{\min,131}\);
- the three-body kernel and its phase-space limits;
- the propagator denominator \(m_V^2+2m_AE_R\).

The selected benchmarks are \(m_s=200,300,360\) keV with
\(\Delta m=1\) MeV, and \(m_s=300\) keV with
\(\Delta m=10\) MeV. Public benchmark normalization is
\[
m_{\chi_1}=1\ {\rm TeV},\quad m_V=10\ {\rm GeV},\quad
(g_1g_2g_{VN})^2=10^{-8},\quad g_2=1,\quad
\rho_\chi=0.3\ {\rm GeV/cm^3}.
\]
The width is the conditional pole width for
\(\chi_2\to\chi_1s\), assuming Dirac \(\chi_2\), a real scalar, a pure
scalar off-diagonal Yukawa, and no other open channels.

The numerical rate is the Xe-131 isotope term per kg of natural xenon.
It must not be described as the sum over all natural-xenon isotopes.

## 5. Numerical implementation and reproducibility map

| Physical object | Definition / approximation | Code | Tests / output |
|---|---|---|---|
| AME2020 atomic masses | unrounded mass_1.mas20 values | isotope_mass_schemes.py | tests/test_isotope_mass_schemes.py |
| Nuclear-mass conversion | \(M_{\rm atom}-54m_e+B_e(54)\), CODATA-2022 | isotope_mass_GeV(..., ame2020_nuclear) | xenon_isotope_ame2020_masses.csv |
| AFH response | full Xe-131 2401-point default-density curve, \(R_A(0)=A^2\) | run_afh_default_xe131.py | output/afh_default_xe131_WM00.csv, output/metadata.json |
| Exact AFH q | \(\sqrt{2m_AE_R+E_R^2}\) | run_ame2020_xe131_halo_partial.py:compute_partial_rate | response_q_convention_rate_comparison.csv |
| NR q diagnostic | \(\sqrt{2m_AE_R}\) | same function, nr_approx branch | same comparison CSV |
| Three-body threshold | exact mass-shell \(v_{\min}\) | rate_kinematics.py:vmin_three_body_km_s | xe131_partial_halo_rates.csv |
| Three-body integral | \(I_6\), pole-width prescription | eq6_kernel.py:reduced_kernel | kernel_quadrature_convergence.csv |
| Halo fold | truncated SHM baseline; untruncated MB diagnostic | run_ame2020_xe131_halo_partial.py | speed_quadrature_convergence.csv |
| End-to-end CI | mass tests, AFH/halo tests, archive regression, stale-q guard, numerical calculation | .github/workflows/ame2020-xe131-exact-spatial.yml | Actions artifact and archived output directory |

The output directory is
research/afh_default_density_xe131/output/ame2020_exact_spatial_xe131_partial/.
It contains the isotope mass table, partial-rate table, mass-scheme comparison,
response-q comparison, speed-grid convergence, kernel-grid convergence,
and metadata.

## 6. Natural-xenon AME2020 limitation

The current main archive contains 28 exact-spatial AFH response samples
(7 isotopes × 4 recoil energies) for the NIST nuclear-mass convention. Those
samples reproduce the archived NIST-mass natural-xenon selected-point rates.
They do not provide the full isotope response curves needed to evaluate
\(R_A(q_{\rm exact}^{\rm AME2020})\) at the shifted AME2020 q values.

The natural-xenon runner now exposes an explicit mass-scheme option and
checks each stored response q against the requested mass/q convention. With
ame2020_nuclear, the old NIST-q samples are rejected rather than silently
relabelled. The AME2020 Xe-131 calculation avoids this problem because it
uses the complete Xe-131 AFH response curve and interpolates at the AME2020
exact-spatial q.

A full AME2020 natural-xenon result requires regenerating the AFH response
values for each isotope with the AME2020 nuclear mass and exact-spatial q,
or archiving complete isotope response curves that can be interpolated at
those q values. No response is borrowed from another isotope, and no
missing-isotope contribution is inferred from the seven-isotope abundance
coverage.

## 7. Primary references

1. M. Wang et al., *The AME 2020 atomic mass evaluation (II). Tables, graphs
   and references*, Chinese Physics C **45** (2021) 030003,
   [DOI: 10.1088/1674-1137/abddaf](https://doi.org/10.1088/1674-1137/abddaf).
2. AMDC, official unrounded AME2020 atomic-mass table,
   [mass_1.mas20](https://amdc.impcas.ac.cn/masstables/Ame2020/mass_1.mas20).
3. P. J. Mohr, D. B. Newell, and B. N. Taylor, *CODATA recommended values of
   the fundamental physical constants: 2022*, Rev. Mod. Phys. **97** (2025)
   025002, [DOI: 10.1103/RevModPhys.97.025002](https://doi.org/10.1103/RevModPhys.97.025002).
4. A. Anand, A. L. Fitzpatrick, and W. C. Haxton, *Weakly interacting
   massive particle-nucleus elastic scattering response*, Phys. Rev. C **89**
   (2014) 065501, arXiv:1308.6288.
5. R. J. Fitzpatrick et al., *Model-independent WIMP Scattering Responses and
   Event Rates*, JCAP **02** (2013) 004, arXiv:1203.3542, especially the
   definition of the nuclear response variable in terms of spatial \(q\).
6. NIST, *Atomic Weights and Isotopic Compositions for Xenon*,
   [NIST Xenon data](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe).
