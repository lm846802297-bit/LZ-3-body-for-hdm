# Supplied L00 benchmark: unit couplings and Delta m = 450 keV

Date: 2026-11-11

## 1. Supplied model point

This benchmark supplements the earlier Eq. (6) diagnostics with the parameter
choice supplied for the target-rest-frame time component:

| Input | Value |
|---|---:|
| g1 | 1 |
| g2 | 1 |
| gVN | 1 |
| m_chi1 | 1 TeV |
| m_chi2 | 1 TeV + 450 keV |
| Delta m | 450 keV |
| mV | 10 GeV |
| ms | 300 keV |

Natural units are used internally. In particular,
m_chi2 = 1000.000450 GeV and ms = 0.000300 GeV.

The quantity checked is
\[
\mathcal L_{00}=\frac12\sum_{\rm spins}
\left|\bar u(p')\Gamma^0u(p)\right|^2,
\]
where Gamma^0 is evaluated in the target-rest frame. The implementation
uses the Dirac trace and the same two coherent emission diagrams as
eq6_kernel.py.

## 2. Explicit kinematic point

The supplied parameter list does not specify the target mass, recoil energy,
incident speed, or the internal phase-space angles. A pointwise numerical
\(\mathcal L_{00}\) therefore is not unique from the supplied list alone.

To make this addition directly reproducible and comparable with the existing
Eq. (6) diagnostic, the script explicitly inherits the established reference
kinematics:

| Kinematic input | Value |
|---|---:|
| Target mass m_A | 122 GeV (approximate Xe-131 reference) |
| Recoil energy E_R | 200 keV |
| Incident speed v | 776 km/s |
| W^2 | midpoint of [W_min^2, W_max^2] |
| z = cos(theta*) | 0.2 |
| phi* | 1.1 rad |
| Frame for Gamma^0 | target rest frame |

These inherited kinematics are calculation conventions for this regression
point; they are not additional values claimed to have been specified in the
source benchmark.

At this point:
\[
W_{\min}^2=1000000.60000009~\mathrm{GeV}^2,
\qquad
W_{\max}^2=1000000.69482081~\mathrm{GeV}^2.
\]
Thus the three-body phase space is open. However,
\[
m_{\chi_2}-\sqrt{W_{\max}^2}
=102.5897~\mathrm{keV}>0,
\]
so the internal \(\chi_2\) cannot be produced on shell at this point.
Equivalently,
\[
m_{\chi_2}^2-W_{\max}^2
=0.20517939~\mathrm{GeV}^2.
\]

## 3. Pointwise target-rest-frame L00

For zero width, the trace decomposition is:

| Contribution | Value |
|---|---:|
| Before-emission diagram | \(6.6821726133\times10^{12}\) |
| After-emission diagram | \(2.5077921539\times10^{14}\) |
| Interference | \(8.1871851208\times10^{13}\) |
| Full \(\mathcal L_{00}\) | \(3.3933323921\times10^{14}\) |

The interference is positive and sizeable. The two diagrams must therefore
be added at amplitude level before squaring.

## 4. Finite-width comparison

Because \(\Delta m=450\) keV exceeds \(m_s=300\) keV, the scalar decay
\(\chi_2\to\chi_1s\) is open. With \(g_2=1\), the conditional Dirac,
pure-scalar, single-open-channel width implemented in
eq6_kernel.chi2_width_dirac_scalar is
\[
\Gamma_{\chi_2}=5.3385608391\times10^{-5}~\mathrm{GeV}
=53.3856084~\mathrm{keV}.
\]

The pointwise trace becomes:

| Contribution | Zero width | Conditional scalar pole width |
|---|---:|---:|
| Before | \(6.6821726133\times10^{12}\) | \(6.6821726133\times10^{12}\) |
| After | \(2.5077921539\times10^{14}\) | \(2.4005588506\times10^{14}\) |
| Interference | \(8.1871851208\times10^{13}\) | \(7.8371007234\times10^{13}\) |
| Full \(\mathcal L_{00}\) | \(3.3933323921\times10^{14}\) | \(3.2510906491\times10^{14}\) |

At this phase-space point the conditional pole width reduces the full trace
by 4.1918%. This is a conditional comparison, not a claim that the full
model width has been established: the vector-sector contribution to the
\(\chi_2\) self-energy and the UV gauge/Goldstone completion are not included
in this scalar-only width.

## 5. Integrated Eq. (6) check

The reduced integral
\[
I_6=\int_{W_{\min}^2}^{W_{\max}^2}dW^2
\sqrt{\lambda}\int_{-1}^{1}dz\,
\langle\mathcal L_{00}\rangle_{\phi_*}
\]
was evaluated with Gauss-Legendre orders
\((n_W,n_z,n_\phi)=(48,40,24)\).

| Width prescription | \(I_6\) [GeV\(^2\)] |
|---|---:|
| Zero width | \(1.6218103154\times10^7\) |
| Conditional scalar pole width | \(1.5439364806\times10^7\) |

The pole-width result is 4.80166% below the zero-width result.

The last two quadrature levels, (40,32,20) and (48,40,24), differ by
approximately \(6.54\times10^{-7}\) for the zero-width integral and
\(6.66\times10^{-7}\) for the pole-width integral. The integral is therefore
well converged at the quoted point for the current Dirac implementation.

## 6. Full prefactor with the supplied mediator and couplings

For the supplied values \(g_1=g_2=g_{VN}=1\) and \(m_V=10\) GeV, the
Eq. (6) prefactor was also evaluated using the same inherited kinematics.
Since the numerical nuclear response \(\mathcal R_A(E_R)\) is a separate
input, the reported quantity is \((d\sigma_A/dE_R)/\mathcal R_A\):

| Width prescription | \((d\sigma_A/dE_R)/\mathcal R_A\) [GeV\(^{-3}\)] |
|---|---:|
| Zero width | 3.71673495 |
| Conditional scalar pole width | 3.53826993 |

The physical differential cross section is obtained by multiplying these
values by the appropriate dimensionless nuclear response at 200 keV.
These numbers are not halo-folded event rates.

## 7. Interpretation and limitations

1. The supplied benchmark is now a separate regression point with its own
   script and tests; it does not overwrite the historical \(\Delta m=1\) MeV
   benchmark.
2. \(g_1\), \(g_{VN}\), and \(m_V\) do not enter the isolated fermion
   current trace \(\mathcal L_{00}\). They enter the overall cross-section
   prefactor. \(g_2\) additionally controls the conditional scalar width.
3. The finite-width calculation assumes Dirac fermions, a pure scalar
   off-diagonal Yukawa vertex, and \(\chi_2\to\chi_1s\) as the only open
   decay channel. It is not the full vector-plus-scalar one-loop self-energy.
4. The source benchmark did not supply \(E_R,v,m_A,W^2,z,\phi_*\). The
   inherited diagnostic point is explicitly documented above so the quoted
   pointwise \(\mathcal L_{00}\) is not misrepresented as unique.
5. The calculation still does not include the nuclear response, halo integral,
   detector efficiency, energy resolution, or exposure.

## 8. Reproduction

From the repository root:

~~~bash
python research/figure2_full_reproduction/run_user_l00_benchmark.py
python -m unittest discover \
  -s research/figure2_full_reproduction/tests \
  -p 'test_user_l00_benchmark.py' -v
~~~

The script accepts --nw, --nz, and --nphi to change quadrature
orders, and --output PATH to write the numerical JSON archive.

Main implementation:
- run_user_l00_benchmark.py
- tests/test_user_l00_benchmark.py

The benchmark is deliberately separate from the natural-xenon halo-fold
calculation. It validates the supplied particle/coupling point at the
amplitude and Eq. (6) levels before any new detector-rate interpretation.
