"""CLI client for actor environments; only the interaction endpoint is required."""

import argparse
import json
import os
import urllib.error
import urllib.request


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["context", "tools", "ask_researcher", "report_progress", "submit_plan", "submit_result"])
    parser.add_argument("--payload", default="{}", help="JSON object; stdin is read when '-' is given")
    args = parser.parse_args(argv)
    token = os.environ.get("PERSONASCIENCEBENCH_SESSION_TOKEN")
    endpoint = os.environ.get("PERSONASCIENCEBENCH_ENDPOINT")
    if not endpoint or not token:
        parser.error("Set PERSONASCIENCEBENCH_ENDPOINT and PERSONASCIENCEBENCH_SESSION_TOKEN")
    import sys
    payload = json.loads(sys.stdin.read() if args.payload == "-" else args.payload)
    get = args.operation in ("context", "tools")
    request = urllib.request.Request(endpoint.rstrip("/") + "/" + args.operation,
                                    data=None if get else json.dumps(payload).encode(),
                                    headers={"Authorization": "Bearer " + token,
                                             "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=400) as response:
            print(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"Researcher endpoint HTTP {exc.code}") from None


if __name__ == "__main__":
    main()
