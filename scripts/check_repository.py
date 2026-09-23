"""Check distributable text without opening ignored credentials or run data."""

from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(r"(?:sk-or-v1-|ghp_)[A-Za-z0-9]{20,}")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
LOCAL_ONLY = {"runs", "prepared", "external", "data"}


def main():
    listed = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT
    ).decode().split("\0")
    errors = []
    checked = 0
    for relative in sorted(set(listed) - {""}):
        path = ROOT / relative
        # A moved/deleted tracked path remains in the index before staging.
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".py", ".json", ".toml", ".yaml", ".yml", ".txt"} and path.name != ".env.example":
            continue
        text = path.read_text()
        checked += 1
        if SECRET.search(text):
            errors.append(f"{relative}: possible credential (value withheld)")
        if path.suffix == ".md":
            for raw in LINK.findall(text):
                target = raw.strip().strip("<>")
                if target.startswith(("http:", "https:", "mailto:", "#")):
                    continue
                target = unquote(target.split("#", 1)[0])
                resolved = (path.parent / target).resolve()
                if not resolved.is_relative_to(ROOT):
                    errors.append(f"{relative}: link outside repository: {target}")
                    continue
                if resolved.relative_to(ROOT).parts[:1] and resolved.relative_to(ROOT).parts[0] in LOCAL_ONLY:
                    continue  # Explicitly documented local artifacts, absent in clean clones.
                if not resolved.exists():
                    errors.append(f"{relative}: missing local link: {target}")
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Checked {checked} distributable text files; {len(errors)} errors.")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
