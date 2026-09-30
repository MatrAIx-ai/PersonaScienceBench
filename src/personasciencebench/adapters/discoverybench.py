"""Benchmark-wide DiscoveryBench conversion and native grading bridge.

Dedicated source fields provide a deterministic information boundary: questions,
dataset metadata, and files are public; domain knowledge belongs to the simulated
researcher; hypotheses, workflows, and answer keys remain evaluator-only.
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
from personasciencebench.context_conversion import field_facts, tabular_facts, POLICY as CONTEXT_POLICY
from personasciencebench.schema import (
    Asset, Episode, EvaluationResult, EvaluatorSpec, Fact, Provenance,
    PublicContext, ResearcherContext, Submission, TaskSummary,
)

SOURCE_REVISION = "c31fcf011e070f021a5f5b906896d0821f6880e8"
ADAPTER_VERSION = "discoverybench-reviewed-v1"
EVALUATOR_VERSION = "discoverybench-native-prompts-settings-strict-errors-v1"
EVALUATOR_SHA256 = "83406ddbe6894429cc5012b17cb82a209d5397aa7863b0aba1bb51edf1dd6c65"
ANSWER_KEY_SHA256 = "67504136becc97f4b4b3c698489bf2222d2a55f75aaa5cf033d6dd62ef5537e0"

# Explicit source reviews complement the benchmark-wide schema conversion.
# Reviewed files are hash-locked; other tasks retain automated review status.
REVIEWED_TASKS: dict[str, dict[str, Any]] = {
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

# Additional cases reviewed for the five-case Luna baseline.
REVIEWED_TASKS.update({'test/meta_regression/metadata_1.json/0/0': {'metadata_sha256': 'ec0cb5a323e2c2585529ac45ea00116515cd0b026e20edb20d9aba5908391991',
                                              'topic': 'study_linkage',
                                              'kind': 'context',
                                              'rationale': 'Reviewed domain-knowledge definitions '
                                                           'and data interpretation; no gold '
                                                           'hypothesis or workflow included.'},
 'test/nls_ses/metadata_1.json/0/0': {'metadata_sha256': '4117a80907e04a67f9b9461a8ca68af7cc30eb184d9814f8faaaa104516a9f91',
                                      'topic': 'academic_measurement',
                                      'kind': 'context',
                                      'rationale': 'Reviewed domain-knowledge definitions and data '
                                                   'interpretation; no gold hypothesis or workflow '
                                                   'included.'},
 'test/worldbank_education_gdp_indicators/metadata_1.json/0/0': {'metadata_sha256': 'f31bd3ded8bbccc633a939f9f57bbd34cd37454b0d8ba1f7daa127739f11b2d2',
                                                                 'topic': 'economic_indicators',
                                                                 'kind': 'context',
                                                                 'rationale': 'Reviewed '
                                                                              'domain-knowledge '
                                                                              'definitions and '
                                                                              'data '
                                                                              'interpretation; no '
                                                                              'gold hypothesis or '
                                                                              'workflow included.'}})


# Six distinct questions from one ecology study; keep this study together in splits.
ECOLOGY_INPUT_SHA256 = {
    "temporal_trends_contingency_table.csv": "f81f68033c9706b44a06c6f46395d2c8c67accdf321707e430f388d9d7400dba",
    "phylogenetic_tree.txt": "5b691dc9bd82ade93ee5b61a5b1d249a37239884363786c438e0724c8ab36d55",
    "invasion_success_pathways.csv": "6efaae2fd0a5020535b92dacce3f82d4f471f0bd19d877d40bc13cf087d16540",
    "invaded_niche_pathways.csv": "f75e971107e81d37519358976ecaaab26806c5808799ef1c5db98315d0d3e58c"
}
ECOLOGY_TASKS = {
    "test/introduction_pathways_non-native_plants/metadata_0.json/0/0": {
        "metadata_sha256": "90890531821829d3e5b461e2762bf103465529f2e5d8caf42bab47316d278c21",
        "topic": "input_schema",
        "kind": "context",
        "rationale": (
            "Temporal changes in introduction pathways, with native time bins and pathway "
            "labels preserved. Input-format notes contain no trend or target period."
        ),
        "validation_method": "source_review",
        "adapter_version": "discoverybench-ecology-v1",
    },
    "test/introduction_pathways_non-native_plants/metadata_1.json/0/1": {
        "metadata_sha256": "0c47b2c847194b856c302495c94a723abc56edad21a48d0e1cc7aa5693894949",
        "topic": "input_schema",
        "kind": "context",
        "rationale": (
            "Urban land use and the gardening-introduced share. Native counts, spatial "
            "scales and descriptions remain public; no fitted relationship is supplied."
        ),
        "validation_method": "source_review",
        "adapter_version": "discoverybench-ecology-v1",
    },
    "test/introduction_pathways_non-native_plants/metadata_2.json/0/0": {
        "metadata_sha256": "843092b9425530ddbd9cb647f62522964dcda93c6c65b92aaa5f9790ea5613c6",
        "topic": "input_schema",
        "kind": "context",
        "rationale": (
            "Habitat differences in gardening-introduced prevalence. Native habitat "
            "categories and counts remain public; no group comparison is supplied."
        ),
        "validation_method": "source_review",
        "adapter_version": "discoverybench-ecology-v1",
    },
}
# Source review of the three follow-up questions; native metadata stay unchanged.
ECOLOGY_TASKS.update({
    'test/introduction_pathways_non-native_plants/metadata_3.json/0/0': {
        "metadata_sha256": '391ff7c223ac86cbd84eed1aaf2eedfd545d4db41c1a2daf204a1353bccde913',
        "topic": "input_schema", "kind": "context",
        "rationale": 'Interacting covariates and gardening-introduced share. Preserve native predictor descriptions and denominator ambiguity; no significant factor or fitted interaction is supplied.',
        "validation_method": "source_review",
        "adapter_version": "discoverybench-ecology-v1",
    },
    'test/introduction_pathways_non-native_plants/metadata_4.json/0/0': {
        "metadata_sha256": '1d1c9db987c7e6d8df05d75454fcd11241672daf5f7791a5fa470cf3727ec349',
        "topic": "input_schema", "kind": "context",
        "rationale": 'Introduction pathway, residence time and invasion success. Preserve the minimum-versus-mean residence-time wording discrepancy and alternative success measures; no reference-derived resolution is supplied.',
        "validation_method": "source_review",
        "adapter_version": "discoverybench-ecology-v1",
    },
    'test/introduction_pathways_non-native_plants/metadata_5.json/0/2': {
        "metadata_sha256": '6bd987ced29f925f334b710d71e111193b8f57c43388a43fee578544b9e081a9',
        "topic": "input_schema", "kind": "context",
        "rationale": 'Urban effects across introduction pathways. Preserve native pathway counts and year/buffer descriptions; no pathway-specific direction or expected conclusion is supplied.',
        "validation_method": "source_review",
        "adapter_version": "discoverybench-ecology-v1",
    },
})
for _review in ECOLOGY_TASKS.values():
    _review["input_sha256"] = ECOLOGY_INPUT_SHA256
    _review["schema_fact_files"] = [name for name in ECOLOGY_INPUT_SHA256 if name.endswith(".csv")]
REVIEWED_TASKS.update(ECOLOGY_TASKS)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contained(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Source path escapes its root: {relative}")
    return path


def _read_task(source_root: Path, task_id: str) -> dict[str, Any]:
    """Return a controller-only record using exact, non-ambiguous source keys."""
    review = REVIEWED_TASKS.get(task_id)
    split, study, metadata_file, group, qid = task_id.split("/")
    relative = f"discoverybench/real/{split}/{study}/{metadata_file}"
    path = _contained(source_root, relative)
    metadata_hash = _sha256(path)
    if review is not None and metadata_hash != review["metadata_sha256"]:
        raise ValueError(f"Reviewed metadata changed; re-curation required: {relative}")
    metadata = json.loads(path.read_text())
    queries = metadata["queries"][int(group)]
    matches = [q for q in queries if str(q["qid"]) == qid]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one native query for {task_id}")
    if split == "test":
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
        gold_hypothesis = references[0]["gold_hypo"]
        reference_path = "eval/answer_key_real.csv"
        reference_hash = ANSWER_KEY_SHA256
    else:
        gold_hypothesis = matches[0].get("true_hypothesis", "").strip()
        if not gold_hypothesis:
            raise ValueError(f"Expected an embedded training reference for {task_id}")
        reference_path = relative
        reference_hash = metadata_hash
    # Do not copy query dictionaries: train queries embed true_hypothesis.
    question = matches[0]["question"]
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Empty DiscoveryBench question")
    datasets = []
    for dataset in metadata["datasets"]:
        name = dataset["name"]
        if (Path(name).name != name or Path(name).suffix.lower() not in {".csv", ".txt", ".dta"}):
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
        "datasets": datasets, "knowledge": (metadata.get("domain_knowledge") or "").strip(),
        "gold_hypothesis": gold_hypothesis, "gold_workflow": metadata.get("workflow"),
        "reference_path": reference_path, "reference_hash": reference_hash,
        "metadata_hash": metadata_hash, "review": review,
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
    """Convert all structurally valid real-data tasks at the pinned revision."""

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
        return list(REVIEWED_TASKS)[:2]

    def convert(self, task_id: str) -> Episode:
        if self.source.revision != SOURCE_REVISION:
            raise ValueError("DiscoveryBench curation applies only to its pinned revision")
        record = _read_task(self.source.repository, task_id)
        datasets = record["datasets"]
        assets = []
        review = record["review"]
        input_locks = review.get("input_sha256", {}) if review else {}
        if input_locks and set(input_locks) != {dataset["name"] for dataset in datasets}:
            raise ValueError("Reviewed input inventory changed; re-curation required")
        for index, dataset in enumerate(datasets):
            relative = f"discoverybench/real/{record['split']}/{record['study']}/{dataset['name']}"
            path = _contained(self.source.repository, relative)
            expected_hash = input_locks.get(dataset["name"])
            if expected_hash and path.is_file() and _sha256(path) != expected_hash:
                raise ValueError(f"Reviewed input changed; re-curation required: {relative}")
            assets.append(Asset(
                id=f"dataset-{index}", source_path=str(path),
                target_path=f"data/{dataset['name']}",
                sha256=expected_hash or (_sha256(path) if path.is_file() else None),
                acquisition=f"Restore {relative} from DiscoveryBench revision {SOURCE_REVISION}.",
            ))
        topic = str(review["topic"]) if review else "domain_knowledge"
        metadata_hash = record["metadata_hash"]
        knowledge = record["knowledge"]
        reference_hash = hashlib.sha256(record["gold_hypothesis"].encode()).hexdigest()
        facts = []
        if knowledge:
            facts = field_facts(knowledge, prefix=f"{record['study']}.{topic}",
                path=record['relative_metadata'], revision=SOURCE_REVISION,
                locator="/domain_knowledge", digest=metadata_hash)
        if review:
            for name in review.get("schema_fact_files", []):
                relative = f"discoverybench/real/{record['split']}/{record['study']}/{name}"
                path = _contained(self.source.repository, relative)
                if not path.is_file():
                    raise ValueError(f"Reviewed schema fact input is missing: {relative}")
                for fact in tabular_facts(path, prefix=f"{record['study']}.{Path(name).stem}",
                        source_path=relative, revision=SOURCE_REVISION):
                    fact.review_status = "reviewed"
                    facts.append(fact)
        fact_pack_hash = hashlib.sha256(knowledge.encode()).hexdigest()
        if review and review.get("schema_fact_files"):
            fact_pack_hash = hashlib.sha256(json.dumps(
                [fact.model_dump(mode="json") for fact in facts], sort_keys=True).encode()).hexdigest()
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
                researcher_topics=sorted({fact.topic for fact in facts}),
            ),
            researcher=ResearcherContext(
                facts=facts,
                unknowns=["Undocumented study details, intended findings, reference statistics, and unavailable runtime resources."],
                notes=["Researcher context consists of source-attributed domain knowledge and, where reviewed, input-header/format observations. Dataset and column descriptions remain public. Preserve uncertainty qualifiers; do not invent missing domain knowledge."],
            ),
            assets=assets,
            evaluator=EvaluatorSpec(
                kind="llm_reference", version=EVALUATOR_VERSION,
                entrypoint="personasciencebench.adapters.discoverybench.run_native_evaluator",
                reference={
                    "gold_hypothesis": record["gold_hypothesis"],
                    "gold_workflow": record["gold_workflow"],
                    "datasets": datasets, "reference_sha256": reference_hash,
                    "source_path": record["reference_path"],
                    "source_locator": {"dataset": record["study"],
                                       "metadataid": Path(record["metadata_file"]).stem.removeprefix("metadata_"),
                                       "query_id": record["qid"]},
                    "source_sha256": record["reference_hash"],
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
            conversion={"context_policy": CONTEXT_POLICY,
                "adapter_version": review.get("adapter_version", ADAPTER_VERSION) if review else ADAPTER_VERSION, "split": record["split"],
                "metadata_path": record["relative_metadata"], "query_group": record["query_group"],
                "qid": record["qid"], "metadata_sha256": metadata_hash,
                "public_allowlist": ["selected question", "datasets.name", "datasets.description", "datasets.columns.raw.name", "datasets.columns.raw.description"],
                "excluded_fields": ["hypotheses", "true_hypothesis", "workflow", "workflow_tags", "intermediate", "answer_key"],
                "fact_pack_sha256": fact_pack_hash,
                "selection_rationale": review["rationale"] if review else
                    "Benchmark-wide deterministic field-boundary conversion.",
                "validation_method": review.get("validation_method", "human_reviewed") if review else
                    "automated_pinned_schema_and_information_boundary",
                "runtime_validation": "not_run", "model_testing": "awaiting_user_confirmation",
            },
            review_status="reviewed" if review else "automated",
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
