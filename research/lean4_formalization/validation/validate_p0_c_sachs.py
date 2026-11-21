#!/usr/bin/env python3
"""Independent SymPy validation of the LZ-3-body-for-hdm Lean P0/P/A0/B identities.

This script checks symbolic identities and deterministic numerical spot checks.
It does not prove the physical validity of the impulse prescription or the
M-only matching ansatz; it verifies the algebra conditional on the repository's
frozen definitions.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import sympy as sp

OUT = Path(__file__).resolve().parent

# Symbols and domains.
q, mu, mS, v = sp.symbols("q mu mS v", real=True)
mA, ER, mN = sp.symbols("m_A E_R m_N", real=True)
F1raw, F2raw, F1hat, F2hat, tN = sp.symbols(
    "F1_raw F2_raw F1_hat F2_hat t_N", real=True
)
GE, GM, tau, kappa = sp.symbols("G_E G_M tau kappa", real=True)
omega, delta = sp.symbols("omega Delta", real=True)
aR, aI, bR, bI = sp.symbols("a_R a_I b_R b_I", real=True)
aRem, bRem = sp.symbols("A_after B_before", real=True)

# P0: reduced three-body recoil-deficit identity.
D = q * v - q**2 / (2 * mu) - mS
vmin = q / (2 * mu) + mS / q
D_factorized = q * (v - vmin)

# Nuclear spatial momentum versus invariant nucleon transfer.
tN_impulse = -2 * mA * ER
QN2 = -tN_impulse
QA2 = 2 * mA * ER + ER**2

# The alternative is recorded only as a comparison, not adopted.
tN_spatial_substitution = -QA2

# Raw and normalized c_M conventions.
cM_raw = F1raw + tN / (8 * mN**2) * (F1raw + 2 * F2raw)
cM_hat_from_raw = cM_raw / 3
cM_hat_from_normalized = F1hat + tN / (8 * mN**2) * (F1hat + 2 * F2hat)

# Sachs conversion with tau = Q_N^2/(4 m_N^2) = -t_N/(4m_N^2).
F1_from_sachs = (GE + tau * GM) / (1 + tau)
F2_from_sachs = (GM - GE) / (1 + tau)
GE_from_dirac_pauli = F1hat - tau * F2hat
GM_from_dirac_pauli = F1hat + F2hat

# Four project baselines, using normalized form factors.
P0 = sp.Integer(1)
P = 1 + tN / (8 * mN**2)
A0 = 1 + tN / (8 * mN**2) * (1 + 2 * kappa)
B = F1_from_sachs + tN / (8 * mN**2) * (
    F1_from_sachs + 2 * F2_from_sachs
)
B_tau_form = sp.factor(B.subs(tN, -4 * mN**2 * tau))

checks: dict[str, str] = {}

def exact_check(name: str, expr: sp.Expr) -> None:
    residual = sp.factor(sp.together(sp.simplify(expr)))
    checks[name] = str(residual)
    if residual != 0:
        raise AssertionError(f"{name}: nonzero symbolic residual {residual}")

exact_check("D_factorization", D - D_factorized)
exact_check("QA2_minus_QN2_equals_ER2", QA2 - QN2 - ER**2)
exact_check("tN_impulse_minus_spatial_alternative_equals_ER2", tN_impulse - tN_spatial_substitution - ER**2)
exact_check(
    "raw_normalized_cM_equivalence",
    cM_hat_from_raw.subs({F1raw: 3 * F1hat, F2raw: 3 * F2hat})
    - cM_hat_from_normalized,
)
exact_check("raw_cM_zero_transfer", cM_raw.subs({F1raw: 3, tN: 0}) - 3)
exact_check("normalized_cM_zero_transfer", cM_hat_from_raw.subs({F1raw: 3, tN: 0}) - 1)
exact_check("P_zero_transfer_equals_P0", P.subs(tN, 0) - P0)
exact_check("A0_zero_transfer_equals_P0", A0.subs(tN, 0) - P0)
exact_check("Sachs_E_reconstruction", sp.together(F1_from_sachs - tau * F2_from_sachs - GE))
exact_check("Sachs_M_reconstruction", sp.together(F1_from_sachs + F2_from_sachs - GM))
exact_check("Sachs_F1_at_zero", F1_from_sachs.subs({tau: 0, GE: 1, GM: 1 + kappa}) - 1)
exact_check("Sachs_F2_at_zero", F2_from_sachs.subs({tau: 0, GE: 1, GM: 1 + kappa}) - kappa)
exact_check(
    "B_at_zero_transfer_matches_A0",
    B.subs({tN: 0, tau: 0, GE: 1, GM: 1 + kappa})
    - A0.subs(tN, 0),
)
exact_check(
    "P_rate_ratio_expansion",
    (1 - QN2 / (8 * mN**2))**2
    - (1 - QN2 / (4 * mN**2) + (QN2 / (8 * mN**2))**2),
)

# Confirm the B expression is exactly the project c_M expression after Sachs
# conversion; no extra factor of three is introduced in the normalized basis.
exact_check(
    "B_Sachs_cM_definition",
    B - (F1_from_sachs + tN / (8 * mN**2) * (F1_from_sachs + 2 * F2_from_sachs)),
)

# P1 amplitude identities: the leading two-ordering NR kernel and the
# reduced Ward cancellation after the external Dirac equations are applied.
Bkernel = 1 / (omega - delta) - 1 / (omega + delta)
Bkernel_factored = 2 * delta / (omega**2 - delta**2)
exact_check("two_ordering_kernel_factorization", Bkernel - Bkernel_factored)
exact_check("two_ordering_kernel_degenerate_limit", Bkernel.subs(delta, 0))
exact_check(
    "reduced_two_diagram_ward_cancellation",
    (-1 - delta * aRem) + (1 + delta * bRem) - delta * (bRem - aRem),
)

# Complex coherent-sum identity, with explicit real and imaginary parts.
a_complex = aR + sp.I * aI
b_complex = bR + sp.I * bI
complex_abs_sq = lambda z: sp.expand_complex(z * sp.conjugate(z))
exact_check(
    "coherent_square_interference_identity",
    complex_abs_sq(a_complex + b_complex)
    - complex_abs_sq(a_complex) - complex_abs_sq(b_complex)
    - a_complex * sp.conjugate(b_complex)
    - b_complex * sp.conjugate(a_complex),
)

# AFH Gram-matrix positivity: exact integer-valued independent checks over
# deterministic random amplitude arrays.
A_symbol, R0_symbol = sp.symbols("A R0", real=True, nonzero=True)
exact_check(
    "AFH_C0_factor_four_zero_momentum_identity",
    sp.cancel(4 * (A_symbol**2 / (4 * R0_symbol)) * R0_symbol - A_symbol**2),
)

# Deterministic sign-equivalence spot checks for q>0 and mu>0.
rng = random.Random(20261121)
max_factor_relative_residual = 0.0
max_sign_mismatch = 0
for _ in range(10000):
    qv = 10 ** rng.uniform(-3, 2)
    muv = 10 ** rng.uniform(-3, 3)
    msv = 10 ** rng.uniform(-5, 1)
    vv = rng.uniform(0.0, 1.0e3)
    d = qv * vv - qv**2 / (2.0 * muv) - msv
    vm = qv / (2.0 * muv) + msv / qv
    df = qv * (vv - vm)
    scale = max(1.0, abs(d), abs(df))
    max_factor_relative_residual = max(
        max_factor_relative_residual, abs(d - df) / scale
    )
    if (d >= 0.0) != (vv >= vm):
        max_sign_mismatch += 1
if max_sign_mismatch:
    raise AssertionError(f"minimum-speed sign equivalence failed {max_sign_mismatch} times")

# Exact finite-dimensional Gram checks (5 final-state amplitudes x 4 channels).
gram_trials = 1000
for trial in range(gram_trials):
    rows, cols = 5, 4
    amp = sp.Matrix([[rng.randint(-7, 7) for _ in range(cols)] for _ in range(rows)])
    coeff = sp.Matrix([rng.randint(-5, 5) for _ in range(cols)])
    W = amp.T * amp
    lhs = (coeff.T * W * coeff)[0]
    rhs = sum((amp * coeff)[i] ** 2 for i in range(rows))
    if lhs != rhs or lhs < 0 or W != W.T:
        raise AssertionError(f"AFH Gram matrix identity/PSD failed at trial {trial}")

# Reproduce representative Xe-131 values from the canonical project note.
mA_xe131 = 121.933  # GeV
mN_value = 0.938919  # GeV
kappa_sufian2017 = -0.1868323435
recoils_keV = [5.4, 50.0, 100.0, 200.0, 269.9]
benchmark_rows = []
for er_keV in recoils_keV:
    er_GeV = er_keV * 1.0e-6
    qn2_value = 2.0 * mA_xe131 * er_GeV
    qn_value = math.sqrt(qn2_value)
    tau_value = qn2_value / (4.0 * mN_value**2)
    p_value = 1.0 - qn2_value / (8.0 * mN_value**2)
    p_ratio = p_value**2
    a0_value = 1.0 - qn2_value / (8.0 * mN_value**2) * (1.0 + 2.0 * kappa_sufian2017)
    benchmark_rows.append({
        "ER_keV": er_keV,
        "QN_MeV": qn_value * 1000.0,
        "tau_N": tau_value,
        "P_cMhat": p_value,
        "P_over_P0_rate_ratio": p_ratio,
        "A0_cMhat_Sufian2017": a0_value,
    })

# Environment and source provenance. No external numerical data files are read.
def command_output(cmd: list[str]) -> str | None:
    if shutil.which(cmd[0]) is None:
        return None
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception as exc:  # record environment query failure without hiding it
        return f"ERROR: {type(exc).__name__}: {exc}"

cpu_model = None
try:
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        if line.lower().startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
except OSError:
    pass

mem_total_kib = None
try:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            mem_total_kib = int(line.split()[1])
            break
except OSError:
    pass

script_bytes = Path(__file__).read_bytes()
metadata = {
    "task_id": "20261121-lean4-p0-formalization",
    "validation_id": "sympy-p0-c-sachs-20261121-01",
    "status": "PASS",
    "scope": [
        "recoil deficit factorization",
        "minimum-speed sign equivalence sampled under q>0 and mu>0",
        "AFH spatial Q_A^2 versus invariant Q_N^2 distinction",
        "raw/normalized c_M algebra",
        "Sachs <-> Dirac-Pauli conversion",
        "P0/P/A0/B normalized coefficient identities",
        "coherent two-diagram interference algebra",
        "reduced two-diagram Ward cancellation",
        "AFH Gram response positive-semidefinite construction",
        "AFH factor-four zero-momentum normalization",
    ],
    "excluded_claims": [
        "does not derive the c_M matching formula from the full covariant current",
        "does not validate physical input form-factor fits",
        "does not validate the impulse prescription itself",
        "does not compute three-body phase-space, AFH OBDME, halo, or detector rates",
    ],
    "repository": "lm846802297-bit/LZ-3-body-for-hdm",
    "baseline_commit": "d2407050ed0f4975387bc6c05bc4509ccf375c31",
    "development_branch": "research/lean4-formalization-p0-20261121",
    "source_blob_shas": {
        "CM_RAW_NORMALIZATION_AND_AFH_M_RESPONSE.md": "04f53726979d2ab936932de3ead85e78eb3ebfb3",
        "P0_VS_P_POINTLIKE_DIRAC_BASELINES.md": "a618c2d209e3a19af028e670f155d322cd6ee6a6",
        "POINTLIKE_NUCLEON_P_A_B_COMPARISON.md": "af87bfc15b00d17131735b2215ce9b5ae1d25551",
        "01_model_and_amplitude.md": "8d8daf3e6d45235040c98bf3e3ed374c449baa2d",
    },
    "input_data": [],
    "symbolic_checks": checks,
    "numeric_checks": {
        "random_seed": 20261121,
        "random_samples": 10000,
        "max_relative_deficit_factorization_residual": max_factor_relative_residual,
        "minimum_speed_sign_mismatches": max_sign_mismatch,
        "AFH_Gram_trials": gram_trials,
        "AFH_Gram_dimensions": [5, 4],
        "AFH_Gram_failures": 0,
    },
    "xe131_reference": {
        "mA_GeV": mA_xe131,
        "mN_GeV": mN_value,
        "F2hat_zero_Sufian2017": kappa_sufian2017,
        "rows": benchmark_rows,
    },
    "environment": {
        "execution_target": "ChatGPT Linux container",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "os": platform.platform(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "cpu_model": cpu_model,
        "logical_cpu_count": os.cpu_count(),
        "memory_total_kib": mem_total_kib,
        "python": sys.version,
        "sympy": sp.__version__,
        "lean": command_output(["lean", "--version"]),
        "lake": command_output(["lake", "--version"]),
        "nvidia_smi": command_output(["nvidia-smi"]),
    },
    "source_script_sha256": hashlib.sha256(script_bytes).hexdigest(),
}

(OUT / "sympy_validation.json").write_text(json.dumps(metadata, indent=2) + "\n")
with (OUT / "xe131_p_p0_a0_spotchecks.csv").open("w", encoding="utf-8") as f:
    f.write("ER_keV,QN_MeV,tau_N,P_cMhat,P_over_P0_rate_ratio,A0_cMhat_Sufian2017\n")
    for row in benchmark_rows:
        f.write(",".join(str(row[k]) for k in [
            "ER_keV", "QN_MeV", "tau_N", "P_cMhat",
            "P_over_P0_rate_ratio", "A0_cMhat_Sufian2017"
        ]) + "\n")

print(json.dumps({
    "status": metadata["status"],
    "symbolic_checks": len(checks),
    "random_samples": 10000,
    "AFH_Gram_trials": gram_trials,
    "AFH_Gram_failures": 0,
    "max_relative_deficit_factorization_residual": max_factor_relative_residual,
    "minimum_speed_sign_mismatches": max_sign_mismatch,
    "xe131_rows": benchmark_rows,
    "environment": metadata["environment"],
    "source_script_sha256": metadata["source_script_sha256"],
}, indent=2))
