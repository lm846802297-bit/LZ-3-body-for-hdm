# ThreeBodyVV UFO export snapshot

This directory preserves the generated UFO source files for the `ThreeBodyVV.fr` model. It is a model-export artifact, not a MadGraph cross-section result.

## Provenance

- Source model: `../ThreeBodyVV.fr`
- Source SHA-256: `ca06a6866fc7eb34bdb8ab985f6dc2b35553dbe031e929355c84586b62b5afd6`
- Generator: FeynRules 2.3.49 with Mathematica 14.2.0 (Windows 64-bit)
- Export date recorded in `ThreeBodyVV_UFO.log`: 2026-11-16
- The exported files contain 5 vertices, 3 couplings, and 8 particle/antiparticle entries.

## Validation scope

The saved model was imported with Python 3.14.7 from its model directory. The import check found 8 particle entries, 5 vertices, and 3 couplings. This checks that the Python model files load and expose the expected objects. **No MadGraph process generation, matrix element, or cross section was run.**

The model log also records that no electric charges were defined and FeynRules assumed zero charge, and that the model omits the Standard Model particle classes. These are expected for this minimal interaction model; the UFO is not a complete Standard Model extension.

## Regenerating the export

Install FeynRules 2.3.49 separately, place its `FeynRules.m` and package files under `FeynRules_check/feynrules-current/`, then run `export_ufo.wls` from the `FeynRules_check` directory. Third-party FeynRules files are not included in this repository. The export script applies the documented Python 3 syntax adjustment to the generated UFO `object_library.py`.

`SHA256SUMS.txt` records the hashes of the preserved export files. `ufo_export_manifest.json` records the model source, generator, environment, and checks actually performed.
