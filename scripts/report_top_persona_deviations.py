#!/usr/bin/env python3
"""Render the ten largest absolute paired score deviations and their evidence."""
from __future__ import annotations

import argparse
import json
import os
from functools import lru_cache
from pathlib import Path

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


def matched_behavior(pairs, controls, metric):
    values = [(simulator_behavior(r.get("trace"), r["benchmark"])[metric],
               simulator_behavior(controls[r["task"]].get("trace"), r["benchmark"])[metric]) for r in pairs]
    values = [(a, b) for a, b in values if a is not None and b is not None]
    assert values, metric
    on, off = (sum(v[i] for v in values) / len(values) for i in (0, 1))
    return {"on": on, "off": off, "delta": on - off, "task_count": len(values)}


def format_behavior(value):
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
    controls = {r["task"]: r for r in episodes if r["arm"] == "persona_off"}
    excluded = {"candidate_009"}
    selected = sorted((r for r in ranking["rankings"] if r["persona"] not in excluded),
                      key=lambda r: (-abs(r["deviation"]), r["persona"]))[:10]
    profiles_dir, traces_dir = output.parent / "profiles", output.parent / "trace_indexes"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Ten personas with the largest absolute performance change", "",
        "Ranked by absolute mean task-paired score difference from persona off across the five retained "
        "benchmarks. The signed difference is shown in percentage points on the normalized 0–1 score. "
        "Positive means higher observed performance; negative means lower. These are descriptive "
        "single-run associations, not causal effect estimates.", "",
        "Performance uses the existing ranking policy: persona-side missing submissions count as zero; "
        "unscorable pairs are excluded. Nine of ten control tasks are scoreable. Candidate 009 is "
        "excluded from this display because it has only 6/9 comparable tasks. All ten displayed "
        "profiles have 9/9 comparable tasks.", "",
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
        "the full available prompts are in the traces. Trace indexes cover all ten tasks, including "
        "excluded tasks. Raw trace links require the local retained run directory and are unavailable "
        "in a GitHub-only checkout.", "",
        "| Persona / full injected profile | Performance difference vs off | Interaction traces | Mean interaction turns: on / off | Simulator words/reply: on / off | Revision requests/task: on / off |",
        "|---|---:|---|---:|---:|---:|",
    ]
    records = []
    for row in selected:
        arm = row["persona"]
        persona = read(run / "configs" / arm / "persona.private.json")
        profile_path = profiles_dir / f"{arm}.md"
        profile_path.write_text("\n".join([
            f"# {arm}: full persona injection", "",
            "Recorded from the retained experiment configuration. The identity below conditions only "
            "the simulator; it is not injected into the actor or judge. The record includes every "
            "injected action rule and the renderer’s fixed boundaries. It does not include separate "
            "task-specific knowledge or shared protocol instructions.", "",
            f"[Source record]({link(run / 'configs' / arm / 'persona.private.json', profiles_dir)}) · "
            f"[Task traces]({link(traces_dir / (arm + '.md'), profiles_dir)})", "",
            "## Exact rendered identity prompt", "", "```text", persona["identity_prompt"], "```", "",
            "## Complete recorded persona configuration", "", "```json", json.dumps(persona, indent=2), "```", "",
        ]))
        arm_rows = sorted((r for r in episodes if r["arm"] == arm), key=lambda r: r["task"])
        pairs = [r for r in arm_rows if normalized(controls[r["task"]]) is not None
                 and (normalized(r) is not None or r["status"] == "missing_submission")]
        assert len(pairs) == row["comparable_pairs"], arm
        on = sum(r["behavior"]["exchanges"] for r in pairs) / len(pairs)
        off = sum(controls[r["task"]]["behavior"]["exchanges"] for r in pairs) / len(pairs)
        words = matched_behavior(pairs, controls, "words_per_reply")
        revisions = matched_behavior(pairs, controls, "revision_requests")
        index_path = traces_dir / f"{arm}.md"
        detail = [f"# {arm}: task traces and interactions", "",
                  f"[Full injected profile]({link(profile_path, traces_dir)}) · "
                  f"[Top-ten table]({link(output, traces_dir)})", "",
                  "All ten retained tasks are listed. Unavailable means the recorded trace file "
                  "is absent; a status alone does not establish that its metrics or raw evidence "
                  "survived cleanup. Turns on excluded tasks are not used in the top-ten mean. "
                  "A dash means that no readable trace is available to support the recorded count.", "",
                  "Words/reply excludes the initial request and private fields. Revisions are result-review "
                  "requests for further work; SciConv revisions are not applicable (—). All metrics show on / off.", "",
                  "| Task | Status | Used in score difference | Persona trace | Off trace | Turns on / off | Simulator words/reply | Revision requests |",
                  "|---|---|---|---|---|---:|---:|---:|"]
        available = 0
        for r in arm_rows:
            base = controls[r["task"]]
            paths = [Path(x["trace"]) if x.get("trace") else None for x in (r, base)]
            exists = [p is not None and p.is_file() for p in paths]
            available += exists[0]
            links = [f"[Read]({link(p, traces_dir)})" if ok else "Unavailable"
                     for p, ok in zip(paths, exists)]
            turns = [str(x["behavior"]["exchanges"]) if ok else "—" for x, ok in zip((r, base), exists)]
            behaviors = [simulator_behavior(x.get("trace"), x["benchmark"]) for x in (r, base)]
            extra = [" / ".join(f"{b[k]:.2f}" if b[k] is not None else "—" for b in behaviors)
                     for k in ("words_per_reply", "revision_requests")]
            detail.append(f"| `{r['task']}` | {r['status']} | {'Yes' if r in pairs else 'No'} | "
                          f"{links[0]} | {links[1]} | {turns[0]} / {turns[1]} | {extra[0]} | {extra[1]} |")
        index_path.write_text("\n".join(detail) + "\n")
        lines.append(f"| [{arm}]({link(profile_path, output.parent)}) | {row['deviation'] * 100:+.2f} pp "
                     f"({len(pairs)}/9 tasks) | [Task traces]({link(index_path, output.parent)}) "
                     f"({available}/10 available) | {on:.2f} / {off:.2f} | {format_behavior(words)} | {format_behavior(revisions)} |")
        records.append({**row, "mean_turns_on": on, "mean_turns_off": off,
                        "simulator_words_per_reply": words, "revision_requests_per_task": revisions,
                        "turns_task_count": len(pairs), "available_traces": available,
                        "profile": link(profile_path, output.parent), "trace_index": link(index_path, output.parent)})
    output.write_text("\n".join(lines) + "\n")
    output.with_suffix(".json").write_text(json.dumps({
        "selection": "top 10 by absolute task-paired normalized performance deviation",
        "excluded_personas": sorted(excluded),
        "interaction_denominator": "same task pairs as each persona's performance difference",
        "personas": records,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
