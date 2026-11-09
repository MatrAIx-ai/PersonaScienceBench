# AWS Bedrock credentials in the environment
export AWS_DEFAULT_REGION=us-west-2 SCICONV_PROFILE=bedrock_glm5 PYTHONUNBUFFERED=1
cd "$REPO"

ARMS=$(ls persona/bigfive/personas | sed 's/\.json$//' | grep -v -e '_noex$' -e '^bf_low_N' | paste -sd,),mute,oracle

"$PYTHON" persona_runner.py --domain foam --mode disambiguation --cases "@$CASES" --arms "$ARMS" \
  --agent_model bedrock_glm5 --user_model bedrock_glm5 --reps 1 --workers 48 --budget_usd 45 --out "$RUN"
"$PYTHON" persona_eval.py --run_dir "$RUN" --judge_model bedrock_glm5 --aux_model bedrock_glm5 \
  --trait_check none --workers 48 --budget_usd 45
"$PYTHON" persona_pairwise.py --run_dir "$RUN" --judge_model bedrock_glm5 --workers 24 --budget_usd 3 &
"$PYTHON" persona_pairwise.py --run_dir "$RUN" --judge_model bedrock_glm5 --workers 24 --budget_usd 3 --probe opposite &
wait
"$PYTHON" persona_analysis.py --family bigfive --run_dir "$RUN" --results "$RUN/results.jsonl" --out "$RUN/../analysis"
