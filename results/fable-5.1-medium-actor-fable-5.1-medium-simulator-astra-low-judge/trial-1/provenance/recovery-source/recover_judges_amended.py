"""Execute the seven-slot judge-only amendment after Robert's recorded approval."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import os
from pathlib import Path

import recover_judges_v2 as repair

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "judge_recovery_cap4096"


def verify_approval(approval, keys):
    assert approval["approved"] is True and approval["approver"] == "Robert"
    assert approval["remaining_native_judge_cap"] == 4096
    assert approval["source"] and approval["received_at"]
    assert approval["slots"] == [list(k) for k in sorted(keys)]
    for name, expected in approval["approved_file_sha256"].items():
        assert repair.digest((ROOT / name).read_bytes()) == expected
    assert set(approval["approved_file_sha256"]) == {
        "judge_cap_amendment_plan.json", "recover_judges_amended.py", "recover_judges_v2.py"}


def main():
    os.umask(0o077)
    previous = repair.read(ROOT / "judge_recovery/results.json")
    keys = {(r["source"], r["task_id"], r["arm"]) for r in previous if r["status"] == "judge_pending"}
    assert len(keys) == 7
    approval = repair.read(ROOT / "judge_cap_approval.json")
    verify_approval(approval, keys)
    assert not OUTPUT.exists()
    approval["approval_file_sha256"] = repair.digest((ROOT / "judge_cap_approval.json").read_bytes())
    inventory = repair.read(ROOT / "failure_inventory.json")
    rows = [r for r in inventory if (r["source"], r["task_id"], r["arm"]) in keys]
    assert len(rows) == 7
    os.environ.update(repair.read(repair.RUN.parent / "pilot_launch.json")["nonsecret_environment_overrides"])
    os.environ["PSB_FATAL_API_FILE"] = str(repair.RUN / "fatal_api.json")
    spec = repair.read(repair.RUN / "configs/persona_off.shared.json")["models"]["judge"]
    catalog = repair.preflight({"judge": spec})
    repair.OUT = OUTPUT
    OUTPUT.mkdir()
    repair.write(OUTPUT / "plan.json", {
        "approval": approval, "slots": [list(k) for k in sorted(keys)],
        "native_variable_relation_cap": 250, "remaining_variable_relation_cap": 4096,
        "judge_model": spec["model"], "reasoning_effort": "low",
        "reuse": "Exact ordered completed ORIGINAL prefix; each remaining call has one fresh invocation.",
        "policy": "No actor reruns. All original and unchanged-cap recovery records retained.",
        "restrictions": "No JavaScript/TypeScript, no servers/listeners, no RLScience cluster.",
    })
    results = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = {pool.submit(repair.one, row, catalog, approval): row for row in rows}
        for job in as_completed(jobs):
            try:
                result = job.result()
            except Exception as error:
                row = jobs[job]
                result = {key: row[key] for key in ("source", "task_id", "arm")}
                result.update(status="recovery_error", error=f"{type(error).__name__}: {error}",
                              recorded_at=datetime.now(timezone.utc).isoformat())
            results.append(result)
            repair.write(OUTPUT / "results.json", results)
    return int(any(r["status"] != "recovered" for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
