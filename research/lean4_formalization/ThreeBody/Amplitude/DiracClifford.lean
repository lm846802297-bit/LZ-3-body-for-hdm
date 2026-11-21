import Mathlib

/-!
# Dirac-Clifford interface for the Dirac benchmark

Metric convention: (+,-,-,-). This is an abstract representation interface:
a concrete 4x4 gamma-matrix representation must later instantiate it and
prove the Clifford relations. The Ward identity below is conditional on the
external on-shell Dirac equations; it is not an unconditional theorem about
an unspecified fermion model.
-/

namespace ThreeBody.Amplitude

def Momentum4 := Fin 4 → ℝ

def minkowskiEta (μ ν : Fin 4) : ℝ :=
  if μ = ν then (if μ.val = 0 then 1 else -1) else 0

/-- A representation of the (+---) Clifford algebra on a complex spinor
space, together with the associated momentum-slash linear map. -/
structure DiracCliffordSystem
    (V : Type) [AddCommGroup V] [Module ℂ V] where
  gamma : Fin 4 → Module.End ℂ V
  slash : Momentum4 →ₗ[ℝ] Module.End ℂ V
  clifford : ∀ μ ν,
    gamma μ * gamma ν + gamma ν * gamma μ =
      (Complex.ofReal (2 * minkowskiEta μ ν)) •
        (1 : Module.End ℂ V)
  slash_basis : ∀ μ,
    slash (Pi.single μ (1 : ℝ)) =
      (Complex.ofReal (minkowskiEta μ μ)) • gamma μ

/-- On-shell vector-current Ward identity for unequal external fermion
masses. The proof uses the left and right Dirac equations explicitly. -/
theorem vector_current_ward_identity
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (D : DiracCliffordSystem V)
    (p p' : Momentum4) (m m' : ℝ)
    (u : V) (ubar : V →ₗ[ℂ] ℂ)
    (hleft : ∀ ψ : V,
      ubar (D.slash p' ψ) = Complex.ofReal m' * ubar ψ)
    (hright : D.slash p u = (Complex.ofReal m) • u) :
    ubar (D.slash (p' - p) u) =
      Complex.ofReal (m' - m) * ubar u := by
  have hslash : D.slash (p' - p) = D.slash p' - D.slash p := by
    exact map_sub D.slash p' p
  rw [hslash]
  calc
    ubar ((D.slash p' - D.slash p) u) =
        ubar (D.slash p' u) - ubar (D.slash p u) := by simp
    _ = Complex.ofReal m' * ubar u -
        Complex.ofReal m * ubar u := by
          rw [hleft u, hright]
          simp
    _ = Complex.ofReal (m' - m) * ubar u := by
          rw [← sub_mul, ← Complex.ofReal_sub]

end ThreeBody.Amplitude
