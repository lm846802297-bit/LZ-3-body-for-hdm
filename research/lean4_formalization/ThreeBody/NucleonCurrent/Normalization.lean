import Mathlib

/-!
# Nucleon charge-matching normalization

This module formalizes the repository's current M-only rate-level
matching definitions. It proves algebraic identities; it does not yet
derive the matching coefficient from the full covariant Dirac-Pauli
current or a spinor reduction.
-/

namespace ThreeBody.NucleonCurrent

/-- Raw flavor-summed charge coefficient. -/
def cMRaw (F1 F2 t mN : ℝ) : ℝ :=
  F1 + t / (8 * mN ^ 2) * (F1 + 2 * F2)

/-- Normalized coefficient paired with g_VN = 3 g_Vq. -/
def cMHat (F1 F2 t mN : ℝ) : ℝ :=
  cMRaw F1 F2 t mN / 3

/-- At zero transfer, the raw universal u+d+s vector charge is three. -/
theorem raw_zero_transfer
    (F2 mN : ℝ) :
    cMRaw 3 F2 0 mN = 3 := by
  simp [cMRaw]

/-- The normalized zero-transfer charge is one. -/
theorem normalized_zero_transfer
    (F2 mN : ℝ) :
    cMHat 3 F2 0 mN = 1 := by
  norm_num [cMHat, cMRaw]

/-- Raw and normalized coefficients differ by exactly a factor of three. -/
theorem raw_eq_three_mul_normalized
    (F1 F2 t mN : ℝ) :
    cMRaw F1 F2 t mN = 3 * cMHat F1 F2 t mN := by
  unfold cMHat
  ring

/-- P0: leading-order normalized point-Dirac charge coefficient. -/
def cMHatP0 : ℝ := 1

/-- P: finite-transfer point-Dirac coefficient in the adopted M-only
matching prescription. qN2 denotes Q_N^2 = -t_N, not AFH Q_A^2. -/
def cMHatP (qN2 mN : ℝ) : ℝ :=
  1 - qN2 / (8 * mN ^ 2)

/-- P reduces to P0 at zero invariant transfer. -/
theorem point_dirac_zero_transfer
    (mN : ℝ) :
    cMHatP 0 mN = cMHatP0 := by
  simp [cMHatP, cMHatP0]

/-- P/P0 differential-rate multiplier in the current M-only comparison. -/
def pToP0RateRatio (qN2 mN : ℝ) : ℝ :=
  (cMHatP qN2 mN) ^ 2

/-- Expanded polynomial form of the P/P0 rate ratio. -/
theorem pToP0RateRatio_expansion
    (qN2 mN : ℝ) :
    pToP0RateRatio qN2 mN =
      1 - qN2 / (4 * mN ^ 2) +
        (qN2 / (8 * mN ^ 2)) ^ 2 := by
  unfold pToP0RateRatio cMHatP
  ring

end ThreeBody.NucleonCurrent
