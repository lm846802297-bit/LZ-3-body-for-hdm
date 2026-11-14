#!/usr/bin/env python3
"""LZ 2026 high-energy NR mean-yield model (Table S5).

Independent Python port of NEST GetYieldNR mean-yield equations, including
the 15-parameter high-energy p(E) extension. This does not simulate NR
quanta fluctuations, S1/S2 detector response, position maps, or selections.

Units: recoil energy keV, field V/cm, density g/cm^3, molar mass g/mol.
Detector-specific inputs are mandatory; no 2024 LZ settings are assumed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import json
import math
from pathlib import Path
from typing import Sequence

# LZ Collaboration, arXiv:2609.02823v1, Supplemental Table S5.
LZ2026_NR_YIELD_PARAMETERS = (
    11.2, 1.1, 0.052, -0.0533,
    10.8, 0.53, 1.4,
    0.31, 2.5, 0.50,
    1.39, 1.74,
    0.0230, 0.0289, 74.7,
)
NEST_DENSITY_REFERENCE_G_CM3 = 2.90
NEST_AVOGADRO = 6.0221409e23
NEST_ATOMIC_NUMBER_XE = 54
ZURICH_EXO_W_FACTOR = 1.1716263232
ZURICH_EXO_Q_FACTOR = 1.08


@dataclass(frozen=True)
class NRMeanYield:
    recoil_energy_keV: float
    p_exponent: float
    thomas_imel: float
    charge_yield_e_per_keV: float
    light_yield_ph_per_keV: float
    electrons_mean: float
    photons_mean: float
    total_quanta_mean: float
    ions_mean_diagnostic: float
    excitons_mean_diagnostic: float
    exciton_to_ion_ratio: float
    lindhard: float
    work_function_eV: float


def high_energy_p(
    energy_keV: float, params: Sequence[float] = LZ2026_NR_YIELD_PARAMETERS
) -> float:
    """Return p(E), with p=0.5 below E0 and logarithmic extension above."""
    if len(params) < 15:
        raise ValueError("LZ 2026 high-energy NR model requires 15 parameters")
    p0, a, b, e0 = params[9], params[12], params[13], params[14]
    if energy_keV <= e0:
        return p0
    return 0.5 + a * math.log1p(b * (energy_keV - e0))


def nr_mean_yield(
    energy_keV: float,
    field_V_cm: float,
    density_g_cm3: float,
    molar_mass_g_mol: float,
    isotope_mass_number: int,
    old_w13ev: bool,
    params: Sequence[float] = LZ2026_NR_YIELD_PARAMETERS,
) -> NRMeanYield:
    """Evaluate NEST GetYieldNR mean-yield equations for one Xe isotope.

    old_w13ev must be taken from the LZ 2026 detector/data-release config.
    It is required because NEST changes Nq, Qy and Wq when this flag is false.
    """
    if len(params) < 15:
        raise ValueError("LZ 2026 high-energy NR model requires 15 parameters")
    if not all(math.isfinite(x) for x in (
        energy_keV, field_V_cm, density_g_cm3, molar_mass_g_mol
    )):
        raise ValueError("All continuous inputs must be finite")
    if energy_keV <= 0 or field_V_cm <= 0 or density_g_cm3 <= 0:
        raise ValueError("Energy, field and density must be positive")
    if molar_mass_g_mol <= 0 or isotope_mass_number <= 0:
        raise ValueError("Molar mass and isotope mass number must be positive")

    alpha, beta, gamma, delta = params[0:4]
    epsilon, zeta, eta = params[4:7]
    theta, iota = params[7:9]
    f1, f2, a, b, e0 = params[10:15]

    nq_pre_scale = alpha * energy_keV**beta
    thomas_imel = (
        gamma * field_V_cm**delta
        * (density_g_cm3 / NEST_DENSITY_REFERENCE_G_CM3)**0.3
    )
    if thomas_imel <= 0 or not math.isfinite(thomas_imel):
        raise ArithmeticError("Non-positive or non-finite Thomas-Imel parameter")

    p = high_energy_p(energy_keV, params)
    qy = 1.0 / (thomas_imel * (energy_keV + epsilon)**p)
    qy *= 1.0 - 1.0 / (1.0 + (energy_keV / zeta)**eta)**f1

    if not old_w13ev:
        nq_pre_scale *= ZURICH_EXO_W_FACTOR
        qy *= ZURICH_EXO_Q_FACTOR

    ly = nq_pre_scale / energy_keV - qy
    qy = max(qy, 0.0)
    ly = max(ly, 0.0)

    isotope_scale = math.sqrt(molar_mass_g_mol / isotope_mass_number)
    electrons = qy * energy_keV * isotope_scale
    photons = ly * energy_keV * isotope_scale
    photons *= 1.0 - 1.0 / (
        1.0 + (energy_keV / theta)**iota
    )**f2
    total_quanta = photons + electrons

    exp_arg = electrons * thomas_imel / 4.0
    if exp_arg > 700:
        raise OverflowError("Thomas-Imel exponential overflow")
    exp_value = math.exp(exp_arg)
    ions = (4.0 / thomas_imel) * math.expm1(exp_arg)
    excitons = -(
        4.0 * exp_value - (electrons + photons) * thomas_imel - 4.0
    ) / thomas_imel
    exciton_to_ion = excitons / ions if ions != 0 else math.inf

    work_alpha = 0.067366 + density_g_cm3 * 0.039693
    electron_density_cm3 = (
        density_g_cm3 / molar_mass_g_mol
        * NEST_AVOGADRO * NEST_ATOMIC_NUMBER_XE
    )
    work_function_eV = 18.7263 - 1.01e-23 * electron_density_cm3
    if old_w13ev:
        work_function_eV *= ZURICH_EXO_W_FACTOR

    if exciton_to_ion < work_alpha and energy_keV > 100.0:
        exciton_to_ion = work_alpha
        ions = total_quanta / (1.0 + exciton_to_ion)
        excitons = total_quanta - ions
    if exciton_to_ion > 1.0 and energy_keV < 1.0:
        exciton_to_ion = 1.0
        ions = total_quanta / 2.0
        excitons = total_quanta - ions

    lindhard = (total_quanta / energy_keV) * work_function_eV * 1e-3
    return NRMeanYield(
        recoil_energy_keV=energy_keV,
        p_exponent=p,
        thomas_imel=thomas_imel,
        charge_yield_e_per_keV=qy,
        light_yield_ph_per_keV=ly,
        electrons_mean=electrons,
        photons_mean=photons,
        total_quanta_mean=total_quanta,
        ions_mean_diagnostic=ions,
        excitons_mean_diagnostic=excitons,
        exciton_to_ion_ratio=exciton_to_ion,
        lindhard=lindhard,
        work_function_eV=work_function_eV,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--energy-kev", type=float, nargs="+", required=True)
    parser.add_argument("--field-v-cm", type=float, required=True)
    parser.add_argument("--density-g-cm3", type=float, required=True)
    parser.add_argument("--molar-mass-g-mol", type=float, required=True)
    parser.add_argument("--isotope-mass-number", type=int, required=True)
    parser.add_argument("--old-w13ev", choices=("true", "false"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    rows = [
        asdict(nr_mean_yield(
            energy_keV=e,
            field_V_cm=args.field_v_cm,
            density_g_cm3=args.density_g_cm3,
            molar_mass_g_mol=args.molar_mass_g_mol,
            isotope_mass_number=args.isotope_mass_number,
            old_w13ev=(args.old_w13ev == "true"),
        ))
        for e in args.energy_kev
    ]
    payload = {
        "model": "LZ 2026 NEST NR mean yield, Table S5",
        "detector_response_complete": False,
        "old_w13ev": args.old_w13ev == "true",
        "field_V_cm": args.field_v_cm,
        "density_g_cm3": args.density_g_cm3,
        "molar_mass_g_mol": args.molar_mass_g_mol,
        "isotope_mass_number": args.isotope_mass_number,
        "parameters": list(LZ2026_NR_YIELD_PARAMETERS),
        "rows": rows,
    }
    text = json.dumps(payload, indent=2)
    if args.output:
        args.output.write_text(text + "\\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
