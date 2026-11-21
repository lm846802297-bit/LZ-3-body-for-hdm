"""Regression tests for the structured research-result validator."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCHEMA_DIR))
from validate_result_records import load_json  # noqa: E402

SCHEMA_PATH = SCHEMA_DIR / "research-result-record-v1.0.0.schema.json"


def minimal_manifest(input_record: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "record_type": "run_manifest",
        "run_id": "TEST-RUN-001",
        "created_at": "2026-11-21T00:00:00Z",
        "project": {"repository": "example/research", "project_id": "validator-test"},
        "source": {"commit_sha": "a" * 40, "script_path": "run.py", "script_sha256": "c" * 64},
        "inputs": [input_record],
        "configuration": {"physics": {}, "numerics": {}, "conventions": {}},
        "environment": {"platform": "Linux", "runtime": {"python": "3.x"}, "dependencies": {}, "hardware": {"cpu": "test"}},
        "execution": {
            "status": "succeeded",
            "command": "python run.py",
            "started_at": "2026-11-21T00:00:00Z",
            "finished_at": "2026-11-21T00:00:01Z",
        },
        "outputs": [],
        "validation": {"status": "not_run", "checks": []},
        "archive": {"status": "local_only"},
    }


class StrictJsonNumberTests(unittest.TestCase):
    def load_text(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            path.write_text(text, encoding="utf-8")
            return load_json(path)

    def test_rejects_nonstandard_constants(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                self.load_text('{"value": ' + token + '}')

    def test_rejects_float_overflow(self):
        with self.assertRaisesRegex(ValueError, "overflows"):
            self.load_text('{"value": 1e9999}')

    def test_rejects_float_underflow_to_zero(self):
        with self.assertRaisesRegex(ValueError, "underflows"):
            self.load_text('{"value": 1e-9999}')

    def test_accepts_finite_float(self):
        self.assertEqual(self.load_text('{"value": 1.25e-4}')["value"], 1.25e-4)


class InputProvenanceSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with SCHEMA_PATH.open("r", encoding="utf-8") as stream:
            cls.schema = json.load(stream)
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema, format_checker=FormatChecker())

    def valid(self, input_record: dict) -> bool:
        return self.validator.is_valid(minimal_manifest(input_record))

    def test_local_input_requires_path_and_sha256(self):
        self.assertTrue(self.valid({
            "name": "local-table",
            "source": "repository input",
            "format": "csv",
            "path": "data/input.csv",
            "sha256": "b" * 64,
        }))

    def test_external_input_requires_immutable_uri_and_version(self):
        self.assertTrue(self.valid({
            "name": "external-table",
            "source": "external dataset",
            "format": "csv",
            "uri": "https://example.org/data.csv",
            "version": "v1",
        }))

    def test_hash_without_locator_is_rejected(self):
        self.assertFalse(self.valid({
            "name": "unlocatable-table",
            "source": "unknown",
            "format": "csv",
            "sha256": "b" * 64,
        }))

    def test_path_without_hash_is_rejected(self):
        self.assertFalse(self.valid({
            "name": "unhashed-table",
            "source": "repository input",
            "format": "csv",
            "path": "data/input.csv",
        }))

    def test_empty_path_is_rejected(self):
        self.assertFalse(self.valid({
            "name": "empty-path",
            "source": "repository input",
            "format": "csv",
            "path": "",
            "sha256": "b" * 64,
        }))

    def test_uri_without_version_is_rejected(self):
        self.assertFalse(self.valid({
            "name": "unversioned-external-table",
            "source": "external dataset",
            "format": "csv",
            "uri": "https://example.org/data.csv",
        }))

    def test_invalid_uri_is_rejected(self):
        self.assertFalse(self.valid({
            "name": "invalid-uri",
            "source": "external dataset",
            "format": "csv",
            "uri": "not-a-uri",
            "version": "v1",
        }))

    def test_script_fingerprint_is_required(self):
        record = minimal_manifest({
            "name": "local-table",
            "source": "repository input",
            "format": "csv",
            "path": "data/input.csv",
            "sha256": "b" * 64,
        })
        record["source"].pop("script_sha256")
        self.assertFalse(self.validator.is_valid(record))

    def test_dependencies_are_required(self):
        record = minimal_manifest({
            "name": "local-table",
            "source": "repository input",
            "format": "csv",
            "path": "data/input.csv",
            "sha256": "b" * 64,
        })
        record["environment"].pop("dependencies")
        self.assertFalse(self.validator.is_valid(record))

    def test_hardware_is_required(self):
        record = minimal_manifest({
            "name": "local-table",
            "source": "repository input",
            "format": "csv",
            "path": "data/input.csv",
            "sha256": "b" * 64,
        })
        record["environment"].pop("hardware")
        self.assertFalse(self.validator.is_valid(record))


if __name__ == "__main__":
    unittest.main()
