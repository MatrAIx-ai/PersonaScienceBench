"""Synthetic boundary/controller tests. No inference and no invented benchmark results."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from personasciencebench.adapters.base import SourceConfig, read_json, sha256
from personasciencebench.adapters.ideagene import (
    IdeaGeneAdapter, REVISION, SOURCE_TREE, NATIVE_JUDGES, PILOT_IDS, SMOKE_IDS,
)
from personasciencebench.ideagene_runner import (run_episode, selected_profiles, pilot_plan, run_pilot,
                                               validate_config, parse_actor_arguments,
                                               PROPOSAL_MAX_CHARACTERS)
from personasciencebench.packaging import export_episode, write_json
from personasciencebench.persona import Persona
from personasciencebench.registry import ADAPTERS, project_root
from personasciencebench.schema import Submission


@pytest.fixture
def adapter(tmp_path):
    repo = tmp_path / "upstream"
    for tid in PILOT_IDS:
        write_json(repo / "gene_arena/task" / f"{tid}.json", {
            "trace_id": tid, "domain": "synthetic-test-domain", "subfield": "synthetic-test-subfield",
            "open_question": "Propose a testable mechanism for this synthetic fixture.",
            "verified": True, "papers": [{"answer": "HIDDEN_PAPER_CANARY"}],
            "edges": [{"evolution_focus": "HIDDEN_EDGE_CANARY"}],
            "extra": {"answer": "NESTED_REFERENCE_CANARY"}})
    return IdeaGeneAdapter(SourceConfig(repo, tmp_path / "assets", REVISION))


@pytest.fixture
def episode(adapter):
    return adapter.convert(PILOT_IDS[0])


def handoff(stage, proposal=None):
    return {"stage": stage, "answer": "Shared design or clarification.", "evidence": "Visible question.",
            "assumptions": ["Data availability unknown"], "uncertainties": [],
            "payload": {} if proposal is None else {"proposal": proposal}, "artifacts": {}}


def native_proposal(label="test", *, long_text=None):
    detail = long_text or f"A substantive {label} statement long enough for the native parser."
    return {
        "title": f"Native-format {label} proposal",
        "idea_genome": {
            "problem_niche": detail,
            "core_mechanism": detail,
            "inherited_genes": [detail],
            "mutated_or_novel_genes": [detail],
            "addressed_limitation": detail,
            "expected_contribution": detail,
        },
        "evolution_rationale": {
            "dynamics_type": "Mutation",
            "source_ideas": ["publicly inferred source"],
            "why_plausible": detail,
            "lineage_risk": detail,
            "inherited_components": [detail],
            "changed_components": [detail],
        },
        "validation_plan": {
            "hypothesis": detail,
            "experiment": detail,
            "baselines": ["baseline"],
            "metrics": ["metric"],
            "falsification_criteria": ["failure criterion"],
        },
        "known_unknowns": ["unknown resource availability"],
    }


def decision(action="continue", approve=False):
    return {"action": action, "interaction": "conclude" if action == "stop" else "refine_analysis",
            "message": "A visible researcher reply.", "evidence": "Shared handoff.",
            "objectives_open": [], "fact_ids": [], "approve_approach": approve}


class Actor:
    def __init__(self, steps):
        self.steps = iter(steps)
        self.requests = []
        self.tool_specs = []

    def completion(self, messages, tools, tool_choice):
        self.requests.append(deepcopy(messages))
        self.tool_specs.append(deepcopy(tools))
        return {"choices": [{"message": {"role": "assistant", "reasoning": "PRIVATE_REASONING_CANARY",
            "tool_calls": [{"id": f"call-{len(self.requests)}", "type": "function", "function": {
                "name": "end_researcher_turn", "arguments": json.dumps(next(self.steps))}}]}}]}


class ResearcherBackend:
    def __init__(self, steps):
        self.steps = iter(steps)
        self.requests = []

    def complete_decision(self, messages, schema):
        self.requests.append(deepcopy(messages))
        return json.dumps(next(self.steps))


def test_registered_opt_in_without_broadening_defaults():
    from personasciencebench.cli import DEFAULT_BENCHMARKS
    assert ADAPTERS["ideagene"] == ("ideagene", "IdeaGeneAdapter")
    assert "ideagene" not in DEFAULT_BENCHMARKS
    source = read_json(project_root() / "manifests/sources.json")["ideagene"]
    assert source["revision"] == REVISION
    assert source["source_tree"] == SOURCE_TREE


def test_registry_accepts_only_explicit_exact_tree_archive(tmp_path, monkeypatch):
    import subprocess
    from personasciencebench.registry import load_adapter
    manifest = tmp_path / "sources.json"
    write_json(manifest, {"ideagene": {
        "repository_directory": "ideagene", "assets_directory": "_assets/ideagene",
        "revision": REVISION, "source_tree": SOURCE_TREE}})
    (tmp_path / "sources/ideagene").mkdir(parents=True)

    def exact_tree(argv, **kwargs):
        if "diff" in argv:
            return ""
        return SOURCE_TREE if argv[-1] == "HEAD^{tree}" else "synthetic-archive-commit"

    monkeypatch.setattr(subprocess, "check_output", exact_tree)
    loaded = load_adapter("ideagene", tmp_path / "sources", manifest)
    assert loaded.source.revision == REVISION
    monkeypatch.setattr(subprocess, "check_output", lambda argv, **kwargs: "unrelated")
    with pytest.raises(ValueError, match="revision/tree"):
        load_adapter("ideagene", tmp_path / "sources", manifest)


def test_automatic_catalog_and_verbatim_question(adapter, episode):
    assert {t.id for t in adapter.enumerate_tasks()} == set(PILOT_IDS)
    assert episode.public.question == adapter._task(PILOT_IDS[0])["open_question"]
    assert episode.track == "design_only"
    assert episode.researcher.facts == []
    assert episode.conversion["scientific_review"] == "not_independently_reviewed"


def test_allowlist_excludes_nested_reference_data(adapter, episode, tmp_path):
    export_episode(episode, tmp_path / "package")
    public = (tmp_path / "package/actor/task.json").read_text(encoding="utf-8")
    for secret in ("HIDDEN_PAPER_CANARY", "HIDDEN_EDGE_CANARY", "NESTED_REFERENCE_CANARY"):
        assert secret not in public
        assert secret not in json.dumps(episode.researcher.model_dump())
    assert "papers" not in episode.actor_input()


@pytest.mark.parametrize("tid", ["../escape", "/absolute", "bad\\path", "bad:drive"])
def test_unsafe_task_ids_rejected(adapter, tid):
    with pytest.raises(ValueError):
        adapter.convert(tid)


def test_exact_complete_profiles_and_persona_off():
    profiles = selected_profiles(["persona_off", "candidate_148", "candidate_046"])
    assert profiles["persona_off"].enabled is False
    assert len(profiles["candidate_046"].system_prompt) == 16828
    assert len(profiles["candidate_148"].system_prompt) == 7218


def test_profile_hash_mismatch_is_fatal(tmp_path):
    root = project_root()
    manifest = read_json(root / "configs/full_persona_v2/cohort.json")
    row = next(r for r in manifest["profiles"] if r["candidate_id"] == "candidate_148")
    write_json(tmp_path / "configs/full_persona_v2/cohort.json", manifest)
    path = tmp_path / row["published_profile"]
    path.parent.mkdir(parents=True)
    path.write_text("```text\nchanged\n```\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hash"):
        selected_profiles(["persona_off", "candidate_148"], tmp_path)


def test_shared_researcher_sealing_and_private_reasoning(episode, tmp_path):
    proposal = native_proposal()
    actor = Actor([handoff("plan"), handoff("result", proposal)])
    backend = ResearcherBackend([decision(), decision(approve=True), decision("stop")])
    profile = Persona(system_prompt="PRIVATE_IDENTITY_CANARY")
    result = run_episode(episode, profile, actor, backend, tmp_path / "run", max_requests=3)
    assert result["status"] == "submitted"
    assert result["plan_reviews"] == result["result_reviews"] == 1
    sealed = read_json(Path(result["submission"]))
    assert json.loads(sealed["answer"]) == proposal
    assert sealed["payload"] == {}
    researcher_text = json.dumps(backend.requests)
    assert "PRIVATE_IDENTITY_CANARY" in researcher_text
    assert "PRIVATE_REASONING_CANARY" not in researcher_text
    assert "PRIVATE_IDENTITY_CANARY" not in json.dumps(actor.requests)
    assert "PRIVATE_REASONING_CANARY" not in json.dumps(actor.requests)
    assert (tmp_path / "run/proposal_receipt.json").exists()
    checkpoint = read_json(tmp_path / "run/handoff_000.json")
    assert checkpoint["handoff"]["stage"] == "plan"
    assert checkpoint["disclosed_context"] == []
    schema = actor.tool_specs[0][0]["function"]["parameters"]
    assert schema["properties"]["payload"]["additionalProperties"] is False
    assert set(schema["properties"]["payload"]["properties"]) == {"proposal"}
    proposal_schema = schema["properties"]["payload"]["properties"]["proposal"]
    assert proposal_schema["type"] == "object"
    assert "idea_genome" in proposal_schema["required"]
    assert set(proposal_schema["properties"]["idea_genome"]["required"]) == {
        "problem_niche", "core_mechanism", "inherited_genes", "mutated_or_novel_genes",
        "addressed_limitation", "expected_contribution"}
    assert schema["properties"]["artifacts"]["properties"] == {}


def test_clarification_retains_previous_complete_candidate(episode, tmp_path):
    proposal = native_proposal("retained")
    actor = Actor([handoff("plan"), handoff("result", proposal), handoff("result")])
    backend = ResearcherBackend([decision(), decision(approve=True), decision(), decision("stop")])
    result = run_episode(episode, Persona(enabled=False), actor, backend, tmp_path / "run", max_requests=4)
    assert json.loads(read_json(Path(result["submission"]))["answer"]) == proposal
    assert result["optional_result_revisions"] == 1
    assert "candidate_retained" in (tmp_path / "run/events.jsonl").read_text(encoding="utf-8")


def test_provider_extra_json_fields_do_not_break_native_compatible_submission(episode, tmp_path):
    proposal = native_proposal("provider extension")
    proposal["evolution_rationale"]["validation_hypotheses_note"] = "An optional explanatory field."
    actor = Actor([handoff("plan"), handoff("result", proposal)])
    backend = ResearcherBackend([decision(), decision(approve=True), decision("stop")])
    result = run_episode(episode, Persona(enabled=False), actor, backend, tmp_path / "run", max_requests=3)
    assert result["status"] == "submitted"
    assert json.loads(read_json(Path(result["submission"]))["answer"])["evolution_rationale"][
        "validation_hypotheses_note"] == "An optional explanatory field."


def test_only_redundant_trailing_braces_are_normalized():
    raw = json.dumps(handoff("result", native_proposal()))
    parsed, normalization = parse_actor_arguments(raw + "}")
    assert parsed == json.loads(raw)
    assert normalization["removed_characters"] == 1
    with pytest.raises(json.JSONDecodeError):
        parse_actor_arguments(raw + " trailing text")


@pytest.mark.parametrize("steps", [
    [handoff("plan", native_proposal("wrong stage")), handoff("plan"),
     handoff("result", native_proposal("corrected"))],
    [handoff("plan"), handoff("result", "not an object"),
     handoff("result", native_proposal("corrected"))],
])
def test_rejected_actor_handoff_gets_one_in_budget_correction(episode, tmp_path, steps):
    backend = ResearcherBackend([decision(), decision(approve=True), decision("stop")])
    result = run_episode(episode, Persona(enabled=False), Actor(steps), backend,
                         tmp_path / "run", max_requests=4)
    assert result["status"] == "submitted"
    events = (tmp_path / "run/events.jsonl").read_text(encoding="utf-8")
    assert "actor_handoff_rejected" in events
    assert "raw_arguments_persisted" in events


@pytest.mark.parametrize("steps", [[handoff("result", native_proposal("too early"))],
    [handoff("plan"), handoff("result")],
    [handoff("plan"), {**handoff("result", native_proposal("artifact")),
                       "artifacts": {"x": "/private/reference"}}],
    [handoff("plan"), handoff("result", native_proposal(
        "oversized", long_text="x" * (PROPOSAL_MAX_CHARACTERS + 1)))]] )
def test_invalid_handoffs_cannot_be_sealed(episode, tmp_path, steps):
    result = run_episode(episode, Persona(enabled=False), Actor(steps),
                         ResearcherBackend([decision(), decision(approve=True), decision("stop")]),
                         tmp_path / "run", max_requests=4)
    assert result["status"] == "infrastructure_error"
    assert result["submission"] is None
    assert not (tmp_path / "run/submission.json").exists()


def test_no_extra_dialogue_quota_and_budget_exhaustion(episode, tmp_path):
    result = run_episode(episode, Persona(enabled=False), Actor([handoff("plan")]),
                         ResearcherBackend([decision(), decision(approve=True)]), tmp_path / "run", max_requests=2)
    assert result["status"] == "missing_submission"
    assert result["approach_approved"] is True
    assert result["submission"] is None


def test_native_request_exact_content_no_persona(adapter, episode, tmp_path):
    content = '{"idea_genome":{"core_mechanism":"test"}}'
    request = adapter.evaluation_request(episode, Submission(episode_id=episode.id, answer=content), tmp_path / "request.json")
    native = tmp_path / "request.native/ideas" / episode.source_task_id / "submission_Question.json"
    assert read_json(native) == {"content": content}
    assert request.argv[-3:] == NATIVE_JUDGES
    assert "--allow-partial-pes-judges" not in request.argv
    assert adapter.evaluate(episode, Submission(episode_id=episode.id, answer=content)).status == "blocked"
    with pytest.raises(FileExistsError):
        adapter.evaluation_request(episode, Submission(episode_id=episode.id, answer=content), tmp_path / "request.json")


def test_missing_optional_genome_db_uses_documented_native_fallback(adapter, episode, tmp_path):
    request_path = tmp_path / "request.json"
    request = adapter.evaluation_request(
        episode, Submission(episode_id=episode.id, answer="proposal"), request_path)
    genome_db = adapter.source.repository / "gene_arena/genome_db/paper_gene_cards.json"
    assert str(genome_db.resolve()) not in request.required_paths
    assert any("optional" in note and "task JSON" in note for note in request.notes)
    provenance = read_json(tmp_path / "request.native/submission_provenance.json")
    record = provenance["optional_native_assets"]["gene_arena/genome_db/paper_gene_cards.json"]
    assert record == {"path": "gene_arena/genome_db/paper_gene_cards.json",
                      "status": "missing_task_json_fallback", "sha256": None}


def test_present_optional_genome_db_is_hashed_but_not_required(adapter, episode, tmp_path):
    genome_db = adapter.source.repository / "gene_arena/genome_db/paper_gene_cards.json"
    write_json(genome_db, [{"trace_id": episode.source_task_id, "paper_index": 0}])
    request_path = tmp_path / "request.json"
    request = adapter.evaluation_request(
        episode, Submission(episode_id=episode.id, answer="proposal"), request_path)
    assert str(genome_db.resolve()) not in request.required_paths
    provenance = read_json(tmp_path / "request.native/submission_provenance.json")
    record = provenance["optional_native_assets"]["gene_arena/genome_db/paper_gene_cards.json"]
    assert record["status"] == "present"
    assert record["sha256"] == sha256(genome_db)


def test_plan_and_mutated_source_cannot_be_graded(adapter, episode, tmp_path):
    with pytest.raises(ValueError):
        adapter.evaluation_request(episode, Submission(episode_id=episode.id, stage="plan", answer="plan"), tmp_path / "r.json")
    path = adapter.task_path(episode.source_task_id)
    path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        adapter.evaluation_request(episode, Submission(episode_id=episode.id, answer="proposal"), tmp_path / "r.json")


def native_result(request, *, partial=False, score=0):
    write_json(Path(request.output_paths[0]), {"scores": {k: score for k in
               ("pes", "heredity_score", "variation_score", "selection_score")}})
    write_json(Path(request.output_paths[1]), {"n_eval_files": 1, "n_incomplete_eval_files_skipped": int(partial),
        "n_incomplete_eval_files_included": 0, "expected_judge_ids": NATIVE_JUDGES,
        "by_participant_setting": {"submission": {"Question": {"n": 1}}}})


@pytest.mark.parametrize("partial,score,status", [(False, 0, "scored"), (True, 40, "error"), (False, 101, "error")])
def test_native_score_missing_partial_and_zero_distinguished(adapter, episode, tmp_path, partial, score, status):
    request = adapter.evaluation_request(episode, Submission(episode_id=episode.id, answer="proposal"), tmp_path / "r.json")
    assert adapter.collect_evaluation(request).status == "error"
    native_result(request, partial=partial, score=score)
    evaluated = adapter.collect_evaluation(request)
    assert evaluated.status == status
    if status == "scored":
        assert evaluated.metrics["pes"] == 0


def test_no_native_calls_when_assets_or_credentials_missing(adapter, episode, tmp_path, monkeypatch):
    import subprocess
    monkeypatch.delenv("API_KEY", raising=False)
    def forbidden(*args, **kwargs):
        raise AssertionError("Native evaluator must not run")
    monkeypatch.setattr(subprocess, "run", forbidden)
    result = adapter.run_native(episode, Submission(episode_id=episode.id, answer="proposal"), tmp_path / "r.json")
    assert result.status == "blocked"
    assert result.metrics == {}


def test_dry_plan_uses_ten_tasks_three_profiles_without_models(adapter):
    cfg = read_json(project_root() / "configs/ideagene/pilot.json")
    plan = pilot_plan(adapter, cfg)
    assert plan["scheduled_episodes"] == 30
    assert plan["model_calls"] == 0
    assert {p["id"] for p in plan["personas"]} == {"persona_off", "candidate_148", "candidate_046"}


def test_preflight_failure_saved_without_zero_scientific_scores(adapter, tmp_path, monkeypatch):
    import personasciencebench.ideagene_runner as runner
    cfg = read_json(project_root() / "configs/ideagene/pilot.json")
    monkeypatch.setattr(runner, "load_adapter", lambda *args: adapter)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    manifest = tmp_path / "manifest.json"
    write_json(manifest, {})
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        run_pilot(tmp_path, manifest, cfg, tmp_path / "run")
    summary = read_json(tmp_path / "run/summary.json")
    assert summary["attempted"] == summary["scored"] == 0
    assert summary["not_attempted"] == 30
    assert summary["mean_pes"] is None


def test_invalid_config_does_not_silently_broaden_scope():
    cfg = read_json(project_root() / "configs/ideagene/pilot.json")
    cfg["task_ids"].append("another_task")
    with pytest.raises(ValueError):
        validate_config(cfg)


def test_config_accepts_reviewed_smoke_subset_but_rejects_duplicates():
    cfg = read_json(project_root() / "configs/ideagene/pilot.json")
    cfg["task_ids"] = list(SMOKE_IDS)
    cfg["persona_ids"] = ["persona_off"]
    cfg["collaboration"]["max_requests"] = 4
    assert validate_config(cfg)["max_requests"] == 4
    cfg["task_ids"].append(cfg["task_ids"][0])
    with pytest.raises(ValueError, match="unique"):
        validate_config(cfg)


def test_pinned_source_conversion_if_available(tmp_path):
    import os
    import shutil
    from personasciencebench.registry import load_adapter
    root = os.environ.get("PERSONASCIENCEBENCH_SOURCE_ROOT")
    snapshots = os.environ.get("PERSONASCIENCEBENCH_IDEAGENE_TASK_DIR")
    if root and (Path(root) / "ideagene/.git").exists():
        source = load_adapter("ideagene", Path(root))
        expected_ids = PILOT_IDS
    elif snapshots:
        # Optional exact task snapshots validate conversion, not runtime/evaluator readiness.
        hashes = {
            "cs_LLMReasoning": "974d6121ebc09cd342223605747d140a502e9a70a87b94f6b09ce81d2da175cc",
            "biology_SingleCellFoundation": "a1784397d60a6766f67dfff930ad9eb31c1a91fc2f0cc2b84247bfc28181879d"}
        destination = tmp_path / "source/gene_arena/task"
        destination.mkdir(parents=True)
        for tid, digest in hashes.items():
            incoming = Path(snapshots) / (tid + ".json")
            assert sha256(incoming) == digest
            shutil.copyfile(incoming, destination / incoming.name)
        source = IdeaGeneAdapter(SourceConfig(tmp_path / "source", tmp_path / "assets", REVISION))
        expected_ids = SMOKE_IDS
    else:
        pytest.skip("Pinned IdeaGene checkout or hash-verified task snapshots unavailable")
    for tid in expected_ids:
        converted = source.convert(tid)
        assert converted.public.question == source._task(tid)["open_question"]
        assert converted.researcher.facts == []
        assert source._task(tid)["verified"] is True


def test_thirty_episode_scheduler_with_scripted_transport(adapter, tmp_path, monkeypatch):
    import personasciencebench.ideagene_runner as runner
    cfg = read_json(project_root() / "configs/ideagene/pilot.json")
    monkeypatch.setattr(runner, "load_adapter", lambda *args: adapter)
    monkeypatch.setattr(runner, "preflight", lambda specs: {k: {"supported_parameters": ["tools"]} for k in specs})
    class Client:
        def __init__(self, *, role, record, **kwargs):
            self.role, self.record = role, record
            self.actor = Actor([handoff("plan"), handoff("result", native_proposal("fixture"))])
            self.researcher = ResearcherBackend([decision(), decision(approve=True), decision("stop")])

        def completion(self, *args, **kwargs):
            self.record({"role": "actor", "usage": {"total_tokens": 1}, "fixture": True})
            return self.actor.completion(*args, **kwargs)

        def complete_decision(self, *args, **kwargs):
            self.record({"role": "researcher", "usage": {"total_tokens": 1}, "fixture": True})
            return self.researcher.complete_decision(*args, **kwargs)
    monkeypatch.setattr(runner, "OpenRouterClient", Client)
    manifest = tmp_path / "manifest.json"
    write_json(manifest, {})
    result = runner.run_pilot(tmp_path, manifest, cfg, tmp_path / "run")
    assert result["scheduled"] == result["attempted"] == result["submitted"] == 30
    assert result["scored"] == result["evaluated"] == 0
    assert result["mean_pes"] is None
    assert len(list((tmp_path / "run").glob("*/trace.md"))) == 30
    assert all(case["reported_cost_usd"] is None for case in result["cases"])


def test_cli_dry_run_routes_to_shared_adapter_without_inference(adapter, tmp_path, monkeypatch):
    import personasciencebench.cli as cli
    monkeypatch.setattr(cli, "load_adapter", lambda *args: adapter)
    result = cli.main(["run-ideagene", "--dry-run", "--output", str(tmp_path / "plan")])
    assert result == 0
    plan = read_json(tmp_path / "plan/plan.json")
    assert plan["scheduled_episodes"] == 30
    assert plan["model_calls"] == 0


def test_native_process_failure_stays_error(adapter, episode, tmp_path, monkeypatch):
    import os
    import subprocess
    request_path = tmp_path / "native.json"
    for relative in ["gene_arena/run_arena.py", "gene_arena/population_evolving_score.py",
                     "gene_arena/dynamics_eval.py", "gene_arena/arena_config.py"]:
        path = adapter.source.repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic fixture", encoding="utf-8")
    monkeypatch.setenv("API_KEY", "synthetic-unit-test-value")
    for name in list(os.environ):
        if name.startswith("GENE_"):
            monkeypatch.delenv(name)
    def source_identity(argv, **kwargs):
        if "diff" in argv:
            return ""
        if argv[-1] == "HEAD":
            return "synthetic-archive-commit"
        if argv[-1] == "HEAD^{tree}":
            return SOURCE_TREE
        raise AssertionError(f"Unexpected source identity command: {argv}")
    monkeypatch.setattr(subprocess, "check_output", source_identity)
    monkeypatch.setattr(subprocess, "run", lambda *args, **kw: subprocess.CompletedProcess(args[0], 2, b"", b"fixture error"))
    result = adapter.run_native(episode, Submission(episode_id=episode.id, answer="fixture"), request_path)
    assert result.status == "error"
    assert result.metrics == {}
    assert read_json(request_path.with_suffix(".execution.json"))["exit_code"] == 2


def test_native_preflight_rejects_unrelated_commit_and_tree(adapter, episode, tmp_path, monkeypatch):
    import os
    import subprocess
    for relative in ["gene_arena/run_arena.py", "gene_arena/population_evolving_score.py",
                     "gene_arena/dynamics_eval.py", "gene_arena/arena_config.py"]:
        path = adapter.source.repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic fixture", encoding="utf-8")
    monkeypatch.setenv("API_KEY", "synthetic-unit-test-value")
    for name in list(os.environ):
        if name.startswith("GENE_"):
            monkeypatch.delenv(name)
    monkeypatch.setattr(subprocess, "check_output",
                        lambda argv, **kwargs: "" if "diff" in argv else "unrelated")
    monkeypatch.setattr(subprocess, "run",
                        lambda *args, **kwargs: (_ for _ in ()).throw(
                            AssertionError("Mismatched source must not execute")))
    result = adapter.run_native(
        episode, Submission(episode_id=episode.id, answer="fixture"), tmp_path / "native.json")
    assert result.status == "blocked"
    assert result.metrics == {}
