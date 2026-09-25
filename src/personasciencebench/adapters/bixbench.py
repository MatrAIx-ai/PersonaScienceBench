"""Benchmark-wide BixBench v1.5 conversion and native grader bridge.

Conversion never exposes an annotation row or capsule notebook. Asset acquisition
and model execution are explicit operations; imports and conversion are offline.
"""

from __future__ import annotations

import ast
import asyncio
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from types import SimpleNamespace
from typing import Any, Literal, Self
import zipfile
from functools import cache
from personasciencebench.context_conversion import tabular_facts, POLICY as CONTEXT_POLICY

from pydantic import BaseModel, Field, field_validator, model_validator

from personasciencebench.adapters.base import Adapter, Judge, check_submission, sha256
from personasciencebench.packaging import asset_readiness
from personasciencebench.schema import (
    Asset, Episode, EvaluationResult, EvaluatorSpec, Fact, Provenance,
    PublicContext, ResearcherContext, Submission, TaskSummary,
)


REPOSITORY_REVISION = "49311180bdacb324c596f2e07596c126f2004008"
DATASET_REVISION = "f8cc3bdcc6357c88b8c3648306522b9c422dc95a"
ANNOTATIONS_SHA256 = "0d1204dcdae7193a9132ced5a3502008f6b3b163debc1b65b2aa2d86cb132dc9"
EVALUATOR_VERSION = "bixbench-1.5-native-openended-49311180-psb-0.1"
NATIVE_DIGESTS = {
    "graders.py": "c5786585fb302594942984636b0809c3fdf92941661ef87ed78d110551ac4733",
    "prompts.py": "960f6cbb7bc634f5b466542ede996382cb748375a8052bf21b185e8f759eea57",
}

# Only reviewed Data members are eligible for extraction and actor mounting.
# Gold notebooks remain in the immutable archive, outside actor/researcher mounts.
CAPSULES = {
    "fbe0e950-76f2-4eb7-a216-a2d377970922": {
        "archive_sha256": "f9ecc2d5000ef1fca4eb845a50517ba0d2a2beeaf98693cf22fbad5d8340765c",
        "files": {
            "TASK008_BCG-CORONA_DM.csv": "f7eaac560fb4b022fc344692436c19417cc6b85bd9f3a86bc90c7784be7d9c91",
            "TASK008_BCG-CORONA_EX.csv": "852b1553d96e6bb30f527473de5fc9854d0923d94e7214e7321ebbb33d8dbce5",
            "TASK008_BCG-CORONA_AE.csv": "4b12795cc0fcfc27d7d4fda50f00a731f7c44c7d8e3f16c4b547e3c78c372f95",
            "TASK008_BCG-CORONA_AE.xlsx": "aaa1a068ebfb0d45e0cc16623c31c99d69647ff3e987b4f1fa8f6e5fea26eba7",
            "TASK008_BCG-CORONA_DM.xlsx": "606d480d96cf1660fa2a86a7707667f363e5d1ccbbd4f50e7b8313e5765a0e56",
            "TASK008_BCG-CORONA_EX.xlsx": "fc9cd1189c640fb0103c760071e11350353d71ec422cf998b2e02d3b8fb22878",
        },
    },
    "48a6b469-9c9d-4bef-b5b4-f29b7d6fa046": {
        "archive_sha256": "6d0bcc4502eb25118564315573a132931d2b8a662e71b21d9b374bd59a884cf8",
        "files": {
            "MeRIP_RNA_result.xlsx": "0e609d50f5c8f85da42f21edaf5e5ec6a00b916c52618ae4fc2fa944bbbed615",
            "Proteomic_data .xlsx": "4797b77b150b85ffae004e1f7c45247b70f20bc7585d811d46f5ecbdc3cf9fed",
        },
    },
}

PILOTS = {
    "bix-10-q2": "fbe0e950-76f2-4eb7-a216-a2d377970922",
    "bix-8-q2": "48a6b469-9c9d-4bef-b5b4-f29b7d6fa046",
}

# Reviewed input-only members and schema facts for the Luna baseline.
CAPSULES.update({'93f63fb8-b56c-4ad1-8d3b-d651e2107423': {'archive_sha256': '5ac4a82eb6aa71cfb8a283f6b6cd13da3419d9f14e9ce61db51d26a6ca98932a',
                                          'files': {'data.xlsx': '0088a66f710fb0e402d46647c2fa1cb2bbf42ffb9f36edc71100b610685d4399'}},
 '9e52daf6-ca58-43e8-e732-fbac3459d295': {'archive_sha256': '71595fce1f8e3c0a209f03bdc3d5fd623d78385a781e1dbef4fac636365a43df',
                                          'files': {'Swarm_2.csv': 'c85fbaa900c3db64d55ffb81421267e68e5c43d7d37d90a767328c6e63522475'}},
 '1d54e4a7-8b0f-4224-bd31-efcfded0d46c': {'archive_sha256': '6b29bb5d03693e4098452042ae0169a98926d45ce6ca26b0a45682c8feb7039f',
                                          'files': {'experiment_metadata.csv': '6a88817c361e575c3ec2a591839cbe5a0241f45d092efcde9c6d54b43a7e4e06',
                                                    'raw_counts.csv': 'a20bb7fa693655b3537379afd1f1675d0bd7648fa9239fa538c139d76cb4f1f1'}}})
PILOTS.update({'bix-51-q1': '93f63fb8-b56c-4ad1-8d3b-d651e2107423',
 'bix-54-q1': '9e52daf6-ca58-43e8-e732-fbac3459d295',
 'bix-13-q1': '1d54e4a7-8b0f-4224-bd31-efcfded0d46c'})
ADDITIONAL_FACTS = {'bix-51-q1': [('input_schema',
                'data_format',
                'data.xlsx',
                'worksheet Sheet1, row 1',
                'The workbook has a worksheet named Sheet1 with columns including Groups, '
                'Efficacy, Age, Family history, ECOG-PS, Child-Pugh, Chemotherapy experience, HBV '
                'infection, Gender, BMI, and Toxic and side effect.')],
 'bix-54-q1': [('input_schema',
                'data_format',
                'Swarm_2.csv',
                'CSV header',
                'The CSV columns are DishNumber, StrainNumber, Ratio, Replicate, Area, '
                'Circularity, and Round. Ratio entries use colon-separated strings.')],
 'bix-13-q1': [('input_schema',
                'data_format',
                'experiment_metadata.csv',
                'CSV headers of experiment_metadata.csv and raw_counts.csv',
                'The experiment metadata columns are SampleNumber, AzentaName, Media, Strain, and '
                'Replicate. Raw-count columns use sample labels such as resub-1, which also occur '
                'in AzentaName.')]}


@dataclass
class _Message:
    """Only the Message.content surface used by the selected native grader."""
    content: str


class _NativeJudgeClient:
    def __init__(self, judge: Judge):
        self.judge = judge
        self.prompt_hashes: list[str] = []
        self.responses: list[str] = []

    async def call_single(self, messages):
        payload = [{"role": "user", "content": message.content} for message in messages]
        self.prompt_hashes.append(hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()).hexdigest())
        answer = self.judge.complete(payload)
        if not isinstance(answer, str):
            raise TypeError("Judge.complete must return text")
        self.responses.append(answer)
        return SimpleNamespace(text=answer)


def _native_grader(repository: Path):
    """Execute only hash-pinned native grading classes and literal templates.

    This avoids importing BixBench's package __init__, aviary, lmi, and notebook
    runners. Class bodies, regex parsing, and open-answer dispatch remain native.
    """
    source = repository / "bixbench"
    for filename, expected in NATIVE_DIGESTS.items():
        if sha256(source / filename) != expected:
            raise ValueError(f"Unreviewed BixBench evaluator source: {filename}")
    prompt_tree = ast.parse((source / "prompts.py").read_text())
    templates = {}
    for node in prompt_tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "OPEN_ENDED_GRADING_PROMPT", "OPEN_ENDED_RANGE_GRADING_PROMPT",
                }:
                    templates[target.id] = ast.literal_eval(node.value)
    names = {"GradeType", "GradeResult", "GradingFunction", "OpenEndedGrader"}
    tree = ast.parse((source / "graders.py").read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name in names]
    if {node.name for node in nodes} != names or len(templates) != 2:
        raise ValueError("Native BixBench grader structure changed")
    scope = {
        "__name__": "personasciencebench.adapters.bixbench",
        "ast": ast, "re": re, "StrEnum": StrEnum, "Any": Any,
        "Literal": Literal, "Self": Self, "BaseModel": BaseModel, "Field": Field,
        "field_validator": field_validator, "model_validator": model_validator,
        "Message": _Message, "LiteLLMModel": Any, **templates,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source / "graders.py"), "exec"), scope)
    # compile inherits this module's future-annotations flag; resolve native scope.
    for name in ("GradeResult", "GradingFunction", "OpenEndedGrader"):
        scope[name].model_rebuild(_types_namespace=scope)
    return scope["OpenEndedGrader"], templates


class BixBenchAdapter(Adapter):
    name = "bixbench"

    @cache
    def _rows(self) -> list[dict[str, Any]]:
        if self.source.revision != REPOSITORY_REVISION:
            raise ValueError("BixBench repository revision is not reviewed")
        if self.source.dataset_revision != DATASET_REVISION:
            raise ValueError("BixBench dataset revision is not reviewed")
        path = self.source.assets / "BixBench.jsonl"
        if sha256(path) != ANNOTATIONS_SHA256:
            raise ValueError("BixBench annotations do not match the reviewed dataset")
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if len({row["question_id"] for row in rows}) != len(rows):
            raise ValueError("Duplicate BixBench question IDs")
        return rows

    def enumerate_tasks(self) -> list[TaskSummary]:
        return [TaskSummary(
            id=row["question_id"], study_id=row["capsule_uuid"],
            domain="computational_biology", title=row["question"],
            source_locator=f'BixBench.jsonl#question_id={row["question_id"]}',
        ) for row in self._rows()]

    def pilot_task_ids(self) -> list[str]:
        return ["bix-10-q2", "bix-8-q2"]

    def _row(self, task_id: str) -> dict[str, Any]:
        matches = [row for row in self._rows() if row["question_id"] == task_id]
        if len(matches) != 1:
            raise ValueError(f"Unknown or duplicate BixBench question: {task_id}")
        return matches[0]

    @staticmethod
    def _permitted_input(name):
        path = PurePosixPath(name)
        allowed = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".json", ".h5", ".h5ad", ".hdf5", ".mtx", ".gz", ".fastq", ".fasta", ".fa", ".fq", ".rds", ".rda", ".RData", ".parquet", ".bed", ".bam", ".bai", ".vcf", ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".npy", ".npz", ".faa", ".fna", ".mafft", ".clipkit", ".treefile", ".nwk", ".newick", ".aln"}
        if any(re.search(r"(?:^|[_-])(solution|answer|gold|notebook)(?:$|[_-])", p.rsplit(".",1)[0], re.I) for p in path.parts):
            return False
        if path.suffix.lower() == ".gz" and (len(path.suffixes) < 2 or path.suffixes[-2].lower() not in {".csv", ".tsv", ".txt", ".fastq", ".fq", ".fasta", ".fa", ".fna", ".faa", ".mtx", ".vcf"}):
            return False
        return path.suffix.lower() in {s.lower() for s in allowed}

    @cache
    def _unclassified_inputs(self, capsule):
        archive = self.source.assets / f"CapsuleFolder-{capsule}.zip"
        if not archive.is_file():
            return []
        prefix = f"CapsuleData-{capsule}/"
        with zipfile.ZipFile(archive) as bundle:
            return [name[len(prefix):] for name in bundle.namelist()
                if name.startswith(prefix) and not name.endswith("/")
                and not self._permitted_input(name[len(prefix):])
                and PurePosixPath(name).suffix.lower() != ".ipynb"
                and not re.search(r"(?:^|[_/-])(solution|answer|gold)(?:$|[_/.-])", name, re.I)]

    @cache
    def _capsule_inventory(self, capsule: str) -> dict[str, str]:
        """Return only data members, never notebooks or reference material."""
        archive = self.source.assets / f"CapsuleFolder-{capsule}.zip"
        if not archive.is_file():
            return {}
        known = CAPSULES.get(capsule)
        if known and sha256(archive) != known["archive_sha256"]:
            raise ValueError("BixBench capsule archive hash mismatch")
        prefix = f"CapsuleData-{capsule}/"
        inventory: dict[str, str] = {}
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            if len(set(names)) != len(names):
                raise ValueError("Duplicate ZIP members are not allowed")
            for info in bundle.infolist():
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                    raise ValueError("Unsafe ZIP member path")
                if info.is_dir() or not info.filename.startswith(prefix):
                    continue
                relative = info.filename[len(prefix):]
                if not relative or PurePosixPath(relative).is_absolute():
                    raise ValueError("Unsafe capsule data member")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlink ZIP members are not allowed")
                if not self._permitted_input(relative):
                    continue
                inventory[relative] = hashlib.sha256(bundle.read(info)).hexdigest()
        if not inventory:
            raise ValueError(f"Capsule contains no input data members: {capsule}")
        if known and inventory != known["files"]:
            raise ValueError("Reviewed BixBench input inventory changed")
        return inventory

    def prepare_assets(self, task_id: str) -> list[Path]:
        """Extract input-only capsule members from an acquired ZIP, offline."""
        capsule = self._row(task_id)["capsule_uuid"]
        archive = self.source.assets / f"CapsuleFolder-{capsule}.zip"
        if not archive.is_file():
            raise FileNotFoundError(
                f"Acquire CapsuleFolder-{capsule}.zip from pinned BixBench dataset revision")
        inventory = self._capsule_inventory(capsule)
        output = self.source.assets / "prepared" / capsule
        if not output.resolve().is_relative_to(self.source.assets.resolve()):
            raise ValueError("Prepared input directory escapes the configured asset root")
        written = []
        with zipfile.ZipFile(archive) as bundle:
            members = bundle.namelist()
            if len(set(members)) != len(members):
                raise ValueError("Duplicate ZIP members are not allowed")
            for member in members:
                path = PurePosixPath(member)
                if path.is_absolute() or ".." in path.parts or "\\" in member:
                    raise ValueError("Unsafe ZIP member path")
            for name, expected in inventory.items():
                member = f"CapsuleData-{capsule}/{name}"
                info = bundle.getinfo(member)
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlink ZIP members are not allowed")
                data = bundle.read(member)
                if hashlib.sha256(data).hexdigest() != expected:
                    raise ValueError(f"BixBench input hash mismatch: {name}")
                target = output / name
                if target.is_symlink() or output.is_symlink():
                    raise ValueError("Prepared inputs must not be symlinks")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                written.append(target)
        manifest = output / "input_manifest.json"
        manifest.write_text(json.dumps({"capsule_uuid": capsule,
                                        "archive_sha256": sha256(archive),
                                        "files": inventory, "dataset_revision": DATASET_REVISION,
                                        "conversion_policy": CONTEXT_POLICY,
                                        "excluded_members": [n for n in members if not n.endswith("/") and
                                            (not n.startswith(f"CapsuleData-{capsule}/") or not self._permitted_input(n))]}, indent=2) + "\n")
        return written

    @cache
    def _automatic_capsule_facts(self, capsule):
        facts = []
        for name, digest in self._capsule_inventory(capsule).items():
            path = self.source.assets / "prepared" / capsule / name
            if path.suffix.lower() not in {".csv", ".tsv", ".xlsx"}:
                continue
            if not path.is_file():
                continue
            if sha256(path) != digest:
                raise ValueError("Prepared metadata source hash mismatch")
            facts.extend(tabular_facts(path, prefix=f"{capsule}.{hashlib.sha256(name.encode()).hexdigest()[:12]}",
                source_path=f"CapsuleFolder-{capsule}.zip#CapsuleData-{capsule}/{name}", revision=DATASET_REVISION))
        return facts

    def _facts(self, task_id: str) -> list[Fact]:
        capsule = self._row(task_id)["capsule_uuid"]
        if task_id not in PILOTS:
            return self._automatic_capsule_facts(capsule)
        if task_id in ADDITIONAL_FACTS:
            items = ADDITIONAL_FACTS[task_id]
        elif task_id == "bix-10-q2":
            items = [
                ("demographics", "sample_metadata", "TASK008_BCG-CORONA_DM.csv", "header; columns TRTGRP, patients_seen, expect_interact, VISITNAM",
                 "The demographics table records TRTGRP as BCG or Placebo, patients_seen as 1-50, 51-100, or >100, and expect_interact as Yes or No. Its VISITNAM entries are Screening-Day -3 to 1."),
                ("identifiers", "data_linkage", "TASK008_BCG-CORONA_AE.csv", "header; USUBJID, AESPID, AESEV",
                 "The adverse-event table includes USUBJID, AESPID, and AESEV. USUBJID is also a column in the demographics and exposure tables. AESEV contains blank entries and the values 1, 2, 3, and 4; these files do not supply a descriptive severity label for each code."),
                ("encoding", "data_format", "TASK008_BCG-CORONA_EX.csv", "file byte encoding and header",
                 "The exposure CSV contains non-UTF-8 bytes and is readable with a Latin-1 decoder. The capsule also supplies XLSX versions of the demographics, exposure, and adverse-event tables."),
            ]
        else:
            items = [
                ("sheet", "data_format", "MeRIP_RNA_result.xlsx", "xl/workbook.xml; sheet name; sheet1.xml row 1",
                 "MeRIP_RNA_result.xlsx has one worksheet named Date Formatting. Its headers include m_log2FC, m_pvalue, g_log2FC, g_pvalue, m6A, DEG, m6A_DEG, gene_id, gene_name, Annotation, and Class. The literal GeneID header appears twice."),
                ("labels", "measurement_labels", "MeRIP_RNA_result.xlsx", "worksheet Date Formatting; F2,F63,F69,G2,G14,G49",
                 "The supplied m6A column uses m6A Hyper, m6A Hypo, and m6A no sig. The DEG column uses Up, Down, and no-DEGs. These are annotations already present in the input workbook."),
                ("identifiers", "sample_metadata", "MeRIP_RNA_result.xlsx", "worksheet Date Formatting; A2:A4,J2:J4,K2:K4",
                 "Rows include transcript identifiers such as ENST identifiers alongside gene_id and gene_name fields. Multiple rows can share a gene_id; the row identifiers and gene identifiers should not be assumed interchangeable."),
            ]
        return [Fact(
            id=f"{task_id}.{key}", topic=topic, text=text, review_status="reviewed",
            source=Provenance(
                source_path=f"CapsuleFolder-{capsule}.zip#CapsuleData-{capsule}/{filename}",
                revision=DATASET_REVISION, locator=locator,
                sha256=CAPSULES[capsule]["files"][filename],
            ),
        ) for key, topic, filename, locator, text in items]

    def convert(self, task_id: str) -> Episode:
        row = self._row(task_id)
        capsule = row["capsule_uuid"]
        if row["version"] != "1.5":
            raise ValueError("Unsupported BixBench question version")
        if task_id in PILOTS and PILOTS[task_id] != capsule:
            raise ValueError("Reviewed BixBench question identity changed")
        facts = self._facts(task_id)
        files = self._capsule_inventory(capsule)
        archive = f"CapsuleFolder-{capsule}.zip"
        assets = [Asset(
            id=filename, source_path=str((self.source.assets / "prepared" / capsule / filename).resolve()),
            target_path=f"data/{filename}", sha256=digest,
            acquisition=(f"https://huggingface.co/datasets/futurehouse/BixBench/resolve/"
                         f"{DATASET_REVISION}/{archive}; call BixBenchAdapter.prepare_assets"),
        ) for filename, digest in files.items()]
        if not files:
            # Preserve readiness information without ever mounting the complete
            # capsule ZIP, which also contains answer-bearing notebooks.
            assets = [Asset(
                id="unprovisioned_capsule_inputs",
                source_path=str((self.source.assets / "prepared" / capsule / ".inputs_ready").resolve()),
                target_path="data/.inputs_ready", required=True,
                acquisition=(f"Acquire {archive} from BixBench revision {DATASET_REVISION} "
                             "and call BixBenchAdapter.prepare_assets."),
            )]
        unclassified = self._unclassified_inputs(capsule)
        if unclassified:
            assets.append(Asset(id="unclassified_input_roles", source_path=str((self.source.assets / "prepared" / capsule / ".file_roles_resolved").resolve()),
                target_path="data/.file_roles_resolved", acquisition="Input roles unresolved; do not declare the partial input set runnable: " + ", ".join(unclassified[:20])))
        categories = [part.strip() for part in str(row.get("categories") or "").split(",") if part.strip()]
        domain = categories[0] if categories else "computational_biology"
        automated = task_id not in PILOTS
        return Episode(
            id=f"bixbench:{task_id}", benchmark=self.name, source_task_id=task_id,
            study_id=capsule, domain=domain,
            source_revision=self.source.revision,
            review_status="automated" if automated else "reviewed",
            public=PublicContext(
                question=row["question"],
                context=("Analyze the supplied capsule inputs to answer the question. "
                         "All specified methods, variables, and adjustments remain required. "
                         "Researcher consultation is optional; data inspection is allowed."),
                documents={"benchmark_canary": row["canary"]},
                submission={
                    "stage": "final", "answer": "Concise open-ended answer to this question.",
                    "payload": {"executed_analysis": "Set true only after executing the analysis."},
                    "artifacts": {"analysis": "Path to the executed notebook or analysis script; retained as evidence."},
                    "grading_scope": "Native grading checks the answer; execution evidence is recorded separately.",
                },
                environment={"input_files": [asset.target_path for asset in assets],
                             "runtime": "Independent analysis runner; Python/R tooling provisioned by the runner.",
                             "requires_gpu": False},
                researcher_topics=sorted({fact.topic for fact in facts}),
            ),
            researcher=ResearcherContext(
                facts=facts,
                unknowns=["The researcher has no expected answer or reference notebook.",
                          "Unspecified clinical-code meanings, preprocessing decisions, and scientific conclusions remain unknown."],
                notes=["Facts were curated from input headers, labels, formats, and identifier examples. No gold notebook, hypothesis, result, or ideal answer was used to generate context."],
            ),
            assets=assets,
            evaluator=EvaluatorSpec(
                kind="native_openended_judge", version=EVALUATOR_VERSION,
                entrypoint="personasciencebench.adapters.bixbench:BixBenchAdapter.evaluate",
                reference={"target": row["ideal"], "question": row["question"]},
                config={"eval_mode": row["eval_mode"], "answer_mode": "openanswer",
                        "partial_match": False, "llm_match": False,
                        "native_source_sha256": NATIVE_DIGESTS,
                        "judge_model": "configured_at_run_time", "denominator": 1},
            ),
            conversion={
                "adapter_version": CONTEXT_POLICY, "dataset_revision": DATASET_REVISION,
                "annotations_sha256": ANNOTATIONS_SHA256,
                "native_categories": row["categories"], "native_paper": row["paper"],
                "annotation_locator": f"BixBench.jsonl#question_id={task_id}",
                "question_preserved_verbatim": True,
                "excluded_fields": ["ideal", "result", "answer", "hypothesis", "distractors"],
                "excluded_assets": ["CapsuleNotebook-*", "*.ipynb"],
                "archive": archive,
                "archive_sha256": sha256(self.source.assets / archive) if (self.source.assets / archive).is_file() else None,
                "selection_reason": ("Distinct capsules; bounded statistical analysis; source-backed metadata clarification."
                                     if not automated else "Benchmark-wide pinned-annotation conversion."),
                "validation_method": "human_reviewed" if not automated else
                    "automated_annotation_boundary_and_input_only_archive_filter",
                "context_status": ("automated_input_schema" if automated else "reviewed_schema_facts") if facts else "no_available_context",
                "researcher_exclusive_information": False,
                "asset_status": "unclassified_input_roles" if unclassified else "inventory_known" if files else "capsule_archive_not_acquired",
                "unclassified_input_members": unclassified,
                "readiness": "Live actor and judge execution not yet tested.",
                "execution_evidence_policy": "Require an analysis artifact and explicit execution declaration before native answer scoring; this is a PSB submission gate, not scientific verification.",
            },
        )

    def evaluate(self, episode: Episode, submission: Submission,
                 judge: Judge | None = None) -> EvaluationResult:
        check_submission(episode, submission)
        details = {"attempted": 1, "submitted": int(bool(submission.answer.strip())),
                   "evaluated": 0, "scored": 0, "denominator": 1,
                   "native_source_sha256": NATIVE_DIGESTS}
        if not submission.answer.strip():
            return EvaluationResult(status="missing_submission", evaluator_version=EVALUATOR_VERSION,
                                    details=details)
        if submission.payload.get("executed_analysis") is not True or not submission.artifacts.get("analysis"):
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["A full-workflow answer requires an executed-analysis declaration and analysis artifact."],
                details=details)
        readiness = asset_readiness(episode)
        if not readiness["assets_ready"]:
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["Required BixBench inputs are missing or failed integrity checks."],
                details={**details, "asset_readiness": readiness})
        mode = episode.evaluator.config["eval_mode"]
        if mode not in {"str_verifier", "range_verifier", "llm_verifier"}:
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Unsupported BixBench eval_mode"], details=details)
        if mode != "str_verifier" and judge is None:
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["This native open-ended verifier requires an explicitly configured judge."], details=details)
        try:
            grader_class, templates = _native_grader(self.source.repository)
            client = _NativeJudgeClient(judge) if judge is not None else None
            grader = grader_class(evaluation_mode=mode, llm_client=client)
            result = asyncio.run(grader.grade(
                question=episode.evaluator.reference["question"],
                target=str(episode.evaluator.reference["target"]), predicted=submission.answer,
                partial_match=False, llm_match=False,
            ))
        except Exception as exc:
            # Provider exceptions may include the complete grading request. Keep
            # references/credentials out of public error strings.
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                errors=[f"Native BixBench evaluation failed ({type(exc).__name__})."], details=details)
        details.update({
            "evaluated": 1, "scored": 1, "grade_type": result.grade_type.value,
            "prompt_template_sha256": hashlib.sha256(templates["OPEN_ENDED_GRADING_PROMPT"].encode()).hexdigest(),
            "prompt_hashes": client.prompt_hashes if client else [],
            "native_parser": "Only <grade>correct</grade> maps to correct; all other responses map to incorrect.",
            "execution_evidence": "Actor-declared; native answer grading does not verify notebook correctness.",
        })
        return EvaluationResult(
            status="scored", evaluator_version=EVALUATOR_VERSION,
            metrics={"grade": result.grade, "correct": result.correct, "refusal": result.refusal},
            details=details,
        )
