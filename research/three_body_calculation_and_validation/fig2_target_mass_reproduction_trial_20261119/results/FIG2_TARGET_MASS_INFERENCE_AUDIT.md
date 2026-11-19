# Fig. 2 fixed-speed target-mass inference — calculation record

**Record date:** 2026-11-19  
**Classification:** exploratory reproduction diagnostic  
**Source:** `3body_for_HDM(2).pdf`, Fig. 2, PDF p. 3

## 1. Direct result

Using the two recoil endpoints read from the vector paths of Fig. 2,

\[
E_R^-=108.4582840\ \mathrm{keV},\qquad
E_R^+=660.2604493\ \mathrm{keV},
\]

and the figure inputs \(v=780\ \mathrm{km/s}\), \(m_s=300\ \mathrm{keV}\), the endpoint equations give

\[
\mu=107.9707623\ \mathrm{GeV},\qquad
m_T=121.0426480\ \mathrm{GeV}.
\]

The implied dark-matter mass is \(999.7844\ \mathrm{GeV}\), consistent with the paper's \(m_{\chi_1}=1\ \mathrm{TeV}\) benchmark.

An independent least-squares fit to the digitized red curve, with \(m_{\chi_1}=1\) TeV fixed, gives \(m_T=121.0252470\) GeV. The endpoint inversion and shape fit therefore agree on \(m_T\simeq121.04\) GeV.

## 2. Endpoint inversion

Write the endpoint formula as

\[
E_\pm=\frac{(\mu v\pm\sqrt{\mu^2v^2-2\mu m_s})^2}{2m_T}.
\]

Set \(S=E_++E_-\), \(P=\sqrt{E_+E_-}\). Directly,

\[
P=\frac{\mu m_s}{m_T},
\qquad
S=\frac{2\mu(\mu v^2-m_s)}{m_T}.
\]

Consequently,

\[
\mu=\frac{m_s}{v^2}\left(1+\frac{S}{2P}\right),
\qquad
m_T=\frac{\mu m_s}{P},
\qquad
m_\chi=\frac{\mu m_T}{m_T-\mu}.
\]

All masses and recoil energies in the numerical implementation are converted consistently to keV; \(v\) is converted to units of \(c\).

## 3. Phase-space shape

The three-body fixed-speed shape uses the paper's

\[
I(D)=\int_0^D d\epsilon\,\sqrt{\epsilon(\epsilon+2m_s)},
\quad
D=vq-\frac{q^2}{2\mu}-m_s,
\quad
q=\sqrt{2m_T E_R}.
\]

The normalized curves are

\[
p_{2\to2}(E_R)=\frac{\Theta(E_R-E_-)\Theta(E_+-E_R)}{E_+-E_-},
\]

\[
p_{2\to3}(E_R)=
\frac{I(D(E_R))\Theta(D(E_R))}
{\int dE_R\,I(D(E_R))\Theta(D(E_R))}.
\]

The plotted ordinate is reported in units of \(10^{-3}\,\mathrm{keV}^{-1}\). This normalizes each channel separately; it is not the dimensionless pointwise ratio of Eq. (8).

## 4. Mass-convention cross-check

For \(A=130\),

\[
130u=121.0942333\ \mathrm{GeV}
\quad (u=0.93149410242\ \mathrm{GeV}).
\]

At this mass, the calculated endpoints are \(108.3525422\) and \(660.8747617\) keV. Their differences from the digitized Fig. 2 endpoints are \(0.105742\) and \(0.614312\) keV, respectively. This is a close numerical match, but the source does not explicitly identify \(A=130\) as the Fig. 2 target.

At \(m_T=122\) GeV, the endpoints become \(106.5925170\) and \(670.7027363\) keV, which are visibly less consistent with Fig. 2.

The paper separately specifies \(m_N=122\) GeV at \(v=770\) km/s in Eq. (107), PDF p. 17. That example is not the Fig. 2 input declaration.

## 5. Source figure reading issue

The Fig. 2 caption uses the phrase “ratio of the differential recoil cross sections,” while the vertical axis displays \((1/\sigma)d\sigma/dE_R\) with units of inverse energy. The calculation archived here follows the vertical-axis normalization. The source's intended relationship between this plotted quantity and Eq. (8) remains an explicit documentary question.

## 6. Scope boundary

This is a fixed-speed phase-space shape reproduction with \(R_A(E_R)\) omitted. It does not include finite-\(t_N\) nucleon form factors, AFH finite-size nuclear responses, isotope-by-isotope masses and abundances, halo averaging, or detector response. It does not change the project's adopted B baseline.

The source PDF SHA-256 is:

`b4fc7bd73265df2bc2ce1640cbf8847b63323ec1dda220f9e7903f4620b871bb`