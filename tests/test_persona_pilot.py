"""Persona pilot planning and reporting on synthetic records; no model calls or task execution."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_persona_pilot as pilot  # noqa: E402

TASKS = ["test/archaeology/metadata_29.json/0/0", "test/nls_ses/metadata_6.json/0/0"]


def config(**overrides):
    value = {"name": "unit-pilot", "tasks": TASKS, "task_metadata": None,
             "personas": {"ids": ["candidate_148", "candidate_046"], "repeats": 2},
             "controls": {"persona_off": {"repeats": 3}, "neutral": {"arms": ["neutral_a"], "repeats": 1}},
             "budget": {"usd": 2.0, "tpm_limit": 2_000_000}}
    value.update(overrides)
    return pilot.PilotConfig.model_validate(value)


def test_jobs_cover_every_condition_repeat_and_task_with_controls_first():
    c = config()
    jobs = pilot.jobs_for(c, pilot.arm_profiles(c))
    assert len(jobs) == len(TASKS) * (2 * 2 + 3 + 1)
    assert {j["condition"] for j in jobs[:6]} == {"persona_off"}
    assert len({j["key"] for j in jobs}) == len(jobs)
    assert pilot.jobs_for(c, pilot.arm_profiles(c)) == jobs  # seeded, reproducible order


def test_arms_carry_exact_published_identities_and_labelled_controls():
    arms = pilot.arm_profiles(config())
    assert arms["persona_off"]["persona"] == {"enabled": False}
    from restore_full_persona_cohort import validated_cohort
    assert arms["candidate_148"]["persona"]["system_prompt"] == validated_cohort()[1]["candidate_148"]
    assert arms["neutral_a"]["condition"] == "neutral"
    assert arms["neutral_a"]["persona"]["system_prompt"] == (ROOT / "configs/persona_controls/neutral_a.txt").read_text()


def test_runner_configs_differ_only_in_the_persona_block():
    c = config()
    arms = pilot.arm_profiles(c)
    off, persona = (pilot.runner_config(c, arms[a]["persona"]) for a in ("persona_off", "candidate_148"))
    assert {k for k in off if off[k] != persona[k]} == {"persona"}
    assert off["pilot_cases_per_benchmark"] == 1
    assert off["collaboration"]["unrestricted_knowledge"] and off["collaboration"]["embody_identity"]


@pytest.mark.parametrize("bad", [
    {"tasks": [TASKS[0], TASKS[0]]},
    {"personas": {"ids": []}, "controls": {"persona_off": {"repeats": 0}}},
    {"name": "bad name"},
    {"unknown_field": 1},
])
def test_invalid_configs_are_rejected(bad):
    with pytest.raises(ValueError):
        config(**bad)


def test_unknown_persona_ids_fail_before_any_run():
    with pytest.raises(ValueError, match="Unknown persona"):
        pilot.arm_profiles(config(personas={"ids": ["candidate_999"]}))


def test_dry_run_estimates_and_writes_nothing(tmp_path, capsys):
    path = tmp_path / "pilot.json"
    path.write_text(json.dumps(config().model_dump()))
    result = pilot.plan(path, tmp_path / "run", dry_run=True, source_root=tmp_path)
    assert not (tmp_path / "run").exists()
    assert result["estimate"]["episodes"] == len(result["jobs"])
    assert result["estimate"]["recommended_parallel"] >= 1
    assert "Dry run: nothing written" in capsys.readouterr().out


def fake_episode(output, job, status, score):
    case = output / "episodes" / job["key"] / "case"
    (case / "controller").mkdir(parents=True)
    evaluation = {"status": status, "evaluator_version": "v", "metrics": {"final_score": score}} if status == "scored" else None
    (case / "result.json").write_text(json.dumps({"status": status, "evaluation": evaluation}))
    (case / "controller/events.jsonl").write_text(json.dumps({"type": "agent_handoff", "payload": {}}) + "\n")
    (case / "controller/api_calls.private.jsonl").write_text(json.dumps(
        {"role": "actor", "model": "m", "usage": {"prompt_tokens": 100, "completion_tokens": 10, "cost": 0.001}}) + "\n")
    pilot.write(output / "finished" / (job["key"] + ".json"),
                {**job, "status": status, "elapsed_seconds": 1.0, "result": str(case / "result.json")})


def test_report_matches_tasks_averages_repeats_and_keeps_failures(tmp_path):
    c = config(personas={"ids": ["candidate_148"], "repeats": 2}, controls={"persona_off": {"repeats": 2}})
    jobs = pilot.jobs_for(c, pilot.arm_profiles(c))
    pilot.write(tmp_path / "manifest.json", {"name": c.name, "benchmark": "discoverybench", "tasks": TASKS,
                                             "jobs": jobs, "task_metadata": {}})
    scores = {("persona_off", 1, TASKS[0]): ("scored", 0.0), ("persona_off", 2, TASKS[0]): ("scored", 0.2),
              ("persona_off", 1, TASKS[1]): ("scored", 0.0), ("persona_off", 2, TASKS[1]): ("infrastructure_error", None),
              ("candidate_148", 1, TASKS[0]): ("scored", 0.5), ("candidate_148", 2, TASKS[0]): ("missing_submission", None),
              ("candidate_148", 1, TASKS[1]): ("scored", 0.3), ("candidate_148", 2, TASKS[1]): ("scored", 0.1)}
    for job in jobs:
        fake_episode(tmp_path, job, *scores[(job["arm"], job["repeat"], job["task"])])
    summary = pilot.report(tmp_path)
    arm = summary["aggregate"]["per_arm"]["candidate_148"]
    # Task means: t0 (0.5 + 0) / 2 = 0.25 (missing counts as 0), t1 0.2; off: t0 0.1, t1 0.0 (error excluded).
    assert arm["mean"] == pytest.approx(0.225)
    assert arm["delta_vs_persona_off"] == pytest.approx(((0.25 - 0.1) + (0.2 - 0.0)) / 2)
    assert summary["statuses"] == {"scored": 6, "missing_submission": 1, "infrastructure_error": 1}
    text = (tmp_path / "REPORT.md").read_text()
    assert "infrastructure_error" in text and "Δ vs persona off" in text
    rows = (tmp_path / "results.csv").read_text().splitlines()
    assert len(rows) == 1 + len(jobs)


def test_contrast_detects_a_consistent_shift_and_not_noise():
    rows = []
    for task in TASKS:
        for i in range(6):
            rows.append({"arm": "a", "task": task, "score_all_attempts": 0.8 + 0.01 * i})
            rows.append({"arm": "b", "task": task, "score_all_attempts": 0.2 + 0.01 * i})
            rows.append({"arm": "c", "task": task, "score_all_attempts": 0.2 + 0.01 * ((i + 3) % 6)})
    shifted = pilot.contrast(rows, "a", "b", permutations=2000, bootstrap=1000)
    assert shifted["delta"] == pytest.approx(0.6) and shifted["p_permutation"] < 0.01
    assert shifted["ci95"][0] > 0.5
    same = pilot.contrast(rows, "c", "b", permutations=2000, bootstrap=1000)
    assert same["delta"] == pytest.approx(0.0) and same["p_permutation"] > 0.5
    assert pilot.contrast(rows, "a", "missing") is None


GENDER = {"name": "gender_swap", "kind": "field", "field": "Gender identity", "map": {"Woman": "Man", "Man": "Woman"}}
SPEED = {"name": "speed_accuracy_flip", "kind": "field", "field": "Speed vs accuracy",
         "map": {"Accuracy first": "Speed first", "Speed first": "Accuracy first", "Accuracy-leaning": "Speed-leaning",
                 "Speed-leaning": "Accuracy-leaning", "Balanced": "Balanced (unchanged)"}}
REORDER = {"name": "reordered", "kind": "reorder"}


def variant_config(**overrides):
    return config(personas={"ids": ["candidate_148", "candidate_046"], "repeats": 1, "variants": [GENDER, SPEED, REORDER]},
                  controls={"persona_off": {"repeats": 0}}, **overrides)


def test_field_variants_change_exactly_one_line_and_are_audited():
    arms = pilot.arm_profiles(variant_config())
    for pid in ("candidate_148", "candidate_046"):
        source = arms[pid]["persona"]["system_prompt"].split("\n")
        for arm in (f"{pid}__gender_swap", f"{pid}__speed_accuracy_flip"):
            varied = arms[arm]["persona"]["system_prompt"].split("\n")
            diff = [(a, b) for a, b in zip(source, varied) if a != b]
            assert len(varied) == len(source) and len(diff) == 1
            assert arms[arm]["source"] == pid and arms[arm]["change"]["kind"] == "field"
        assert arms[f"{pid}__gender_swap"]["change"]["to"] == "Man"
    assert arms["candidate_046__speed_accuracy_flip"]["change"] == {
        "kind": "field", "field": "Speed vs accuracy", "line": arms["candidate_046__speed_accuracy_flip"]["change"]["line"],
        "from": "Speed-leaning", "to": "Accuracy-leaning"}


def test_reordered_twin_keeps_every_line_and_pr8_naming():
    arms = pilot.arm_profiles(variant_config())
    twin, source = arms["candidate_148__reordered"], arms["candidate_148"]
    assert sorted(twin["persona"]["system_prompt"].split("\n")) == sorted(source["persona"]["system_prompt"].split("\n"))
    assert twin["persona"]["system_prompt"] != source["persona"]["system_prompt"]
    assert twin["condition"] == "reordered"


@pytest.mark.parametrize("bad", [
    {"name": "x", "kind": "field", "field": "Gender identity", "map": {"Woman": "Woman"}},  # no-op mapping
    {"name": "persona", "kind": "reorder"},  # collides with a built-in condition
    {"name": "y", "kind": "reorder", "field": "Gender identity"},
    {"name": "z", "kind": "field", "map": {"a": "b"}},  # no field
])
def test_invalid_variants_are_rejected(bad):
    with pytest.raises(ValueError):
        pilot.Variant.model_validate(bad)


def test_variants_fail_loudly_when_the_field_or_value_is_absent():
    missing = {"name": "missing", "kind": "field", "field": "No such field", "map": {"a": "b"}}
    with pytest.raises(ValueError, match="exactly one 'No such field' line"):
        pilot.arm_profiles(config(personas={"ids": ["candidate_148"], "variants": [missing]}))
    unmapped = {"name": "unmapped", "kind": "field", "field": "Gender identity", "map": {"Man": "Woman"}}
    with pytest.raises(ValueError, match="no mapping"):
        pilot.arm_profiles(config(personas={"ids": ["candidate_148"], "variants": [unmapped]}))


def test_report_contrasts_each_variant_with_its_source_and_pools_across_personas(tmp_path):
    c = config(personas={"ids": ["candidate_148", "candidate_046"], "repeats": 2, "variants": [GENDER]},
               controls={"persona_off": {"repeats": 0}})
    jobs = pilot.jobs_for(c, pilot.arm_profiles(c))
    pilot.write(tmp_path / "manifest.json", {"name": c.name, "benchmark": "discoverybench", "tasks": TASKS,
                                             "jobs": jobs, "task_metadata": {}})
    for job in jobs:
        fake_episode(tmp_path, job, "scored", 0.6 if job["condition"] == "gender_swap" else 0.2)
    summary = pilot.report(tmp_path)
    tests = summary["aggregate"]["variant_tests"]
    assert tests["candidate_148__gender_swap - candidate_148|score_all_attempts"]["delta"] == pytest.approx(0.4)
    pooled = tests["gender_swap (pooled) - persona|score_all_attempts"]
    assert pooled["delta"] == pytest.approx(0.4) and pooled["tasks"] == 4  # 2 personas x 2 tasks
    assert "Counterfactual variants" in (tmp_path / "REPORT.md").read_text()


@pytest.mark.parametrize("config_name, summary", [
    ("pilot", "summary.json"), ("neutral_b", "neutral_b/summary.json"), ("counterfactual", "counterfactual/summary.json")])
def test_configs_reproduce_the_prompts_injected_in_the_published_runs(config_name, summary):
    """Every arm of the committed configs yields the persona record hash stored with the recorded run."""
    from personasciencebench.persona import Persona, persona_record
    recorded = json.loads((ROOT / "reports/discoverybench_persona_pilot" / summary).read_text())["arms"]
    arms = pilot.arm_profiles(pilot.PilotConfig.load(ROOT / f"configs/discoverybench_pilot/{config_name}.json"))
    assert set(arms) == set(recorded)
    for arm, record in recorded.items():
        assert persona_record(Persona.model_validate(arms[arm]["persona"]))["sha256"] == record["persona_sha256"], arm


@pytest.mark.parametrize("status, errors, expected", [
    ("infrastructure_error", None, True),
    ("error", ["Native judge bridge failed: RemoteProtocolError: Server disconnected without sending a response."], True),
    ("error", ["Native judge bridge failed: RuntimeError: judge: OpenAI HTTP 503"], True),
    ("error", ["Native judge bridge failed: ValueError: Judge response must be a JSON object"], False),
    ("missing_submission", None, False),
    ("scored", None, False),
])
def test_only_infrastructure_failures_are_retried(tmp_path, status, errors, expected):
    result = tmp_path / "result.json"
    result.write_text(json.dumps({"status": status, "evaluation": {"errors": errors} if errors else None}))
    assert pilot.infrastructure_failure({"status": status, "result": str(result)}) is expected
