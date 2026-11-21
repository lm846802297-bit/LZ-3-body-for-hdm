import Mathlib

/-!
# Sachs <-> Dirac-Pauli conversion

Spacelike convention: t_N = -Q_N^2 and tau_N = Q_N^2/(4 m_N^2)
= -t_N/(4 m_N^2). All form factors in this module are normalized
flavor-summed form factors (the common factor 3 has already been removed).
-/

namespace ThreeBody.NucleonCurrent

def tauN (qN2 mN : ℝ) : ℝ := qN2 / (4 * mN ^ 2)

def diracFromSachs (GE GM tau : ℝ) : ℝ :=
  (GE + tau * GM) / (1 + tau)

def pauliFromSachs (GE GM tau : ℝ) : ℝ :=
  (GM - GE) / (1 + tau)

def electricSachs (F1 F2 tau : ℝ) : ℝ := F1 - tau * F2

def magneticSachs (F1 F2 : ℝ) : ℝ := F1 + F2

theorem one_add_tau_ne_zero {tau : ℝ} (htau : 0 ≤ tau) :
    1 + tau ≠ 0 := by
  have hpos : 0 < 1 + tau := by linarith
  exact ne_of_gt hpos

theorem electric_reconstruction
    (GE GM tau : ℝ) (htau : 0 ≤ tau) :
    electricSachs (diracFromSachs GE GM tau)
      (pauliFromSachs GE GM tau) tau = GE := by
  have hden : 1 + tau ≠ 0 := one_add_tau_ne_zero htau
  unfold electricSachs diracFromSachs pauliFromSachs
  field_simp [hden]
  <;> ring

theorem magnetic_reconstruction
    (GE GM tau : ℝ) (htau : 0 ≤ tau) :
    magneticSachs (diracFromSachs GE GM tau)
      (pauliFromSachs GE GM tau) = GM := by
  have hden : 1 + tau ≠ 0 := one_add_tau_ne_zero htau
  unfold magneticSachs diracFromSachs pauliFromSachs
  field_simp [hden]
  <;> ring

theorem dirac_zero_transfer (kappa : ℝ) :
    diracFromSachs 1 (1 + kappa) 0 = 1 := by
  simp [diracFromSachs]

theorem pauli_zero_transfer (kappa : ℝ) :
    pauliFromSachs 1 (1 + kappa) 0 = kappa := by
  simp [pauliFromSachs]

end ThreeBody.NucleonCurrent
