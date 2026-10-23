"""Build, verify and install a fresh results directory without inference."""
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

sys.dont_write_bytecode = True
import export_fable_bundle as export
import package_provenance as provenance
from materialize_bundle import Bundle
from verify_bundle import verify


def check_readme(text, delivery):
    labels = {
        "Scored submission": "scored", "Legitimate missing submission": "missing_submission",
        "Actor refusal": "actor_refusal", "Simulator refusal before any actor response": "simulator_refusal_pre_actor",
        "Simulator refusal after actor responses": "simulator_refusal_mid_episode",
        "Actor response hit 32,768 tokens": "actor_token_limit",
        "Completed actor submission; grading pending": "grading_pending",
    }
    table = {}
    for line in text.splitlines():
        if line.startswith("|"):
            fields = [field.strip() for field in line.split("|")]
            if fields[1] in labels:
                table[labels[fields[1]]] = int(fields[2])
    assert set(delivery["counts"]) <= set(labels.values())
    assert table == {status: delivery["counts"].get(status, 0) for status in labels.values()}, \
        "README table differs from the verified data"
    assert f'**{delivery["numeric_scores"]} slots have numeric primary scores:' in text
    assert delivery["judge_cap_amendment_state"] == "run", "README describes an executed judge amendment"
    assert "**250 to 4,096 tokens was approved and applied**" in text
    assert delivery["grading_pending"] == 0 and "no grades remain pending" in text
    assert "All seven remaining grades recovered." in text
    verification = export.read(export.OUT / "provenance/recovery/judge_cap4096_verification.json")
    assert verification["approved_slots"] == verification["recovered_slots"] == 7
    assert verification["actor_reruns"] == 0
    for reference in re.findall(r"`(provenance/[^`]+)`", text):
        if "*" in reference:
            assert list(export.OUT.glob(reference)), reference
        else:
            assert (export.OUT / reference).exists(), reference
    assert not delivery["checkpoint"] and not delivery["infrastructure_unresolved"]


def manifest(directory):
    files = {str(path.relative_to(directory)): {"bytes": path.stat().st_size,
                                              "sha256": export.sha(path.read_bytes())}
             for path in sorted(directory.rglob("*")) if path.is_file() and path.name != "bundle_manifest.json"}
    (directory / "bundle_manifest.json").write_bytes(export.raw_json({
        "schema_version": 1, "hash_algorithm": "sha256", "files": files}))


def main():
    target = export.OUT
    build_parent = Path(tempfile.mkdtemp(prefix=".delivery-build-", dir=export.DELIVERY_REPO))
    build = build_parent / "trial-1"
    export.OUT = provenance.OUT = build
    export.export()
    provenance.main()
    for name in ("materialize_bundle.py", "verify_bundle.py"):
        shutil.copyfile(export.ROOT / name, build / name)
    shutil.copyfile(export.ROOT / "README.delivery.md", build / "README.md")
    shutil.copyfile(export.ROOT / "README.delivery.md", build / "provenance/recovery-source/README.delivery.md")
    check_readme((build / "README.md").read_text(), export.read(build / "delivery.json"))
    logical = export.read(build / "logical_files.json")
    parts = {part["path"] for item in logical.values() for part in item["parts"]}
    for path in list(build.rglob("*")):
        if path.is_file() and str(path.relative_to(build)) not in parts and path.name != "logical_files.json":
            export.split_large(path, logical)
    export.write("logical_files.json", logical)
    manifest(build)
    report = verify(Bundle(build), export.RUN)
    export.write("provenance/verification.json", {
        **report, "verified_at": datetime.now(timezone.utc).isoformat(),
        "physical_file_count_scope": "Excludes this subsequently written verification receipt and bundle_manifest.json itself.",
        "native_source_comparison": "Every archived native file, artifact and shared/tool event compared with the retained original run.",
        "verifier_sha256": export.sha((build / "verify_bundle.py").read_bytes()),
        "materializer_sha256": export.sha((build / "materialize_bundle.py").read_bytes()),
    })
    manifest(build)
    spec = importlib.util.spec_from_file_location("repository_audit", export.DELIVERY_REPO / "scripts/audit_result_bundles.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.audit(build)
    if target.exists():
        previous = export.BASE / ("delivery-before-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S"))
        target.rename(previous)
    target.parent.mkdir(parents=True, exist_ok=True)
    build.rename(target)
    build_parent.rmdir()
    result = audit.audit(target)
    print(json.dumps({"delivered_directory": str(target), "verification": report, "repository_audit": result}, indent=2))


if __name__ == "__main__":
    main()
