# Structured result-record schema and validator

This directory contains the repository-local copy of the shared structured research-result standard v1.0.0.

## Contents

- `research-result-record-v1.0.0.schema.json`: JSON Schema Draft 2020-12 for run manifests, result summaries, and validation reports
- `validate_result_records.py`: strict JSON parsing, schema validation, input/output path and SHA-256 checks, and CSV structural/unit checks
- `requirements-result-validation.txt`: pinned `jsonschema[format]==4.26.0` dependency, including URI format validation
- `tests/test_validate_result_records.py`: regression tests for non-standard constants, float overflow/underflow, input provenance, source fingerprints, and environment records

## Run the tests

```bash
python -m pip install -r research/schemas/requirements-result-validation.txt
python -m unittest discover -s research/schemas/tests -v
python -m compileall -q research/schemas
```

## Required provenance

A repository-local input records both its repository-relative path and SHA-256. An external input whose bytes are unavailable records an immutable URI and version. A run manifest records the entry-script SHA-256, runtime, dependencies, and hardware. These requirements are checked by the schema and the archive writer.

The AFH and three-body archive writer is implemented in `research/result_archive.py`; its regression tests are in `research/afh_default_density_natural_xenon_halo/tests/test_result_archive.py`. Domain-specific metadata remains in each record's `extensions` namespace.
