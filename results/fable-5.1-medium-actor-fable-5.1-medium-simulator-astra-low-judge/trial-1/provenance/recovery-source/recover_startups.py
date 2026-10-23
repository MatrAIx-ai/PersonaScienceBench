"""Retry the nine audited startup throttles under the original configuration."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / "checkout"
RUN = ROOT.parent / "actor32768/run"


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan():
    inventory = json.loads((ROOT / "failure_inventory.json").read_text())
    rows = [r for r in inventory if r["category"] == "startup_throttled"]
    if len(rows) != 9:
        raise ValueError("Expected the nine independently audited startup failures")
    commands = []
    for item in rows:
        path = Path(item["state_path"])
        if not path.resolve().is_relative_to(RUN / "episodes"):
            raise ValueError("State path escapes the campaign")
        old = json.loads(path.read_text())
        if old["status"] != "infrastructure_error" or old["attempt"] != item["attempt"]:
            raise ValueError("Audited state changed; inspect before rerunning")
        if old.get("native_results"):
            raise ValueError("This repair is restricted to failed startup preflights")
        if "GetInferenceProfile" not in (path.parent / "attempt-1/process.log").read_text():
            raise ValueError("Missing recorded preflight throttle")
        base = path.parent
        attempt = base / "attempt-2"
        if attempt.exists():
            raise ValueError("Attempt already exists; never overwrite a repair")
        prepared = RUN / "prepared" / base.parent.name
        source = old["source"]
        config = RUN / "configs" / f'{old["arm"]}.{"exp" if source == "expbench" else "shared"}.json'
        output = attempt / "output"
        command = [str(REPO / ".venv/bin/python"), "-m"]
        if source == "expbench":
            command += ["expbench.realistic", "run", "--mode", "live", "--tasks",
                        str(prepared / "tasks.jsonl"), "--config", str(config),
                        "--output", str(output), "--env-file", str(REPO / ".env"),
                        "--parallel", "1"]
        elif source == "sciconvbench":
            command += ["personasciencebench.sciconv_runner", "--prepared", str(prepared),
                        "--output", str(output), "--config", str(config), "--parallel", "1"]
        else:
            command += ["personasciencebench.cli", "--source-root", str(REPO / "external/sources"),
                        "run", "--prepared", str(prepared), "--benchmarks", source,
                        "--output", str(output), "--actor-python", str(REPO / ".actor-venv"),
                        "--config", str(config), "--parallel", "1"]
        commands.append((path, old, attempt, config, command))
    return commands


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    options = parser.parse_args()
    os.umask(0o077)
    commands = plan()
    if not options.execute:
        print(json.dumps({"slots": len(commands), "workers": 3,
                          "sources": dict(Counter(old["source"] for _, old, *_ in commands)),
                          "commands": [cmd for *_, cmd in commands]}, indent=2))
        return 0
    lock = (RUN / "coordinator.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (RUN / "fatal_api.json").exists():
        raise RuntimeError("Resolve the fatal API marker before retrying")
    original_launch = json.loads((RUN.parent / "pilot_launch.json").read_text())
    os.environ.update(original_launch["nonsecret_environment_overrides"])
    os.environ["PSB_FATAL_API_FILE"] = str(RUN / "fatal_api.json")
    if os.environ.get("PSB_MACHINE_POLICY") != "robert-20261003":
        raise RuntimeError("Required machine restrictions are not enabled")
    spec = importlib.util.spec_from_file_location("campaign_runner", REPO / "scripts/run_main.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    write(ROOT / "startup_recovery_plan.json", {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "policy": "Retry exactly nine startup throttles once; retain original attempts and all completed outcomes.",
        "workers": 3, "actor_cap": 32768, "researcher_cap": 8192,
        "machine_policy": "No JavaScript/TypeScript, no servers/listeners, no RLScience cluster.",
        "transport_sha256": sha(REPO / "src/personasciencebench/bedrock_transport.py"),
        "script_sha256": sha(Path(__file__)),
        "slots": [{k: old[k] for k in ("source", "task_id", "arm")} for _, old, *_ in commands],
    })

    def one(item):
        path, old, attempt, config, command = item
        if (RUN / "fatal_api.json").exists():
            raise RuntimeError("Fatal API marker appeared; stopped before another episode")
        write(path.parent / "attempt-1/state_snapshot.json", old)
        attempt.mkdir()
        state = {k: v for k, v in old.items()
                 if k not in ("native_results", "returncode", "finished_at", "result_read_error")}
        state.update(attempt=2, status="running", started_at=time.time(),
                     repair_reason="GetInferenceProfile startup throttle; original settings, bounded SDK backoff.")
        write(path, state)
        write(attempt / "repair_provenance.json", {
            "command": command, "source_attempt": 1, "config_sha256": sha(config),
            "reason": state["repair_reason"], "preflight_retry_mode": "standard",
            "preflight_total_max_attempts": 8,
        })
        try:
            with (attempt / "process.log").open("x") as log:
                process = subprocess.run(command, cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
            native = runner.load_native_result(attempt / "output", old["source"],
                                               old["task_id"], path.parent.parent.name)
            status = "infrastructure_error" if (
                process.returncode or not native
                or any(r.get("status") in ("infrastructure_error", "runtime_error", "error") for r in native)
            ) else "finished"
            state.update(returncode=process.returncode, native_results=native, status=status)
        except Exception as error:
            state.update(status="infrastructure_error", recovery_error=f"{type(error).__name__}: {error}")
        state["finished_at"] = time.time()
        write(path, state)
        write(attempt / "state_snapshot.json", state)
        print(json.dumps({k: state[k] for k in ("source", "task_id", "arm", "attempt", "status")}), flush=True)
        return state

    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(one, item) for item in commands]
        for future in as_completed(futures):
            results.append(future.result())
            write(ROOT / "startup_recovery_progress.json",
                  {"processed": len(results), "planned": 9,
                   "statuses": dict(Counter(r["status"] for r in results))})
    write(ROOT / "startup_recovery_results.json", results)
    return int(any(r["status"] != "finished" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
