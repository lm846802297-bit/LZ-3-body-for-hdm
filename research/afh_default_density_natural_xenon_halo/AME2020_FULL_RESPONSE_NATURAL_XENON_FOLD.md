# AME2020/CODATA-2022 seven-isotope natural-xenon halo fold

**Status:** end-to-end numerical fold completed and archived for the seven AFH v6.0 default-density isotopes. This is a 99.8158%-abundance subset, not a nine-isotope-complete xenon prediction.

## 1. Main result and scope

The natural-xenon three-body rate has now been recomputed using:

1. unrounded AME2020 atomic masses converted to nuclear masses with CODATA-2022;
2. AFH v6.0 built-in default-density responses for Xe-128, Xe-129, Xe-130,
   Xe-131, Xe-132, Xe-134, and Xe-136;
3. the exact spatial response momentum
   \[
   q_{\rm AFH}=q_{\rm exact}=\sqrt{2m_AE_R+E_R^2};
   \]
4. isotope-specific exact three-body thresholds and kernels;
5. the truncated Standard Halo Model (SHM) as the baseline velocity
   distribution.

The seven available natural atom fractions sum to
\[
\sum_{A\in\{128,129,130,131,132,134,136\}}\xi_A=0.998158.
\]
They are used without renormalization. Xe-124 and Xe-126 are omitted because
the official AFH v6.0 package does not contain the corresponding built-in
default-density matrices. Their combined natural abundance is 0.001842.

The calculation is therefore a **seven-isotope natural-xenon prediction**
covering 99.8158% of the natural atom fraction. It is not labelled as a
complete nine-isotope prediction.

The numerical outputs are archived under
research/afh_default_density_natural_xenon_halo/output/ame2020_full_response/.
The full AFH response curves and extracted density matrices are archived
under research/afh_default_density_xenon_all_isotopes/output/.

## 2. Why isotope composition and the halo velocity distribution both enter

For a detector target made of natural xenon, the target is a mixture of
isotopes. The number of target nuclei of isotope \(A\) in one kilogram is
\[
N_{T,A}=\frac{1000\,N_{\rm Av}}{\bar M_{\rm Xe}}\,\xi_A,
\]
where \(\bar M_{\rm Xe}=131.2927614478\ {\rm g/mol}\) is the abundance-weighted
natural-xenon atomic molar mass and \(\xi_A\) is the natural atom fraction.

The rate is an isotope sum and a halo-speed integral:
\[
\boxed{
\frac{dR_{\rm Xe}}{dE_R}
=
\frac{\rho_\chi}{m_{\chi_1}}\,c
\sum_A N_{T,A}
\int_{v_{\min,A}(E_R)}^{v_{\max}}
dv\,f_{\rm lab}(v)\frac{v}{c}
\frac{d\sigma_A}{dE_R}(v)
}
\]
with the sum restricted here to the seven AFH default-density isotopes.

These two ingredients have different physical roles:

- \(\xi_A\) weights how many nuclei of isotope \(A\) are present in the
  detector target.
- \(m_A\) determines isotope-specific recoil kinematics, \(q\),
  \(v_{\min,A}\), three-body phase-space limits, the reduced kernel, and
  the mediator denominator.
- \(R_A(q)\) is the isotope-specific AFH nuclear response. It cannot be
  replaced by a single average response or by the Xe-131 response for every
  isotope.
- \(f_{\rm lab}(v)\) weights the incident dark-matter population in the
  laboratory frame. It is not part of the nuclear response and is not an
  isotope abundance factor.

Equivalently, the velocity integral can be written over the full speed range
with \(\Theta(v-v_{\min,A})\). In the implementation, it is evaluated directly
from \(v_{\min,A}\) to the halo endpoint. Thus different isotopes can be open
or closed at the same recoil energy and benchmark.

## 3. Exact response momentum and three-body kinematics

The AFH response is a function of the magnitude of the spatial momentum
transfer \(q=|\mathbf q|\). For a target nucleus initially at rest,
\[
P^\mu=(m_A,\mathbf 0),\qquad
P'^\mu=(m_A+E_R,\mathbf q),\qquad P'^2=P^2=m_A^2,
\]
so
\[
q_{\rm exact}^2=2m_AE_R+E_R^2.
\]
The approximation \(q_{\rm NR}^2=2m_AE_R\) is used only in the separate
Xe-131 sensitivity comparison; it is not used in the natural-xenon baseline.

The propagator depends on the invariant momentum transfer:
\[
t=(P'-P)^2=-2m_AE_R,\qquad
m_V^2-t=m_V^2+2m_AE_R.
\]
This is not \(m_V^2+q_{\rm exact}^2\). The extra \(E_R^2\) in
\(q_{\rm exact}^2\) belongs to the spatial momentum magnitude and must not
be inserted into the invariant propagator denominator.

The exact three-body threshold \(v_{\min,A}\) is evaluated independently
for each isotope using its own AME2020 nuclear mass. Changing the AFH
response interpolation convention does not change this kinematic threshold;
changing the nuclear mass does.

## 4. AME2020 nuclear masses

The nuclear mass is obtained from the neutral-atom AME2020 mass:
\[
m_Ac^2=M_{\rm atom}^{\rm AME2020}(A,Z)c^2-Zm_ec^2+B_e(Z),
\]
\[
B_e(Z)=14.4381Z^{2.39}
      +1.55468\times10^{-6}Z^{5.35}\ {\rm eV}.
\]
For xenon, \(Z=54\) and
\[
B_e(54)=202.378277717\ {\rm keV}.
\]

The implementation uses the unrounded AME2020 mass_1.mas20 atomic masses and
CODATA-2022 constants:
\[
uc^2=931.49410372\ {\rm MeV},\qquad
m_ec^2=0.51099895069\ {\rm MeV}.
\]
The approximate electronic-binding correction is retained as prescribed by
the AME2020 evaluation; no unsupported precision is assigned to it.

The full nine-isotope mass table and the Xe-131 mass comparison are documented
in
[AME2020/CODATA-2022 Xe-131 exact-spatial audit](../afh_default_density_xe131/AME2020_CODATA2022_EXACT_SPATIAL_XE131.md).

## 5. AFH v6.0 default-density response regeneration

The official DMFormFactor v6.0 source archive was downloaded from the
[author's software page](https://www.ocf.berkeley.edu/~nanand/software/dmformfactor/)
and checked against the pinned SHA-256 digest
4e0f70e6e780f3f4a40faa14792cae239d1989cf15d1e211b4fd7389b0460727.

The source matrices selected are:
\[
{\tt SetIsotope[54,A,"default","default"]},
\qquad A=128,129,130,131,132,134,136.
\]
The extracted density-matrix entry counts are:

| Isotope | Matrix entries | Isoscalar rank-0 entries | Isoscalar rank-2 entries |
|---|---:|---:|---:|
| Xe-128 | 21 | 16 | 0 |
| Xe-129 | 39 | 16 | 0 |
| Xe-130 | 21 | 16 | 0 |
| Xe-131 | 67 | 16 | 8 |
| Xe-132 | 21 | 16 | 0 |
| Xe-134 | 21 | 16 | 0 |
| Xe-136 | 21 | 16 | 0 |

The absence of a rank-2 term for the spin-zero isotopes is retained as a
physical zero contribution; it is not treated as a parser failure.

For each isotope, the response is evaluated on 2401 spatial-q points:
\[
q\in[0,0.6]\ {\rm GeV},\qquad \Delta q=0.25\ {\rm MeV}.
\]
The equal-proton/equal-neutron response shape is normalized as
\[
R_A(q)=A^2\frac{W_M^{00}(q)}{W_M^{00}(0)},\qquad R_A(0)=A^2.
\]
The combined response file contains 16,807 rows.

Validation results:

- interpolation against the 28 previously archived selected isotope/recoil
  response samples: maximum relative difference
  \(1.1864\times10^{-9}\);
- the new Xe-131 2401-point curve against the previously validated
  Xe-131 curve: maximum relative difference \(3.33\times10^{-16}\);
- maximum absolute Xe-131 curve difference \(3.64\times10^{-12}\).

The 28 old samples are used only as a validation set. The AME2020 fold
interpolates the full curves at each isotope's own AME2020 exact-spatial q.

This is a source-translated Python evaluation of the AFH v6.0 matrices, not
a native Mathematica re-execution.

## 6. Halo model and benchmark inputs

The baseline halo is the normalized truncated SHM:
\[
v_0=220\ {\rm km/s},\qquad
v_E=232\ {\rm km/s},\qquad
v_{\rm esc}=544\ {\rm km/s},\qquad
v_{\max}=776\ {\rm km/s}.
\]
An untruncated boosted Maxwell-Boltzmann distribution integrated to
1600 km/s is retained only as a high-speed-tail diagnostic. It is not the
baseline result.

The benchmark normalization is
\[
m_{\chi_1}=1\ {\rm TeV},\qquad
m_V=10\ {\rm GeV},\qquad
(g_1g_2g_{VN})^2=10^{-8},\qquad
g_2=1,\qquad
\rho_\chi=0.3\ {\rm GeV/cm^3}.
\]
The width prescription is the conditional pole width for
\(\chi_2\to\chi_1s\), with Dirac \(\chi_2\), a real scalar, a pure scalar
off-diagonal Yukawa, and no other open channels.

The seven benchmark/recoil combinations are:
- four benchmarks at \(E_R=101\) keV:
  \(m_s=200,300,360\) keV with \(\Delta m=1\) MeV, and
  \(m_s=300\) keV with \(\Delta m=10\) MeV;
- the green benchmark \(m_s=300\) keV, \(\Delta m=1\) MeV at
  \(E_R=200,267,542\) keV.

## 7. AME2020 seven-isotope rate results

Rates are in events/(kg day keV). They are per kilogram of natural xenon,
using the seven available isotope fractions without renormalization.

| Benchmark | \(E_R\) [keV] | Truncated-SHM rate | Untruncated-MB diagnostic |
|---|---:|---:|---:|
| \(m_s=200\) keV, \(\Delta m=1\) MeV | 101 | \(5.28100\times10^{-11}\) | \(8.60076\times10^{-11}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 101 | \(2.62707\times10^{-22}\) | \(1.38366\times10^{-12}\) |
| \(m_s=360\) keV, \(\Delta m=1\) MeV | 101 | 0 | \(6.22366\times10^{-14}\) |
| \(m_s=300\) keV, \(\Delta m=10\) MeV | 101 | \(2.19051\times10^{-24}\) | \(1.10789\times10^{-14}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 200 | \(1.81365\times10^{-11}\) | \(1.64616\times10^{-10}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 267 | \(2.72724\times10^{-13}\) | \(1.78724\times10^{-12}\) |
| \(m_s=300\) keV, \(\Delta m=1\) MeV | 542 | \(1.45632\times10^{-15}\) | \(8.17141\times10^{-14}\) |

At \(E_R=101\) keV:
- the red benchmark has all seven isotopes kinematically open;
- the green and blue benchmarks have only Xe-136 open in the truncated SHM;
- the black benchmark has no open isotope in the truncated SHM.

The green and blue Xe-136-only rates are extremely small because the
corresponding \(v_{\min,136}\) values lie just below the 776 km/s SHM endpoint.
The untruncated-MB values are diagnostics of the high-speed tail and should
not be substituted for the truncated-SHM baseline.

## 8. NIST-to-AME2020 mass-scheme comparison

The NIST-mass exact-spatial fold was recomputed from the newly generated full
AFH curves and compared against the archived 28-sample natural-xenon result.
The comparison covers 98 isotope contributions and 14 total-rate rows:
\[
\max\left|\frac{R_{\rm new}^{\rm NIST}-R_{\rm archived}}
{R_{\rm archived}}\right|=3.432\times10^{-12}.
\]
The maximum relative differences in the isotope-level inputs and contributions
are all below \(4.34\times10^{-10}\). This is the end-to-end regression check
for the new full-response fold.

The NIST-to-AME2020 total-rate shifts are:

| Benchmark / recoil | Halo | Relative AME2020 vs NIST |
|---|---|---:|
| red, 101 keV | truncated SHM | \(-8.37\times10^{-6}\) |
| green, 101 keV | truncated SHM | \(+1.0594\%\) |
| blue, 101 keV | truncated SHM | \(+1.0594\%\) |
| green, 200 keV | truncated SHM | \(+2.25\times10^{-5}\) |
| green, 267 keV | truncated SHM | \(+4.61\times10^{-5}\) |
| green, 542 keV | truncated SHM | \(+1.24\times10^{-4}\) |

The largest relative shift, about 1.06%, occurs only for the green/blue
101-keV cases where Xe-136 is the sole open isotope and the rate is
\(O(10^{-22})\) or smaller. It is a near-endpoint velocity-tail sensitivity,
not a global 1% normalization correction. For the multi-isotope-open green
benchmarks at 200, 267, and 542 keV, the mass-scheme shifts are at most
\(1.24\times10^{-4}\) (0.0124%).

The open-isotope sets are identical between NIST and AME2020 for all 14
calculated rate cases. The mass update shifts the numerical values of
\(m_A\), \(q\), \(R_A(q)\), \(v_{\min,A}\), the three-body kernel, and the
propagator denominator, but it does not change the open-isotope set in the
benchmarks studied.

## 9. Formula-to-code-to-result traceability

| Quantity | Code | Validation / output |
|---|---|---|
| AME2020 nuclear masses | research/figure2_full_reproduction/isotope_mass_schemes.py | tests/test_isotope_mass_schemes.py |
| AFH default density-matrix extraction and response | research/afh_default_density_xenon_all_isotopes/run_afh_default_xenon_responses.py | output/afh_default_xenon_WM00.csv; output/density_matrices/; output/metadata.json |
| Three-body threshold | research/figure2_full_reproduction/rate_kinematics.py | vmin_three_body_km_s; isotope_halo_contributions.csv |
| Three-body kernel | research/figure2_full_reproduction/eq6_kernel.py | reduced_kernel; isotope_halo_contributions.csv |
| Natural-xenon isotope and halo fold | research/afh_default_density_natural_xenon_halo/run_afh_natural_xenon_halo_fold_full_response.py | nist_nuclear/ and ame2020_nuclear/ output directories |
| Mass-scheme comparison | research/afh_default_density_natural_xenon_halo/compare_full_response_mass_schemes.py | mass_scheme_comparison/ |
| End-to-end workflow | .github/workflows/ame2020-full-natural-xenon-fold.yml | [GitHub Actions run 43189847488](https://github.com/lm846802297-bit/LZ-3-body-for-hdm/actions/runs/43189847488) |

The calculation archive includes the full 98-row isotope contribution table
and 14-row total-rate table for each mass scheme, plus the NIST reproduction
comparison, NIST/AME2020 mass-scheme comparison, source metadata, and SHA-256
of the 16,807-row response grid.

## 10. Limitations and next steps

1. Xe-124 and Xe-126 are absent from the AFH v6.0 default-density matrix set.
   Their combined abundance is 0.1842%; no response is borrowed from another
   isotope and the remaining abundances are not renormalized.
2. The response curves are generated by a Python translation of the AFH v6.0
   source. The 28-point cross-check and the Xe-131 full-grid comparison pass,
   but native Mathematica re-execution has not been performed in this workflow.
3. The rates are before detector efficiency, resolution, exposure, analysis
   cuts, backgrounds, and likelihood. They are not LZ event yields or an
   exclusion contour.
4. The untruncated-MB values are diagnostic only. The truncated SHM remains
   the baseline.
5. The Xe-131 NR-q comparison is retained as a response-convention diagnostic;
   the seven-isotope result uses exact spatial q throughout.

The next detector-level step, if required, is to fold the seven-isotope
AME2020 rate with the LZ acceptance, energy resolution, exposure, and
likelihood. The 0.1842% isotope-coverage gap must remain explicit unless
the missing Xe-124/Xe-126 responses are independently supplied or regenerated.
