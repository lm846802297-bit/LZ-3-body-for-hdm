"""Join the AFH xenon W_M response to the manuscript's Eq. (6) three-body kernel.

Conventions:
- All energies and masses are GeV; speeds are km/s.
- AFH nuclear responses are functions of the spatial momentum transfer
  q, with y=(q*b_A/2)^2. For exact three-body recoil kinematics we use
  q_response^2 = 2*m_A*E_R + E_R^2.
- q_NR^2=2*m_A*E_R is retained only as a small-recoil approximation.
- m_A = A * atomic mass unit is the same mass approximation used by the
  current response archive; replace it only when an isotope-mass source is
  selected and recorded.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from scipy.interpolate import PchipInterpolator

import eq6_kernel

U_GEV = 0.93149410242
RESPONSE_COLUMN = "R_A=4pi/(2J+1)*W_M00"


@dataclass(frozen=True)
class NuclearResponse:
    A: int
    model: str
    q_grid_GeV: np.ndarray
    response_grid: np.ndarray
    interpolator: Callable[[float], float]
    R0: float

    def at_recoil(self, ER_GeV: float, mA_GeV: float) -> tuple[float, float]:
        """Return (R_A, q_response) using exact spatial recoil momentum."""
        if ER_GeV < 0.0:
            raise ValueError("ER must be non-negative")
        q_response = math.sqrt(2.0 * mA_GeV * ER_GeV + ER_GeV**2)
        if q_response < self.q_grid_GeV[0] or q_response > self.q_grid_GeV[-1]:
            raise ValueError(
                f"response q={q_response:g} GeV is outside "
                f"[{self.q_grid_GeV[0]:g}, {self.q_grid_GeV[-1]:g}] GeV"
            )
        value = float(self.interpolator(q_response))
        if not math.isfinite(value) or value < -1e-10:
            raise ArithmeticError(f"invalid interpolated response: {value}")
        return max(0.0, value), q_response


def isotope_mass_GeV(A: int) -> float:
    if A <= 0:
        raise ValueError("A must be positive")
    return A * U_GEV


def load_nuclear_response(csv_path: str | Path, A: int, model: str) -> NuclearResponse:
    path = Path(csv_path)
    q_values: list[float] = []
    response_values: list[float] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "q_GeV" not in reader.fieldnames:
            raise ValueError(f"missing q_GeV column in {path}")
        if RESPONSE_COLUMN not in reader.fieldnames:
            raise ValueError(f"missing {RESPONSE_COLUMN!r} column in {path}")
        for row in reader:
            q_values.append(float(row["q_GeV"]))
            response_values.append(float(row[RESPONSE_COLUMN]))

    q = np.asarray(q_values, dtype=float)
    response = np.asarray(response_values, dtype=float)
    if len(q) < 4 or len(q) != len(response):
        raise ValueError("response table is incomplete")
    if not np.all(np.diff(q) > 0.0):
        raise ValueError("q grid must be strictly increasing")
    if not np.all(np.isfinite(response)):
        raise ValueError("response table contains non-finite values")

    interpolator = PchipInterpolator(q, response, extrapolate=False)
    R0 = float(response[0])
    expected = float(A * A)
    relative_error = abs(R0 / expected - 1.0)
    if relative_error > 2.0e-5:
        raise ArithmeticError(
            f"zero-momentum normalization failed for Xe-{A}/{model}: "
            f"R(0)={R0:.12g}, A^2={expected:.12g}, relerr={relative_error:.3g}"
        )
    return NuclearResponse(
        A=A,
        model=model.upper(),
        q_grid_GeV=q,
        response_grid=response,
        interpolator=interpolator,
        R0=R0,
    )


def incoming_momentum_GeV(mchi_GeV: float, speed_km_s: float) -> float:
    if mchi_GeV <= 0.0:
        raise ValueError("mchi must be positive")
    beta = speed_km_s / eq6_kernel.C_KM_S
    if beta <= 0.0 or beta >= 1.0:
        raise ValueError("speed must satisfy 0 < v < c")
    gamma = 1.0 / math.sqrt(1.0 - beta * beta)
    return mchi_GeV * gamma * beta


def differential_cross_section(
    response: NuclearResponse,
    *,
    mchi_GeV: float,
    ms_GeV: float,
    delta_m_GeV: float,
    ER_GeV: float,
    speed_km_s: float,
    coupling_product_sq: float,
    mV_GeV: float | None = None,
    width_scheme: str = "zero",
    g2: float | None = None,
    nw: int = 16,
    nz: int = 16,
    nphi: int = 8,
) -> dict[str, float | str | bool]:
    """Evaluate d sigma_A / d E_R with explicit mediator and width inputs.

    coupling_product_sq means (g1*g2*gVN)^2, as printed in the Figure 2
    caption. The separate g2 is required only for the conditional Dirac
    pole/running-width prescriptions in eq6_kernel.
    """
    values = (mchi_GeV, ms_GeV, delta_m_GeV, ER_GeV, coupling_product_sq)
    if not all(math.isfinite(float(x)) for x in values):
        raise ValueError("all scalar inputs must be finite")
    if mV_GeV is not None and (
        not math.isfinite(float(mV_GeV)) or float(mV_GeV) < 0.0
    ):
        raise ValueError("mV must be finite and non-negative when supplied")
    if mchi_GeV <= 0.0 or ms_GeV < 0.0 or delta_m_GeV < 0.0:
        raise ValueError("invalid dark-sector masses")
    if ER_GeV <= 0.0 or coupling_product_sq < 0.0:
        raise ValueError("require ER>0 and coupling_product_sq>=0")

    A = response.A
    mA = isotope_mass_GeV(A)
    R_A, q_response = response.at_recoil(ER_GeV, mA)
    q_exact = math.sqrt(2.0 * mA * ER_GeV + ER_GeV * ER_GeV)
    pchi = incoming_momentum_GeV(mchi_GeV, speed_km_s)

    wmin2, wmax2 = eq6_kernel.limits(
        mchi_GeV, ms_GeV, mA, ER_GeV, speed_km_s
    )
    open_phase_space = wmax2 > wmin2
    if wmax2 > 0.0:
        wmax = math.sqrt(wmax2)
        chi2_pole_gap_GeV = mchi_GeV + delta_m_GeV - wmax
    else:
        chi2_pole_gap_GeV = float("nan")

    I6 = eq6_kernel.reduced_kernel(
        mchi_GeV,
        ms_GeV,
        delta_m_GeV,
        mA,
        ER_GeV,
        speed_km_s,
        nw=nw,
        nz=nz,
        nphi=nphi,
        width_scheme=width_scheme,
        g2=g2,
    )

    # This coefficient excludes only the vector propagator denominator.
    # Its units are GeV; d sigma/dER has units GeV^-3.
    C_A = (
        mA * coupling_product_sq
        / (256.0 * math.pi**3 * pchi**2)
        * R_A
        * I6
    )
    if mV_GeV is None:
        propagator_denominator = None
        dsigma_dER = None
    else:
        propagator_denominator = (mV_GeV**2 + 2.0 * mA * ER_GeV) ** 2
        dsigma_dER = (
            C_A / propagator_denominator
            if propagator_denominator > 0.0 else float("inf")
        )

    return {
        "A": A,
        "model": response.model,
        "mA_GeV": mA,
        "ER_GeV": ER_GeV,
        "q_response_GeV": q_response,
        "q_kinematics_exact_GeV": q_exact,
        "R_A": R_A,
        "R_A_over_A2": R_A / (A * A),
        "pchi_GeV": pchi,
        "Wmin2_GeV2": wmin2,
        "Wmax2_GeV2": wmax2,
        "chi2_pole_gap_GeV": chi2_pole_gap_GeV,
        "phase_space_open": open_phase_space,
        "I6_GeV2": I6,
        "coupling_product_sq": coupling_product_sq,
        "width_scheme": width_scheme,
        "mV_GeV": mV_GeV,
        "C_A_GeV": C_A,
        "propagator_denominator_GeV4": propagator_denominator,
        "dsigma_dER_GeVminus3": dsigma_dER,
    }
