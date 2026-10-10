"""Offline model comparison using each model's own available question panels.

Bars summarize four fixed personas; study-cluster percentile intervals reuse
the scorecard estimator. No new inference, significance tests or regrading.
"""
from pathlib import Path
import json
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

import model_scorecard as scorecard

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "Experiment/02_performance_and_fields"
DATA = BASE / "data/model_leaderboard"
FIGURES = BASE / "figures/model_leaderboard"
sys.path.insert(0, str(ROOT / "Experiment/01_behavioral_diversity/code"))
from audit_panel_alignment import require_matplotlib_panel_alignment
from analysis_utils import B, SEED, write_csv, write_json, markdown_table

MODELS = ["GPT-6 Astra (low)", "Claude Haiku 4.5"]
METRICS = ["performance", "fact_recovery", "self_repetition"]
COLORS = ["#4C78A8", "#D99561"]


def question(row):
    return row["source"], row["task_id"], row["study_id"]


def eligible_questions(rows, metric):
    """Require observed finite values for all five settings, per model."""
    settings = []
    for arm in scorecard.ARMS:
        settings.append({question(r) for r in rows
                         if r["arm"] == arm and r.get(metric) is not None})
    return set.intersection(*settings)


def build_data():
    paths = [scorecard.OUT / "episodes.json",
             scorecard.OUT / "haiku_metric_episodes.json"]
    rows_by_model = dict(zip(MODELS, [json.loads(p.read_text()) for p in paths]))
    for rows in rows_by_model.values():
        assert len({scorecard.key(r) for r in rows}) == len(rows)
        assert set(r["arm"] for r in rows) == set(scorecard.ARMS)
        for row in rows:
            for metric in METRICS:
                if row.get(metric) is not None:
                    assert np.isfinite(row[metric]) and 0 <= row[metric] <= 100

    results = {"models": MODELS, "arms": scorecard.ARMS, "metrics": {},
               "question_support": "model-specific available cases; all five settings required within each model/metric; no cross-model intersection",
               "bootstrap": {"draws": B, "seed": SEED,
                             "unit": "study cluster within source benchmark",
                             "ci": "pointwise percentile 95%",
                             "shared_weights_across_settings_within_model": True,
                             "cross_model_pairing": False},
               "weighting": "available trials within question/setting; equal questions within source; equal sources; equal four injected personas",
               "inputs": {str(p.relative_to(ROOT)): scorecard.sha(p) for p in paths},
               "analysis_code": {str(p.relative_to(ROOT)): scorecard.sha(p) for p in
                                 [Path(__file__), Path(scorecard.__file__), ROOT / "Experiment/shared/analysis_utils.py"]},
               "no_inference": True}
    source_data, coverage = [], []
    for metric in METRICS:
        panel = {"models": {}}
        for model, rows in rows_by_model.items():
            # The user's reporting choice retains each model's own data.
            # Only the existing within-model five-setting eligibility applies.
            eligible = eligible_questions(rows, metric)
            assert eligible, (model, metric)
            estimates = scorecard.panel(rows, metric)
            assert {tuple(q) for q in estimates["question_keys"]} == eligible
            estimates["study_clusters"] = len({(q[0], q[2]) for q in eligible})
            panel["models"][model] = estimates
            available = {question(r) for r in rows if r.get(metric) is not None}
            coverage.append({"model": model, "metric": metric,
                             "available_questions_any_setting": len(available),
                             "eligible_questions": len(eligible),
                             "excluded_incomplete_setting_panel": len(available - eligible),
                             "excluded_by_cross_model_matching": 0,
                             "source_questions": json.dumps(estimates["source_questions"]),
                             "study_clusters": estimates["study_clusters"],
                             "episodes_by_setting": json.dumps(estimates["episodes_by_setting"]),
                             "trials_by_setting": json.dumps(estimates["trials_by_setting"])})
            for setting in ["persona_mean", "off"]:
                value = estimates[setting]
                assert value["ci95"][0] <= value["mean"] <= value["ci95"][1]
                source_data.append({"model": model, "metric": metric, "setting": setting,
                                    "estimate": value["mean"], "ci_low": value["ci95"][0],
                                    "ci_high": value["ci95"][1], "questions": len(eligible),
                                    "study_clusters": estimates["study_clusters"],
                                    "plotted_as": "bar_with_ci" if setting == "persona_mean" else
                                        "point_reference_only" if metric == "performance" else "supporting_only"})
        results["metrics"][metric] = panel
    write_json(DATA / "summary.json", results)
    write_csv(DATA / "source_data.csv", source_data)
    write_csv(DATA / "coverage.csv", coverage)
    write_csv(DATA / "question_panel.csv", [dict(model=model, metric=m, source=q[0], task_id=q[1], study_id=q[2])
              for m, p in results["metrics"].items() for model, v in p["models"].items() for q in v["question_keys"]])
    table = markdown_table(["Model", "Metric", "Mean [95% CI]", "Available eligible questions"], [
        [r["model"], r["metric"], f'{r["estimate"]:.2f} [{r["ci_low"]:.2f}, {r["ci_high"]:.2f}]', r["questions"]]
        for r in source_data if r["setting"] == "persona_mean"])
    (DATA / "estimates.md").write_text(table + "\n")
    return results


def draw(results=None):
    results = build_data() if results is None else results
    FIGURES.mkdir(parents=True, exist_ok=True)
    style = {"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"], "font.size": 9,
             "axes.titlesize": 10, "axes.labelsize": 9, "xtick.labelsize": 8.5,
             "ytick.labelsize": 8, "legend.fontsize": 8,
             "axes.spines.top": False, "axes.spines.right": False,
             "axes.linewidth": .7, "pdf.fonttype": 42, "svg.fonttype": "none",
             "savefig.facecolor": "white", "figure.facecolor": "white"}
    titles = ["Mean Persona\nPerformance", "Fact recovery", "Self-repetition"]
    axis_labels = ["Native score (0–100)", "Recovered facts (%)", "Repeated windows (%)"]
    # No truncated bar axes. Metric-specific ranges are explicitly labelled.
    limits = [(0, 70), (0, 110), (0, 30)]
    ticks = [[0, 20, 40, 60], [0, 25, 50, 75, 100], [0, 10, 20, 30]]
    with mpl.rc_context(style):
        fig, axes = plt.subplots(1, 3, figsize=(7.2047244094, 3.2283464567))
        fig.subplots_adjust(left=.07, right=.995, bottom=.17, top=.81, wspace=.50)
        for index, (ax, metric) in enumerate(zip(axes, METRICS)):
            panel = results["metrics"][metric]
            ax.set_label(chr(97 + index))
            ax.set_title(titles[index], pad=12)
            ax.annotate(chr(65 + index), xy=(0, 1), xycoords="axes fraction",
                        xytext=(-24, 14), textcoords="offset points",
                        fontsize=11, fontweight="bold", ha="left", va="bottom")
            ax.set_axisbelow(True)
            ax.yaxis.grid(False)
            ax.set_ylim(*limits[index])
            ax.set_yticks(ticks[index])
            ax.set_xlim(-.55, 1.55)
            ax.set_ylabel(axis_labels[index], labelpad=4)
            ax.tick_params(axis="x", length=0, pad=5)
            ax.tick_params(axis="y", width=.7, length=3, pad=3)
            ax.set_xticks([0, 1], ["GPT-6 Astra\n(low)", "Claude Haiku\n4.5"])
            for x, (model, color) in enumerate(zip(MODELS, COLORS)):
                value = panel["models"][model]["persona_mean"]
                mean, (lo, hi) = value["mean"], value["ci95"]
                ax.bar(x, mean, width=.58, color=color, edgecolor="none", zorder=2)
                ax.errorbar(x, mean, yerr=[[mean - lo], [hi - mean]], fmt="none",
                            ecolor="#292929", elinewidth=.9, capsize=3, capthick=.9, zorder=4)
                ax.annotate(f"{mean:.1f}", (x, hi), xytext=(0, 4),
                            textcoords="offset points", ha="center", va="bottom", fontsize=9)
                if metric == "performance":
                    off = panel["models"][model]["off"]["mean"]
                    ax.hlines(off, x-.24, x+.24, color="#202020", linewidth=1.6, zorder=5)
        axes[0].legend([Line2D([0], [0], color="#202020", linewidth=1.6)], ["Persona-off"],
                       loc="upper center", bbox_to_anchor=(.5, 1.0), frameon=False,
                       handlelength=1.2, borderaxespad=.15)
        stem = FIGURES / "model_leaderboard"
        fig.canvas.draw()
        require_matplotlib_panel_alignment(fig, json_out=stem.with_suffix(".alignment.json"),
                                           tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
        fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=.025)
        fig.savefig(stem.with_suffix(".svg"), bbox_inches="tight", pad_inches=.025)
        fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight", pad_inches=.025)
    return fig, results


if __name__ == "__main__":
    figure, result = draw()
    print((DATA / "estimates.md").read_text())
    print(FIGURES / "model_leaderboard.pdf")
    plt.close(figure)
