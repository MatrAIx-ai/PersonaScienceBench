#!/usr/bin/env python3
"""Render the ten largest absolute paired score deviations per benchmark and their evidence."""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from personasciencebench.arms import PERSONA, arm_kind, is_control
from summarize_persona_benchmark_scores import normalized


def read(path):
    return json.loads(path.read_text())


def link(path, parent):
    return os.path.relpath(path, parent).replace(os.sep, "/")


@lru_cache(maxsize=None)
def simulator_behavior(trace, benchmark):
    if not trace:
        return {"words_per_reply": None, "revision_requests": None}
    case = Path(trace).parent
    path = next((p for p in (case / "controller/events.jsonl", case / "events.jsonl") if p.is_file()), None)
    if path is None:
        return {"words_per_reply": None, "revision_requests": None}
    events = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    decisions = [e["payload"] for e in events if e["type"] == "researcher_decision"]
    if benchmark == "sciconvbench":
        messages = [e["payload"]["answer"] for e in events if e["type"] == "researcher_reply"]
        revisions = None  # Native clarification has no result-review revision stage.
    else:
        messages = [d.get("message", "") for d in decisions
                    if d.get("phase") != "initial_inspection" and d.get("interaction") != "initial_request"]
        revisions = sum(d.get("phase") == "result_review" and d.get("action") == "continue" for d in decisions) if decisions else None
    return {"words_per_reply": sum(len(m.split()) for m in messages) / len(messages) if messages else None,
            "revision_requests": revisions}


def mean_or_none(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def persona_score(row):
    score = normalized(row)
    return 0.0 if score is None and row["status"] == "missing_submission" else score


def benchmark_rankings(episodes, personas):
    """Rank personas separately per benchmark over the tasks that every persona and the control mean can score."""
    personas = [p for p in personas if arm_kind(p) == PERSONA]
    controls, lookup = defaultdict(list), {}
    for r in episodes:
        if is_control(r["arm"]):
            controls[r["task"]].append(r)
        lookup[r["arm"], r["task"]] = r
    result = {}
    for benchmark in sorted({r["benchmark"] for r in episodes}):
        tasks = sorted({r["task"] for r in episodes if r["benchmark"] == benchmark})
        common = [t for t in tasks if mean_or_none(normalized(c) for c in controls[t]) is not None
                  and all((p, t) in lookup and persona_score(lookup[p, t]) is not None for p in personas)]
        rows = []
        for persona in personas if common else []:
            on = sum(persona_score(lookup[persona, t]) for t in common) / len(common)
            off = sum(mean_or_none(normalized(c) for c in controls[t]) for t in common) / len(common)
            rows.append({"persona": persona, "benchmark": benchmark, "score_average": on,
                         "paired_baseline_average": off, "deviation": on - off,
                         "comparable_pairs": len(common), "benchmark_tasks": len(tasks)})
        rows.sort(key=lambda r: (-abs(r["deviation"]), r["persona"]))
        result[benchmark] = {"tasks": tasks, "common_tasks": common, "rankings": rows}
    return result, controls


def matched_behavior(pairs, controls, metric):
    values = [(simulator_behavior(r.get("trace"), r["benchmark"])[metric],
               mean_or_none(simulator_behavior(c.get("trace"), r["benchmark"])[metric] for c in controls[r["task"]]))
              for r in pairs]
    values = [(a, b) for a, b in values if a is not None and b is not None]
    if not values:
        return None
    on, off = (sum(v[i] for v in values) / len(values) for i in (0, 1))
    return {"on": on, "off": off, "delta": on - off, "task_count": len(values)}


def format_behavior(value):
    if value is None:
        return "—"
    return f"{value['on']:.2f} / {value['off']:.2f} (Δ {value['delta']:+.2f}; n={value['task_count']})"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--ranking", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run, output = args.run.resolve(), args.output.resolve()
    ranking = read(args.ranking)
    episodes = read(run / "comparison.json")["episodes"]
    excluded = {"candidate_009"}
    personas = sorted(r["persona"] for r in ranking["rankings"] if r["persona"] not in excluded)
    benchmarks, controls = benchmark_rankings(episodes, personas)
    common = {t for b in benchmarks.values() for t in b["common_tasks"]}
    control_counts = sorted({len(v) for v in controls.values()})
    profiles_dir, traces_dir = output.parent / "profiles", output.parent / "trace_indexes"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Ten personas with the largest absolute performance change per benchmark", "",
        "Ranked separately for each benchmark by absolute mean task-paired score difference from persona off, "
        "using only that benchmark's tasks on which every displayed persona and the persona-off control are "
        "comparable. Scores are never averaged across benchmarks. The signed difference is shown in percentage "
        "points on the normalized 0–1 score. Positive means higher observed performance; negative means lower. "
        "These are descriptive associations, not causal effect estimates.", "",
        "Performance uses the existing ranking policy: persona-side missing submissions count as zero; "
        "unscorable pairs are excluded. Persona off is the per-task mean over "
        + ("/".join(map(str, control_counts)) or "no") + " control run(s). Candidate 009 is excluded from "
        "this display because of its low comparable coverage.", "",
        "Interaction turns are mean actor–simulator exchanges per case on the same task pairs used "
        "for that persona’s performance difference. One exchange is an actor handoff with simulator "
        "response, including required reviews; SciConv uses native clarification Q&A. Tool calls are "
        "not counted. The table gives persona on / matched persona off.", "",
        "Simulator words/reply counts whitespace-separated words in shared reply text only, excluding "
        "the initial request, private evidence fields, and tool output. Reply lengths are averaged "
        "within each task, then equally across matched tasks. Revision requests count result-review "
        "decisions to continue work; initial inspection and approach approval are excluded. SciConv "
        "has no result-review revision stage, so it is omitted from that metric, not scored zero. "
        "Each added column shows on / off, the paired change (Δ), and its task count (n). "
        "Clarification intent and persona adherence are not inferred from these structural counts.", "",
        "Profile links contain the complete recorded persona configuration and exact rendered identity "
        "prompt injected into the simulator. Task facts and common system instructions are separate; "
        "the full available prompts are in the traces. Trace indexes cover all scheduled tasks, including "
        "excluded tasks. Raw trace links require the local retained run directory and are unavailable "
        "in a GitHub-only checkout.", "",
    ]
    records, written = [], {}
    for benchmark, block in benchmarks.items():
        lines += [f"## {benchmark}", ""]
        if not block["rankings"]:
            lines += ["No task is comparable for every persona and the control.", ""]
            continue
        lines += [f"Common tasks ({len(block['common_tasks'])}/{len(block['tasks'])}): "
                  + ", ".join(f"`{t}`" for t in block["common_tasks"]) + ".", "",
                  "| Persona / full injected profile | Performance difference vs off | Interaction traces | Mean interaction turns: on / off | Simulator words/reply: on / off | Revision requests/task: on / off |",
                  "|---|---:|---|---:|---:|---:|"]
        for row in block["rankings"][:10]:
            arm = row["persona"]
            profile_path, index_path = profiles_dir / f"{arm}.md", traces_dir / f"{arm}.md"
            if arm not in written:
                written[arm] = write_arm(run, arm, episodes, controls, common, profile_path, index_path, output, profiles_dir, traces_dir)
            pairs = [r for r in episodes if r["arm"] == arm and r["task"] in block["common_tasks"]]
            on = sum(r["behavior"]["exchanges"] for r in pairs) / len(pairs)
            off = sum(mean_or_none(c["behavior"]["exchanges"] for c in controls[r["task"]]) for r in pairs) / len(pairs)
            words = matched_behavior(pairs, controls, "words_per_reply")
            revisions = matched_behavior(pairs, controls, "revision_requests")
            available, scheduled = written[arm]
            lines.append(f"| [{arm}]({link(profile_path, output.parent)}) | {row['deviation'] * 100:+.2f} pp "
                         f"({len(pairs)}/{len(block['tasks'])} tasks) | [Task traces]({link(index_path, output.parent)}) "
                         f"({available}/{scheduled} available) | {on:.2f} / {off:.2f} | {format_behavior(words)} | {format_behavior(revisions)} |")
            records.append({**row, "mean_turns_on": on, "mean_turns_off": off,
                            "simulator_words_per_reply": words, "revision_requests_per_task": revisions,
                            "turns_task_count": len(pairs), "available_traces": available,
                            "profile": link(profile_path, output.parent), "trace_index": link(index_path, output.parent)})
        lines.append("")
    output.write_text("\n".join(lines) + "\n")
    output.with_suffix(".json").write_text(json.dumps({
        "selection": "top 10 per benchmark by absolute task-paired normalized performance deviation on that benchmark's common tasks",
        "excluded_personas": sorted(excluded),
        "interaction_denominator": "same task pairs as each persona's performance difference",
        "control_runs_per_task": control_counts,
        "common_tasks": {b: v["common_tasks"] for b, v in benchmarks.items()},
        "personas": records,
    }, indent=2) + "\n")


def write_arm(run, arm, episodes, controls, common, profile_path, index_path, output, profiles_dir, traces_dir):
    persona = read(run / "configs" / arm / "persona.private.json")
    profile_path.write_text("\n".join([
        f"# {arm}: full persona injection", "",
        "Recorded from the retained experiment configuration. The identity below conditions only "
        "the simulator; it is not injected into the actor or judge. The record includes every "
        "injected action rule and the renderer’s fixed boundaries. It does not include separate "
        "task-specific knowledge or shared protocol instructions.", "",
        f"[Source record]({link(run / 'configs' / arm / 'persona.private.json', profiles_dir)}) · "
        f"[Task traces]({link(index_path, profiles_dir)})", "",
        "## Exact rendered identity prompt", "", "```text", persona["identity_prompt"], "```", "",
        "## Complete recorded persona configuration", "", "```json", json.dumps(persona, indent=2), "```", "",
    ]))
    arm_rows = sorted((r for r in episodes if r["arm"] == arm), key=lambda r: r["task"])
    detail = [f"# {arm}: task traces and interactions", "",
              f"[Full injected profile]({link(profile_path, traces_dir)}) · "
              f"[Top-ten tables]({link(output, traces_dir)})", "",
              "All retained tasks are listed. Unavailable means the recorded trace file "
              "is absent; a status alone does not establish that its metrics or raw evidence "
              "survived cleanup. Turns on tasks outside a benchmark's common set are not used in its top-ten mean. "
              "A dash means that no readable trace is available to support the recorded count. "
              "Off values are means over the available persona-off control runs.", "",
              "Words/reply excludes the initial request and private fields. Revisions are result-review "
              "requests for further work; SciConv revisions are not applicable (—). All metrics show on / off.", "",
              "| Task | Status | Used in score difference | Persona trace | Off trace | Turns on / off | Simulator words/reply | Revision requests |",
              "|---|---|---|---|---|---:|---:|---:|"]
    available = 0
    for r in arm_rows:
        bases = controls[r["task"]]
        path = Path(r["trace"]) if r.get("trace") else None
        exists = path is not None and path.is_file()
        available += exists
        base_paths = [Path(b["trace"]) if b.get("trace") else None for b in bases]
        base_exists = [p is not None and p.is_file() for p in base_paths]
        links = [f"[Read]({link(path, traces_dir)})" if exists else "Unavailable",
                 ", ".join(f"[Read]({link(p, traces_dir)})" if ok else "Unavailable"
                           for p, ok in zip(base_paths, base_exists)) or "Unavailable"]
        off_turns = mean_or_none(b["behavior"]["exchanges"] for b, ok in zip(bases, base_exists) if ok)
        turns = [str(r["behavior"]["exchanges"]) if exists else "—", "—" if off_turns is None else f"{off_turns:g}"]
        behaviors = [simulator_behavior(r.get("trace"), r["benchmark"]),
                     {k: mean_or_none(simulator_behavior(b.get("trace"), r["benchmark"])[k] for b in bases)
                      for k in ("words_per_reply", "revision_requests")}]
        extra = [" / ".join(f"{b[k]:.2f}" if b[k] is not None else "—" for b in behaviors)
                 for k in ("words_per_reply", "revision_requests")]
        detail.append(f"| `{r['task']}` | {r['status']} | {'Yes' if r['task'] in common else 'No'} | "
                      f"{links[0]} | {links[1]} | {turns[0]} / {turns[1]} | {extra[0]} | {extra[1]} |")
    index_path.write_text("\n".join(detail) + "\n")
    return available, len(arm_rows)


if __name__ == "__main__":
    main()
