import Mathlib

/-!
# Three-body recoil kinematics

This module formalizes the reduced heavy-particle recoil kernel.
Here q is the positive magnitude of the nuclear spatial momentum transfer
in this reduced formula. It is not a generic four-momentum and must not be
confused with q_N, q_chi, or k_s.
-/

namespace ThreeBody.Kinematics

/-- Available internal kinetic energy for scalar emission. -/
def deficit (q mu mS v : ℝ) : ℝ :=
  q * v - q ^ 2 / (2 * mu) - mS

/-- Minimum incident speed at fixed positive recoil momentum. -/
def minimumSpeed (q mu mS : ℝ) : ℝ :=
  q / (2 * mu) + mS / q

/-- Exact factorization of the recoil deficit. -/
theorem deficit_factorization
    {q mu mS v : ℝ} (hq : q ≠ 0) (hmu : mu ≠ 0) :
    deficit q mu mS v = q * (v - minimumSpeed q mu mS) := by
  unfold deficit minimumSpeed
  field_simp [hq, hmu]
  <;> ring

/-- For q > 0 and mu > 0, nonnegative available energy is equivalent
to satisfying the minimum-speed condition. -/
theorem deficit_nonneg_iff_minimum_speed
    {q mu mS v : ℝ} (hq : 0 < q) (hmu : 0 < mu) :
    0 ≤ deficit q mu mS v ↔ minimumSpeed q mu mS ≤ v := by
  rw [deficit_factorization (ne_of_gt hq) (ne_of_gt hmu)]
  constructor
  · intro h
    have hgap : 0 ≤ v - minimumSpeed q mu mS :=
      (mul_nonneg_iff_of_pos_left hq).mp h
    linarith
  · intro hv
    apply mul_nonneg hq
    linarith

/-- Adopted impulse-matching invariant: t_N = t_A = -2 m_A E_R. -/
def tNImpulse (mA ER : ℝ) : ℝ :=
  -2 * mA * ER

/-- Positive invariant transfer Q_N^2 = -t_N in the adopted convention. -/
def qNInvariantSquared (mA ER : ℝ) : ℝ :=
  -tNImpulse mA ER

/-- Exact spatial momentum squared entering the AFH oscillator variable. -/
def qASpatialSquared (mA ER : ℝ) : ℝ :=
  2 * mA * ER + ER ^ 2

/-- Q_A^2 - Q_N^2 = E_R^2: these are distinct kinematic variables. -/
theorem qA_spatial_minus_qN_invariant
    (mA ER : ℝ) :
    qASpatialSquared mA ER - qNInvariantSquared mA ER = ER ^ 2 := by
  unfold qASpatialSquared qNInvariantSquared tNImpulse
  ring

/-- Alternative substitution t_N = -Q_A^2, kept separate and not adopted. -/
def tNFromSpatialSubstitution (mA ER : ℝ) : ℝ :=
  -qASpatialSquared mA ER

/-- The adopted impulse invariant differs from the spatial substitution
by exactly E_R^2. -/
theorem impulse_minus_spatial_substitution
    (mA ER : ℝ) :
    tNImpulse mA ER - tNFromSpatialSubstitution mA ER = ER ^ 2 := by
  unfold tNImpulse tNFromSpatialSubstitution qASpatialSquared
  ring

end ThreeBody.Kinematics
