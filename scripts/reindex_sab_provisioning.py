#!/usr/bin/env python3
"""Narrow ScienceAgentBench evaluator dependencies in an existing full bundle."""

import json
from pathlib import Path

from personasciencebench.scienceagentbench_provision import refresh_evaluator_dependencies


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "external/sources/_assets/scienceagentbench/benchmark_verified"


if __name__ == "__main__":
    record = refresh_evaluator_dependencies(DESTINATION)
    counts = [len(value["dependencies"]) for value in record["reviewed_evaluators"].values()]
    print(json.dumps({"tasks": len(counts), "dependency_files": sum(counts),
                      "maximum_per_task": max(counts, default=0)}))
