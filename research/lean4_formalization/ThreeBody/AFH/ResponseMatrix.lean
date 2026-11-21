import Mathlib

/-!
# AFH response-matrix algebra

A response matrix constructed as a Gram matrix of multipole amplitudes is
symmetric and positive semidefinite. The statement applies to a common set of
final nuclear states/multipoles represented by the amplitude array below;
it does not assert that arbitrary independently tabulated response numbers
are positive semidefinite without checking their common-state construction.
-/

namespace ThreeBody.AFH

def gramResponse {n k : ℕ}
    (amplitude : Fin k → Fin n → ℝ) (i j : Fin n) : ℝ :=
  ∑ a : Fin k, amplitude a i * amplitude a j

def matrixQuadraticForm {n : ℕ}
    (response : Fin n → Fin n → ℝ) (coefficient : Fin n → ℝ) : ℝ :=
  ∑ i : Fin n, ∑ j : Fin n,
    coefficient i * response i j * coefficient j

def gramQuadraticForm {n k : ℕ}
    (amplitude : Fin k → Fin n → ℝ) (coefficient : Fin n → ℝ) : ℝ :=
  ∑ a : Fin k,
    (∑ i : Fin n, coefficient i * amplitude a i) ^ 2

theorem gramResponse_symmetric {n k : ℕ}
    (amplitude : Fin k → Fin n → ℝ) (i j : Fin n) :
    gramResponse amplitude i j = gramResponse amplitude j i := by
  unfold gramResponse
  apply Finset.sum_congr rfl
  intro a ha
  ring

theorem gramResponse_diagonal_nonnegative {n k : ℕ}
    (amplitude : Fin k → Fin n → ℝ) (i : Fin n) :
    0 ≤ gramResponse amplitude i i := by
  unfold gramResponse
  apply Finset.sum_nonneg
  intro a ha
  exact sq_nonneg (amplitude a i)

theorem gram_quadratic_form_identity {n k : ℕ}
    (amplitude : Fin k → Fin n → ℝ) (coefficient : Fin n → ℝ) :
    matrixQuadraticForm (gramResponse amplitude) coefficient =
      gramQuadraticForm amplitude coefficient := by
  classical
  calc
    matrixQuadraticForm (gramResponse amplitude) coefficient =
        ∑ i : Fin n, ∑ j : Fin n, ∑ a : Fin k,
          (coefficient i * amplitude a i) *
            (amplitude a j * coefficient j) := by
          unfold matrixQuadraticForm gramResponse
          simp_rw [Finset.mul_sum, Finset.sum_mul]
    _ = ∑ i : Fin n, ∑ a : Fin k, ∑ j : Fin n,
          (coefficient i * amplitude a i) *
            (amplitude a j * coefficient j) := by
          apply Finset.sum_congr rfl
          intro i hi
          exact Finset.sum_comm
    _ = ∑ a : Fin k, ∑ i : Fin n, ∑ j : Fin n,
          (coefficient i * amplitude a i) *
            (amplitude a j * coefficient j) := by
          exact Finset.sum_comm
    _ = ∑ a : Fin k,
          (∑ i : Fin n, coefficient i * amplitude a i) *
            (∑ j : Fin n, amplitude a j * coefficient j) := by
          apply Finset.sum_congr rfl
          intro a ha
          rw [← Finset.mul_sum, ← Finset.sum_mul]
    _ = gramQuadraticForm amplitude coefficient := by
          unfold gramQuadraticForm
          apply Finset.sum_congr rfl
          intro a ha
          have hsum :
              (∑ j : Fin n, amplitude a j * coefficient j) =
                (∑ i : Fin n, coefficient i * amplitude a i) := by
            apply Finset.sum_congr rfl
            intro i hi
            ring
          rw [hsum]
          ring

theorem gram_response_positive_semidefinite {n k : ℕ}
    (amplitude : Fin k → Fin n → ℝ) (coefficient : Fin n → ℝ) :
    0 ≤ matrixQuadraticForm (gramResponse amplitude) coefficient := by
  rw [gram_quadratic_form_identity]
  unfold gramQuadraticForm
  apply Finset.sum_nonneg
  intro a ha
  exact sq_nonneg _

/-- M-only response: the single retained amplitude is multiplied by one
normalized nucleon charge coefficient. -/
def mOnlyResponse {k : ℕ} (amplitude : Fin k → ℝ) : ℝ :=
  ∑ a : Fin k, amplitude a ^ 2

def mOnlyRate {k : ℕ} (amplitude : Fin k → ℝ) (cM : ℝ) : ℝ :=
  ∑ a : Fin k, (cM * amplitude a) ^ 2

theorem mOnly_rate_factorization {k : ℕ}
    (amplitude : Fin k → ℝ) (cM : ℝ) :
    mOnlyRate amplitude cM = cM ^ 2 * mOnlyResponse amplitude := by
  unfold mOnlyRate mOnlyResponse
  calc
    (∑ a : Fin k, (cM * amplitude a) ^ 2) =
        ∑ a : Fin k, cM ^ 2 * amplitude a ^ 2 := by
          apply Finset.sum_congr rfl
          intro a ha
          ring
    _ = cM ^ 2 * (∑ a : Fin k, amplitude a ^ 2) := by
          rw [Finset.mul_sum]

/-- AFH v6 package-to-physical response map. The factor four belongs here
exactly once; C0 is a separate finite-precision q=0 normalization. -/
def c0Normalization (A responseAtZero : ℝ) : ℝ :=
  A ^ 2 / (4 * responseAtZero)

def physicalResponse (C0 packageResponse : ℝ) : ℝ :=
  4 * C0 * packageResponse

theorem physical_response_zero_momentum_normalization
    (A responseAtZero : ℝ) (hresponse : responseAtZero ≠ 0) :
    physicalResponse (c0Normalization A responseAtZero) responseAtZero =
      A ^ 2 := by
  unfold physicalResponse c0Normalization
  field_simp [hresponse]
  <;> ring

theorem physical_response_contains_one_factor_four
    (C0 packageResponse : ℝ) :
    physicalResponse C0 packageResponse = 4 * (C0 * packageResponse) := by
  unfold physicalResponse
  ring

end ThreeBody.AFH
