"""Package exact configuration/source evidence; no inference or external writes."""
from collections import Counter
import gzip
import io
import json
from pathlib import Path
import subprocess
import tarfile

import export_fable_bundle as bundle

BASE, ROOT, REPO, RUN, OUT = bundle.BASE, bundle.ROOT, bundle.REPO, bundle.RUN, bundle.OUT


def copy(source, name, normalize=False):
    raw = source.read_bytes()
    if normalize:
        # Validate the metadata boundary while retaining exact original bytes.
        # Reformatting/rebasing would break recorded config and amendment hashes.
        bundle.clean(json.loads(raw))
    bundle.checked(raw, str(source))
    target = OUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def source_archive():
    names = subprocess.check_output(["git", "diff", "HEAD", "--name-only", "--diff-filter=d"], cwd=REPO, text=True).splitlines()
    names += subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard",
                                      "src", "scripts", "tests"], cwd=REPO, text=True).splitlines()
    hashes = {}
    with tarfile.open(OUT / "provenance/recovery-runtime-source.tar.gz", "w:gz") as archive:
        for name in sorted(set(names)):
            path = REPO / name
            assert path.suffix in (".py", ".sh", ".json", ".md", ".txt")
            raw = bundle.checked(path.read_bytes(), name)
            info = tarfile.TarInfo(name)
            info.size, info.mode, info.mtime = len(raw), 0o600, 0
            archive.addfile(info, io.BytesIO(raw))
            hashes[name] = bundle.sha(raw)
    bundle.write("provenance/recovery-runtime-hashes.json", hashes)
    diff = subprocess.check_output(["git", "diff", "HEAD", "--binary"], cwd=REPO)
    (OUT / "provenance/recovery-runtime.patch").write_bytes(bundle.checked(diff, "runtime diff"))
    deletions = subprocess.check_output(["git", "diff", "HEAD", "--name-only", "--diff-filter=D"],
                                       cwd=REPO, text=True).splitlines()
    bundle.write("provenance/recovery-runtime-deletions.json", deletions)


def judge_history():
    history = []
    for directory in ["judge_recovery", "judge_recovery_cap4096"]:
        if not (ROOT / directory).is_dir():
            continue
        for name in ("plan.json", "results.json"):
            if (ROOT / directory / name).is_file():
                copy(ROOT / directory / name, f"provenance/recovery/{directory}/{name}", normalize=True)
        for inputs in sorted((ROOT / directory).glob("*/*/inputs.json")):
            copy(inputs, "provenance/recovery/" + str(inputs.relative_to(ROOT)), normalize=True)
        for path in sorted((ROOT / directory).glob("*/*/evaluation.json")):
            item = bundle.read(path)
            receipts = path.parent / "replay_receipts.jsonl"
            item["replay_receipts"] = [json.loads(line) for line in receipts.open()]
            item["cohort"] = directory
            item["fresh_native_calls"] = []
            wires = path.parent / "wire_calls.private.jsonl"
            if wires.exists():
                for line in wires.open():
                    call = json.loads(line)
                    raw, request = call["response"], call["request"]
                    item["fresh_native_calls"].append({
                        "requested_model": request["model"], "actual_model": raw["model"],
                        "reasoning": request["reasoning"], "cap": request["max_output_tokens"],
                        "status": raw["status"], "incomplete_details": raw.get("incomplete_details"),
                        "transport_retries": call["transport_retries"],
                        "usage": raw.get("usage"), "request_sha256": bundle.sha(json.dumps(request, ensure_ascii=False,
                            sort_keys=True, separators=(",", ":")).encode()),
                        "response_sha256": bundle.sha(json.dumps(raw, ensure_ascii=False,
                            sort_keys=True, separators=(",", ":")).encode()),
                    })
            history.append(bundle.clean(item))
    bundle.write_jsonl("provenance/judge-recovery-history.jsonl", history)


def excluded_pilots():
    old_run = BASE / "run"
    records = []
    with tarfile.open(OUT / "provenance/excluded-default-cap-pilots.tar.gz", "w:gz") as archive:
        for state_path in sorted((old_run / "episodes").glob("*/*/state.json")):
            state = bundle.read(state_path)
            config_path = old_run / "configs" / (state["arm"] + (".exp.json" if state["source"] == "expbench" else ".shared.json"))
            actor_config = bundle.read(config_path)["models"]["actor"]
            actor_cap = actor_config.get("max_tokens", actor_config.get("max_output_tokens"))
            assert actor_cap == 12288
            for attempt in sorted(state_path.parent.glob("attempt-*"), key=lambda p: int(p.name.split("-")[1])):
                if not attempt.is_dir():
                    continue
                key = bundle.safe(state["source"] + ":" + state["task_id"])
                case_name = state["task_id"].replace("/", "__") if state["source"] == "expbench" else key
                case = attempt / "output" / case_name
                events, events_hash, _ = bundle.shared_events(case)
                record = {"source": state["source"], "task_id": state["task_id"], "arm": state["arm"],
                          "attempt": int(attempt.name.split("-")[1]), "excluded_from_primary_trial": True,
                          "actor_cap": actor_cap, "config_sha256": bundle.sha(config_path.read_bytes()),
                          "shared_events": events, "source_event_sha256": events_hash,
                          "native_result": bundle.clean(bundle.read(case / "result.json")) if (case / "result.json").exists() else None,
                          "files": {}}
                paths = [case / name for name in [
                    "result.json", "evaluation.json", "actor_result.json", "initial_design.json",
                    "final_design.json", "controller/submission.json", "controller/submission_hashes.json"]]
                submission_path = case / "controller/submission.json"
                if submission_path.exists():
                    paths += [Path(p) for p in bundle.read(submission_path).get("artifacts", {}).values()]
                for path in paths:
                    if not path.is_file():
                        continue
                    assert path.resolve().is_relative_to(case.resolve()) and not path.is_symlink()
                    raw = bundle.checked(path.read_bytes(), str(path))
                    member = f'{key}/{state["arm"]}/{attempt.name}/{path.relative_to(case)}'
                    if member in record["files"]:
                        continue
                    info = tarfile.TarInfo(member)
                    info.size, info.mode, info.mtime = len(raw), 0o600, 0
                    archive.addfile(info, io.BytesIO(raw))
                    record["files"][member] = {"bytes": len(raw), "sha256": bundle.sha(raw)}
                records.append(record)
    bundle.write("provenance/excluded-default-cap-pilots.json", records)


def main():
    (OUT / "provenance").mkdir(parents=True, exist_ok=True)
    for name in ["manifest.json", "preparation_receipt.json", "api_access.json",
                 "campaign_amendment.json", "campaign_amendment.v2.json",
                 "campaign_amendment.v3.json", "campaign_amendment.v4.json"]:
        copy(RUN / name, "provenance/original/" + name, normalize=True)
    for path in sorted(RUN.glob("code.*.json")):
        copy(path, "provenance/original/" + path.name)
    for path in sorted((RUN / "configs").glob("*.json")):
        copy(path, "provenance/configs/" + path.name, normalize=True)
    for name in ["selection.csv"]:
        copy(RUN / name, "provenance/" + name)
    for path in sorted((REPO / "configs/main_run/personas").iterdir()):
        if path.is_file():
            copy(path, "provenance/personas/" + path.name)
    for name in ["sources.json"]:
        copy(REPO / "manifests" / name, "provenance/" + name)
    for name in ["pyproject.toml", "uv.lock"]:
        if (REPO / name).is_file():
            copy(REPO / name, "provenance/dependencies/" + name)
    for name in ["full_launch.json", "pilot_launch.json", "pilot_qualification.json",
                 "controller_environment.json", "collection_exit.json"]:
        copy(RUN.parent / name, "provenance/original/" + name, normalize=True)
    for path in (REPO / "configs/main_run/frozen/astra-20260929-v1").iterdir():
        if path.is_file():
            copy(path, "grading_inputs/frozen/" + path.name)
    for name in ["implementation-source-v2.tar.gz", "implementation-source-v3.tar.gz",
                 "implementation-v2.patch", "implementation-v3.patch"]:
        copy(BASE / name, "provenance/original/" + name)
    for path in sorted(ROOT.glob("*.py")):
        if path.name != "upstream_pr28_exporter.reference.py":
            copy(path, "provenance/recovery-source/" + path.name)
    for name in ["startup_recovery_plan.json", "startup_recovery_launch.json",
                 "startup_recovery_results.json", "judge_cap_amendment_plan.json",
                 "judge_cap_approval.json", "judge_cap4096_launch.json", "judge_cap4096_verification.json",
                 "verification_tests.json", "all_states.before.json"]:
        if (ROOT / name).is_file():
            copy(ROOT / name, "provenance/recovery/" + name, normalize=True)
    for path in sorted(ROOT.glob("current*-environment.json")):
        copy(path, "provenance/dependencies/" + path.name, normalize=True)
    source_archive()
    judge_history()
    excluded_pilots()
    metadata = []
    for path in sorted(ROOT.glob("opus_*.metadata.json")):
        data = bundle.read(path)
        metadata.append({k: v for k, v in data.items() if k not in ("review_path",)})
    bundle.write("provenance/review-models.json", {
        "reviews": metadata, "actual_review_model": "claude-opus-5-5",
        "notes": "Advice was checked against native logs and offline fixtures. Private reasoning and review prompts are excluded.",
    })
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    bundle.write("provenance/source-layout.json", {
        "base_repository": "MatrAIx-ai/PersonaScienceBench", "base_commit": commit,
        "original_runtime_overlay": "provenance/original/implementation-source-v3.tar.gz",
        "recovery_runtime_overlay": "provenance/recovery-runtime-source.tar.gz",
        "tracked_diff": "provenance/recovery-runtime.patch",
        "untracked_runtime_files": "Included in both source archives where applicable.",
        "path_variables": {"${REPO}": "checkout of the pinned repository with the required overlay",
                           "${RUN}": "restored frozen preparation and run directory",
                           "${CAMPAIGN}": "campaign control directory"},
        "original_text_paths": "Shared/tool event text, archived native files, configs, launch receipts and original amendments preserve original paths verbatim. Only derived summaries rebase paths. Use materialize_bundle.py to produce separate portable submission JSON.",
        "frozen_input_restoration": "Use the pinned scripts/restore_main_preparation.py after acquiring pinned assets; no preparation inference.",
        "restrictions": "No JavaScript/TypeScript, no servers/listeners, no RLScience cluster.",
        "pricing": "No verified dollar costs; native token counts retained.",
    })
    print(json.dumps({"provenance_packaged": True, "base_commit": commit}), flush=True)


if __name__ == "__main__":
    main()
