# Fixed-speed Fig. 2 target-mass reproduction trial

**Status:** exploratory reproduction diagnostic  
**Date:** 2026-11-19  
**Source:** uploaded `3body_for_HDM(2).pdf`, Fig. 2 (PDF page 3)

## Question and scope

This study asks which effective target-nucleus mass reproduces the fixed-speed curves displayed in Fig. 2 of the supplied paper, for

\[
m_{\chi_1}=1\ \mathrm{TeV},\qquad
v=780\ \mathrm{km/s},\qquad
m_s=\delta_{\mathrm{iDM}}=300\ \mathrm{keV}.
\]

The calculation is deliberately restricted to the paper's fixed-speed, normalized phase-space comparison. The displayed curves are treated as normalized spectra, \((1/\sigma_i)d\sigma_i/dE_R\), with no isotope-dependent nuclear response \(R_A(E_R)\). The source PDF's Fig. 2 caption also contains the note that \((2m_T)^2\) is considered while \(R_A(E_R)\) is omitted.

This trial does **not** calculate a physical natural-xenon spectrum, a halo average, a detector response, or the project's adopted finite-\(t_N\) nucleon-form-factor plus finite-size AFH baseline.

## Source and provenance

- Source file name: `3body_for_HDM(2).pdf`
- Source SHA-256: `b4fc7bd73265df2bc2ce1640cbf8847b63323ec1dda220f9e7903f4620b871bb`
- Fig. 2: PDF page 3.
- Fixed-speed endpoint equation: Eq. (4), PDF page 2.
- Three-body phase-space kernel: Eq. (6), PDF page 2; normalized shape as plotted in Fig. 2.
- The red trace was extracted from the vector drawing paths embedded in the supplied PDF using PyMuPDF. No web image or substitute figure was used. The 199 digitized points and axis calibration are archived under `inputs/`.

The paper denotes the target-nucleus mass by \(m_N\) in its kinematics section. This archive calls it \(m_T\) to distinguish a target nucleus from a single nucleon in the project's nuclear-current notation.

## Method

For a target mass \(m_T\), the reduced mass is

\[
\mu=\frac{m_{\chi}m_T}{m_\chi+m_T}.
\]

The common recoil endpoints are

\[
E_R^\pm=
\frac{\mu^2}{2m_T}
\left(v\pm\sqrt{v^2-\frac{2m_s}{\mu}}\right)^2.
\]

The fixed-speed normalized two-body spectrum is flat inside this interval:

\[
\frac{1}{\sigma_{2\to2}}\frac{d\sigma_{2\to2}}{dE_R}
=\frac{1}{E_R^+-E_R^-}.
\]

For the three-body channel, the plotted normalized shape is obtained from

\[
I(D)=\int_0^D d\epsilon\,
\sqrt{\epsilon(\epsilon+2m_s)},\qquad
D=vq-\frac{q^2}{2\mu}-m_s,\qquad
q=\sqrt{2m_T E_R},
\]

with \(I(D)=0\) for \(D\leq0\), followed by normalization over \(E_R\).

Two independent mass determinations were used:

1. **Endpoint inversion.** Define \(S=E_R^++E_R^-\) and \(P=\sqrt{E_R^+E_R^-}\). The endpoint equations imply
   \[
   \mu=\frac{m_s}{v^2}\left(1+\frac{S}{2P}\right),\qquad
   m_T=\frac{\mu m_s}{P}.
   \]
   This inversion uses the two digitized endpoints and does not need a prior \(m_\chi\) input. It also gives an implied \(m_\chi=\mu m_T/(m_T-\mu)\), which is an independent consistency check.

2. **Red-shape fit.** With \(m_\chi=1\) TeV fixed as stated in the paper's benchmark, minimize the mean squared residual between the digitized red curve and the normalized \(I(D)\) spectrum over \(120<E_R<645\) keV.

## Results

The vector-digitized Fig. 2 red curve gives

\[
E_R^-\simeq108.4583\ \mathrm{keV},\qquad
E_R^+\simeq660.2604\ \mathrm{keV}.
\]

Endpoint inversion gives

\[
\mu\simeq107.9708\ \mathrm{GeV},\qquad
\boxed{m_T^{\rm endpoint}=121.04265\ \mathrm{GeV}},
\]

and an implied dark-matter mass

\[
m_\chi^{\rm implied}\simeq999.784\ \mathrm{GeV}.
\]

The independent red-shape fit gives

\[
\boxed{m_T^{\rm shape}=121.02525\ \mathrm{GeV}}.
\]

The two determinations agree at the level expected from reading the plotted line and axis calibration. The adopted summary for this reproduction attempt is therefore \(m_T\simeq121.04\) GeV, not a claim that the paper explicitly stated this input.

### Comparison with candidate mass conventions

| Candidate input | \(m_T\) [GeV] | \(E_R^-\) [keV] | \(E_R^+\) [keV] | \(2\to2\) plateau \([10^{-3}\,\mathrm{keV}^{-1}]\) |
|---|---:|---:|---:|---:|
| Endpoint inversion | 121.04265 | 108.4548 | 660.3122 | 1.81206 |
| Red-shape fit | 121.02525 | 108.4894 | 660.1223 | 1.81280 |
| \(A=130\) mass-number approximation, \(130u\) | 121.09423 | 108.3525 | 660.8748 | 1.80988 |
| \(122\) GeV | 122.00000 | 106.5925 | 670.7027 | 1.77270 |

The \(A=130\) approximation is numerically consistent with the Fig. 2 inference: its endpoints differ from the digitized endpoints by about \(0.11\) keV and \(0.61\) keV. This is evidence that the plotted effective target mass is close to \(130u\), but it is **not documentary proof** that the authors selected \(A=130\) for Fig. 2. The PDF does not explicitly state the Fig. 2 target isotope or mass.

The \(122\) GeV value is explicitly used in Eq. (107), PDF page 17, together with \(v=770\) km/s. That is a separate illustration and does not establish the target mass used in Fig. 2.

## Figure and machine-readable outputs

- `figures/fig2_target_mass_inference.svg`: vector-digitized paper trace overlaid with the reconstructed normalized spectra.
- `results/fig2_target_mass_inference.json`: fit, endpoint inversion, comparison cases, and source provenance.
- `inputs/fig2_red_curve_digitized.csv`: 199 vector-digitized red-curve points.
- `inputs/fig2_digitization_metadata.json`: source hash, axis calibration, endpoints, peak, and blue plateau.
- `run_manifest.json`: execution environment, commands, and file hashes.

## Reproduction

From the repository root:

```bash
python research/three_body_calculation_and_validation/fig2_target_mass_reproduction_trial_20261119/scripts/reproduce_fig2_mass_inference.py
python -m unittest discover -s research/three_body_calculation_and_validation/fig2_target_mass_reproduction_trial_20261119/tests -v
```

Dependencies used for the archived run: Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8, and PyMuPDF for the one-time vector extraction. The reproduction script itself reads the archived CSV and does not require the source PDF or PyMuPDF.

## Source-interpretation issue retained for follow-up

The Fig. 2 caption calls the plotted quantity a “ratio of the differential recoil cross sections,” while the vertical axis is labelled as \((1/\sigma)\,d\sigma/dE_R\) and carries units of inverse energy. A literal pointwise ratio of two differential cross sections would be dimensionless. This archive reproduces the **normalized shapes indicated by the vertical axis**, not the dimensionless pointwise ratio in Eq. (8). The caption wording and the plotted normalization should be checked against the authors' plotting convention before this figure is used for any absolute cross-section statement.

## Boundary with the adopted project calculation

The project's adopted production baseline remains **B: finite-\(t_N\) nucleon Dirac–Pauli form factors \(F_{1,2}^{V,N}(t_N)\) multiplied by the finite-size AFH charge response \(W_M(y_A)\)**, under the current approved one-body-current transfer prescription. This trial is only a source-figure phase-space reproduction without \(R_A(E_R)\), nucleon form factors, AFH responses, isotope summation, halo folding, or detector response. It does not replace, redefine, or validate the adopted B baseline.

## Validation status and remaining work

- **Completed:** vector-path extraction, endpoint inversion, normalized phase-space reconstruction, independent red-shape fit, and comparison with \(130u\) and \(122\) GeV.
- **Local tests:** 5/5 tests pass for endpoint inversion, the \(A=130\) endpoint comparison, the \(122\) GeV mismatch, normalized three-body area, and the analytic peak location.
- **Status:** exploratory reproduction diagnostic. It is reproducible from the archived digitized trace and script; it is not a validated physical target-isotope identification.
- **Remaining:** locate an author-stated Fig. 2 mass/isotope input or original plotting source; resolve the caption-versus-axis normalization wording if the paper's authors provide the intended convention. No changes to the adopted B calculation are part of this trial.