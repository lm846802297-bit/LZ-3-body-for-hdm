import ThreeBody.NucleonCurrent.SachsConversion
import ThreeBody.NucleonCurrent.Normalization

/-!
# P0 / P / A0 / B nucleon-current baselines

These are the project's normalized M-only rate-level coefficients. They
share the same finite-size AFH W_M response in the numerical comparison.
The definitions do not claim that M-only exhausts the full covariant nuclear
current.
-/

namespace ThreeBody.NucleonCurrent

/-- P0: leading-order point-nucleon charge baseline. -/
def cMP0 : ℝ := 1

/-- P: pointlike Dirac form factors, retaining the finite-transfer term. -/
def cMP (tN mN : ℝ) : ℝ := cMNormalized 1 0 tN mN

/-- A0: freeze normalized F1(0)=1 and F2(0)=kappa, retaining t_N. -/
def cMA0 (kappa tN mN : ℝ) : ℝ := cMNormalized 1 kappa tN mN

/-- B: finite-transfer normalized Dirac and Pauli form factors reconstructed
from the normalized Sachs form factors. The Sachs variable is tied to -t_N. -/
def cMB (GE GM tN mN : ℝ) : ℝ :=
  cMNormalized (diracFromSachs GE GM (tauN (-tN) mN))
    (pauliFromSachs GE GM (tauN (-tN) mN)) tN mN

theorem P_formula (tN mN : ℝ) :
    cMP tN mN = 1 + tN / (8 * mN ^ 2) := by
  simp [cMP, cMNormalized]
  <;> ring

theorem A0_formula (kappa tN mN : ℝ) :
    cMA0 kappa tN mN =
      1 + tN / (8 * mN ^ 2) * (1 + 2 * kappa) := by
  simp [cMA0, cMNormalized]
  <;> ring

theorem P_zero_transfer (mN : ℝ) :
    cMP 0 mN = cMP0 := by
  simp [cMP, cMNormalized, cMP0]

theorem A0_zero_transfer (kappa mN : ℝ) :
    cMA0 kappa 0 mN = cMP0 := by
  simp [cMA0, cMNormalized, cMP0]

theorem A0_minus_P (kappa tN mN : ℝ) :
    cMA0 kappa tN mN - cMP tN mN =
      tN * kappa / (4 * mN ^ 2) := by
  rw [A0_formula, P_formula]
  ring

theorem B_zero_transfer_matches_A0 (kappa mN : ℝ) :
    cMB 1 (1 + kappa) 0 mN = cMA0 kappa 0 mN := by
  simp [cMB, cMA0, cMNormalized, diracFromSachs,
    pauliFromSachs, tauN]

theorem B_at_zero_has_F1_one (kappa mN : ℝ) :
    diracFromSachs 1 (1 + kappa) (tauN 0 mN) = 1 := by
  simp [diracFromSachs, tauN]

theorem B_at_zero_has_F2_kappa (kappa mN : ℝ) :
    pauliFromSachs 1 (1 + kappa) (tauN 0 mN) = kappa := by
  simp [pauliFromSachs, tauN]

end ThreeBody.NucleonCurrent
