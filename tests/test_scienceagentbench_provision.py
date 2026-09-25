"""Synthetic ZIP boundary tests; never load real scientific pickle data."""

import json
from pathlib import Path
import tempfile
import unittest
import zipfile

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = pq = None

from personasciencebench.adapters.base import sha256
from personasciencebench.adapters.scienceagentbench import PILOTS
from personasciencebench.scienceagentbench_provision import SELECTED_PRIVATE_FILES, provision_archive


@unittest.skipIf(pa is None, "ScienceAgentBench fixtures require optional pyarrow")
class ProvisionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.annotations = self.root / "verified.parquet"
        rows = [{"instance_id": int(key), "eval_script_name": spec["script"],
                 "gold_program_name": spec["program"], "output_fname": PILOTS[key]["output"]}
                for key, spec in SELECTED_PRIVATE_FILES.items()]
        pq.write_table(pa.Table.from_pylist(rows), self.annotations)
        self.archive = self.root / "verified.zip"
        with zipfile.ZipFile(self.archive, "w") as output:
            for key, spec in SELECTED_PRIVATE_FILES.items():
                names = ["datasets/" + name for name in PILOTS[key]["files"]]
                names += ["eval_programs/" + spec["script"], "gold_programs/" + spec["program"], spec["reference"]]
                for name in names:
                    output.writestr("benchmark/" + name, b"synthetic bytes: not a pickle")
            output.writestr("benchmark/unreviewed_secret.txt", b"must not extract")

    def test_extracts_exact_allowlist_and_records_measured_provenance(self):
        destination = self.root / "extracted"
        result = provision_archive(self.archive, destination, self.annotations)
        expected = set()
        for key, spec in SELECTED_PRIVATE_FILES.items():
            expected.update("datasets/" + name for name in PILOTS[key]["files"])
            expected.update({"eval_programs/" + spec["script"],
                             "gold_programs/" + spec["program"], spec["reference"]})
        self.assertEqual(set(result["files"]), expected)
        extracted = {path.relative_to(destination).as_posix()
                     for path in destination.rglob("*") if path.is_file()}
        self.assertEqual(extracted, expected | {"provisioning.json"})
        for relative, digest in result["files"].items():
            self.assertEqual(digest, sha256(destination / relative))
            self.assertEqual((destination / relative).read_bytes(), b"synthetic bytes: not a pickle")
        self.assertEqual(result["archive_sha256"], sha256(self.archive))
        self.assertFalse((destination / "unreviewed_secret.txt").exists())
        self.assertIsNone(result["evaluator_image"])
        self.assertEqual(json.loads((destination / "provisioning.json").read_text()), result)

    def test_rejects_archive_traversal_before_any_extraction(self):
        with zipfile.ZipFile(self.archive, "a") as archive:
            archive.writestr("benchmark/../../escape", b"unsafe")
        destination = self.root / "extracted"
        with self.assertRaisesRegex(ValueError, "benchmark-root contract"):
            provision_archive(self.archive, destination, self.annotations)
        self.assertFalse(destination.exists())

    def test_rejects_changed_existing_member_without_overwriting_it(self):
        destination = self.root / "extracted"
        provision_archive(self.archive, destination, self.annotations)
        selected = destination / "datasets" / PILOTS["22"]["files"][0]
        selected.write_bytes(b"unexpected local change")
        with self.assertRaisesRegex(ValueError, "Existing extracted member differs"):
            provision_archive(self.archive, destination, self.annotations)
        self.assertEqual(selected.read_bytes(), b"unexpected local change")


if __name__ == "__main__":
    unittest.main()
