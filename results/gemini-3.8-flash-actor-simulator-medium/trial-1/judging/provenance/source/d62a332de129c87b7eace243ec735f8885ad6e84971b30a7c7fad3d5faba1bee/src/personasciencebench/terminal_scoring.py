"""Terminal scoring policy, shared by live runs and historical summaries.

Only an explicit missing_submission outcome receives a policy zero. Interrupted
runs and infrastructure failures remain unscored; no native verdict is invented.
"""

MISSING_SUBMISSION_POLICY = "terminal-missing-submission-false-v1"


def missing_submission_evaluation():
    return {
        "status": "missing_submission",
        "evaluator_version": MISSING_SUBMISSION_POLICY,
        "metrics": {"reward": 0.0},
        "errors": [],
        "details": {
            "score_source": "missing_submission_policy",
            "passed": False,
            "native_verifier_invoked": False,
            "score_denominator": 1,
            "reason": "Actor finished without a sealed submission; counted as false.",
        },
    }


def terminal_score_fields(result, evaluation=None):
    """Derive a score without changing the saved attempt or verifier record."""
    evaluation = evaluation if evaluation is not None else result.get("evaluation") or {}
    status = evaluation.get("status", result["status"])
    if result["status"] == "missing_submission":
        status, score, source = "missing_submission", 0.0, "missing_submission_policy"
    elif status == "scored" and evaluation.get("metrics", {}).get("reward") is not None:
        score, source = evaluation["metrics"]["reward"], "native_verifier"
    else:
        score, source = None, "unscored"
    return {
        "status": status,
        "score": score,
        "passed": bool(score) if score is not None else None,
        "score_source": source,
        "scoring_policy": MISSING_SUBMISSION_POLICY,
        "native_graded": source == "native_verifier",
    }
