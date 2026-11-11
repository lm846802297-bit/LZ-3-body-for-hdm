# Figure 2 kinematic audit

**Status:** reproducible kinematic check; not a full event-rate reproduction.

## Research question

Check whether the scalar-mass labels \(m_s=300,360\,\mathrm{MeV}\) in
Figure 2 are compatible with the manuscript's printed three-body phase space,
and compare them with the keV interpretation.

## Contents

- kinematic_threshold.py: maximizes the kinematically allowed scalar mass
  over recoil energy at fixed incident speed.
- phase_space_threshold.csv: archived numerical output.
- RESULTS.md: equations, inputs, numerical results, and interpretation.

## Reproduce

Requires Python 3, NumPy, and SciPy. From the repository root:

~~~bash
python research/figure2_kinematic_audit/kinematic_threshold.py
~~~

The script writes phase_space_threshold.csv in the working directory.
Run it from this study directory if you want to regenerate the archived CSV
in place.

## Validation boundary

This is a kinematic/phase-space check using the manuscript's printed
\(W_{\max}\) expression. It is not a calculation of the differential event
rate, nuclear response, mediator propagator, or Galactic-halo integral.
The evidence favors the keV interpretation of the two labels but does not
identify the original numerical inputs used to draw Figure 2.
