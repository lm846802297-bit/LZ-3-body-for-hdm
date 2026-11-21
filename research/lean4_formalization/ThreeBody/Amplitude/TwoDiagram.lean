import ThreeBody.Amplitude.DiracClifford

/-!
# Coherent two-diagram scalar-radiation amplitude

The order of gamma matrices follows the two diagrams in the project source:
(after emission) (slash r_after + m_chi2) gamma^mu / D_after, and
(before emission) gamma^mu (slash r_before + m_chi2) / D_before.
The project production prescription keeps the before-emission denominator
zero-width and puts the pole width in the after-emission denominator.
-/

namespace ThreeBody.Amplitude

def beforeDenominator (rBeforeSq mChi2 : ℝ) : ℂ :=
  Complex.ofReal (rBeforeSq - mChi2 ^ 2)

def afterDenominator (wSq mChi2 gammaPole : ℝ) : ℂ :=
  Complex.ofReal (wSq - mChi2 ^ 2) +
    Complex.I * Complex.ofReal (mChi2 * gammaPole)

def propagatorNumerator
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (D : DiracCliffordSystem V) (r : Momentum4) (mChi2 : ℝ) :
    Module.End ℂ V :=
  D.slash r + (Complex.ofReal mChi2) • (1 : Module.End ℂ V)

def diagramAfter
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (D : DiracCliffordSystem V) (μ : Fin 4)
    (rAfter : Momentum4) (mChi2 wSq gammaPole : ℝ) :
    Module.End ℂ V :=
  (afterDenominator wSq mChi2 gammaPole)⁻¹ •
    (propagatorNumerator D rAfter mChi2 * D.gamma μ)

def diagramBefore
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (D : DiracCliffordSystem V) (μ : Fin 4)
    (rBefore : Momentum4) (mChi2 rBeforeSq : ℝ) :
    Module.End ℂ V :=
  (beforeDenominator rBeforeSq mChi2)⁻¹ •
    (D.gamma μ * propagatorNumerator D rBefore mChi2)

/-- The physical amplitude is the coherent sum of the two diagrams. -/
def totalDiagramAmplitude
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (D : DiracCliffordSystem V) (μ : Fin 4)
    (rAfter rBefore : Momentum4) (mChi2 wSq gammaPole rBeforeSq : ℝ) :
    Module.End ℂ V :=
  diagramAfter D μ rAfter mChi2 wSq gammaPole +
    diagramBefore D μ rBefore mChi2 rBeforeSq

def spinorBilinear
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (ubar : V →ₗ[ℂ] ℂ) (u : V) (T : Module.End ℂ V) : ℂ :=
  ubar (T u)

theorem coherent_bilinear_is_sum
    {V : Type} [AddCommGroup V] [Module ℂ V]
    (ubar : V →ₗ[ℂ] ℂ) (u : V)
    (Tafter Tbefore : Module.End ℂ V) :
    spinorBilinear ubar u (Tafter + Tbefore) =
      spinorBilinear ubar u Tafter +
        spinorBilinear ubar u Tbefore := by
  simp [spinorBilinear]

def complexAbsSq (z : ℂ) : ℂ := z * conj z

theorem coherent_square_contains_interference (a b : ℂ) :
    complexAbsSq (a + b) =
      complexAbsSq a + complexAbsSq b +
        a * conj b + b * conj a := by
  simp [complexAbsSq, Complex.conj_add]
  ring

/-- Leading nonrelativistic two-ordering kernel from the project's
Dirac benchmark: B(omega) = 1/(omega-Delta)-1/(omega+Delta). -/
def twoOrderingKernel (omega delta : ℝ) : ℝ :=
  1 / (omega - delta) - 1 / (omega + delta)

theorem twoOrderingKernel_factorization
    (omega delta : ℝ)
    (hminus : omega - delta ≠ 0)
    (hplus : omega + delta ≠ 0) :
    twoOrderingKernel omega delta =
      2 * delta / (omega ^ 2 - delta ^ 2) := by
  have hden : omega ^ 2 - delta ^ 2 ≠ 0 := by
    have hprod : (omega - delta) * (omega + delta) ≠ 0 :=
      mul_ne_zero hminus hplus
    have heq : omega ^ 2 - delta ^ 2 =
        (omega - delta) * (omega + delta) := by ring
    rw [heq]
    exact hprod
  unfold twoOrderingKernel
  field_simp [hminus, hplus, hden]
  <;> ring

theorem twoOrderingKernel_degenerate
    (omega : ℝ) (homega : omega ≠ 0) :
    twoOrderingKernel omega 0 = 0 := by
  simp [twoOrderingKernel, homega]

/-- Algebraic form of the cancellation between the two contracted diagrams
once the external Dirac equations have reduced their numerator terms.
The Clifford/spinor reduction hypotheses are deliberately kept separate. -/
def reducedWardAfter (delta afterRemainder : ℂ) : ℂ :=
  -1 - delta * afterRemainder

def reducedWardBefore (delta beforeRemainder : ℂ) : ℂ :=
  1 + delta * beforeRemainder

theorem reduced_two_diagram_ward_identity
    (delta afterRemainder beforeRemainder : ℂ) :
    reducedWardAfter delta afterRemainder +
      reducedWardBefore delta beforeRemainder =
        delta * (beforeRemainder - afterRemainder) := by
  unfold reducedWardAfter reducedWardBefore
  ring

theorem reduced_two_diagram_ward_degenerate
    (afterRemainder beforeRemainder : ℂ) :
    reducedWardAfter 0 afterRemainder +
      reducedWardBefore 0 beforeRemainder = 0 := by
  simp [reducedWardAfter, reducedWardBefore]

end ThreeBody.Amplitude
