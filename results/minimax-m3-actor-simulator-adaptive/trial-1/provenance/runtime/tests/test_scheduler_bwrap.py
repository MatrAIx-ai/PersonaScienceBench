"""The batch scheduler's Bubblewrap selection is portable across hosts; no processes are started."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_persona_benchmarks import bubblewrap_environment  # noqa: E402


def test_explicit_override_always_wins(tmp_path):
    local = tmp_path / "bwrap"
    local.write_text("")
    env = bubblewrap_environment({"PERSONASCIENCEBENCH_BWRAP": "/opt/custom/bwrap"}, local)
    assert env["PERSONASCIENCEBENCH_BWRAP"] == "/opt/custom/bwrap"


def test_historical_local_build_is_used_only_where_it_exists(tmp_path):
    local = tmp_path / "bwrap"
    assert "PERSONASCIENCEBENCH_BWRAP" not in bubblewrap_environment({}, local)  # system bwrap
    local.write_text("")
    assert bubblewrap_environment({}, local)["PERSONASCIENCEBENCH_BWRAP"] == str(local)
