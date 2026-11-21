import Mathlib

/-!
# Nucleon charge-matching normalization

This module formalizes the repository's current M-only rate-level matching
definitions. It proves algebraic identities; it does not derive the matching
coefficient from the full covariant Dirac-Pauli current or a spinor reduction.
-/

namespace ThreeBody.NucleonCurrent

/-- Raw flavor-summed charge coefficient. -/
def cMRaw (F1 F2 t mN : ℝ) : ℝ :=
  F1 + t / (8 * mN ^ 2) * (F1 + 2 * F2)

/-- Raw coefficient divided by the universal u+d+s charge normalization 3. -/
def cMHat (F1 F2 t mN : ℝ) : ℝ := cMRaw F1 F2 t mN / 3

/-- Normalized-form-factor expression paired with g_VN = 3 g_Vq. -/
def cMNormalized (F1 F2 t mN : ℝ) : ℝ :=
  F1 + t / (8 * mN ^ 2) * (F1 + 2 * F2)

theorem raw_zero_transfer (F2 mN : ℝ) :
    cMRaw 3 F2 0 mN = 3 := by
  simp [cMRaw]

theorem normalized_zero_transfer (F2 mN : ℝ) :
    cMHat 3 F2 0 mN = 1 := by
  norm_num [cMHat, cMRaw]

theorem raw_eq_three_mul_normalized (F1 F2 t mN : ℝ) :
    cMRaw F1 F2 t mN = 3 * cMHat F1 F2 t mN := by
  unfold cMHat
  ring

theorem normalized_raw_matches_hat
    (F1raw F2raw F1hat F2hat t mN : ℝ)
    (hF1 : F1raw = 3 * F1hat)
    (hF2 : F2raw = 3 * F2hat) :
    cMHat F1raw F2raw t mN =
      cMNormalized F1hat F2hat t mN := by
  unfold cMHat cMRaw cMNormalized
  rw [hF1, hF2]
  ring

/-- P0: leading-order normalized point-Dirac charge coefficient. -/
def cMHatP0 : ℝ := 1

/-- P: finite-transfer pointlike Dirac coefficient in the adopted M-only
matching prescription. qN2 is Q_N^2=-t_N, not AFH Q_A^2. -/
def cMHatP (qN2 mN : ℝ) : ℝ :=
  1 - qN2 / (8 * mN ^ 2)

theorem point_dirac_zero_transfer (mN : ℝ) :
    cMHatP 0 mN = cMHatP0 := by
  simp [cMHatP, cMHatP0]

def pToP0RateRatio (qN2 mN : ℝ) : ℝ :=
  (cMHatP qN2 mN) ^ 2

theorem pToP0RateRatio_expansion (qN2 mN : ℝ) :
    pToP0RateRatio qN2 mN =
      1 - qN2 / (4 * mN ^ 2) +
        (qN2 / (8 * mN ^ 2)) ^ 2 := by
  unfold pToP0RateRatio cMHatP
  ring

end ThreeBody.NucleonCurrent
