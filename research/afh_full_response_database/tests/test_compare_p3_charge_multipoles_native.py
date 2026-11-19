import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import compare_p3_charge_multipoles_native as comparator


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixture(root):
    multipoles = []
    validations = []
    for A, ranks in comparator.EXPECTED_RANKS.items():
        for i in range(comparator.NQ):
            q = i * 0.00025
            m_values = []
            p_values = []
            for J in ranks:
                m = A * 1.0e-3 + J * 1.0e-2 + q * 2.0e-2
                p = A * 1.0e-4 + J * 2.0e-3 - q * 1.0e-3
                m_values.append(complex(m, 0.0))
                p_values.append(complex(p, 0.0))
                multipoles.append({
                    "A": A, "q_GeV": q, "y": q*q, "multipole_J": J,
                    "M_J_native": m, "Im_M_J_native": 0.0,
                    "PhiPP_J_native": p, "Im_PhiPP_J_native": 0.0,
                })
            validations.append({
                "A": A, "q_GeV": q, "y": q*q,
                "W_M_rank_sum": 0.25*sum(abs(x)**2 for x in m_values),
                "W_M_native": 0.25*sum(abs(x)**2 for x in m_values),
                "W_PhiPP_rank_sum": 0.25*sum(abs(x)**2 for x in p_values),
                "W_PhiPP_native": 0.25*sum(abs(x)**2 for x in p_values),
                "W_MPhiPP_rank_sum": 0.25*sum((x*y.conjugate()).real for x,y in zip(m_values,p_values)),
                "W_MPhiPP_native": 0.25*sum((x*y.conjugate()).real for x,y in zip(m_values,p_values)),
            })
    mp = root / "charge_multipoles.csv"
    vp = root / "charge_rank_sum_validation.csv"
    write_csv(mp, list(multipoles[0]), multipoles)
    write_csv(vp, list(validations[0]), validations)
    meta = {
        "status": "PASS_NATIVE_AFH_CHARGE_MULTIPOLE_RANK_SUM",
        "AFH_source_sha256": comparator.EXPECTED_SOURCE_SHA256,
        "native_afh_charge_multipoles_validated": True,
        "rank_map": ["129=0,1", "131=0,1,2,3"],
        "multipole_file": mp.name,
        "validation_file": vp.name,
        "multipole_file_sha256": file_sha(mp),
        "validation_file_sha256": file_sha(vp),
    }
    (root / "charge_multipole_metadata.json").write_text(json.dumps(meta), encoding="utf-8")
    return mp, vp, root / "charge_multipole_metadata.json"


class NativeChargeMultipoleComparatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.mp, self.vp, self.meta = make_fixture(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_native_charge_rank_sum_passes(self):
        result = comparator.run(self.root)
        self.assertEqual(result["status"], "PASS_NATIVE_AFH_CHARGE_MULTIPOLE_RANK_SUM")
        self.assertEqual(result["multipole_rows"], 2401*(2+4))
        self.assertEqual(result["validation_rows"], 2401*2)
        self.assertLessEqual(result["max_native_imaginary_residual"], comparator.IMAG_ATOL)

    def test_wrong_source_hash_is_rejected(self):
        meta = json.loads(self.meta.read_text())
        meta["AFH_source_sha256"] = "0"*64
        self.meta.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError, "source SHA-256"):
            comparator.run(self.root)

    def test_rank_sum_mismatch_is_rejected(self):
        rows = comparator.read_csv(self.vp)
        rows[0]["W_M_native"] = str(float(rows[0]["W_M_native"]) + 1.0e-3)
        write_csv(self.vp, list(rows[0]), rows)
        meta = json.loads(self.meta.read_text())
        meta["validation_file_sha256"] = file_sha(self.vp)
        self.meta.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError, "rank-sum mismatch"):
            comparator.run(self.root)

    def test_multipole_hash_mismatch_is_rejected(self):
        with self.mp.open("a", encoding="utf-8") as stream:
            stream.write("\n")
        with self.assertRaisesRegex(ValueError, "CSV SHA-256 mismatch"):
            comparator.run(self.root)


if __name__ == "__main__":
    unittest.main()
