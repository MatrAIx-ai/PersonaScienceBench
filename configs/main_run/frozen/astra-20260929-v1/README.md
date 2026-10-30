# Frozen main-run preparation

This tracked bundle restores the original Astra preparation from
`runs/openai-astra-first-pass-20260929T075354Z/prepared/`: **200 questions,
40 from each benchmark**. Use it for all five persona settings in a new-model
trial, with `--require-prepared`. No maintainer-only preparation path is needed.

## Restore on another host

From the repository root, after installing dependencies and downloading the
pinned public benchmark assets with `bash scripts/setup_main.sh`:

```bash
RUN_DIR="$PWD/runs/main/gemini38-self-medium-trial-1"
# Optional read-only check; requires a fresh preparation destination.
python scripts/restore_main_preparation.py --run-dir "$RUN_DIR" --check-only
python scripts/restore_main_preparation.py --run-dir "$RUN_DIR"
```

Pass **that same run directory** and `--require-prepared` to the campaign
launcher. Use the provider/model-role configuration documented in
[the evaluation README](../../../../README.md); restoration does not configure
models or launch episodes. An existing `prepared/` is never overwritten.

The script verifies the selection, source pins, metadata and public asset hashes,
rewrites old repository/preparation paths, and creates `prepared/` plus
`preparation_receipt.json`. Copy the receipt into the campaign's delivered
provenance. It uses standard-library Python and makes no API calls. Optional
`--link-assets` uses hardlinks instead of copies on the same filesystem; keep
the downloaded source assets immutable when using this option.

## Included and external inputs

- `preparation.json.gz`: approximately **1.57 MiB**, containing 1,160 frozen
  metadata files (160 packaged tasks and 40 final EXP cards), the original EXP
  source records, asset mappings and reference runtime hashes.
- `manifest.json`: archive and original metadata SHA-256 checksums, frozen
  selection hash, source pins and question counts.
- The roughly 2.8 GiB of public task assets remain separate downloads. The
  restorer verifies the hashes for 629 staged actor asset copies (347 distinct
  content hashes) and required evaluator files with recorded hashes. Evaluator
  directories without historical tree hashes are checked for presence and rely
  on the pinned source acquisition; they are not independently tree-hashed.

The final EXP cards are already extracted. **No EXP extraction cache or new
extraction inference is required** with this bundle and `--require-prepared`.
If a local `data/exp_bench/tasks.jsonl` differs from the frozen source, restoration
stops rather than overwriting it; preserve that file before restoring.

Controller metadata includes withheld facts and evaluator references. The runner
keeps those outside the actor workspace. Do not mount the whole preparation
bundle into an actor sandbox.

## Runtime and delivery

This version freezes task inputs, not the runner or interaction protocol.
Record the actual code revision/configuration, particularly for SciConv, and do
not assume a current run reproduces historical outcomes. Bubblewrap isolation
must still work on the execution host. Successful restoration does not resolve
namespace/mount restrictions or replace the sandbox readiness check.

After collection, publish traces, submissions and provenance under
`results/<model-slug>/trial-1/` following the handoff. Restoring inputs alone does
not collect or deliver the 1,000-episode trial.

## Maintainer rebuild and verification

```bash
python scripts/build_main_preparation_bundle.py \
  --prepared runs/openai-astra-first-pass-20260929T075354Z/prepared
python -m unittest discover -s tests -p test_frozen_preparation.py -v
```

The archive preserves original metadata text; restored JSON may be reformatted
and paths are deliberately rebased. The receipt records hashes of the restored
files. Keep this version fixed for comparisons; publish a separately identified
bundle if task content changes.
