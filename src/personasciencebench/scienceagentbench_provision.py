"""Provision only reviewed ScienceAgentBench pilot members from the private ZIP."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

from personasciencebench.adapters.base import sha256
from personasciencebench.adapters.scienceagentbench import DATASET_REVISION, PILOTS


SELECTED_PRIVATE_FILES = {
    "22": {"script": "eval_papyrus.py", "program": "papyrus_filtering.py",
           "reference": "eval_programs/gold_results/papyrus_filtered_gold.pkl"},
    "45": {"script": "biopsykit_questionnaire_eval.py", "program": "questionnaire.py",
           "reference": "eval_programs/gold_results/biopsykit_questionnaire_gold.csv"},
}


def provision_archive(archive: Path, destination: Path, annotations: Path) -> dict:
    """Hash and selectively extract; no pickle or scientific code is executed.

    Provenance records the user-supplied archive, without claiming a comparison
    with an unpublished upstream archive checksum. Source-row contracts and ZIP
    member identities must match the pinned verified annotation split.
    """
    import pyarrow.parquet as pq
    rows = {str(row["instance_id"]): row for row in pq.read_table(annotations).to_pylist()}
    selected = []
    for key, private in SELECTED_PRIVATE_FILES.items():
        row = rows[key]
        if (row["eval_script_name"] != private["script"] or row["gold_program_name"] != private["program"]
                or row["output_fname"] != PILOTS[key]["output"]):
            raise ValueError("Verified annotation task contract differs from the reviewed pilot")
        selected.extend("datasets/" + file for file in PILOTS[key]["files"])
        selected.extend(["eval_programs/" + private["script"], private["reference"],
                         "gold_programs/" + private["program"]])
    archive_hash = sha256(archive)
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as source:
        entries = source.infolist()
        names = [entry.filename for entry in entries]
        if len(set(names)) != len(names):
            raise ValueError("Duplicate ZIP members are not permitted")
        for entry in entries:
            path = PurePosixPath(entry.filename)
            mode = entry.external_attr >> 16
            if (path.is_absolute() or ".." in path.parts or "\\" in entry.filename
                    or not path.parts or path.parts[0] != "benchmark"
                    or stat.S_ISLNK(mode)):
                raise ValueError("ZIP member violates the expected benchmark-root contract")
        for relative in selected:
            name = "benchmark/" + relative
            if name not in names or source.getinfo(name).is_dir():
                raise ValueError(f"Required verified bundle member is missing: {relative}")
        with tempfile.TemporaryDirectory(prefix="sab-extract-", dir=destination.parent) as temp:
            staged = Path(temp)
            file_hashes = {}
            for relative in selected:
                target = staged / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open("benchmark/" + relative, pwd=b"scienceagentbench") as incoming, target.open("xb") as outgoing:
                    shutil.copyfileobj(incoming, outgoing)
                file_hashes[relative] = sha256(target)
            record = {
                "split": "verified", "dataset_revision": DATASET_REVISION,
                "annotation_sha256": sha256(annotations), "archive_sha256": archive_hash,
                "acquisition": "User supplied benchmark_verified.zip; original archive retained privately.",
                "release_match_evidence": "Archive name, expected benchmark/ layout, and native task filenames match the pinned verified annotations; no published upstream archive digest was available.",
                "selected_task_ids": list(SELECTED_PRIVATE_FILES), "files": file_hashes,
                "reviewed_evaluators": {
                    key: {"script_sha256": file_hashes["eval_programs/" + spec["script"]],
                          "dependencies": {spec["reference"]: file_hashes[spec["reference"]]},
                          "python_dependencies": ["pandas"] if key == "22" else ["Python standard library csv"],
                          "judge_model_required": False}
                    for key, spec in SELECTED_PRIVATE_FILES.items()},
                "evaluator_runtime": "bubblewrap-separate-native-verifier-v1",
                "evaluator_image": None,
                "runtime_dependency_validation": "pending isolated check",
            }
            if destination.exists():
                if not destination.is_dir() or destination.is_symlink():
                    raise ValueError("Destination is not a private regular directory")
                for relative, digest in file_hashes.items():
                    path = destination / relative
                    if path.exists() and (path.is_symlink() or sha256(path) != digest):
                        raise ValueError(f"Existing extracted member differs: {relative}")
            destination.mkdir(mode=0o700, exist_ok=True)
            destination.chmod(0o700)
            for relative in selected:
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    shutil.copyfile(staged / relative, target)
                target.chmod(0o600)
            manifest = destination / "provisioning.json"
            if manifest.exists():
                prior = json.loads(manifest.read_text())
                if prior.get("archive_sha256") != archive_hash:
                    raise ValueError("Existing provisioning record refers to another archive")
                record = {**prior, **record}
            manifest.write_text(json.dumps(record, indent=2) + "\n")
            manifest.chmod(0o600)
    return record
