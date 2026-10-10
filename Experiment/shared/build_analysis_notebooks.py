#!/usr/bin/env python3
"""Create and execute the two offline notebooks with a real local Python kernel."""
import argparse
import json
import os
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[2]
COMMON="""from pathlib import Path
import sys, json
from IPython.display import display, Markdown, Image, Code
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p/'Experiment/shared/task_selection.csv').exists())
sys.path.insert(0, str(ROOT/'Experiment/shared'))
from analysis_utils import ARMS, SOURCES, FAMILIES, NAMES, label, cell, markdown_table
"""

def markdown(s):return nbformat.v4.new_markdown_cell(s)
def code(s):return nbformat.v4.new_code_cell(s)

def behavior_notebook():
    return [markdown('# Experiment 01: behavior, repeat variation and lexical repetition\n\nEight personas plus off from completed Astra trial jobs. Off/148/155/089/001/127 have three trials; 003/004/046 have one. Cancelled initial runs are excluded. Original endpoints preserve the prior behavioral method; repairs are not pooled. No semantic trajectories, embeddings, model calls or human realism judgments. Every statistic can be reproduced from the numeric/hashed snapshot. Private conversation text is not embedded.'),
        code(COMMON+"sys.path.insert(0, str(ROOT/'Experiment/01_behavioral_diversity/code'))\nimport analyze_behavior_all_personas as analysis\nimport plot_behavior_all_personas as plotting\nARMS=analysis.ARMS\n"),
        markdown('## Definitions and extraction\nInitial researcher requests, private evidence and tool output are excluded from message-length summaries. Extra reviews subtract the required first review. Script labels are Unicode proxies, not inferred languages. The extractor below documents the event mapping; rerun `analysis.collect()` only when intentionally refreshing the saved snapshot.'),
        code("import inspect\ndisplay(Code(inspect.getsource(analysis.extract), language='python'))"),
        code("snapshot=json.loads((analysis.DATA/'snapshot.json').read_text())\nassert len(snapshot['episodes']) == 4200\nassert len({(r['trial'],r['source'],r['task_id'],r['arm']) for r in snapshot['episodes']}) == 4200\nsummary=analysis.analyze(snapshot)\nanalysis.report(summary)\nprint('Coverage:',json.dumps(summary['coverage'],indent=2))"),
        markdown('## Paired behavioral changes\nEpisode summaries are paired by task/trial, averaged within task, then source balanced. Intervals resample studies within source and condition on observed trials. One-trial CIs do not estimate run-to-run variation. These are pointwise descriptive intervals, not a multiple-testing result.'),
        code("for metric in analysis.HEAT_METRICS:\n    display(Markdown('### '+analysis.METRICS[metric][0]))\n    display(Markdown(markdown_table(['Persona','Mean [95% CI]','Paired change [95% CI]'],[[label(a),cell(summary['absolute'][metric]['all'][a]),'reference' if a==ARMS[0] else cell(summary['paired'][metric]['all'][a],True)] for a in ARMS])))"),
        markdown('## Repeatability and template concentration\nEach repeat-distance metric requires a complete three-trial/six-setting task panel. Pairwise combinations are summarized within task, not treated as independent observations. Script-matched opening collisions use the same eligible personas for within- and between-persona comparisons. English-primary length sensitivity is separate from the full-panel comparison.'),
        code("for metric, values in summary['repeat_variation'].items():\n    display(Markdown('### '+metric))\n    display(Markdown(markdown_table(['Comparison','Mean [95% CI]; tasks'],[[k,cell(v,counts=False)+f\"; n={v['tasks']} tasks\"] for k,v in values.items()])))"),
        markdown('## Figure generation\nThe plotting module exports editable PDF/SVG and 600 dpi PNG/TIFF plus source-data CSV. Render-time alignment is checked before export. Final PDF collision/font audits are saved beside the figures.'),
        code("display(Code(inspect.getsource(plotting.main),language='python'))\nplotting.main()\nfor name in ['behavior_effects','repeat_variation','reply_length_distribution']:\n    display(Image(filename=str(plotting.FIG/f'{name}.png'),width=1000))"),
        code("assert summary['invalid_native_metric_episodes']==0\nassert sum(c.get('analyzed',0) for c in summary['coverage'].values())==sum(r['eligible'] for r in snapshot['episodes'])\nprint('Validated: unique episode slots, coverage totals, native metric bounds and saved figure exports.')"),
        markdown('## Interpretation boundary\nReply length and exact phrase reuse measure observable communication, not semantic coverage or human realism. Source-balanced results mix workflows; per-source summaries and denominators are in `data/behavior_all_personas/summary.json`. Language/script, incomplete traces and selected personas limit generalization. See `ALL_PERSONAS_BEHAVIOR.md` for all metrics. Previous figures and report are preserved. Semantic analysis is deferred by request.')]

def performance_notebook():
    return [markdown('# Performance analysis — all personas with completed trial jobs\n\nHeatmaps retained. Eight personas plus off; include all available results from their completed Astra trial jobs. Off/148/155/089/001/127 have three trials; 003/004/046 have one. The cancelled initial run and personas without any completed trial are excluded. Repairs replace endpoints within a trial and are not extra repeats.'),
        code(COMMON+"sys.path.insert(0,str(ROOT/'Experiment/02_performance_and_fields/code'))\nimport analyze_all_available as analysis\nimport plot_all_available as plotting\n"),
        markdown('## Frozen data and aggregation\nUse `analysis.collect()` only to intentionally refresh saved campaign results. Available endpoints prefer an evaluable repaired outcome, with fallback to an evaluable original when repair failed. This is not selection of the highest score. Missing submissions score zero; infrastructure failures remain missing. Average observed repeats within task before averaging tasks. Study-cluster CIs condition on available trials and do not quantify run variation for one-trial personas.'),
        code("snapshot=json.loads((analysis.DATA/'snapshot.json').read_text())\nsummary=analysis.analyze()\nanalysis.report(summary)\nprint('Frozen snapshot SHA256:',summary['snapshot_sha256'])\nprint('Personas:',summary['arms'])"),
        code("display(Markdown(markdown_table(['Persona','Trials with scores','Evaluable episodes','Tasks','Recorded unscored'],[[label(a),','.join(map(str,v['trials_with_scores'])) or 'none',v['evaluable'],v['tasks'],v['recorded_slots']-v['evaluable']] for a,v in summary['coverage'].items()])))"),
        markdown('## Available performance tables\nAll available scored outcomes from eligible trials contribute. Absolute ASI values span historical judge versions and are descriptive. Super-families mix native metrics and source compositions. Each cell gives mean [95% CI], distinct tasks and evaluable trial episodes.'),
        code("for field,groups in [('source',SOURCES),('family',FAMILIES)]:\n    display(Markdown('### '+field))\n    display(Markdown(markdown_table(['Persona',*[NAMES[g] for g in groups]],[[label(a),*[analysis.cell(summary['absolute']['available'][a][field][g]) for g in groups]] for a in summary['arms']])))"),
        markdown('## Matched differences\nMatch task and trial before averaging differences. ASI requires the corrected judge on both episodes; evaluator configurations elsewhere must be compatible. Missing matched data stay missing. Denominators differ by persona; these are not ranking or equivalence tests.'),
        code("for field,groups in [('source',SOURCES),('family',FAMILIES)]:\n    display(Markdown('### '+field))\n    display(Markdown(markdown_table(['Persona Δ vs off',*[NAMES[g] for g in groups]],[[label(a),*[analysis.cell(summary['paired']['available'][a][field][g],True) for g in groups]] for a in summary['arms'][1:]])))"),
        markdown('## Expanded heatmaps\nThe original heatmap design is retained. The first figure shows absolute performance for eight personas plus off; the second shows all eight matched persona-minus-off effects. T identifies the number of trials with results, not independent tasks. Exact per-cell denominators and uncertainty limits are in the tables and CSVs.'),
        code("display(Code(Path(plotting.__file__).read_text(),language='python'))\nplotting.main()\nfor name in ['absolute_performance','paired_performance']:\n    display(Image(filename=str(plotting.FIG/f'{name}.png'),width=1000))"),
        code("from collections import Counter\nrows=snapshot['episodes']\nassert len(rows)==8400\nassert len({(r['view'],r['trial'],r['source'],r['task_id'],r['arm']) for r in rows})==8400\nassert all(n==200 for n in Counter((r['view'],r['trial'],r['arm']) for r in rows).values())\nassert all(r['status'] not in ['running','pending'] for r in rows if r['view']=='available')\nassert not {'candidate_228','candidate_137','candidate_262','candidate_224','candidate_026'} & set(summary['arms'])\nassert all('first-pass-20260929T075354Z' not in p['file'] for p in snapshot['provenance'])\nprint('Validated 4,200 trial slots in each of two outcome views; no partial cancelled-job records or duplicate trials.')"),
        markdown('## Preserved previous heatmap\nThe earlier six-setting analysis remains available as a historical figure. The forest-plot alternative has been discarded. Original benchmark and super-family bar figures remain in `figures/three_trials/`.'),
        code("display(Image(filename=str(analysis.BASE/'figures/consolidated/matched_performance.png'),width=1000))"),
        markdown('## Limits and report\nAt least one trial job must be complete; individual episodes can still be unscored. Unequal trial counts, technical missingness, conditional repairs and persona selection limit inference. Fewer than two studies yields an unavailable CI; singleton source-by-family strata cannot contribute estimable between-study variation. The full report is `ALL_AVAILABLE_PERFORMANCE.md`; its original-only sensitivity retains pre-repair evidence. No new API calls.')]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--which',choices=['behavior','performance','both'],default='both');args=parser.parse_args()
    runtime=Path('/tmp/psb-analysis-jupyter');kernel=runtime/'kernels/python3';kernel.mkdir(parents=True,exist_ok=True)
    (kernel/'kernel.json').write_text(json.dumps({'argv':[str(ROOT/'.venv/bin/python'),'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (PersonaScienceBench)','language':'python'}))
    os.environ['JUPYTER_PATH']=str(runtime)
    os.environ['JUPYTER_RUNTIME_DIR']=str(runtime/'runtime')
    os.environ['IPYTHONDIR']=str(runtime/'ipython')
    os.environ['MPLCONFIGDIR']='/tmp/psb-mpl'
    os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
    for which,folder,name,builder in [('behavior','01_behavioral_diversity','behavioral_analysis.ipynb',behavior_notebook),('performance','02_performance_and_fields','performance_analysis.ipynb',performance_notebook)]:
        if args.which not in [which,'both']:continue
        nb=nbformat.v4.new_notebook(cells=builder(),metadata={'kernelspec':{'name':'python3','display_name':'Python (PersonaScienceBench)','language':'python'},'language_info':{'name':'python','version':sys.version.split()[0]}})
        path=ROOT/'Experiment'/folder/name
        nbformat.write(nb,path)
        NotebookClient(nb,timeout=300,startup_timeout=60,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
        nbformat.validate(nb);nbformat.write(nb,path)
        print(f'Executed and validated {path.relative_to(ROOT)}: {sum(c.cell_type=="code" for c in nb.cells)} code cells',flush=True)

if __name__=='__main__':main()
