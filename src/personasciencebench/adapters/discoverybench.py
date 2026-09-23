"""Reviewed DiscoveryBench conversions and a dependency-free native grading bridge.

The upstream repository remains untouched.  Only two reviewed queries are
exportable; enumeration does not imply that every source row is safe to export.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

from personasciencebench.adapters.base import Adapter, Judge, check_submission
from personasciencebench.schema import (
    Asset, Episode, EvaluationResult, EvaluatorSpec, Fact, Provenance,
    PublicContext, ResearcherContext, Submission, TaskSummary,
)

SOURCE_REVISION = "c31fcf011e070f021a5f5b906896d0821f6880e8"
ADAPTER_VERSION = "discoverybench-reviewed-v1"
EVALUATOR_VERSION = "discoverybench-native-prompts-settings-strict-errors-v1"
EVALUATOR_SHA256 = "83406ddbe6894429cc5012b17cb82a209d5397aa7863b0aba1bb51edf1dd6c65"
ANSWER_KEY_SHA256 = "67504136becc97f4b4b3c698489bf2222d2a55f75aaa5cf033d6dd62ef5537e0"

# Explicit review records: the entire domain_knowledge field is safe for these
# two queries.  Other source records are NOT automatically approved.
REVIEWED_TASKS: dict[str, dict[str, str | int]] = {
    "test/requirements_engineering_for_ML_enabled_systems/metadata_1.json/0/0": {
        "metadata_sha256": "adae7b01f3018b9c3689bff15e10888bad1cf8b1a915255c1d17bc92f30d77f1",
        "topic": "missing_values",
        "kind": "context",
        "rationale": "Survey missing-value interpretation helps select valid responses without disclosing proportions or confidence intervals.",
    },
    "test/nls_incarceration/metadata_1.json/0/0": {
        "metadata_sha256": "68ffe188dc004d2119c81ac09ffaa60d715fa427a45328e4d37b3c8f49fa9cff",
        "topic": "incarceration_measurement",
        "kind": "context",
        "rationale": "Incarceration ascertainment is background context; the prepared dataset already supplies ever_jailed and no reconstruction is required.",
    },
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contained(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Source path escapes its root: {relative}")
    return path


def _read_reviewed(source_root: Path, task_id: str) -> dict[str, Any]:
    """Return a controller-only record using exact, non-ambiguous source keys."""
    review = REVIEWED_TASKS.get(task_id)
    if review is None:
        raise ValueError(f"Task has no reviewed information boundary: {task_id}")
    split, study, metadata_file, group, qid = task_id.split("/")
    relative = f"discoverybench/real/{split}/{study}/{metadata_file}"
    path = _contained(source_root, relative)
    if _sha256(path) != review["metadata_sha256"]:
        raise ValueError(f"Reviewed metadata changed; re-curation required: {relative}")
    metadata = json.loads(path.read_text())
    queries = metadata["queries"][int(group)]
    matches = [q for q in queries if str(q["qid"]) == qid]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one native query for {task_id}")
    # Test references are in the answer key, not the placeholder hypotheses field.
    key_path = _contained(source_root, "eval/answer_key_real.csv")
    if _sha256(key_path) != ANSWER_KEY_SHA256:
        raise ValueError("Pinned DiscoveryBench answer key changed")
    with key_path.open(newline="") as stream:
        references = [
            row for row in csv.DictReader(stream)
            if row["dataset"] == study
            and row["metadataid"] == Path(metadata_file).stem.removeprefix("metadata_")
            and row["query_id"] == qid
        ]
    if len(references) != 1 or not references[0]["gold_hypo"].strip():
        raise ValueError(f"Expected one nonempty reference for {task_id}")
    # Do not copy query dictionaries: train queries embed true_hypothesis.
    question = matches[0]["question"]
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Empty DiscoveryBench question")
    datasets = []
    for dataset in metadata["datasets"]:
        name = dataset["name"]
        if Path(name).name != name or Path(name).suffix.lower() != ".csv":
            raise ValueError(f"Unreviewed asset name: {name}")
        datasets.append({
            "name": name,
            "description": dataset["description"],
            "columns": {"raw": [
                {"name": col["name"], "description": col["description"]}
                for col in dataset["columns"]["raw"]
            ]},
        })
    return {
        "task_id": task_id, "split": split, "study": study,
        "metadata_file": metadata_file, "query_group": int(group), "qid": int(qid),
        "relative_metadata": relative, "metadata_path": path,
        "question": question, "domain": metadata["domain"],
        "datasets": datasets, "knowledge": metadata["domain_knowledge"].strip(),
        "gold_hypothesis": references[0]["gold_hypo"],
        "gold_workflow": metadata.get("workflow"), "review": review,
    }


_NATIVE_FUNCTIONS = {
    "get_score_from_answer", "ask_dimension_question", "prepare_dataset_metadata_json",
    "get_sub_hypotheses", "match_context_with_gpt", "is_matching_context",
    "run_eval_gold_vs_gen_NL_subhypo", "run_eval_gold_vs_gen_NL_hypo_workflow",
}


def run_native_evaluator(
    source_root: Path,
    *,
    query: str,
    gold_hypothesis: str,
    gold_workflow: str | None,
    hypothesis: str,
    workflow: str | None,
    datasets: list[dict[str, Any]],
    judge: Callable[..., Any],
    model: str,
) -> dict[str, Any]:
    """Run pinned upstream prompts/aggregation with an explicitly injected judge.

    ``judge`` receives messages, model, temperature, max_tokens, and json_response;
    it returns text.  There is no client construction, environment-key lookup,
    implicit retry, network operation, or upstream import here.  Invalid model
    outputs raise instead of becoming misleading negative/zero scientific scores.
    """
    evaluator_path = _contained(Path(source_root), "eval/new_eval.py")
    if _sha256(evaluator_path) != EVALUATOR_SHA256:
        raise ValueError("Native evaluator source changed; review and version the bridge")
    tree = ast.parse(evaluator_path.read_text(), filename=str(evaluator_path))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in _NATIVE_FUNCTIONS]
    if {node.name for node in functions} != _NATIVE_FUNCTIONS:
        raise ValueError("Native evaluator is missing required functions")
    calls: list[dict[str, Any]] = []

    def call_judge(messages: list[dict[str, str]], *, json_response: bool = False,
                   temperature: float = 0, max_tokens: int = 250) -> str:
        request = {"messages": messages, "model": model, "temperature": temperature,
                   "max_tokens": max_tokens, "json_response": json_response,
                   "top_p": 1.0, "frequency_penalty": 0, "presence_penalty": 0}
        value = judge(**request)
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Judge must return nonempty response text")
        calls.append({"request": request, "response": value})
        return value

    def get_response(client: Any, prompt: str, model: str, **kwargs: Any) -> dict[str, Any]:
        # Prompt and fence parsing match utils/openai_helpers.py. Failed parses
        # are explicit errors here; upstream can retry and return None.
        output = call_judge([
            {"role": "system", "content": "You are a helpful assistant who is not talkative. You only respond with the exact answer to a query without additional conversation."},
            {"role": "user", "content": prompt},
        ], temperature=1.0, max_tokens=4096)
        parsed = json.loads(output.strip().strip("```json").strip("```"))
        if not isinstance(parsed, dict):
            raise ValueError("Judge response must be a JSON object")
        if "sub_hypo" in parsed:
            if not isinstance(parsed["sub_hypo"], list):
                raise ValueError("sub_hypo must be a list")
            for sub in parsed["sub_hypo"]:
                if not isinstance(sub, dict) or not isinstance(sub.get("text"), str) or not isinstance(sub.get("context"), str):
                    raise ValueError("Each sub-hypothesis needs text and context strings")
        elif type(parsed.get("match")) is not bool:
            raise ValueError("Context match must be a boolean")
        return parsed

    def chat(messages: list[dict[str, str]], **kwargs: Any) -> SimpleNamespace:
        output = call_judge(messages, json_response=kwargs.get("json_response", False))
        if kwargs.get("json_response"):
            parsed = json.loads(output)
            if "sizeA" in parsed:
                for key in ("sizeA", "sizeB", "intersection"):
                    if type(parsed.get(key)) is not int or parsed[key] < 0:
                        raise ValueError("Variable counts must be nonnegative integers")
                if parsed["intersection"] > min(parsed["sizeA"], parsed["sizeB"]):
                    raise ValueError("Variable intersection exceeds a set size")
                if "explanation" not in parsed:
                    raise ValueError("Variable grade has no explanation")
            elif not isinstance(parsed.get("answer"), str):
                raise ValueError("Relation grade has no answer")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=output))])

    scope: dict[str, Any] = {
        "json": json, "OpenAI": lambda: None, "get_response": get_response,
        "run_chatgpt_query_multi_turn": chat,
        # Native evaluator prints private references. Keep them in the returned
        # evaluator-only record rather than sending them to shared stdout.
        "print": lambda *args, **kwargs: None,
    }
    code = ast.Module(body=functions, type_ignores=[])
    exec(compile(code, str(evaluator_path), "exec"), scope)
    result = scope["run_eval_gold_vs_gen_NL_hypo_workflow"](
        query=query, gold_hypo=gold_hypothesis, gold_workflow=gold_workflow,
        gen_hypo=hypothesis, gen_workflow=workflow,
        dataset_meta={"datasets": datasets}, llm_used=model, dataset_type="real",
        use_column_metadata=True,
    )
    if not 0 <= result["final_score"] <= 1:
        raise ValueError("Native grader returned an invalid score")
    for pair in result["matched_gold_gen_subh_evals"].values():
        if pair["var"]["score"]["f1"] < 0 or pair["rel"]["score"] < 0:
            raise ValueError("Native grader could not parse a dimension score")
    result["judge_calls"] = calls
    result["evaluator_sha256"] = EVALUATOR_SHA256
    result["evaluator_version"] = EVALUATOR_VERSION
    result["model"] = model
    return result


class DiscoveryBenchAdapter(Adapter):
    """Convert two reviewed real-data tasks; keep all other queries inventory-only."""

    name = "discoverybench"

    def enumerate_tasks(self) -> list[TaskSummary]:
        summaries = []
        root = self.source.repository / "discoverybench" / "real"
        for path in sorted(root.glob("*/*/metadata_*.json")):
            split, study, filename = path.relative_to(root).parts
            metadata = json.loads(path.read_text())
            for group, queries in enumerate(metadata["queries"]):
                for query in queries:
                    task_id = f"{split}/{study}/{filename}/{group}/{query['qid']}"
                    summaries.append(TaskSummary(
                        id=task_id, study_id=f"discoverybench:{study}",
                        domain=metadata["domain"], title=query["question"],
                        source_locator=f"{path.relative_to(self.source.repository).as_posix()}#/queries/{group}/qid={query['qid']}",
                    ))
        return summaries

    def pilot_task_ids(self) -> list[str]:
        return list(REVIEWED_TASKS)

    def convert(self, task_id: str) -> Episode:
        if self.source.revision != SOURCE_REVISION:
            raise ValueError("DiscoveryBench curation applies only to its pinned revision")
        record = _read_reviewed(self.source.repository, task_id)
        datasets = record["datasets"]
        assets = []
        for index, dataset in enumerate(datasets):
            relative = f"discoverybench/real/{record['split']}/{record['study']}/{dataset['name']}"
            path = _contained(self.source.repository, relative)
            assets.append(Asset(
                id=f"dataset-{index}", source_path=str(path),
                target_path=f"data/{dataset['name']}",
                sha256=_sha256(path) if path.is_file() else None,
                acquisition=f"Restore {relative} from DiscoveryBench revision {SOURCE_REVISION}.",
            ))
        topic = str(record["review"]["topic"])
        metadata_hash = str(record["review"]["metadata_sha256"])
        knowledge = record["knowledge"]
        reference_hash = hashlib.sha256(record["gold_hypothesis"].encode()).hexdigest()
        return Episode(
            id=f"discoverybench:{task_id}", benchmark=self.name,
            source_task_id=task_id, study_id=f"discoverybench:{record['study']}",
            domain=record["domain"], source_revision=SOURCE_REVISION,
            public=PublicContext(
                question=record["question"],
                context="Analyze the supplied data and submit a data-grounded natural-language hypothesis answering the question. You may ask the researcher for study context. Asking is optional.",
                documents={"datasets.json": json.dumps({"datasets": datasets}, indent=2)},
                submission={
                    "stage": "final", "answer": "Natural-language hypothesis answering the question.",
                    "payload": {"hypothesis": "Optional explicit hypothesis; otherwise answer is used.",
                                "workflow": "Optional description of the executed analysis workflow."},
                    "artifacts": "Optional analysis code, notebook, or supporting outputs.",
                    "native_metric": "Context recall multiplied by mean variable-F1 × relation agreement (0–1).",
                },
                environment={"data_paths": [asset.target_path for asset in assets],
                             "execution": "Independent actor runtime; only staged public assets are permitted.",
                             "resource_limits": "Supplied by the selected actor runtime; no common reduced budget is imposed."},
                researcher_topics=[topic],
            ),
            researcher=ResearcherContext(
                facts=[Fact(
                    id=f"{record['study']}.{topic}", topic=topic, text=knowledge,
                    kind="context", review_status="reviewed",
                    source=Provenance(source_path=record["relative_metadata"],
                                      revision=SOURCE_REVISION, locator="/domain_knowledge",
                                      sha256=metadata_hash),
                )],
                unknowns=["Undocumented study details, intended findings, reference statistics, and unavailable runtime resources."],
                notes=["Only the reviewed domain-knowledge statement is researcher-owned; dataset and column descriptions remain public. Preserve the source's uncertainty qualifiers."],
            ),
            assets=assets,
            evaluator=EvaluatorSpec(
                kind="llm_reference", version=EVALUATOR_VERSION,
                entrypoint="personasciencebench.adapters.discoverybench.run_native_evaluator",
                reference={
                    "gold_hypothesis": record["gold_hypothesis"],
                    "gold_workflow": record["gold_workflow"],
                    "datasets": datasets, "reference_sha256": reference_hash,
                    "source_path": "eval/answer_key_real.csv",
                    "source_locator": {"dataset": record["study"],
                                       "metadataid": Path(record["metadata_file"]).stem.removeprefix("metadata_"),
                                       "query_id": record["qid"]},
                    "source_sha256": ANSWER_KEY_SHA256,
                },
                config={
                    "model": None, "provider": None,
                    "native_default_model": "gpt-4-1106-preview",
                    "native_helper_settings": {"decomposition_and_context": {"temperature": 1.0, "max_tokens": 4096},
                                               "variable_and_relation": {"temperature": 0, "max_tokens": 250}},
                    "judge_settings_policy": "Native per-call settings are forwarded to the configured Judge; incompatible providers must reject rather than ignore them.",
                    "adaptations": ["Injected independent judge instead of hardcoded OpenAI client.",
                                    "Malformed judge output raises an evaluation error; no hidden retries.",
                                    "Private evaluator stdout suppressed."],
                    "evaluator_sha256": EVALUATOR_SHA256,
                    "aggregation": "recall_context * mean_accuracy_score; unmatched predicted contexts stay in denominator",
                    "native_behavior_preserved": "Variable/relation comparisons receive full hypotheses for each matched context pair.",
                },
            ),
            conversion={
                "adapter_version": ADAPTER_VERSION, "split": record["split"],
                "metadata_path": record["relative_metadata"], "query_group": record["query_group"],
                "qid": record["qid"], "metadata_sha256": metadata_hash,
                "public_allowlist": ["selected question", "datasets.name", "datasets.description", "datasets.columns.raw.name", "datasets.columns.raw.description"],
                "excluded_fields": ["hypotheses", "true_hypothesis", "workflow", "workflow_tags", "intermediate", "answer_key"],
                "fact_pack_sha256": hashlib.sha256(knowledge.encode()).hexdigest(),
                "selection_rationale": record["review"]["rationale"],
                "runtime_validation": "not_run", "model_testing": "awaiting_user_confirmation",
            },
            review_status="reviewed",
        )

    def evaluate(self, episode: Episode, submission: Submission,
                 judge: Judge | None = None) -> EvaluationResult:
        version = episode.evaluator.version
        try:
            check_submission(episode, submission)
        except ValueError as error:
            return EvaluationResult(status="error", evaluator_version=version, errors=[str(error)])
        hypothesis = submission.payload.get("hypothesis", submission.answer)
        workflow = submission.payload.get("workflow")
        if not isinstance(hypothesis, str) or not hypothesis.strip():
            return EvaluationResult(status="missing_submission", evaluator_version=version,
                                    errors=["A final hypothesis is required; no numeric score was assigned."])
        if workflow is not None and not isinstance(workflow, str):
            return EvaluationResult(status="error", evaluator_version=version,
                                    errors=["workflow must be a string or null"])
        missing = [asset.source_path for asset in episode.assets if asset.required and
                   not Path(asset.source_path).is_file()]
        if missing:
            return EvaluationResult(status="blocked", evaluator_version=version,
                                    errors=[f"Missing required source dataset: {path}" for path in missing])
        if judge is None:
            return EvaluationResult(status="blocked", evaluator_version=version,
                                    errors=["No judge configured; evaluation has not been run."])
        try:
            def invoke(**request: Any) -> str:
                settings = {key: request[key] for key in
                            ("temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty")}
                return judge.complete(request["messages"], json_mode=request["json_response"], settings=settings)

            reference = episode.evaluator.reference
            result = run_native_evaluator(
                self.source.repository, query=episode.public.question,
                gold_hypothesis=reference["gold_hypothesis"],
                gold_workflow=reference["gold_workflow"], hypothesis=hypothesis,
                workflow=workflow, datasets=reference["datasets"], judge=invoke,
                model=episode.evaluator.config.get("model") or "externally-configured-judge",
            )
        except Exception as error:
            return EvaluationResult(status="error", evaluator_version=version,
                                    errors=[f"Native judge bridge failed: {type(error).__name__}: {error}"])
        return EvaluationResult(
            status="scored", evaluator_version=version,
            metrics={name: result[name] for name in ("final_score", "recall_context", "mean_accuracy_score")},
            details={"native_result": result, "attempted": 1, "submitted": 1, "evaluated": 1,
                     "scored": 1, "denominator": 1, "visibility": "evaluator_only",
                     "evaluator_config": episode.evaluator.config,
                     "score_scope": "Reference agreement of submitted hypothesis; execution is not independently verified by this native metric."},
        )
