#!/usr/bin/env bash
# Run the full 200-task Haiku actor / Opus collaborator campaign.
#
# Default design:
#   200 frozen tasks x 5 conditions x 1 trial
#   = 1,000 total agent episodes.
#
# The five package conditions are persona_off plus four enabled personas:
# candidate_155, candidate_001, candidate_003, and candidate_046.
#
# Safe to rerun: completed episodes are reused. Infrastructure failures are
# retried only when RETRY_INFRASTRUCTURE=1 is explicitly supplied.
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_root"

aws_dir="${PSB_AWS_DIR:-/home/exf/.aws}"
aws_profile="${AWS_PROFILE:-default}"
aws_region="${AWS_REGION:-us-west-2}"
ada_account="${ADA_ACCOUNT:-457663127526}"
ada_role="${ADA_ROLE:-Admin}"
workers="${WORKERS:-5}"
trials_text="${TRIALS:-1}"
campaign_name="${CAMPAIGN_NAME:-haiku-actor-opus-five-condition-full}"
refresh_credentials="${REFRESH_CREDENTIALS:-1}"
prepare_assets="${PREPARE_ASSETS:-1}"
retry_infrastructure="${RETRY_INFRASTRUCTURE:-0}"
archive_fatal_api="${ARCHIVE_FATAL_API:-0}"
dry_run="${DRY_RUN:-0}"

actor_model="us.anthropic.claude-haiku-4-5-20251001-v1:0"
opus_model="us.anthropic.claude-opus-4-6-v1"
arms=(persona_off candidate_155 candidate_001 candidate_003 candidate_046)
log_dir="logs/${campaign_name}"
credential_pid=""

read -r -a trials <<< "$trials_text"

cleanup() {
  if [[ -n "$credential_pid" ]] && kill -0 "$credential_pid" 2>/dev/null; then
    kill "$credential_pid" 2>/dev/null || true
    wait "$credential_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

[[ -x docker/run.sh ]] || die "docker/run.sh is missing or not executable"
[[ -f configs/main_run/selection.csv ]] || die "Frozen main selection is missing"
[[ -d "$aws_dir" ]] || die "AWS credential directory does not exist: $aws_dir"
command -v docker >/dev/null || die "docker is not available"
mkdir -p -- "$log_dir"

for trial in "${trials[@]}"; do
  [[ "$trial" =~ ^[123]$ ]] || die "TRIALS may contain only 1, 2, and 3"
done
[[ "$workers" =~ ^[1-9][0-9]*$ ]] || die "WORKERS must be a positive integer"
(( workers <= 30 )) || die "WORKERS must not exceed 30"

ada_args=(
  credentials update
  --provider=isengard
  --profile="$aws_profile"
  --account="$ada_account"
  --role="$ada_role"
)

if [[ "$dry_run" == "1" ]]; then
  refresh_credentials="0"
fi

if [[ "$prepare_assets" == "1" ]]; then
  mapfile -t bix_tasks < <(
    awk -F, 'NR > 1 && $1 == "bixbench" {print $2}' \
      configs/main_run/selection.csv
  )
  mapfile -t asi_tasks < <(
    awk -F, 'NR > 1 && $1 == "asibench" {print $2}' \
      configs/main_run/selection.csv
  )
  (( ${#bix_tasks[@]} == 40 )) || die "Expected 40 frozen BixBench tasks"
  (( ${#asi_tasks[@]} == 40 )) || die "Expected 40 frozen ASI-Bench tasks"

  printf 'Preparing public assets for all 40 BixBench and 40 ASI-Bench tasks...\n'
  if [[ "$dry_run" == "1" ]]; then
    printf 'Would acquire %s BixBench tasks and %s ASI-Bench tasks.\n' \
      "${#bix_tasks[@]}" "${#asi_tasks[@]}"
  else
    docker/run.sh .venv/bin/python scripts/acquire_conversion_assets.py \
      bixbench --tasks "${bix_tasks[@]}" \
      2>&1 | tee -a "$log_dir/asset-preparation.log"
    docker/run.sh .venv/bin/python scripts/acquire_conversion_assets.py \
      asibench --tasks "${asi_tasks[@]}" \
      2>&1 | tee -a "$log_dir/asset-preparation.log"
  fi
fi

if [[ "$refresh_credentials" == "1" ]]; then
  command -v ada >/dev/null || die "ada is required when REFRESH_CREDENTIALS=1"
  printf 'Refreshing initial AWS credentials for account %s...\n' "$ada_account"
  ada "${ada_args[@]}" --once

  # Without --once, ADA stays active and refreshes the selected profile. New
  # benchmark subprocesses read the refreshed profile throughout a long run.
  printf 'Starting continuous ADA credential refresh. Log: %s\n' \
    "$log_dir/ada-credentials.log"
  ada "${ada_args[@]}" >>"$log_dir/ada-credentials.log" 2>&1 &
  credential_pid="$!"
fi

for trial in "${trials[@]}"; do
  run_dir="runs/main/${campaign_name}-trial-${trial}"
  console_log="$log_dir/trial-${trial}.console.log"
  fatal_api="$run_dir/fatal_api.json"

  if [[ "$refresh_credentials" == "1" ]] \
      && ! kill -0 "$credential_pid" 2>/dev/null; then
    die "ADA credential refresher stopped; inspect $log_dir/ada-credentials.log"
  fi

  if docker/run.sh test -f "$fatal_api"; then
    if [[ "$archive_fatal_api" == "1" ]]; then
      archived="${fatal_api%.json}.before-resume.$(date -u +%Y%m%dT%H%M%SZ).json"
      docker/run.sh mv -- "$fatal_api" "$archived"
      printf 'Archived stale fatal API marker to %s\n' "$archived"
    else
      die "Found $fatal_api. Refresh credentials, inspect it, then rerun with ARCHIVE_FATAL_API=1."
    fi
  fi

  command=(
    docker/run.sh
    .venv/bin/python
    scripts/run_main.py
    --run-dir "$run_dir"
    --selection configs/main_run/selection.csv
    --provider bedrock
    --model "$opus_model"
    --actor-model "$actor_model"
    --reasoning-effort none
    --aws-profile "$aws_profile"
    --aws-region "$aws_region"
    --arms "${arms[@]}"
    --workers "$workers"
  )
  if [[ "$retry_infrastructure" == "1" ]]; then
    command+=(--retry-infrastructure)
  fi

  printf '\n=== Trial %s of the full campaign ===\n' "$trial"
  printf 'Run directory: %s\n' "$run_dir"
  printf 'Console log: %s\n' "$console_log"
  printf 'Command:'
  printf ' %q' "${command[@]}"
  printf '\n'

  if [[ "$dry_run" == "1" ]]; then
    continue
  fi

  if ! PSB_AWS_DIR="$aws_dir" \
      AWS_PROFILE="$aws_profile" \
      AWS_REGION="$aws_region" \
      "${command[@]}" 2>&1 | tee -a "$console_log"; then
    printf '\nTrial %s stopped with an error.\n' "$trial" >&2
    printf 'Inspect %s and %s/progress.json.\n' "$console_log" "$run_dir" >&2
    printf 'After fixing infrastructure, rerun with RETRY_INFRASTRUCTURE=1.\n' >&2
    printf 'Do not retry missing submissions; they are benchmark outcomes.\n' >&2
    exit 1
  fi

  printf 'Trial %s completed successfully.\n' "$trial"
done

if [[ "$dry_run" == "1" ]]; then
  printf '\nDry run complete; no credentials or benchmark episodes were started.\n'
else
  printf '\nRequested full-campaign trials completed.\n'
fi
