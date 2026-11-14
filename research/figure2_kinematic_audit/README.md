# Figure 2 kinematic audit

**Status:** reproducible kinematic check; not a full event-rate reproduction.

## Research question

Check whether the scalar-mass labels \(m_s=300,360\\,\\mathrm{MeV}\) in Figure 2 are compatible with the manuscript's printed three-body phase space, and compare them with the keV interpretation.

## Directory map

- `calculations/kinematic_threshold.py`: calculation entry point; maximizes the kinematically allowed scalar mass over recoil energy at fixed incident speed.
- `results/RESULTS.md`: equations, assumptions, numerical results, and interpretation.
- `results/phase_space_threshold.csv`: 25-row machine-readable result table.
- `results/run_manifest.json` and `results/SHA256SUMS.txt`: execution environment, validation record, and output integrity.
- `tests/test_kinematic_threshold.py`: regression checks for benchmark values and phase-space boundaries.

## Reproduce

Requires Python 3, NumPy, and SciPy. Run from the repository root:

~~~bash
python research/figure2_kinematic_audit/calculations/kinematic_threshold.py
~~~

The script always writes to `research/figure2_kinematic_audit/results/phase_space_threshold.csv`, independent of the current working directory.

Run regression tests from the repository root:

~~~bash
python -m unittest discover -s research/figure2_kinematic_audit/tests -v
~~~

## Validation boundary

This is a kinematic/phase-space check using the manuscript's printed \(W_{\\max}\) expression. It is not a calculation of the differential event rate, nuclear response, mediator propagator, or Galactic-halo integral. The evidence favors the keV interpretation of the two labels but does not identify the original numerical inputs used to draw Figure 2.

The archived CSV was regenerated after the output-path-only code relocation and matched the pre-move CSV byte for byte. Four regression checks cover the 776 km/s maximum, the 360 keV recoil interval, the 300 keV minimum-speed threshold, and closure of the 300/360 MeV labels.
