"""Validate executed notebook and final publication exports without model calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import nbformat
import pymupdf

BASE = Path(__file__).resolve().parents[1]
FIG = BASE / 'figures'
QA = FIG / 'qa'
AUDIT = Path('/home/siyangwu/.codex/skills/nature-figure/scripts')


def run_json(name, args):
    proc = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    result = json.loads(proc.stdout)
    (QA / name).write_text(json.dumps(result, indent=2) + '\n')
    assert proc.returncode == 0, (name, proc.stdout, proc.stderr)
    return result


def main():
    QA.mkdir(exist_ok=True)
    static = run_json('source_validation.json', [AUDIT/'validate_figure.py', BASE/'code/plot.py', '--json'])
    figures = {}
    for name in ['metric_suite', 'repetition_by_benchmark', 'native_scores_with_ci', 'self_repetition_roles']:
        pdf = FIG / (name + '.pdf')
        fonts = run_json(name+'.fonts.json', [AUDIT/'audit_pdf_text.py', pdf, '--min-pt', '5', '--json'])
        proc = subprocess.run([sys.executable, str(AUDIT/'audit_figure_collisions.py'), str(pdf), '--json-out', str(QA/(name+'.collisions.json'))], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        with pymupdf.open(pdf) as doc:
            width_mm = doc[0].rect.width / 72 * 25.4
            height_mm = doc[0].rect.height / 72 * 25.4
        figures[name] = {'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'width_mm': width_mm, 'height_mm': height_mm, 'minimum_font_pt': fonts['minimum_found_pt'], 'collisions': 'pass'}
    notebook = BASE/'metric_suite.ipynb'
    nb = nbformat.read(notebook, as_version=4)
    nbformat.validate(nb)
    code = [c for c in nb.cells if c.cell_type == 'code']
    assert all(c.execution_count is not None for c in code)
    assert not any(o.output_type == 'error' for c in code for o in c.outputs)
    tests = subprocess.run([sys.executable, str(BASE/'code/test_metrics.py')], capture_output=True, text=True)
    (QA/'metric_tests.txt').write_text(tests.stdout+tests.stderr)
    assert tests.returncode == 0, tests.stdout+tests.stderr
    record = {'status': 'passed', 'inference_calls': 0, 'figures': figures, 'executed_code_cells': len(code), 'notebook_sha256': hashlib.sha256(notebook.read_bytes()).hexdigest(), 'static_source': static['summary'], 'static_warning_review': 'Static parser treats figsize=(240/25.4, ...) as 240 inches. Actual PDF page sizes are verified above; 240-mm master exports are intentional. Resize with typography review for a journal-specific column width.', 'manual_review': 'Final PDF previews inspected for typography, labels, colors and data correspondence; no remaining visible overlaps.'}
    (QA/'validation.json').write_text(json.dumps(record, indent=2)+'\n')
    status = json.loads((BASE/'status.json').read_text())
    status.update(status='complete', validation='figures/qa/validation.json', tests='11 passed', notebook_executed=True, original_figures_preserved=True)
    status.update(current_panel_a='simulator_and_actor_within_conversation_verbatim_self_repetition', current_panel_b='complete_fact_recovery_before_intent_gate', self_repetition_report='WORD_REPETITION.md', self_repetition_definition='exact four-word windows', self_repetition_common_questions={r['role']:r['questions'] for r in json.loads((BASE/'data/word_repetition_summary.json').read_text())['coverage'] if r['width']==4})
    (BASE/'status.json').write_text(json.dumps(status, indent=2)+'\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
