"""Offline persona validation, prompt preview, and configuration attachment."""

import argparse
import json
from pathlib import Path

from .config import attach_profile
from .profiles import SciencePersona, profile_json_schema, profile_record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "render", "attach"):
        command = commands.add_parser(name)
        command.add_argument("--profile", required=True, type=Path)
        command.add_argument("--output", type=Path)
        if name == "attach":
            command.add_argument("--config", required=True, type=Path)
    command = commands.add_parser("schema")
    command.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "schema":
            result = profile_json_schema()
        else:
            profile = SciencePersona.model_validate_json(args.profile.read_text())
            if args.command == "validate":
                result = {"valid": True, "id": profile.id, "attributes": len(profile.attributes)}
            elif args.command == "render":
                result = profile_record(profile)
            else:
                result = attach_profile(json.loads(args.config.read_text()), profile)
        text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            # Input configs are never overwritten by the attachment command.
            with args.output.open("x", encoding="utf-8") as output:
                output.write(text)
        else:
            print(text, end="")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
