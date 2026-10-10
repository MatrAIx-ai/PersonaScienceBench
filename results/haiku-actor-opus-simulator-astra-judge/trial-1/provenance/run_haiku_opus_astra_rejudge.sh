#!/usr/bin/env bash
# Rejudge the completed Haiku-actor / Opus-researcher campaign with
# Bedrock GPT-6 Astra-low. Actors and researchers are never rerun.
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$repo_root"

source_run="${SOURCE_RUN:-runs/main/haiku-actor-opus-five-condition-full-trial-1}"
output_dir="${OUTPUT_DIR:-runs/rejudge/haiku-actor-opus-researcher-astra-judge-trial-1}"
aws_dir="${PSB_AWS_DIR:-/home/exf/.aws}"
aws_profile="${AWS_PROFILE:-default}"
aws_region="${AWS_REGION:-us-west-2}"
ada_account="${ADA_ACCOUNT:-457663127526}"
ada_role="${ADA_ROLE:-Admin}"
workers="${WORKERS:-12}"
refresh_credentials="${REFRESH_CREDENTIALS:-1}"
retry_infrastructure="${RETRY_INFRASTRUCTURE:-0}"
dry_run="${DRY_RUN:-0}"
log_dir="${LOG_DIR:-logs/haiku-actor-opus-researcher-astra-rejudge}"
console_log="$log_dir/rejudge.console.log"
credential_pid=""

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
docker/run.sh test -d "$source_run" \
  || die "Source campaign is missing or unreadable in Docker: $source_run"
[[ -d "$aws_dir" ]] || die "AWS credential directory is missing: $aws_dir"
[[ "$workers" =~ ^[1-9][0-9]*$ ]] || die "WORKERS must be a positive integer"
available_cpus="$(nproc)"
(( workers <= available_cpus )) \
  || die "WORKERS must not exceed the ${available_cpus} logical CPUs"
mkdir -p -- "$log_dir"

if [[ "$dry_run" == "1" ]]; then
  refresh_credentials="0"
fi

ada_args=(
  credentials update
  --provider=isengard
  --profile="$aws_profile"
  --account="$ada_account"
  --role="$ada_role"
)

if [[ "$refresh_credentials" == "1" ]]; then
  command -v ada >/dev/null || die "ada is required when REFRESH_CREDENTIALS=1"
  printf 'Refreshing initial AWS credentials for account %s...\n' "$ada_account"
  ada "${ada_args[@]}" --once
  printf 'Starting continuous ADA credential refresh. Log: %s\n' \
    "$log_dir/ada-credentials.log"
  ada "${ada_args[@]}" >>"$log_dir/ada-credentials.log" 2>&1 &
  credential_pid="$!"
fi

command=(
  docker/run.sh
  .venv/bin/python
  scripts/rejudge_main_campaign.py
  --source-run "$source_run"
  --output-dir "$output_dir"
  --model us.openai.gpt-6-astra
  --aws-profile "$aws_profile"
  --aws-region "$aws_region"
  --workers "$workers"
)
if [[ "$retry_infrastructure" == "1" ]]; then
  command+=(--retry-infrastructure)
fi
if [[ "$dry_run" == "1" ]]; then
  command+=(--dry-run)
fi

printf 'Source trajectories: %s\n' "$source_run"
printf 'Judge-only output: %s\n' "$output_dir"
printf 'Console log: %s\n' "$console_log"
printf 'Command:'
printf ' %q' "${command[@]}"
printf '\n'

if [[ "$dry_run" == "1" ]]; then
  "${command[@]}"
  exit 0
fi

if ! PSB_AWS_DIR="$aws_dir" \
    AWS_PROFILE="$aws_profile" \
    AWS_REGION="$aws_region" \
    "${command[@]}" 2>&1 | tee -a "$console_log"; then
  printf '\nJudge-only regrade stopped before all endpoints finished.\n' >&2
  printf 'Inspect %s and %s/progress.json.\n' "$console_log" "$output_dir" >&2
  printf 'Rerun the same command to resume running/interrupted endpoints.\n' >&2
  printf 'Use RETRY_INFRASTRUCTURE=1 after correcting failed judge calls.\n' >&2
  exit 1
fi

printf '\nJudge-only Astra regrade completed successfully.\n'
