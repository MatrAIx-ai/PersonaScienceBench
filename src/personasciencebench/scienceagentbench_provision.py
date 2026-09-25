"""Provision only reviewed ScienceAgentBench pilot members from the private ZIP."""

from __future__ import annotations

import ast
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
import zipfile

from personasciencebench.adapters.base import sha256
from personasciencebench.adapters.scienceagentbench import DATASET_REVISION, PILOTS, dataset_files


SELECTED_PRIVATE_FILES = {
    "22": {"script": "eval_papyrus.py", "program": "papyrus_filtering.py",
           "reference": "eval_programs/gold_results/papyrus_filtered_gold.pkl"},
    "45": {"script": "biopsykit_questionnaire_eval.py", "program": "questionnaire.py",
           "reference": "eval_programs/gold_results/biopsykit_questionnaire_gold.csv"},
}

SELECTED_PRIVATE_FILES.update({'67': {'script': 'CogSci_pattern_high_sim_eval.py',
        'program': 'CogSci_pattern_high_sim.py',
        'reference': 'eval_programs/gold_results/CogSci_pattern_high_sim_data_gold.csv'},
 '87': {'script': 'eval_polynomial_fit.py',
        'program': 'polynomial_fit.py',
        'reference': 'eval_programs/gold_results/polynomial_fit_gold.csv'},
 '92': {'script': 'eval_h_importances.py',
        'program': 'h_importances.py',
 'reference': 'eval_programs/gold_results/jnmf_h_importances_gold.json'}})


def _evaluator_dependencies(script: Path, gold_files: dict[str, str]) -> dict[str, str]:
    """Find private gold files named by a pinned evaluator without executing it."""
    text = script.read_text()
    try:
        tree = ast.parse(text, filename=str(script))
    except SyntaxError:
        # Synthetic boundary fixtures need not contain executable evaluators.
        tree = ast.parse("")
    strings = [node.value for node in ast.walk(tree)
               if isinstance(node, ast.Constant) and isinstance(node.value, str)]
    dependencies = {
        name: digest for name, digest in gold_files.items()
        if any(name in value or PurePosixPath(name).name in value for value in strings)
    }
    # Two EEG evaluators build ``sub03.npy`` by string concatenation.
    if "gold_results/sub' +" in text:
        name = "eval_programs/gold_results/sub03.npy"
        if name in gold_files:
            dependencies[name] = gold_files[name]
    return dependencies


def refresh_evaluator_dependencies(destination: Path) -> dict:
    """Narrow an existing full-bundle manifest to evaluator-specific references."""
    manifest = destination / "provisioning.json"
    record = json.loads(manifest.read_text())
    gold = {name: digest for name, digest in record["files"].items()
            if name.startswith("eval_programs/gold_results/")}
    scripts = {sha256(path): path for path in (destination / "eval_programs").glob("*.py")}
    for task_id, spec in record["reviewed_evaluators"].items():
        script = scripts.get(spec["script_sha256"])
        if script is None:
            raise ValueError(f"Missing evaluator matching task {task_id}")
        spec["dependencies"] = _evaluator_dependencies(script, gold)
        known = SELECTED_PRIVATE_FILES.get(task_id, {}).get("reference")
        if known in gold:
            spec["dependencies"][known] = gold[known]
        spec["dependency_discovery"] = "static literal-path extraction; dynamic EEG path handled explicitly"
    manifest.write_text(json.dumps(record, indent=2) + "\n")
    return record


def provision_archive(archive: Path, destination: Path, annotations: Path) -> dict:
    """Extract verified inputs and private evaluator material without executing it.

    Provenance records the user-supplied archive, without claiming a comparison
    with an unpublished upstream archive checksum. Source-row contracts and ZIP
    member identities must match the pinned verified annotation split.
    """
    import pyarrow.parquet as pq
    rows = {str(row["instance_id"]): row for row in pq.read_table(annotations).to_pylist()}
    task_specs = {}
    selected = set()
    for key, row in rows.items():
        files = PILOTS[key]["files"] if key in PILOTS else dataset_files(row["dataset_folder_tree"])
        script = row["eval_script_name"]
        program = row["gold_program_name"]
        if (PurePosixPath(script).name != script or PurePosixPath(program).name != program):
            raise ValueError(f"Unsafe native filename for verified task {key}")
        task_specs[key] = {"files": files, "script": script, "program": program,
                           "output": row["output_fname"]}
        selected.update("datasets/" + file for file in files)
        selected.update(["eval_programs/" + script, "gold_programs/" + program])
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
        # Native evaluator references are controller-private. Extracting the
        # complete gold-results subtree avoids guessing dynamic file accesses;
        # it never enters actor or researcher packages.
        selected.update(name.removeprefix("benchmark/") for name in names
                        if name.startswith("benchmark/eval_programs/gold_results/")
                        and not source.getinfo(name).is_dir())
        for relative in sorted(selected):
            name = "benchmark/" + relative
            if name not in names or source.getinfo(name).is_dir():
                raise ValueError(f"Required verified bundle member is missing: {relative}")
        with tempfile.TemporaryDirectory(prefix="sab-extract-", dir=destination.parent) as temp:
            staged = Path(temp)
            file_hashes = {}
            for relative in sorted(selected):
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
                "selected_task_ids": sorted(task_specs, key=int), "files": file_hashes,
                "reviewed_evaluators": {
                    key: {"script_sha256": file_hashes["eval_programs/" + spec["script"]],
                          "dependencies": {},
                          "dependency_discovery": "pending static literal-path extraction",
                          "python_dependencies": [], "judge_model_required": False,
                          "validation_method": "automated archive and annotation contract"}
                    for key, spec in task_specs.items()},
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
            for relative in sorted(selected):
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
    return refresh_evaluator_dependencies(destination)
