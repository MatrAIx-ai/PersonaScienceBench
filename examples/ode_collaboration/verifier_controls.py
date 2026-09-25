"""CONTROLLER ONLY: create oracle/negative grader controls, never actor inputs.

These fixtures validate verifier wiring. They are not agent solutions or model
performance measurements. Keep their output outside every actor-visible mount.
"""

import argparse
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys


def create_controls(task: Path, output: Path):
    # Importing a pinned source helper must not create files in the source tree.
    sys.dont_write_bytecode = True
    output.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location("control_checker", task / "tests/submission_checker.py")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    reference = json.loads((task / "tests/hidden_reference.json").read_text())
    for label in ("positive_oracle_control", "negative_control"):
        dest = output / label
        dest.mkdir()
        eqs = reference["equations"] if label.startswith("positive") else {"x": "-x", "y": "-y", "z": "-z"}
        complexity = {v: checker.symbolic_complexity(checker.parse_expression(eqs[v])) for v in ("x", "y", "z")}
        complexity["total"] = sum(complexity.values())
        (dest / "equations.json").write_text(json.dumps({
            "state_variables": ["x", "y", "z"], "time_variable": "t", "equations": eqs,
            "parameters": {}, "complexity": complexity}, indent=2))
        if label.startswith("positive"):
            shutil.copyfile(task / "tests/hidden_test_trajectories.csv", dest / "predictions.csv")
        else:
            metadata = json.loads((task / "environment/data/metadata.json").read_text())
            with (task / "environment/data/test_initial_conditions.csv").open() as stream:
                initials = list(csv.DictReader(stream))
            with (dest / "predictions.csv").open("w") as stream:
                writer = csv.writer(stream)
                writer.writerow(["trajectory_id", "time", "x", "y", "z"])
                for row in initials:
                    for i in range(metadata["num_time_points"]):
                        writer.writerow([row["trajectory_id"], metadata["time_start"]+i*metadata["dt"], 0, 0, 0])
        (dest / "report.md").write_text(f"# {label}\n\nController-only verifier fixture; not an agent-produced scientific result.\n")
    print("Created controller-only fixtures; no equations or private values printed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    create_controls(args.task, args.output)
