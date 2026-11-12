# Xenon nuclear-mass and AFH response-q audit

## 1. Scope and calculation baseline

This note integrates the AME2020 nuclear-mass prescription with the AFH
response-momentum audit on the current Xe-131 mainline. It keeps three
mass prescriptions and two response-q prescriptions separate.

The calculation is an isotope-resolved Xe-131 partial contribution to a
natural-xenon target. It is **not** the complete natural-xenon rate because
the full AFH response curves for the other isotopes are not presently archived
in this repository.

## 2. AME2020 nuclear masses

AME2020 tabulates neutral-atom masses. The nuclear mass is obtained from

\[
M_N(A,Z)=M_A(A,Z)-Z\,m_e+B_e(Z),
\]

where the approximate total electronic binding energy is

\[
B_e(Z)=14.4381 Z^{2.39}
       +1.55468\times10^{-6}Z^{5.35}\ {\rm eV}.
\]

For xenon, \(Z=54\), giving

\[
B_e(54)=202378.277717\ {\rm eV}
       =202.378277717\ {\rm keV}.
\]

The implementation uses the **unrounded AME2020 atomic masses** from the
official mass_1.mas20 file, not the lower-precision NIST isotope-mass
values used by the legacy calculation. The mass conversion uses CODATA-2022:

\[
u c^2=931.49410372\ {\rm MeV},\qquad
m_e c^2=0.51099895069\ {\rm MeV},
\]

\[
m_e=5.485799090441\times10^{-4}u.
\]

The AME2020 paper explicitly notes that the precision of calculated
\(B_e(Z)\) is not established as precisely as the measured atomic masses.
The binding correction is therefore included as the prescribed approximate
correction, but no unsupported uncertainty is assigned to it.

### 2.1 Nine natural-xenon isotopes

The AME2020 atomic masses below are the unrounded values in mass_1.mas20.
The abundance column retains the NIST natural atom fractions used in the
natural-xenon target weighting.

| Isotope | Natural fraction | AME2020 atomic mass [u] | AME2020 nuclear mass [GeV] | AME2020 − NIST nuclear [keV] |
|---|---:|---:|---:|---:|
| Xe-124 | 0.000952 | 123.905885174 | 115.390209890729 | +196.181 |
| Xe-126 | 0.000890 | 125.904297422 | 117.251719116542 | +201.724 |
| Xe-128 | 0.019102 | 127.90353075341 | 119.113993176711 | +202.315 |
| Xe-129 | 0.264006 | 128.90478085742 | 120.046651744946 | +202.542 |
| Xe-130 | 0.040710 | 129.903509346 | 120.976961443275 | +202.544 |
| Xe-131 | 0.212324 | 130.90508412808 | 121.909922447217 | +202.612 |
| Xe-132 | 0.269086 | 131.90415508346 | 122.840551151352 | +202.548 |
| Xe-134 | 0.104357 | 133.905393030 | 124.704692498694 | +201.034 |
| Xe-136 | 0.088573 | 135.907214474 | 126.569377370481 | +202.546 |

The three mass schemes are now:

1. A_u: historical \(m_A=A\,u\), retained only for exact reproduction
   of older calculations.
2. nist_nuclear: NIST neutral-atom isotope mass minus 54 electron rest
   masses, using the historical CODATA-2018 constants and neglecting
   electronic binding.
3. ame2020_nuclear: unrounded AME2020 neutral-atom mass minus 54 electron
   masses plus \(B_e(54)\), using CODATA-2022 constants.

For Xe-131,

\[
m_A^{\rm AME2020}=121.909922447217\ {\rm GeV},
\]

\[
m_A^{\rm NIST\ nuclear}=121.909719835384\ {\rm GeV},
\qquad
m_A^{A u}=122.025727417020\ {\rm GeV}.
\]

Thus the AME2020 nuclear mass is \(202.612\) keV above the legacy NIST
nuclear-mass conversion for Xe-131, while the \(A u\) approximation is
about \(115.805\) MeV too large. Across the nine isotopes, the AME2020
versus NIST-nuclear difference is approximately \(196\)–\(203\) keV;
the small isotope dependence also reflects differences between the NIST and
AME2020 atomic-mass inputs.

### 2.2 Isotope-dependent velocity thresholds

For the benchmark $m_{\chi_1}=1$ TeV, $m_s=300$ keV and
$E_R=101$ keV, the AME2020 masses give:

| Isotope | $v_{\min}$ [km/s] |
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

With the truncated-SHM endpoint $v_{\max}=776$ km/s, only Xe-136 is open
at this recoil energy. This does **not** imply that Xe-136 dominates the
integrated spectrum at every $E_R$; the open-isotope set changes with recoil
energy and the full rate also contains the isotope-dependent AFH response.

## 3. AFH response momentum: exact spatial transfer is the baseline

AFH defines its harmonic-oscillator variable as

\[
y=\left(\frac{q b_A}{2}\right)^2,
\]

where \(q=|\mathbf q|\) is the **spatial momentum-transfer magnitude**.
It is not the Lorentz invariant \(-t\).

For an initially stationary target nucleus,

\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q),
\]

and the exact target mass-shell condition \(P'^2=P^2=m_A^2\) gives

\[
(m_A+E_R)^2-q^2=m_A^2
\quad\Longrightarrow\quad
\boxed{q_{\rm exact}=\sqrt{2m_AE_R+E_R^2}}.
\]

Therefore the exact AFH response variable is

\[
\boxed{y_{\rm exact}=\frac{b_A^2}{4}
       \left(2m_AE_R+E_R^2\right)}.
\]

Only after making the small-recoil approximation \(E_R/m_A\ll1\) does one obtain

\[
q_{\rm NR}=\sqrt{2m_AE_R},\qquad
y_{\rm NR}=\frac{b_A^2m_AE_R}{2}.
\]

This distinction is also documented in the current mainline
[Appendix G: AFH spatial momentum transfer and the NR recoil approximation](../docs/appendices/09G_recoil_momentum_convention_audit.md).
The current implementation therefore uses:

- exact_spatial: \(q_{\rm resp}=q_{\rm exact}\), the baseline AFH response input;
- nr_approx: \(q_{\rm resp}=q_{\rm NR}\), retained only as an approximation diagnostic;
- legacy_exact: backward-compatible alias for exact_spatial.

For both response-q choices, the three-body kinematics, \(v_{\min}\),
phase-space limits, and mediator invariant use the exact mass-shell
kinematics. In particular,

\[
t=(P'-P)^2=E_R^2-q_{\rm exact}^2=-2m_AE_R,
\]

so the mediator denominator is

\[
(m_V^2-t)^2=(m_V^2+2m_AE_R)^2.
\]

The fact that \(t=-2m_AE_R\) is exact does not imply
\(q_{\rm exact}^2=2m_AE_R\): the former is a four-momentum invariant,
whereas AFH uses the spatial magnitude \(q=|\mathbf q|\).

### 3.1 Xe-131 response sensitivity to the NR approximation

For Xe-131 with the AME2020 nuclear mass, direct PCHIP interpolation of the
complete 2401-point AFH response curve gives the following comparison.
At fixed \(E_R\), the differential cross section is linear in \(R_A\), so
the relative response shift is also the relative shift in
\(d\sigma_{131}/dE_R\) and \(dR_{131}/dE_R\), before detector folding.

| \(E_R\) [keV] | \(q_{\rm NR}\) [GeV] | \(q_{\rm exact}\) [GeV] | \(R_A(q_{\rm exact})\) | \(R_A(q_{\rm NR})\) | NR vs exact [ppm] |
|---:|---:|---:|---:|---:|---:|
| 101 | 0.156926111066 | 0.156926143569 | 0.320979635189 | 0.320986807329 | +22.344 |
| 200 | 0.220825652900 | 0.220825743470 | 9.62844388981 | 9.62849643886 | +5.458 |
| 267 | 0.255146817709 | 0.255146957410 | 0.00676540962832 | 0.00676684899246 | +212.708 |
| 542 | 0.363524904144 | 0.363525308193 | 0.00328013662691 | 0.00328045596122 | +97.344 |

The largest selected-point response difference is at the AFH minimum near
267 keV: the NR approximation raises the response and differential rate
by \(2.12708\times10^{-4}\), or \(0.0212708\%\), relative to the exact
spatial-q baseline. This is a local interpolation effect, not a change to
\(v_{\min}\), three-body phase-space support, or the halo distribution.

The AFH default oscillator-length prescription \(b_A\) and response
normalization are unchanged. No isotope-specific \(b_A\) is fitted to a
Figure-2 minimum.

## 4. Xe-131 three-body kinematics and halo fold

The Xe-131 partial rate uses the full 2401-point AFH v6.0 default-density
response curve. It includes the Xe-131 natural atom fraction \(0.212324\)
and is normalized per kg of natural xenon using the NIST abundance-weighted
mean atomic molar mass.

For each benchmark and recoil energy, the calculation evaluates

\[
\frac{dR_{131}}{dE_R}
=
N_T\,\frac{\rho_\chi}{m_{\chi_1}}\,\xi_{131}
\int_{v_{\min,131}}^{v_{\max}}
dv\, f_{\rm lab}(v)\,v\,
\frac{d\sigma_{131}}{dE_R},
\]

with the velocity convention written in the code as \(v/c\) times \(c\).
The truncated SHM is the baseline:

\[
v_0=220\ {\rm km/s},\quad
v_E=232\ {\rm km/s},\quad
v_{\rm esc}=544\ {\rm km/s},\quad
v_{\max}=776\ {\rm km/s}.
\]

An untruncated boosted Maxwell-Boltzmann distribution is retained only as
a high-speed-tail diagnostic. It is not used as the baseline halo model.

The isotope sum and velocity integral have distinct physical roles:

- The natural isotope fraction \(\xi_A\) determines how many target nuclei of
  isotope \(A\) are present. For a one-kg natural-xenon target,
  \(N_{T,A}=1000\,N_{\rm Av}\,\xi_A/\bar M_{\rm Xe}\), with
  \(\bar M_{\rm Xe}\) in g/mol.
- The lab-frame speed distribution \(f_{\rm lab}(v)\) weights the incident
  dark-matter population. It is not a nuclear form factor and is not included
  inside \(R_A\).
- The isotope mass \(m_A\) determines the isotope-specific kinematic
  threshold \(v_{\min,A}(E_R)\), the recoil momentum, the three-body
  invariant-mass limits, the kernel, and the mediator denominator.
- The nuclear response \(R_A(q)\) is evaluated separately for each isotope.
  Replacing the isotope sum by one average nuclear mass would therefore lose
  both isotope-dependent kinematic support and isotope-dependent nuclear
  structure.

In the code, the one-dimensional lab-frame speed PDF is already normalized.
The velocity integral is evaluated from \(v_{\min,A}\) to the halo endpoint;
equivalently, a Heaviside factor \(\Theta(v-v_{\min,A})\) can be inserted
inside an integral over the full speed range. At the 101-keV benchmark above,
only Xe-136 is open at the truncated-SHM endpoint, but the open-isotope set
changes with \(E_R\).

The mass dependence is propagated consistently through \(q_{\rm resp}\),
\(q_{\rm kin}\), \(v_{\min}\), the three-body kernel, and the propagator
denominator. The AFH response is re-interpolated at each mass/q prescription.

The calculation compares:
- all three mass schemes (A_u, nist_nuclear, ame2020_nuclear);
- exact_spatial as the response-q baseline and nr_approx as a diagnostic;
- 16/32-node speed quadrature;
- \(8\times8\times4\) baseline kernel quadrature and
  \(16\times16\times8\) independent kernel cross-checks.

The numerical tables are written to
output/ame2020_q_convention_xe131_partial/, including separate
mass-scheme and response-q rate-comparison CSV files.

### 4.1 Numerical result and convergence

The integrated workflow completed successfully in GitHub Actions run
[43045746227](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43045746227).
All 12 nuclear-mass tests and all 5 Xe-131 response/halo-fold tests passed.
The speed-grid and kernel-grid comparisons give

\[
\max\delta_{\rm speed}=1.099\times10^{-4},\qquad
\max\delta_{\rm kernel}=2.098\times10^{-4}.
\]

The largest exact-q versus manuscript-NR rate shift across the tested
mass schemes and recoil points is \(2.250\times10^{-4}\). For the AME2020
reference mass, the largest shift is \(2.12708\times10^{-4}\), at
\(E_R=267\) keV.

For the AME2020 mass and manuscript-NR response convention, the selected
Xe-131 partial rates are:

| Benchmark | \(E_R\) [keV] | \(v_{\min}\) [km/s] | Truncated-SHM rate | Untruncated-MB diagnostic |
|---|---:|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 101 | 598.554 | \(3.86785\times10^{-12}\) | \(6.35054\times10^{-12}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 101 | 789.593 | 0 | \(9.91093\times10^{-14}\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | 101 | 904.216 | 0 | \(4.32454\times10^{-15}\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | 101 | 789.593 | 0 | \(7.93870\times10^{-16}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 200 | 711.898 | \(3.88333\times10^{-12}\) | \(3.68810\times10^{-11}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 267 | 704.458 | \(5.22186\times10^{-15}\) | \(3.91667\times10^{-14}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 542 | 748.872 | \(1.13236\times10^{-16}\) | \(1.14552\times10^{-14}\) |

Rates are in events/(kg day keV). They use
\((g_1g_2g_{VN})^2=10^{-8}\), \(g_2=1\), \(m_{\chi_1}=1\) TeV,
\(m_V=10\) GeV, and \(\rho_\chi=0.3\ {\rm GeV\,cm^{-3}}\). They are
reference-normalized Xe-131 contributions per kg of natural xenon, not
detector event predictions. The untruncated-MB column is a tail diagnostic,
not the baseline halo result.

### 4.2 Mass-scheme effect at fixed response convention

For the green benchmark (\(m_s=300\) keV, \(\Delta m=1\) MeV) with
manuscript-NR response interpolation and truncated SHM:

| \(E_R\) [keV] | \(A u\) | NIST nuclear | AME2020 nuclear |
|---:|---:|---:|---:|
| 200 | \(3.93719\times10^{-12}\) | \(3.88324\times10^{-12}\) | \(3.88333\times10^{-12}\) |
| 267 | \(4.39897\times10^{-15}\) | \(5.22338\times10^{-15}\) | \(5.22186\times10^{-15}\) |
| 542 | \(1.13489\times10^{-16}\) | \(1.13236\times10^{-16}\) | \(1.13236\times10^{-16}\) |

At 267 keV, the AME2020 rate is \(18.7065\%\) above the \(A u\)
approximation and \(0.02913\%\) below the NIST-nuclear result. The strong
\(A u\)-versus-physical-mass difference is amplified by the steep AFH response
minimum. By contrast, the NIST-to-AME2020 mass update is a much smaller
correction. The rate response is not determined by \(R_A\) alone: \(m_A\)
also changes \(q\), \(v_{\min}\), the three-body kernel and the propagator
denominator.

## 5. Natural-xenon limitation

The repository contains the complete 2401-point AFH v6.0 response grid
for Xe-131 and 28 selected-point samples for the seven AFH-default xenon
isotopes (Xe-128, 129, 130, 131, 132, 134, and 136). The full all-isotope
source input is identified in the provenance record as
afh_xe_isotope_responses.csv, with SHA-256
44c88f3aaf2fb212facbe68432d38389374255432eec04ce8a76437c82c1be3a and
16,807 data rows. However, the original 16,807-row file itself is not
currently present in the repository; only its checksum and row count are
archived. The 28 selected samples were generated using exact-spatial q and
NIST nuclear masses.

The exact-spatial-q / NIST-nuclear reproduction passed on the current
mainline in
[Actions run 43177232910](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43177232910).
It compared 98 isotope contributions and 14 total-rate rows against the
archived selected-point results. The maximum relative difference in the
total natural-xenon rate was \(2.67168\times10^{-12}\). This validates the
exact-spatial-q NIST baseline at the selected recoil points.

The 28 archived samples are tied to the NIST nuclear masses. They cannot be
silently reused at AME2020 masses because the exact response momentum changes
with \(m_A\), and each isotope's \(R_A(q)\) must be evaluated at the new
\(q_{\rm exact}\). The current Xe-131 calculation can do this because its
complete 2401-point AFH response curve is archived. The corresponding full
response q-grids for the other six AFH-default xenon isotopes are not
currently archived. No missing response is inferred from Xe-131, interpolated
across isotopes, or replaced by GCN/JJ55 data.

Thus the present AME2020 result is a controlled Xe-131 isotope contribution,
not a complete AME2020 natural-xenon sum. Completing the latter requires
regenerating the six other AFH-default isotope responses at their AME2020
exact-spatial q values from the original source input or AFH v6.0 package.
Xe-124 and Xe-126 remain omitted because the current AFH default-density set
does not provide their response matrices.

The rate is also before detector efficiency, energy resolution, exposure,
cuts, backgrounds, and likelihood.

## 6. Primary sources

1. M. Wang et al., *The AME 2020 atomic mass evaluation (II). Tables, graphs
   and references*, Chinese Physics C **45** (2021) 030003,
   [DOI: 10.1088/1674-1137/abddaf](https://doi.org/10.1088/1674-1137/abddaf).
   Equations (1) and (2) give the atomic-to-nuclear mass conversion and the
   approximate total electronic binding-energy formula.
2. AMDC, official unrounded AME2020 atomic-mass table:
   [mass_1.mas20](https://amdc.impcas.ac.cn/masstables/Ame2020/mass_1.mas20).
3. P. J. Mohr, D. B. Newell, and B. N. Taylor, *CODATA recommended values of
   the fundamental physical constants: 2022*, Rev. Mod. Phys. **97** (2025)
   025002, [DOI: 10.1103/RevModPhys.97.025002](https://doi.org/10.1103/RevModPhys.97.025002).
4. NIST, *Atomic Weights and Isotopic Compositions for Xenon*:
   [NIST Xenon data](https://physics.nist.gov/cgi-bin/Compositions/stand_alone.pl?ele=Xe).
5. A. Anand, A. L. Fitzpatrick, and W. C. Haxton, *Weakly interacting
   massive particle-nucleus elastic scattering response*, Phys. Rev. C **89**
   (2014) 065501, arXiv:1308.6288.
