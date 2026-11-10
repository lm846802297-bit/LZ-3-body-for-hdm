"""Three-body recoil kinematics and halo-speed helpers for Fig. 2.

This module implements only the tree-level kinematic support condition
printed in the manuscript and the standard untruncated Maxwell-Boltzmann
lab-frame speed distribution used as a documented DMFormFactor default.

Units:
  masses, recoil energy: GeV
  speeds passed to the halo function: km/s
  vmin_three_body_beta returns v/c (dimensionless)
"""
from __future__ import annotations

import math

C_KM_S = 299_792.458


def momentum_transfer(mA_GeV: float, ER_GeV: float) -> float:
    """Exact recoil momentum q=sqrt(2 mA ER + ER^2), in GeV."""
    if mA_GeV <= 0.0 or ER_GeV < 0.0:
        raise ValueError("Require mA>0 and ER>=0")
    return math.sqrt(2.0 * mA_GeV * ER_GeV + ER_GeV**2)


def wmax_squared(
    mchi_GeV: float,
    mA_GeV: float,
    ER_GeV: float,
    speed_km_s: float,
) -> float:
    """W_max^2 from the manuscript, in GeV^2."""
    if mchi_GeV <= 0.0 or mA_GeV <= 0.0 or ER_GeV < 0.0:
        raise ValueError("Require positive masses and ER>=0")
    beta = speed_km_s / C_KM_S
    if not 0.0 <= beta < 1.0:
        raise ValueError("Incident speed must satisfy 0<=v<c")
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    Echi = mchi_GeV * gamma
    pchi = Echi * beta
    q = momentum_transfer(mA_GeV, ER_GeV)
    return (
        mchi_GeV**2
        + 2.0 * pchi * q
        - 2.0 * (Echi + mA_GeV) * ER_GeV
    )


def vmin_three_body_beta(
    mchi_GeV: float,
    ms_GeV: float,
    mA_GeV: float,
    ER_GeV: float,
) -> float:
    r"""Minimum incident speed for chi1+A -> chi1+A+s.

    It solves W_max^2(E_R,v)=(m_chi+m_s)^2 using the W_max expression
    printed in the manuscript. The result is dimensionless beta=v/c.

    Define q=sqrt(2 m_A E_R+E_R^2) and
      a=m_s+(m_A E_R+m_s^2/2)/m_chi.
    Then
      beta_min=(q E_R+a sqrt(q^2-E_R^2+a^2))/(q^2+a^2).

    This is not the usual elastic-recoil v_min formula.
    """
    if mchi_GeV <= 0.0 or mA_GeV <= 0.0 or ms_GeV < 0.0 or ER_GeV < 0.0:
        raise ValueError("Require mchi,mA>0 and ms,ER>=0")
    if ER_GeV == 0.0 and ms_GeV == 0.0:
        return 0.0
    q = momentum_transfer(mA_GeV, ER_GeV)
    a = ms_GeV + (mA_GeV * ER_GeV + 0.5 * ms_GeV**2) / mchi_GeV
    denom = q * q + a * a
    if denom == 0.0:
        return 0.0
    radicand = q * q - ER_GeV * ER_GeV + a * a
    beta = (q * ER_GeV + a * math.sqrt(radicand)) / denom
    return beta


def vmin_three_body_km_s(
    mchi_GeV: float,
    ms_GeV: float,
    mA_GeV: float,
    ER_GeV: float,
) -> float:
    """Three-body minimum speed in km/s."""
    return C_KM_S * vmin_three_body_beta(mchi_GeV, ms_GeV, mA_GeV, ER_GeV)


def mb_lab_speed_pdf(
    speed_km_s: float,
    v0_km_s: float = 220.0,
    vE_km_s: float = 232.0,
) -> float:
    """Normalized lab-frame speed PDF for an untruncated MB halo.

    This is the analytic speed distribution corresponding to
    f_gal(u) proportional to exp(-u^2/v0^2), boosted by vE.
    It integrates to one over speed in [0,infinity). No escape-speed
    cutoff is applied here.
    """
    if speed_km_s < 0.0 or v0_km_s <= 0.0 or vE_km_s <= 0.0:
        raise ValueError("Require speed>=0 and positive v0,vE")
    v = speed_km_s
    return (
        v
        / (math.sqrt(math.pi) * v0_km_s * vE_km_s)
        * (
            math.exp(-((v - vE_km_s) / v0_km_s) ** 2)
            - math.exp(-((v + vE_km_s) / v0_km_s) ** 2)
        )
    )
