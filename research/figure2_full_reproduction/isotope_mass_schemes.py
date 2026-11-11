"""Xenon isotope mass prescriptions for direct-detection kinematics.

A_u reproduces the existing mass-number approximation m_A=A*u.
nist_nuclear uses NIST atomic isotope masses minus 54 electron rest masses.
The latter neglects the total atomic-electron binding energy (order 0.1 MeV
for xenon), a relative correction below 1e-6 to the nuclear mass.
"""
from __future__ import annotations

U_GEV = 0.93149410242
ELECTRON_MASS_U = 0.000548579909065
Z_XE = 54

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


def isotope_mass_GeV(A: int, scheme: str = "A_u") -> float:
    """Return the isotope nuclear mass in GeV for an explicit mass scheme."""
    if A not in NIST_XE_ATOMIC_MASS_U:
        raise ValueError(f"NIST xenon isotope mass unavailable for A={A}")
    if scheme == "A_u":
        return A * U_GEV
    if scheme == "nist_nuclear":
        nuclear_mass_u = NIST_XE_ATOMIC_MASS_U[A] - Z_XE * ELECTRON_MASS_U
        return nuclear_mass_u * U_GEV
    raise ValueError("mass scheme must be 'A_u' or 'nist_nuclear'")
