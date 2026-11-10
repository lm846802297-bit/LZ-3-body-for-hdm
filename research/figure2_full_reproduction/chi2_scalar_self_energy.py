"""One-loop chi2 self-energy from the off-diagonal scalar Yukawa channel.

Convention:
  L_int = g2 s bar(chi2) chi1 + h.c.
  S^{-1}(p) = slash(p) - m_chi2 - Sigma(slash(p)).
  Sigma = slash(p) Sigma_V(p^2) + Sigma_S(p^2).

Assumptions for this module:
  * chi1 and chi2 are Dirac fermions;
  * s is a real scalar;
  * the vertex is a pure scalar Yukawa coupling;
  * only the chi1+s loop is included.

The vector chi1+V loop is deliberately not included: the manuscript does not
supply m_V or the gauge/Goldstone completion needed to define that contribution.
All masses and energies are in GeV. NumPy is the only non-standard dependency.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np
from numpy.polynomial.legendre import leggauss


@dataclass(frozen=True)
class ScalarSelfEnergy:
    W: float
    B0: complex
    B1: complex
    B0_prime: complex
    B1_prime: complex
    sigma_V: complex
    sigma_S: complex
    sigma_V_prime: complex
    sigma_S_prime: complex
    delta_M: complex
    gamma_from_cut: float


def _f0_root(a: float) -> float:
    """Integral_0^1 dx log|x-a|."""
    if a == 0.0 or a == 1.0:
        return -1.0
    return (1.0 - a) * math.log1p(-a) + a * math.log(a) - 1.0


def _weighted_log_root(a: float) -> float:
    """Integral_0^1 dx (1-x) log|x-a|."""
    def F0(u: float) -> float:
        return u * math.log(abs(u)) - u if u != 0.0 else 0.0

    def F1(u: float) -> float:
        return 0.5 * u * u * math.log(abs(u)) - 0.25 * u * u if u != 0.0 else 0.0

    return ((1.0 - a) * (F0(1.0 - a) - F0(-a))
            - (F1(1.0 - a) - F1(-a)))


def _quad01(function, order: int = 256) -> float:
    x, w = leggauss(order)
    xs = 0.5 * (x + 1.0)
    return 0.5 * float(np.dot(w, function(xs)))


def _threshold_roots(s: float, m1: float, ms: float):
    lam2 = (s - (m1 + ms) ** 2) * (s - (m1 - ms) ** 2)
    lam = math.sqrt(max(0.0, lam2))
    x_minus = (s - m1 * m1 + ms * ms - lam) / (2.0 * s)
    x_plus = (s - m1 * m1 + ms * ms + lam) / (2.0 * s)
    return x_minus, x_plus, lam


def pv_b0_b1(s: float, m1: float, ms: float,
             mu_r: float = 1000.0, order: int = 256):
    """Finite MS-bar parts of B0 and the internal-fermion B1.

    B0 = DeltaUV - int_0^1 dx log(Delta(x)/mu_r^2)
    B1 = DeltaUV/2 - int_0^1 dx (1-x) log(Delta(x)/mu_r^2)

    For s above threshold, the real parts are integrated analytically and
    the absorptive parts are added from the Feynman +i0 prescription.
    """
    if min(s, m1, ms, mu_r) <= 0.0:
        raise ValueError("s, masses and mu_r must be positive")

    threshold = (m1 + ms) ** 2
    if s < threshold:
        def delta(x):
            return x * m1 * m1 + (1.0 - x) * ms * ms - x * (1.0 - x) * s

        b0 = -_quad01(lambda x: np.log(delta(x) / (mu_r * mu_r)), order)
        b1 = -_quad01(lambda x: (1.0 - x) * np.log(delta(x) / (mu_r * mu_r)), order)
        return complex(b0, 0.0), complex(b1, 0.0)

    x_minus, x_plus, lam = _threshold_roots(s, m1, ms)
    log_s_mu = math.log(s / (mu_r * mu_r))
    b0_re = -(log_s_mu + _f0_root(x_minus) + _f0_root(x_plus))
    b1_re = -(0.5 * log_s_mu
              + _weighted_log_root(x_minus)
              + _weighted_log_root(x_plus))
    b0_im = math.pi * (x_plus - x_minus)
    b1_im = math.pi * ((x_plus - x_minus)
                       - 0.5 * (x_plus * x_plus - x_minus * x_minus))
    return complex(b0_re, b0_im), complex(b1_re, b1_im)


def pv_b0_b1_derivatives(s: float, m1: float, ms: float,
                         order: int = 256):
    """Derivatives dB_i/ds, including the principal-value and cut pieces."""
    threshold = (m1 + ms) ** 2
    if s < threshold:
        def delta(x):
            return x * m1 * m1 + (1.0 - x) * ms * ms - x * (1.0 - x) * s

        b0p = _quad01(lambda x: x * (1.0 - x) / delta(x), order)
        b1p = _quad01(lambda x: x * (1.0 - x) ** 2 / delta(x), order)
        return complex(b0p, 0.0), complex(b1p, 0.0)

    x_minus, x_plus, lam = _threshold_roots(s, m1, ms)
    if lam <= 1.0e-30:
        raise ValueError("B0/B1 derivatives are singular at the two-body threshold")

    separation = x_plus - x_minus
    root_sum = x_minus + x_plus

    def pv_integral(numerator, polynomial_integral):
        A = numerator(x_minus) / (s * (x_minus - x_plus))
        B = numerator(x_plus) / (s * (x_plus - x_minus))
        real = (polynomial_integral
                + A * math.log(abs((1.0 - x_minus) / x_minus))
                + B * math.log(abs((1.0 - x_plus) / x_plus)))
        imag = math.pi * (numerator(x_minus) + numerator(x_plus)) / (s * separation)
        return complex(real, imag)

    # x(1-x)/[s(x-x_-)(x-x_+)] has polynomial quotient -1/s.
    b0p = pv_integral(lambda x: x * (1.0 - x), -1.0 / s)

    # x(1-x)^2/[s(x-x_-)(x-x_+)] has quotient (x+x_-+x_+-2)/s.
    b1p = pv_integral(lambda x: x * (1.0 - x) ** 2,
                      (root_sum - 1.5) / s)
    return b0p, b1p


def chi2_scalar_self_energy(W: float, m_chi1: float, m_s: float,
                             g2: complex, mu_r: float = 1000.0,
                             order: int = 256) -> ScalarSelfEnergy:
    """Return the renormalized-MS-bar scalar-loop form factors at p^2=W^2."""
    if W <= 0.0:
        raise ValueError("W must be positive")
    s = W * W
    B0, B1 = pv_b0_b1(s, m_chi1, m_s, mu_r, order)
    B0p, B1p = pv_b0_b1_derivatives(s, m_chi1, m_s, order)
    loop = abs(g2) ** 2 / (16.0 * math.pi ** 2)

    sigma_v = -loop * B1
    sigma_s = -loop * m_chi1 * B0
    sigma_vp = -loop * B1p
    sigma_sp = -loop * m_chi1 * B0p
    delta_m = W * sigma_v + sigma_s

    return ScalarSelfEnergy(
        W=W, B0=B0, B1=B1, B0_prime=B0p, B1_prime=B1p,
        sigma_V=sigma_v, sigma_S=sigma_s,
        sigma_V_prime=sigma_vp, sigma_S_prime=sigma_sp,
        delta_M=delta_m, gamma_from_cut=-2.0 * delta_m.imag,
    )


def scalar_two_body_width(W: float, m_chi1: float, m_s: float,
                          g2: complex) -> float:
    """Tree-level width for a Dirac fermion of invariant mass W -> chi1+s."""
    lam2 = (W * W - (m_chi1 + m_s) ** 2) * (W * W - (m_chi1 - m_s) ** 2)
    if lam2 <= 0.0:
        return 0.0
    return (abs(g2) ** 2 * math.sqrt(lam2)
            * ((W + m_chi1) ** 2 - m_s * m_s)
            / (16.0 * math.pi * W ** 3))


def on_shell_counterterms(m_chi1: float, m_s: float, delta_m: float,
                          g2: complex, mu_r: float = 1000.0,
                          order: int = 256):
    """Real on-shell mass and residue counterterms for the scalar channel.

    Convention:
      Gamma^(2)_R = (1 + dZ - Sigma_V) slash(p)
                    - [M + M dZ + dm_ct + Sigma_S].
    """
    M = m_chi1 + delta_m
    pole = chi2_scalar_self_energy(M, m_chi1, m_s, g2, mu_r, order)
    dm_ct = -(M * pole.sigma_V + pole.sigma_S).real
    dZ = (pole.sigma_V + M * M * pole.sigma_V_prime
          + M * pole.sigma_S_prime).real
    return {"M": M, "pole": pole, "delta_m_ct": dm_ct, "delta_Z": dZ}


def on_shell_inverse_denominator(W: float, m_chi1: float, m_s: float,
                                 delta_m: float, g2: complex,
                                 mu_r: float = 1000.0, order: int = 256):
    """One-loop OS-renormalized inverse-propagator denominator.

    The linearized denominator is the consistent fixed one-loop result.
    The Dyson-resummed determinant is also returned as a diagnostic; when
    |delta_Z| is large, the latter includes uncontrolled higher orders.
    """
    ct = on_shell_counterterms(m_chi1, m_s, delta_m, g2, mu_r, order)
    M = ct["M"]
    cur = chi2_scalar_self_energy(W, m_chi1, m_s, g2, mu_r, order)
    dZ = ct["delta_Z"]
    dm_ct = ct["delta_m_ct"]

    sigma_v_r = cur.sigma_V - dZ
    sigma_s_r = cur.sigma_S + M * dZ + dm_ct
    s = W * W

    d_linear = (s - M * M - 2.0 * s * sigma_v_r - 2.0 * M * sigma_s_r)
    d_resummed = ((1.0 - sigma_v_r) ** 2 * s
                  - (M + sigma_s_r) ** 2)
    return {
        "counterterms": ct,
        "current": cur,
        "sigma_V_R": sigma_v_r,
        "sigma_S_R": sigma_s_r,
        "denominator_one_loop": d_linear,
        "denominator_resummed": d_resummed,
    }
