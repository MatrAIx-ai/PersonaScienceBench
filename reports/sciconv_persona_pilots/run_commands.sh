#!/bin/bash
# Exact runner / eval commands of the persona pilots, local paths replaced by placeholders.
# $RUNS: runs root; $CASES: directory with cases_cards.txt (= cases_foam_full1.txt) and cases_matraix.txt (= cases_mx1.txt).
# Run from the SciConvBench checkout named in each block, with model credentials set in the environment.
set -euo pipefail
export SCICONV_PROFILE=bedrock_glm5 PYTHONUNBUFFERED=1

# tone1 (frozen-history replay), SciConvBench ein/tone-replay 1885a5221
S=$RUNS/tone1/run
python persona_tone_replay.py select --src_run $RUNS/full1/foam/run --n_cases 50 --seed 0 --out $S
python persona_tone_replay.py rewrite --styles para,lowA --out $S --budget_usd 0.9 --workers 12
python persona_tone_replay.py judge --out $S --budget_usd 0.4 --workers 12
python persona_tone_replay.py replay --arms para,lowA --orig_slots 60 --seed 0 --out $S --budget_usd 2.0 --workers 16
python persona_tone_replay.py analyze --out $S

# tone2 (live restyle), SciConvBench ein/tone-live 14665bad9
RUN=$RUNS/tone2/foam/run
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards.txt" --arms rs_para,rs_lowA \
  --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 16 --budget_usd 3.5 --out "$RUN"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 2.5

# tone3 (live restyle round 2 + hostile tone), SciConvBench ein/tone-live d5ebbdf9a
RUN=$RUNS/tone3/foam/run
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards.txt" --arms rs_para,rs_lowA,rs_lowAc \
  --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 16 --budget_usd 7 --out "$RUN"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 4.5
# judge and analysis, from the persona-behaviour-cards checkout (persona/analysis/pilots/), PILOT_RUNS=$RUNS
python persona/analysis/pilots/tone3_judge.py --run_dir "$RUN" --budget_usd 0.6
python persona/analysis/pilots/remark_strict.py persona/analysis/pilots/tone3_judge.jsonl
python persona/analysis/pilots/tone3_an.py

# mx1 (MatrAIx personas), SciConvBench fork 7173d41e2; second runner call fills skipped_budget jobs
RUN=$RUNS/mx1/foam/run
ARMS=bf_neutral,$(python3 -c "import json;print(','.join('mx_'+c for c in json.load(open('persona/matraix/selection.json'))['selected']))")
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_matraix.txt" --arms "$ARMS" \
  --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 16 --budget_usd 9 --out "$RUN"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 7
python persona_analysis.py --family matraix --run_dir "$RUN" --results "$RUN/results.jsonl" --out "$RUNS/mx1/foam/analysis"
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_matraix.txt" --arms "$ARMS" \
  --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 16 --budget_usd 1.6 --out "$RUN"

# vol1 (behaviour cards), SciConvBench fork ein/behaviour-cards (COMMIT set at launch)
RUN=$RUNS/vol1/foam/run
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards.txt" \
  --arms bf_neutral,bv_terse,bv_volunteer --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 16 \
  --budget_usd 7 --out "$RUN" --shared_first "$RUNS/vol1/first"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 5
# vol1 rep2
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards.txt" \
  --arms bf_neutral,bv_terse,bv_volunteer --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 2 --workers 16 \
  --budget_usd 5 --out "$RUN" --shared_first "$RUNS/vol1/first"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 5
# vol1 rounds 3-6 (commit da3734809: runner code identical to 818ba5902), run together with the harder extra cases below
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards.txt" \
  --arms bf_neutral,bv_terse,bv_volunteer --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 6 --workers 32 \
  --budget_usd 17 --out "$RUN" --shared_first "$RUNS/vol1/first"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 32 --budget_usd 18
# vol1 harder extra cases, rounds 1-6
RUN=$RUNS/vol1/foam/hard
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards_hard_extra.txt" \
  --arms bf_neutral,bv_terse,bv_volunteer --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 6 --workers 16 \
  --budget_usd 6.5 --out "$RUN" --shared_first "$RUNS/vol1/first"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 7
# vol1 turn cap 20
RUN=$RUNS/vol1/foam/cap20
python persona_runner.py --domain foam --mode disambiguation --cases "@$CASES/cases_cards.txt" \
  --arms bf_neutral,bv_terse --max_turns 20 --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 16 \
  --budget_usd 5 --out "$RUN" --shared_first "$RUNS/vol1/first"
python persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 --trait_check none --workers 16 --budget_usd 4
