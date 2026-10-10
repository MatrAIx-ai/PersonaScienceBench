#!/usr/bin/env python3
"""Run the figure source/font/collision checks on final notebook exports."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
SKILL=Path('/home/siyangwu/.codex/skills/nature-figure/scripts')
ITEMS=[
 *[('01_behavioral_diversity','code/plot_behavior_all_personas.py','figures/behavior_all_personas',n) for n in ['behavior_effects','repeat_variation','reply_length_distribution']],
 ('01_behavioral_diversity','code/plot_behavior.py','figures/behavior','behavior_effects'),
 ('01_behavioral_diversity','code/plot_behavior.py','figures/behavior','repeat_variation'),
 ('01_behavioral_diversity','code/plot_behavior.py','figures/behavior','reply_length_distribution'),
 ('02_performance_and_fields','code/plot_matched_performance.py','figures/consolidated','matched_performance'),
 ('02_performance_and_fields','code/plot_all_available.py','figures/all_available','absolute_performance'),
 ('02_performance_and_fields','code/plot_all_available.py','figures/all_available','paired_performance'),
]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--experiment',choices=['01_behavioral_diversity','02_performance_and_fields'])
    options=parser.parse_args()
    failures=[]
    for folder,source,dest,name in ITEMS:
        if options.experiment and folder!=options.experiment:
            continue
        base=ROOT/'Experiment'/folder;out=base/dest;qa=out/'qa';qa.mkdir(parents=True,exist_ok=True)
        jobs=[('source',['validate_figure.py',str(base/source),'--json']),
              ('text',['audit_pdf_text.py',str(out/f'{name}.pdf'),'--min-pt','5','--json']),
              ('collision',['audit_figure_collisions.py',str(out/f'{name}.pdf'),'--json-out',str(qa/f'{name}.collision.json')])]
        for kind,args in jobs:
            result=subprocess.run([sys.executable,str(SKILL/args[0]),*args[1:]],capture_output=True,text=True)
            if kind!='collision':
                try:value=json.loads(result.stdout)
                except json.JSONDecodeError:value={'stdout':result.stdout,'stderr':result.stderr,'returncode':result.returncode}
                (qa/f'{name}.{kind}.json').write_text(json.dumps(value,indent=2)+'\n')
            print(name,kind,'exit',result.returncode,flush=True)
            if result.returncode:
                failures.append((name,kind,result.stdout[-2500:],result.stderr[-500:]))
    if failures:
        print(json.dumps(failures,indent=2));raise SystemExit(1)

if __name__=='__main__':main()
