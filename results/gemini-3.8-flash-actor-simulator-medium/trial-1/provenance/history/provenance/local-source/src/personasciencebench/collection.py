"""Explicitly defer final grading while retaining the intended judge identity."""


def active_models(models, collect_only=False):
    return {role: spec for role, spec in models.items()
            if not (collect_only and role == "judge")}


def pending_evaluation(judge):
    return {
        "status": "grading_pending", "metrics": {}, "score": None,
        "details": {"reason": "Final evaluation deferred by collect_only",
                    "intended_judge": judge, "judge_calls": 0},
    }
