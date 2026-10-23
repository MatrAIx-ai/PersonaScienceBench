#!/usr/bin/env python3
"""Verify and restore this delivery offline. Never run actors, graders, or servers."""
import argparse
from collections import Counter
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def safe(root, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or ".." in name.parts or "\\" in relative or relative in ("", "."):
        raise ValueError(f"Unsafe relative path: {relative!r}")
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes directory: {relative!r}")
    return path


def check(raw, metadata, label):
    if len(raw) != metadata["bytes"] or sha(raw) != metadata["sha256"]:
        raise ValueError(f"Size or SHA-256 mismatch: {label}")
    return raw


def slot(row):
    return (row.get("benchmark", row.get("source")), row["task_id"], row["arm"])


def attempt_key(row):
    return (*slot(row), int(row["attempt"]))


class Bundle:
    def __init__(self, root):
        self.root = root.resolve()
        self.receipt = json.loads((self.root / "bundle_manifest.json").read_text())
        self.logical = json.loads((self.root / "logical_files.json").read_text())

    def physical(self):
        files = self.receipt["files"]
        for name, metadata in files.items():
            check(safe(self.root, name).read_bytes(), metadata, name)
        actual = {str(p.relative_to(self.root)) for p in self.root.rglob("*")
                  if p.is_file() and p.name != "bundle_manifest.json" and "__pycache__" not in p.parts}
        if actual != set(files):
            raise ValueError(f"Physical file inventory mismatch: {actual ^ set(files)}")
        return len(files)

    def raw(self, name):
        if name not in self.logical:
            return check(safe(self.root, name).read_bytes(), self.receipt["files"][name], name)
        item = self.logical[name]
        parts = [check(safe(self.root, p["path"]).read_bytes(), p, p["path"]) for p in item["parts"]]
        encoded = b"".join(parts)
        if sha(encoded) != item["encoded_sha256"]:
            raise ValueError(f"Encoded checksum mismatch: {name}")
        if item["encoding"] not in ("gzip", "identity"):
            raise ValueError(f"Unknown encoding: {name}")
        raw = gzip.decompress(encoded) if item["encoding"] == "gzip" else encoded
        return check(raw, item, name)

    def json(self, name):
        return json.loads(self.raw(name))

    def jsonl(self, name):
        return [json.loads(line) for line in self.raw(name).splitlines()]

    def csv(self, name):
        return list(csv.DictReader(io.StringIO(self.raw(name).decode())))

    def submissions(self, destination=None):
        rows = self.jsonl("submissions/manifest.jsonl")
        if len({attempt_key(r) for r in rows}) != len(rows):
            raise ValueError("Duplicate submission attempt key")
        refs = {}
        for row in rows:
            entries = list(row["files"].values()) + list(row["artifacts"].values())
            entries += [row[k] for k in ("submission", "initial_design", "final_design") if row[k]]
            for entry in entries:
                pair = entry["archive"], entry["member"]
                if pair in refs and refs[pair] != entry:
                    raise ValueError("Conflicting archive reference")
                refs[pair] = entry
        seen = set()
        for archive_name in sorted({a for a, _ in refs}):
            with tarfile.open(fileobj=io.BytesIO(self.raw(archive_name)), mode="r:gz") as archive:
                for member in archive:
                    pair = archive_name, member.name
                    if not member.isfile() or pair in seen or pair not in refs:
                        raise ValueError(f"Unexpected archive member: {pair}")
                    relative = PurePosixPath(member.name)
                    if relative.is_absolute() or ".." in relative.parts or "\\" in member.name or member.name in ("", "."):
                        raise ValueError(f"Unsafe archive member: {member.name}")
                    raw = check(archive.extractfile(member).read(), refs[pair], str(pair))
                    seen.add(pair)
                    if destination is not None:
                        source = Path(archive_name).name.removesuffix(".tar.gz")
                        target = safe(destination / "extracted" / source, member.name)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with target.open("xb") as stream:
                            stream.write(raw)
        if seen != set(refs):
            raise ValueError("Missing archive members")
        return rows, len(seen)

    def verify(self):
        files = self.physical()
        for name in self.logical:
            self.raw(name)
        rows, members = self.submissions()
        episodes = self.csv("episodes.csv")
        selected = self.csv("provenance/selection.csv")
        arms = ["persona_off", "candidate_155", "candidate_001", "candidate_003", "candidate_046"]
        expected = {(r["source"], r["task_id"], arm) for r in selected for arm in arms}
        if len(episodes) != 1000 or len(expected) != 1000 or {slot(r) for r in episodes} != expected:
            raise ValueError("Episode coverage differs from frozen selection")
        canonical = [r for r in rows if r["canonical"]]
        if len(canonical) != 1000 or {attempt_key(r) for r in canonical} != {attempt_key(r) for r in episodes}:
            raise ValueError("Canonical submission attempts do not match episodes")
        counts = dict(Counter(r["derived_status"] for r in episodes))
        if counts != self.json("delivery.json")["counts"]:
            raise ValueError("Delivery counts differ from episodes")
        return {"physical_files": files, "logical_files": len(self.logical), "slots": len(episodes),
                "attempts": len(rows), "archive_members": members, "counts": counts}

    def restore(self, destination):
        destination = destination.resolve()
        if destination.exists():
            raise ValueError("Use a fresh, nonexistent output directory")
        result = self.verify()
        destination.mkdir(parents=True)
        parts = {part["path"] for item in self.logical.values() for part in item["parts"]}
        for name in self.receipt["files"]:
            if name in parts:
                continue
            target = safe(destination, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(safe(self.root, name), target)
        for name in self.logical:
            target = safe(destination, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.raw(name))
        rows, _ = self.submissions(destination)
        canonical = []
        for row in rows:
            if not row["canonical"]:
                continue
            restored = {k: row[k] for k in ("benchmark", "task_id", "arm", "trial", "attempt")}
            restored["files"] = {}
            for name, ref in row["files"].items():
                source = Path(ref["archive"]).name.removesuffix(".tar.gz")
                restored["files"][name] = str(safe(destination / "extracted" / source, ref["member"]))
            restored["submission"] = None
            if row["submission"]:
                original = Path(restored["files"]["controller/submission.json"])
                submission = json.loads(original.read_bytes())
                if set(submission.get("artifacts", {})) != set(row["artifacts"]):
                    raise ValueError("Artifact names differ from original submission")
                rebased = {}
                for name, ref in row["artifacts"].items():
                    source = Path(ref["archive"]).name.removesuffix(".tar.gz")
                    artifact = safe(destination / "extracted" / source, ref["member"])
                    basename = Path(submission["artifacts"][name]).name
                    new_path = safe(original.parent / "restored-artifacts", ref["sha256"][:16] + "-" + basename)
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    if not new_path.exists():
                        shutil.copyfile(artifact, new_path)
                    check(new_path.read_bytes(), ref, str(new_path))
                    rebased[name] = str(new_path)
                submission["artifacts"] = rebased
                new_submission = original.with_name("submission.rebased.json")
                new_submission.write_text(json.dumps(submission, ensure_ascii=False, indent=2) + "\n")
                restored["submission"] = str(new_submission)
                restored["original_submission_sha256"] = row["submission"]["sha256"]
                restored["rebased_submission_sha256"] = sha(new_submission.read_bytes())
            canonical.append(restored)
        (destination / "canonical-submissions.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in canonical))
        (destination / "RESTORATION.json").write_text(json.dumps({
            **result, "source_manifest_sha256": sha((self.root / "bundle_manifest.json").read_bytes()),
            "original_files_preserved": True, "submission_change": "Only artifact paths rebased in separate submission.rebased.json files.",
            "inference_performed": False, "canonical_index": "canonical-submissions.jsonl",
            "note": "This materialized working copy has a different file inventory. Verify the original delivered directory.",
        }, indent=2) + "\n")
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, help="Optional fresh directory for reconstruction and submission-path rebasing")
    args = parser.parse_args()
    bundle = Bundle(args.bundle)
    result = bundle.restore(args.output) if args.output else bundle.verify()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
