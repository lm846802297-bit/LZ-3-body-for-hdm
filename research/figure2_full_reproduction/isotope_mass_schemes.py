"""Xenon isotope mass prescriptions for direct-detection kinematics.

Legacy schemes are retained for exact reproduction of archived results:
  A_u          : m_A = A * u using the historical CODATA-2018 conversion;
  nist_nuclear : NIST neutral-atom masses minus 54 electron rest masses,
                 using the historical constants and neglecting electron binding.

The new ame2020_nuclear scheme uses the unrounded AME2020 atomic masses from
mass_1.mas20, converts them to nuclear masses with the AME2020 total-electron-
binding correction, and uses CODATA-2022 mass/electron constants.
"""
from __future__ import annotations

U_GEV = 0.93149410242
ELECTRON_MASS_U = 0.000548579909065
Z_XE = 54

# CODATA 2022 recommended constants (Mohr et al., Rev. Mod. Phys. 97, 025002).
U_GEV_CODATA2022 = 0.93149410372
ELECTRON_MASS_MEV_CODATA2022 = 0.51099895069
ELECTRON_MASS_U_CODATA2022 = 0.0005485799090441

# Unrounded AME2020 atomic masses from mass_1.mas20, in unified atomic mass units.
# Values are taken from the final atomic-mass column of the official AME2020 file.
AME2020_XE_ATOMIC_MASS_U = {
    124: 123.905885174,
    126: 125.904297422,
    128: 127.90353075341,
    129: 128.90478085742,
    130: 129.903509346,
    131: 130.90508412808,
    132: 131.90415508346,
    134: 133.905393030,
    136: 135.907214474,
}

# NIST relative atomic masses in unified atomic mass units.
NIST_XE_ATOMIC_MASS_U = {
    124: 123.9058920,
    126: 125.9042983,
    128: 127.9035310,
    129: 128.9047808611,
    130: 129.903509349,
    131: 130.90508406,
    132: 131.9041550856,
    134: 133.90539466,
    136: 135.907214484,
}


def electron_binding_energy_eV(Z: int) -> float:
    """AME2020 approximate total electronic binding energy B_e(Z), in eV."""
    if Z < 0:
        raise ValueError("Z must be non-negative")
    if Z == 0:
        return 0.0
    return 14.4381 * Z**2.39 + 1.55468e-6 * Z**5.35


def isotope_mass_GeV(A: int, scheme: str = "A_u") -> float:
    """Return the isotope nuclear mass in GeV for an explicit mass scheme."""
    if A not in NIST_XE_ATOMIC_MASS_U:
        raise ValueError(f"NIST xenon isotope mass unavailable for A={A}")
    if scheme == "A_u":
        return A * U_GEV
    if scheme == "nist_nuclear":
        nuclear_mass_u = NIST_XE_ATOMIC_MASS_U[A] - Z_XE * ELECTRON_MASS_U
        return nuclear_mass_u * U_GEV
    if scheme == "ame2020_nuclear":
        # M_nucleus = M_neutral_atom - Z*m_e + B_e(Z), with B_e in energy units.
        atomic_mass_u = AME2020_XE_ATOMIC_MASS_U[A]
        nuclear_mass_GeV = (
            (atomic_mass_u - Z_XE * ELECTRON_MASS_U_CODATA2022)
            * U_GEV_CODATA2022
            + electron_binding_energy_eV(Z_XE) * 1.0e-9
        )
        return nuclear_mass_GeV
    raise ValueError(
        "mass scheme must be 'A_u', 'nist_nuclear', or 'ame2020_nuclear'"
    )
