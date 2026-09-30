#!/usr/bin/env python3
"""Config-driven persona pilots: plan (with a no-cost dry run), run, and report.

One JSON config names the tasks, personas, labelled control conditions, repeats, models,
budget and rate limit. `plan --dry-run` prints the job list and a cost estimate measured
from recorded episodes and writes nothing. `plan` prepares task packages and frozen per-arm
configs (still no model calls). `run` executes jobs through the existing scheduler's
`execute()` (one subprocess per episode) and stops scheduling before the budget is spent.
`report` writes REPORT.md, results.csv and summary.json broken down by persona, task,
domain and condition. Every attempt is kept; missing submissions and infrastructure
failures stay explicit.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import estimate_run_cost as estimate  # noqa: E402

CONDITIONS = ("persona", "persona_off", "neutral")  # built-in conditions; variants add their own names


def condition_order(condition: str) -> tuple[int, str]:
    return (CONDITIONS.index(condition), "") if condition in CONDITIONS else (len(CONDITIONS), condition)
PRIMARY = {"discoverybench": "final_score", "openproblems_denoising": "score"}
SUCCESS_STATUSES = {"scored", "missing_submission"}


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Variant(Record):
    """A counterfactual copy of every listed persona, labelled as its own condition.

    `field` swaps exactly one profile line `- <field>: <value>` using `map` (every source value
    must be mapped to a different value); `reorder` shuffles bullets within sections (same
    content, different wording order) and is the wording-noise reference.
    """
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    kind: Literal["field", "reorder"]
    field: str | None = None
    map: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def complete(self):
        if self.name in CONDITIONS:
            raise ValueError(f"Variant name {self.name!r} is a built-in condition")
        if self.kind == "field" and (not self.field or not self.map or any(k == v for k, v in self.map.items())):
            raise ValueError("A field variant needs a field and a map whose values differ from its keys")
        if self.kind == "reorder" and (self.field or self.map):
            raise ValueError("A reorder variant takes no field or map")
        return self


class Personas(Record):
    ids: list[str] = Field(default_factory=list)
    repeats: int = Field(default=1, ge=1, le=10)
    variants: list[Variant] = Field(default_factory=list)


class OffControl(Record):
    repeats: int = Field(default=1, ge=0, le=10)


class NeutralControl(Record):
    arms: list[Literal["neutral_a", "neutral_b"]] = Field(default_factory=list)
    repeats: int = Field(default=1, ge=1, le=10)


class Controls(Record):
    persona_off: OffControl = Field(default_factory=OffControl)
    neutral: NeutralControl = Field(default_factory=NeutralControl)


class Budget(Record):
    usd: float = Field(gt=0)
    tpm_limit: int | None = Field(default=None, gt=0)
    headroom: float = Field(default=0.6, gt=0, le=1)


class PilotConfig(Record):
    schema_version: Literal["1"] = "1"
    name: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_.-]+$")
    description: str = ""
    status: Literal["provisional", "approved"] = "provisional"
    benchmark: Literal["discoverybench", "openproblems_denoising"] = "discoverybench"
    # Dedicated actor environment for every episode (e.g. single-cell packages); default: the shared .actor-venv.
    actor_python: str | None = None
    # Cost estimates use recorded episodes of this benchmark; before any exist, name a proxy benchmark.
    estimate_benchmark: str | None = None
    base_config: str = "configs/full_persona_v2/shared.json"
    models: dict | None = None
    collaboration: dict = Field(default_factory=lambda: {
        "unrestricted_knowledge": True, "embody_identity": True, "volunteer_information": True})
    tasks: list[str] = Field(min_length=1)
    task_metadata: str | None = "configs/discoverybench_pilot/candidates.json"
    personas: Personas = Field(default_factory=Personas)
    controls: Controls = Field(default_factory=Controls)
    budget: Budget
    parallel: int | None = Field(default=None, ge=1, le=12)
    seed: int = 20260929

    @model_validator(mode="after")
    def consistent(self):
        if len(set(self.tasks)) != len(self.tasks):
            raise ValueError("Task IDs must be unique")
        if len(set(self.personas.ids)) != len(self.personas.ids):
            raise ValueError("Persona IDs must be unique")
        if len({v.name for v in self.personas.variants}) != len(self.personas.variants):
            raise ValueError("Variant names must be unique")
        if self.personas.variants and not self.personas.ids:
            raise ValueError("Variants need personas to vary")
        if not (self.personas.ids or self.controls.persona_off.repeats or self.controls.neutral.arms):
            raise ValueError("The pilot has no arms")
        return self

    @classmethod
    def load(cls, path: Path) -> "PilotConfig":
        return cls.model_validate(json.loads(path.read_text()))


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def git_revision() -> str | None:
    try:
        revision = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"], text=True).strip()
        return revision + ("+uncommitted" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return None


def reorder_bullets(text: str, seed: str) -> str:
    """Shuffle '- ' bullet lines within each '#' section; headers and other lines keep their places.

    Same algorithm as the reordered-twin arms of the persona-controls work (#8, to be resubmitted).
    """
    rng = random.Random(seed)
    lines = text.split("\n")
    sections = [[]]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            sections.append([])
        elif line.startswith("- "):
            sections[-1].append(i)
    for positions in sections:
        bullets = [lines[i] for i in positions]
        rng.shuffle(bullets)
        for i, bullet in zip(positions, bullets):
            lines[i] = bullet
    return "\n".join(lines)


def apply_variant(prompt: str, variant: Variant, persona_id: str) -> tuple[str, dict]:
    """Return the varied prompt and an audit record; refuse anything but the intended change."""
    lines = prompt.split("\n")
    if variant.kind == "reorder":
        varied = reorder_bullets(prompt, persona_id)
        if sorted(varied.split("\n")) != sorted(lines) or varied == prompt:
            raise ValueError(f"Reordering {persona_id} must permute its lines without adding or removing any")
        return varied, {"kind": "reorder", "moved_lines": sum(a != b for a, b in zip(lines, varied.split("\n")))}
    prefix = f"- {variant.field}: "
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"{persona_id}: expected exactly one '{variant.field}' line, found {len(matches)}")
    index = matches[0]
    value = lines[index][len(prefix):].strip()
    if value not in variant.map:
        raise ValueError(f"{persona_id}: no mapping for {variant.field} = {value!r}")
    varied_lines = list(lines)
    varied_lines[index] = prefix + variant.map[value]
    varied = "\n".join(varied_lines)
    changed = [i for i, (a, b) in enumerate(zip(lines, varied_lines)) if a != b]
    assert changed == [index] and len(varied_lines) == len(lines)
    return varied, {"kind": "field", "field": variant.field, "line": index + 1, "from": value, "to": variant.map[value]}


def arm_profiles(config: PilotConfig) -> dict[str, dict]:
    """Arm name -> {'condition', 'persona' (the profile block for the runner config)}."""
    arms = {}
    if config.controls.persona_off.repeats:
        arms["persona_off"] = {"condition": "persona_off", "repeats": config.controls.persona_off.repeats,
                               "persona": {"enabled": False}}
    if config.personas.ids:
        from restore_full_persona_cohort import validated_cohort
        _, prompts = validated_cohort()
        unknown = sorted(set(config.personas.ids) - set(prompts))
        if unknown:
            raise ValueError(f"Unknown persona IDs (expected full_persona_v2 candidates): {', '.join(unknown)}")
        for pid in config.personas.ids:
            arms[pid] = {"condition": "persona", "repeats": config.personas.repeats, "source": pid,
                         "persona": {"enabled": True, "id": pid, "version": "full-persona-v2",
                                     "system_prompt": prompts[pid]}}
            for variant in config.personas.variants:
                varied, change = apply_variant(prompts[pid], variant, pid)
                # "__reordered" keeps PR #8's arm naming for twins (arms.TWIN); other variants are named by kind.
                arm = f"{pid}__reordered" if variant.kind == "reorder" else f"{pid}__{variant.name}"
                arms[arm] = {"condition": variant.name, "repeats": config.personas.repeats, "source": pid,
                             "change": change,
                             "persona": {"enabled": True, "id": arm, "version": f"full-persona-v2+{variant.name}",
                                         "system_prompt": varied}}
    for arm in config.controls.neutral.arms:
        arms[arm] = {"condition": "neutral", "repeats": config.controls.neutral.repeats,
                     "persona": {"enabled": True, "id": arm, "version": "neutral-v1",
                                 "system_prompt": (ROOT / "configs/persona_controls" / f"{arm}.txt").read_text()}}
    return arms


def runner_config(config: PilotConfig, persona: dict) -> dict:
    shared = read(ROOT / config.base_config)
    if config.models is not None:
        shared["models"] = deepcopy(config.models)
    shared["collaboration"] = {**shared.get("collaboration", {}), **config.collaboration}
    shared["pilot_cases_per_benchmark"] = 1
    if config.actor_python:
        shared["actor_python_overrides"] = {f"{config.benchmark}:{task}": str((ROOT / config.actor_python).resolve())
                                            for task in config.tasks}
    shared["persona"] = deepcopy(persona)
    shared["notes"] = [f"Persona pilot {config.name}; frozen by scripts/run_persona_pilot.py.",
                       "The persona block is the only difference between arms; tasks, models and budgets are shared."]
    return shared


def task_metadata(config: PilotConfig) -> dict[str, dict]:
    if not config.task_metadata or not (ROOT / config.task_metadata).is_file():
        return {}
    return {row["task_id"]: row for row in read(ROOT / config.task_metadata)["candidates"]}


def slug(task_id: str) -> str:
    return hashlib.sha256(task_id.encode()).hexdigest()[:12]


def jobs_for(config: PilotConfig, arms: dict[str, dict]) -> list[dict]:
    """Controls first (they calibrate everything else), then a seeded shuffle of the rest."""
    metadata = task_metadata(config)
    jobs = []
    for arm, spec in arms.items():
        for repeat in range(1, spec["repeats"] + 1):
            for task in config.tasks:
                episode_id = f"{config.benchmark}:{task}"
                jobs.append({"id": episode_id, "slug": slug(episode_id), "kind": "python",
                             "benchmark": config.benchmark, "task": task, "arm": arm,
                             "condition": spec["condition"], "repeat": repeat, "source": spec.get("source"),
                             "domain": metadata.get(task, {}).get("domain"),
                             "key": f"{arm}-r{repeat}-{slug(episode_id)}"})
    controls = [j for j in jobs if j["condition"] == "persona_off"]
    rest = [j for j in jobs if j["condition"] != "persona_off"]
    random.Random(config.seed).shuffle(rest)
    return controls + rest


def cost_model(config: PilotConfig) -> tuple[str, dict[str, int]]:
    models = config.models or read(ROOT / config.base_config)["models"]
    actor = models["actor"]["model"]
    return actor, {role: spec.get("max_tokens", 0) for role, spec in models.items()}


def estimate_plan(config: PilotConfig, jobs: list[dict]) -> dict:
    model, max_tokens = cost_model(config)
    sources = [ROOT / "reports/full_persona_v2/recorded_traces", *sorted((ROOT / "runs").glob("*/episodes"))]
    samples = estimate.load_samples(sources, config.estimate_benchmark or config.benchmark)
    summary = estimate.summarize(samples, episodes=len(jobs), model=model, max_tokens=max_tokens,
                                 tpm_limit=config.budget.tpm_limit, headroom=config.budget.headroom)
    summary["by_condition"] = dict(Counter(j["condition"] for j in jobs))
    summary["proxy_benchmark"] = config.estimate_benchmark
    summary["within_budget_at_p90"] = summary["plan"]["p90"]["cost_usd"] <= config.budget.usd
    return summary


def plan_text(config: PilotConfig, jobs: list[dict], summary: dict) -> str:
    arms = Counter((j["condition"], j["arm"]) for j in jobs)
    lines = [f"Pilot {config.name} ({config.status}): {len(config.tasks)} tasks, {len(jobs)} episodes.", ""]
    lines += [f"  {condition:12} {arm:22} {n} episodes" for (condition, arm), n in sorted(arms.items())]
    if config.estimate_benchmark:
        lines.append(f"Estimate uses recorded {config.estimate_benchmark} episodes as a proxy; no {config.benchmark} episodes are recorded yet.")
    lines += ["", estimate.render(summary), "",
              f"Budget ${config.budget.usd:.2f}: p90 plan cost ${summary['plan']['p90']['cost_usd']:.2f} "
              f"({'within' if summary['within_budget_at_p90'] else 'OVER'} budget)."]
    parallel = config.parallel or summary.get("recommended_parallel")
    lines.append(f"Parallel workers: {parallel or 'set parallel or budget.tpm_limit'}"
                 + ("" if config.parallel else " (from the TPM limit)" if parallel else ""))
    if summary.get("single_worker_exceeds_limit"):
        lines.append("One worker exceeds the TPM limit: run with parallel 1 and rely on the provider's rate-limit retries.")
    return "\n".join(lines)


def prepare(config: PilotConfig, output: Path, source_root: Path) -> dict[str, str]:
    """Export each task once (no model calls) and give every task its own one-case manifest."""
    selection = output / "selection.json"
    write(selection, {config.benchmark: config.tasks})
    prepared = output / "prepared"
    subprocess.run([sys.executable, "-m", "personasciencebench", "--source-root", str(source_root), "prepare",
                    "--benchmarks", config.benchmark, "--selection", str(selection),
                    "--cases-per-benchmark", str(len(config.tasks)), "--output", str(prepared)],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    manifest = read(prepared / "pilot_manifest.json")
    packages = {}
    for record in manifest["cases"]:
        if not record["assets_ready"]:
            raise ValueError(f"Assets are not ready for {record['episode_id']}")
        target = output / "inputs" / slug(record["episode_id"])
        write(target / "pilot_manifest.json", {**manifest, "cases": [record], "cases_per_benchmark": 1})
        packages[record["episode_id"]] = str(target)
    return packages


def plan(config_path: Path, output: Path, *, dry_run: bool, source_root: Path) -> dict:
    config = PilotConfig.load(config_path)
    arms = arm_profiles(config)
    jobs = jobs_for(config, arms)
    summary = estimate_plan(config, jobs)
    print(plan_text(config, jobs, summary))
    if dry_run:
        print("\nDry run: nothing written, no packages prepared, no model calls.")
        return {"jobs": jobs, "estimate": summary}
    if output.exists():
        raise ValueError(f"{output} exists; use a fresh output directory for every pilot")
    output.mkdir(parents=True)
    output.chmod(0o700)
    packages = prepare(config, output, source_root)
    for job in jobs:
        job["prepared"] = packages[job["id"]]
    records = {}
    from personasciencebench.persona import Persona, persona_record
    for arm, spec in arms.items():
        shared = runner_config(config, spec["persona"])
        write(output / "configs" / arm / "shared.json", shared)
        record = persona_record(Persona.model_validate(spec["persona"]))
        write(output / "configs" / arm / "persona.private.json", record)
        records[arm] = {"condition": spec["condition"], "repeats": spec["repeats"], "source": spec.get("source"),
                        "change": spec.get("change"), "persona_sha256": record["sha256"],
                        "config_sha256": hashlib.sha256((output / "configs" / arm / "shared.json").read_bytes()).hexdigest()}
    manifest = {"version": "persona-pilot-v1", "name": config.name, "status": config.status,
                "config": config.model_dump(), "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
                "git_revision": git_revision(), "benchmark": config.benchmark, "tasks": config.tasks,
                "task_metadata": task_metadata(config), "arms": records, "jobs": jobs,
                "models": runner_config(config, {"enabled": False})["models"], "estimate": summary,
                "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    write(output / "manifest.json", manifest)
    print(f"\nPlanned {len(jobs)} episodes in {output}. No model calls were made.")
    return manifest


def case_directory(output: Path, job: dict) -> Path | None:
    found = list((output / "episodes" / job["key"]).glob("*/result.json"))
    return found[0].parent if len(found) == 1 else None


def call_cost(usage: dict, price: tuple[float, float, float]) -> float:
    """Provider-reported cost where given (OpenRouter), otherwise tokens at list price (OpenAI, Azure)."""
    if isinstance(usage.get("cost"), (int, float)):
        return usage["cost"]
    cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0) or 0
    prompt = usage.get("prompt_tokens", 0) or 0
    return ((prompt - cached) * price[0] + cached * price[2]
            + (usage.get("completion_tokens", 0) or 0) * price[1]) / 1e6


def spent_usd(output: Path, price: tuple[float, float, float]) -> float:
    spent = 0.0
    for calls in (output / "episodes").glob("*/*/controller/api_calls.private.jsonl"):
        for line in calls.read_text().splitlines():
            spent += call_cost(json.loads(line).get("usage") or {}, price)
    return spent


INFRASTRUCTURE_STATUSES = {"infrastructure_error", "runtime_error", "launch_error"}
# Evaluation errors whose recorded cause is transport, not the submission: the judge never answered.
TRANSPORT_ERROR = re.compile(r"RemoteProtocolError|ConnectError|ReadError|transport failed|HTTP 5\d\d|HTTP 429")
# Recorded causes meaning the evaluator process itself was killed (e.g. out of memory); the submission stands.
EVALUATOR_FAILURE = re.compile(r"Signals\.SIGKILL|killed by signal|Native evaluator failure \(infrastructure\)")


def infrastructure_failure(finished: dict) -> bool:
    """Retry only failures of the infrastructure, never low or missing scientific outcomes."""
    if finished["status"] in INFRASTRUCTURE_STATUSES:
        return True
    if finished["status"] != "error" or not finished.get("result"):
        return False
    result = Path(finished["result"].replace("/repo/", str(ROOT) + "/", 1))
    if not result.is_file():
        return False
    errors = (read(result).get("evaluation") or {}).get("errors") or []
    return bool(errors) and all(TRANSPORT_ERROR.search(e) for e in errors)


def _result_path(finished: dict) -> Path | None:
    if not finished.get("result"):
        return None
    path = Path(finished["result"].replace("/repo/", str(ROOT) + "/", 1))
    return path if path.is_file() else None


def regrade_candidates(output: Path) -> list[dict]:
    """Latest attempt per cell whose every recorded error is an evaluator kill, with a sealed submission."""
    latest = {}
    for finished in sorted((read(p) for p in (output / "finished").glob("*.json")), key=lambda f: f.get("attempt", 1)):
        latest[(finished["arm"], finished["repeat"], finished["task"])] = finished
    chosen = []
    for finished in latest.values():
        result = _result_path(finished)
        if result is None or not (result.parent / "controller/submission.json").is_file():
            continue
        errors = (read(result).get("evaluation") or {}).get("errors") or []
        if errors and all(EVALUATOR_FAILURE.search(e) for e in errors):
            chosen.append(finished)
    return chosen


def regrade(output: Path) -> list[dict]:
    """Re-evaluate sealed submissions whose native evaluator was killed. Programmatic evaluators only; no model calls.

    The actor's work is kept; only grading is repeated. Originals stay; each regrade is recorded as attempt 2.
    """
    from personasciencebench.registry import load_adapter
    from personasciencebench.schema import Episode, Submission
    prepared = read(output / "prepared/pilot_manifest.json")
    done = []
    for finished in regrade_candidates(output):
        result_path = _result_path(finished)
        case = result_path.parent
        episode = Episode.model_validate(read(case / "controller/episode.private.json"))
        if episode.evaluator.kind != "native_programmatic":
            raise ValueError(f"{finished['key']}: regrade supports programmatic evaluators only (no judge calls)")
        adapter = load_adapter(episode.benchmark, Path(prepared["source_root"]), Path(prepared["source_manifest"]))
        submission = Submission.model_validate(read(case / "controller/submission.json"))
        evaluation = adapter.evaluate(episode, submission, None)
        evaluation.details.update(judge_model=None, judge_kind="native_programmatic_verifier", regrade_of=finished["key"])
        record = {**read(result_path), "status": evaluation.status, "evaluation": evaluation.model_dump(mode="json"),
                  "regraded_from": finished["key"]}
        regraded = case / "result.regrade2.json"
        write(regraded, record)
        key = finished["key"] + "-regrade2"
        entry = {**finished, "key": key, "attempt": finished.get("attempt", 1) + 1, "status": evaluation.status,
                 "result": str(regraded), "regrade": True}
        write(output / "finished" / (key + ".json"), entry)
        print(f"{key}: {evaluation.status} {evaluation.metrics.get('score')}", flush=True)
        done.append(entry)
    print(f"Regraded {len(done)} sealed submissions; no model calls.")
    return done


def run(output: Path, *, parallel: int | None, yes: bool, allow_provisional: bool, retry_errors: bool) -> dict:
    import run_persona_benchmarks as scheduler
    manifest = read(output / "manifest.json")
    config = PilotConfig.model_validate(manifest["config"])
    if manifest["status"] != "approved" and not allow_provisional:
        raise ValueError("This pilot config is provisional; set status to approved (or pass --allow-provisional)")
    workers = parallel or config.parallel or manifest["estimate"].get("recommended_parallel") or 1
    pending = [j for j in manifest["jobs"] if not (output / "finished" / (j["key"] + ".json")).exists()]
    if retry_errors:
        for job in manifest["jobs"]:
            done = output / "finished" / (job["key"] + ".json")
            retry = {**job, "key": job["key"] + "-retry2", "attempt": 2}
            if (done.exists() and infrastructure_failure(read(done))
                    and not (output / "finished" / (retry["key"] + ".json")).exists()):
                pending.append(retry)
    model, _ = cost_model(config)
    price = estimate.price_for(model, None)
    p90_episode = manifest["estimate"]["per_episode"]["p90"]["cost_usd"]
    print(f"{len(pending)} pending episodes, {workers} parallel workers, budget ${config.budget.usd:.2f}, "
          f"already spent ${spent_usd(output, price):.2f}.")
    if not yes:
        raise ValueError("Paid run: re-run with --yes after reviewing the plan and estimate above")
    active, stopped = {}, None
    with ThreadPoolExecutor(max_workers=workers) as pool:
        while pending or active:
            # Reserve a p90 episode for every running and newly started job before launching it.
            while pending and len(active) < workers:
                projected = spent_usd(output, price) + p90_episode * (len(active) + 1)
                if projected > config.budget.usd:
                    stopped = f"budget: spent plus in-flight p90 would exceed ${config.budget.usd:.2f}"
                    pending = []
                    break
                job = pending.pop(0)
                active[pool.submit(scheduler.execute, output, job)] = job
            if not active:
                break
            done, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in done:
                job = active.pop(future)
                result = future.result()
                print(f"{job['key']}: {result['status']} ({result['elapsed_seconds']:.0f}s)", flush=True)
    state = {"spent_usd": spent_usd(output, price), "stopped": stopped,
             "finished": len(list((output / "finished").glob("*.json"))), "planned": len(manifest["jobs"])}
    write(output / "run_state.json", state)
    print(json.dumps(state))
    return state


def episode_row(output: Path, manifest: dict, finished: dict, price=(0.0, 0.0, 0.0)) -> dict:
    case = Path(finished["result"]).parent if finished.get("result") else None
    # The record this attempt points to: result.json, or result.regrade2.json for a regraded submission.
    record = read(Path(finished["result"])) if case and Path(finished["result"]).is_file() else {}
    events = []
    if case and (case / "controller/events.jsonl").is_file():
        events = [json.loads(line) for line in (case / "controller/events.jsonl").read_text().splitlines() if line.strip()]
    counts = Counter(e["type"] for e in events)
    decisions = [e["payload"] for e in events if e["type"] == "researcher_decision"]
    usage = {"prompt": 0, "completion": 0, "cost": 0.0, "calls": 0}
    models = set()
    if case and (case / "controller/api_calls.private.jsonl").is_file():
        for line in (case / "controller/api_calls.private.jsonl").read_text().splitlines():
            call = json.loads(line)
            u = call.get("usage") or {}
            usage["calls"] += 1
            usage["prompt"] += u.get("prompt_tokens", 0) or 0
            usage["completion"] += u.get("completion_tokens", 0) or 0
            usage["cost"] += call_cost(u, price)
            models.add(call.get("resolved_model") or call.get("model"))
    evaluation = record.get("evaluation") or {}
    metric = PRIMARY[manifest["benchmark"]]
    value = (evaluation.get("metrics") or {}).get(metric)
    hypothesis = None
    if case and (case / "controller/submission.json").is_file():
        submission = read(case / "controller/submission.json")
        hypothesis = (submission.get("payload") or {}).get("hypothesis") or submission.get("answer") or ""
    return {"key": finished["key"], "task": finished["task"], "domain": finished.get("domain"),
            "source": finished.get("source"),
            "hypothesis_chars": len(hypothesis) if hypothesis is not None else None,
            "hypothesis_numbers": len(re.findall(r"\d+(?:\.\d+)?", hypothesis)) if hypothesis is not None else None,
            "condition": finished["condition"], "arm": finished["arm"], "repeat": finished["repeat"],
            "attempt": finished.get("attempt", 1), "status": finished["status"],
            "score": value if finished["status"] == "scored" else None,
            # Report convention of full_persona_v2: a missing submission counts as zero; errors stay missing.
            "score_all_attempts": (value if finished["status"] == "scored" else
                                   0.0 if finished["status"] == "missing_submission" else None),
            "exchanges": counts["agent_handoff"], "researcher_decisions": len(decisions),
            "revision_requests": sum(d.get("phase") == "result_review" and d.get("action") == "continue" for d in decisions),
            "researcher_words": sum(len(str(d.get("message", "")).split()) for d in decisions),
            "researcher_chars": sum(len(str(d.get("message", ""))) for d in decisions),
            "api_calls": usage["calls"], "prompt_tokens": usage["prompt"], "completion_tokens": usage["completion"],
            "cost_usd": usage["cost"], "resolved_models": ";".join(sorted(m for m in models if m)),
            "evaluator_version": evaluation.get("evaluator_version"), "elapsed_seconds": finished.get("elapsed_seconds"),
            "trace": str(case / "trace.md") if case and (case / "trace.md").is_file() else None}


def mean_or_none(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


def sd_or_none(values):
    values = [v for v in values if v is not None]
    return statistics.stdev(values) if len(values) > 1 else None


def fmt(value, scale=100, digits=1, suffix=""):
    return "–" if value is None else f"{value * scale:.{digits}f}{suffix}"


def _matched_delta(scores, a, b, tasks):
    return statistics.mean(statistics.mean(scores[(a, t)]) - statistics.mean(scores[(b, t)]) for t in tasks)


def contrast(rows: list[dict], a: str, b: str, *, permutations=20000, bootstrap=5000, seed=1,
             value: str = "score_all_attempts", arm_key: str = "arm", stratum_key: str = "task") -> dict | None:
    """Task-matched delta a - b with a permutation p (labels shuffled within each task, which keeps
    task difficulty fixed) and a percentile bootstrap CI (episodes resampled within arm x task)."""
    scores = defaultdict(list)
    for row in rows:
        if row.get(value) is not None:
            scores[(row[arm_key], row[stratum_key])].append(float(row[value]))
    tasks = sorted(t for t in {r[stratum_key] for r in rows} if scores.get((a, t)) and scores.get((b, t)))
    if not tasks:
        return None
    rng = random.Random(seed)
    observed = _matched_delta(scores, a, b, tasks)
    extreme = 0
    for _ in range(permutations):
        shuffled = {}
        for t in tasks:
            pool = scores[(a, t)] + scores[(b, t)]
            rng.shuffle(pool)
            k = len(scores[(a, t)])
            shuffled[(a, t)], shuffled[(b, t)] = pool[:k], pool[k:]
        extreme += abs(_matched_delta(shuffled, a, b, tasks)) >= abs(observed) - 1e-12
    draws = sorted(_matched_delta({(x, t): [rng.choice(scores[(x, t)]) for _ in scores[(x, t)]]
                                   for x in (a, b) for t in tasks}, a, b, tasks) for _ in range(bootstrap))
    return {"delta": observed, "ci95": [draws[int(0.025 * bootstrap)], draws[int(0.975 * bootstrap)]],
            "p_permutation": extreme / permutations, "tasks": len(tasks)}


def aggregate(rows: list[dict]) -> dict:
    """Task-matched means: average repeats within (arm, task) first, then over tasks."""
    cells = defaultdict(list)
    for row in rows:
        cells[(row["arm"], row["task"])].append(row["score_all_attempts"])
    cell_mean = {key: mean_or_none(v) for key, v in cells.items()}
    arms = sorted({row["arm"] for row in rows})
    tasks = sorted({row["task"] for row in rows})
    control = {t: cell_mean.get(("persona_off", t)) for t in tasks}
    neutral_arms = sorted({r["arm"] for r in rows if r["condition"] == "neutral"})
    neutral = {t: mean_or_none([cell_mean.get((a, t)) for a in neutral_arms]) for t in tasks}
    per_arm = {}
    for arm in arms:
        condition = next(r["condition"] for r in rows if r["arm"] == arm)
        shared = [t for t in tasks if cell_mean.get((arm, t)) is not None]
        vs_off = [t for t in shared if control.get(t) is not None]
        vs_neutral = [t for t in shared if neutral.get(t) is not None]
        per_arm[arm] = {
            "condition": condition, "tasks": len(shared),
            "mean": mean_or_none([cell_mean[(arm, t)] for t in shared]),
            "delta_vs_persona_off": (mean_or_none([cell_mean[(arm, t)] - control[t] for t in vs_off])
                                     if condition != "persona_off" else None),
            "tasks_vs_persona_off": len(vs_off),
            "delta_vs_neutral": (mean_or_none([cell_mean[(arm, t)] - neutral[t] for t in vs_neutral])
                                 if condition == "persona" else None),
        }
    off_sd = [sd_or_none(v) for (arm, _), v in cells.items() if arm == "persona_off"]
    return {"cell_mean": {f"{a}|{t}": v for (a, t), v in cell_mean.items()}, "per_arm": per_arm,
            "noise": {"persona_off_sd_mean_over_tasks": mean_or_none(off_sd),
                      "tasks_with_repeated_off": sum(v is not None for v in off_sd)}}


def report(output: Path) -> dict:
    manifest = read(output / "manifest.json")
    finished = [read(p) for p in sorted((output / "finished").glob("*.json"))]
    model = (manifest.get("models") or {}).get("actor", {}).get("model", "")
    try:
        price = estimate.price_for(model, None)
    except ValueError:
        price = (0.0, 0.0, 0.0)
    all_rows = [episode_row(output, manifest, f, price) for f in finished]
    # Retries replace only infrastructure failures of the same job; every attempt stays in results.csv.
    latest = {}
    for row in sorted(all_rows, key=lambda r: r["attempt"]):
        latest[(row["arm"], row["repeat"], row["task"])] = row
    rows = list(latest.values())
    agg = aggregate([r for r in rows if r["status"] in SUCCESS_STATUSES])
    metric = PRIMARY[manifest["benchmark"]]
    lines = [f"# Persona pilot: {manifest['name']}", "",
             f"Benchmark **{manifest['benchmark']}**, primary metric `{metric}` (native, 0–100 here). "
             f"{len(rows)}/{len(manifest['jobs'])} planned episodes finished; statuses "
             f"{dict(Counter(r['status'] for r in rows))}. Code {manifest.get('git_revision')}; "
             f"models {', '.join(sorted({r['resolved_models'] for r in rows if r['resolved_models']})) or 'n/a'}.", "",
             "Scores average repeats within each arm × task first, then tasks. Missing submissions count as 0 "
             "(full_persona_v2 convention); infrastructure and evaluator errors are excluded and listed. "
             "Deltas are task-matched against the persona-off mean (and the neutral mean). These are descriptive "
             "pilot results, not significance tests.", "",
             "## By condition and arm", "",
             "| Condition | Arm | Tasks | Mean score | Δ vs persona off | Δ vs neutral |", "|---|---|---:|---:|---:|---:|"]
    for arm, a in sorted(agg["per_arm"].items(), key=lambda kv: (condition_order(kv[1]["condition"]), kv[0])):
        lines.append(f"| {a['condition']} | {arm} | {a['tasks']} | {fmt(a['mean'])} | "
                     f"{fmt(a['delta_vs_persona_off'], suffix=' pp')} | {fmt(a['delta_vs_neutral'], suffix=' pp')} |")
    noise = agg["noise"]
    lines += ["", f"Persona-off run-to-run SD (mean over {noise['tasks_with_repeated_off']} tasks with repeats): "
              f"{fmt(noise['persona_off_sd_mean_over_tasks'], suffix=' pp')}. A persona delta smaller than this is "
              "indistinguishable from ordinary variation.", ""]
    scored = [r for r in rows if r["status"] in SUCCESS_STATUSES]
    references = [a for a in ("persona_off", *sorted({r["arm"] for r in scored if r["condition"] == "neutral"}))
                  if any(r["arm"] == a for r in scored)]
    tests = {}
    for reference in references:
        for arm in sorted({r["arm"] for r in scored} - {reference}):
            if reference != "persona_off" and agg["per_arm"][arm]["condition"] != "persona":
                continue
            result = contrast(scored, arm, reference)
            if result:
                tests[f"{arm} - {reference}"] = result
    agg["tests"] = tests
    variant_arms = sorted(a for a, v in agg["per_arm"].items() if v["condition"] not in CONDITIONS)
    variant_tests = {}
    if variant_arms:
        sources = {r["arm"]: r["source"] for r in scored}
        for arm in variant_arms:
            for measure in ("score_all_attempts", "hypothesis_chars"):
                result = contrast(scored, arm, sources[arm], value=measure)
                if result:
                    variant_tests[f"{arm} - {sources[arm]}|{measure}"] = result
        # Pooled: each variant kind against the unchanged personas, stratified by persona x task.
        pooled_rows = [{**r, "kind": r["condition"], "stratum": f"{r['source']}|{r['task']}"}
                       for r in scored if r.get("source")]
        for kind in sorted({agg["per_arm"][a]["condition"] for a in variant_arms}):
            for measure in ("score_all_attempts", "hypothesis_chars"):
                result = contrast(pooled_rows, kind, "persona", value=measure, arm_key="kind", stratum_key="stratum")
                if result:
                    variant_tests[f"{kind} (pooled) - persona|{measure}"] = result
        agg["variant_tests"] = variant_tests
        lines += ["## Counterfactual variants", "",
                  "Each variant against its own unchanged persona, task-matched; pooled rows stratify by persona × task. "
                  "Score in pp; hypothesis length in characters. The `reordered` variant changes only line order, so its "
                  "contrast is the wording-noise reference for the others.", "",
                  "| Contrast | Measure | Δ | 95% CI | Permutation p |", "|---|---|---:|---:|---:|"]
        for name, t in variant_tests.items():
            contrast_name, measure = name.split("|")
            scale, unit = (100, " pp") if measure == "score_all_attempts" else (1, "")
            lines.append(f"| {contrast_name} | {'score' if scale == 100 else 'hypothesis chars'} | "
                         f"{t['delta'] * scale:+.1f}{unit} | [{t['ci95'][0] * scale:+.1f}, {t['ci95'][1] * scale:+.1f}] | "
                         f"{t['p_permutation']:.3f} |")
        lines.append("")
    if tests:
        lines += ["## Uncertainty", "",
                  "Task-matched deltas with a 95% percentile bootstrap interval (episodes resampled within arm × task) "
                  "and a two-sided permutation p (condition labels shuffled within each task). p values are not "
                  f"corrected for the {len(tests)} comparisons shown; treat single p < 0.05 results as leads.", "",
                  "| Contrast | Δ (pp) | 95% CI (pp) | Permutation p |", "|---|---:|---:|---:|"]
        for name, t in tests.items():
            lines.append(f"| {name} | {t['delta'] * 100:+.1f} | [{t['ci95'][0] * 100:+.1f}, {t['ci95'][1] * 100:+.1f}] | {t['p_permutation']:.3f} |")
        lines.append("")
    lines += ["## By task", ""]
    arms = sorted({r["arm"] for r in rows}, key=lambda a: (condition_order(next(r["condition"] for r in rows if r["arm"] == a)), a))
    lines += ["| Task | Domain | " + " | ".join(arms) + " |", "|---|---|" + "---:|" * len(arms)]
    for task in manifest["tasks"]:
        domain = (manifest.get("task_metadata") or {}).get(task, {}).get("domain", "")
        cells = [fmt(agg["cell_mean"].get(f"{a}|{task}")) for a in arms]
        lines.append(f"| `{task}` | {domain} | " + " | ".join(cells) + " |")
    lines += ["", "## By domain and condition", "", "| Domain | Condition | Episodes | Mean score |", "|---|---|---:|---:|"]
    by_domain = defaultdict(list)
    for row in rows:
        if row["status"] in SUCCESS_STATUSES:
            by_domain[(row["domain"] or "unknown", row["condition"])].append(row["score_all_attempts"])
    for (domain, condition), values in sorted(by_domain.items()):
        lines.append(f"| {domain} | {condition} | {len(values)} | {fmt(mean_or_none(values))} |")
    lines += ["", "## Interaction behavior (means per episode)", "",
              "| Condition | Episodes | Handoffs | Revision requests | Researcher chars | Hypothesis chars | Numbers in hypothesis | API calls | Tokens | Cost (USD) |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for condition in sorted({r["condition"] for r in rows}, key=condition_order):
        subset = [r for r in rows if r["condition"] == condition]
        if subset:
            m = lambda k: mean_or_none([r[k] for r in subset])
            lines.append(f"| {condition} | {len(subset)} | {m('exchanges'):.2f} | {m('revision_requests'):.2f} | "
                         f"{m('researcher_chars'):.0f} | {fmt(m('hypothesis_chars'), 1, 0)} | "
                         f"{fmt(m('hypothesis_numbers'), 1, 1)} | {m('api_calls'):.1f} | "
                         f"{mean_or_none([r['prompt_tokens'] + r['completion_tokens'] for r in subset]):,.0f} | "
                         f"{m('cost_usd'):.4f} |")
    errors = [r for r in all_rows if r["status"] not in SUCCESS_STATUSES]
    lines += ["", "## Failures and retries", ""]
    lines += ([f"- `{r['key']}` (attempt {r['attempt']}): {r['status']}" for r in errors] or ["None."])
    lines += ["", f"Total cost ${sum(r['cost_usd'] for r in all_rows):.4f} (provider-reported where given, "
              f"otherwise tokens at list price) over "
              f"{sum(r['api_calls'] for r in all_rows)} API calls. Raw records: `episodes/`; per-episode rows: `results.csv`."]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n")
    if all_rows:
        with (output / "results.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]))
            writer.writeheader()
            writer.writerows(all_rows)
    summary = {"name": manifest["name"], "benchmark": manifest["benchmark"], "metric": metric,
               "git_revision": manifest.get("git_revision"), "config_sha256": manifest.get("config_sha256"),
               "models": manifest.get("models"), "arms": manifest.get("arms"),
               "statuses": dict(Counter(r["status"] for r in rows)), "aggregate": agg,
               "cost_usd": sum(r["cost_usd"] for r in all_rows)}
    write(output / "summary.json", summary)
    print(f"Wrote {output / 'REPORT.md'}, results.csv and summary.json ({len(all_rows)} attempts).")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    planning = commands.add_parser("plan", help="Validate, estimate and (without --dry-run) prepare a pilot")
    planning.add_argument("--config", type=Path, required=True)
    planning.add_argument("--output", type=Path)
    planning.add_argument("--dry-run", action="store_true", help="Print jobs and estimate; write nothing")
    planning.add_argument("--source-root", type=Path, default=ROOT / "external/sources")
    running = commands.add_parser("run", help="Execute planned episodes (paid model calls)")
    running.add_argument("--output", type=Path, required=True)
    running.add_argument("--parallel", type=int)
    running.add_argument("--yes", action="store_true", help="Confirm the paid run after reviewing the estimate")
    running.add_argument("--allow-provisional", action="store_true")
    running.add_argument("--retry-errors", action="store_true", help="Retry infrastructure failures once; keep originals")
    regrading = commands.add_parser("regrade", help="Re-grade sealed submissions whose native evaluator was killed (no model calls)")
    regrading.add_argument("--output", type=Path, required=True)
    reporting = commands.add_parser("report", help="Regenerate REPORT.md, results.csv and summary.json")
    reporting.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "plan":
            if not args.dry_run and args.output is None:
                parser.error("plan needs --output unless --dry-run")
            plan(args.config, args.output, dry_run=args.dry_run, source_root=args.source_root)
        elif args.command == "run":
            run(args.output.resolve(), parallel=args.parallel, yes=args.yes,
                allow_provisional=args.allow_provisional, retry_errors=args.retry_errors)
            report(args.output.resolve())
        elif args.command == "regrade":
            regrade(args.output.resolve())
            report(args.output.resolve())
        else:
            report(args.output.resolve())
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
