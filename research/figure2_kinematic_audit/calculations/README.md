# Calculation entry point

`kinematic_threshold.py` evaluates the maximum scalar mass permitted by the manuscript's printed three-body phase-space boundary.

- Internal energy units: GeV.
- Recoil-energy output units: keV.
- Incident-speed input: km/s.
- Target approximation: Xe-131 nuclear mass, 122 GeV.
- Dependencies: Python 3, NumPy, SciPy.

The script is deliberately self-contained and is not imported by the Eq. (6) kernel or other study modules. It writes its CSV to the sibling `../results/` directory, not to the current working directory.

Run from the repository root:

~~~bash
python research/figure2_kinematic_audit/calculations/kinematic_threshold.py
~~~
