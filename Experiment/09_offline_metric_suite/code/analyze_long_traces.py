"""Exploratory opportunity-to-repeat sensitivity on existing traces only."""
import csv
from self_repetition import analyze_rows
from extract import DATA,write_json,write_csv
from analyze import flatten

def main():
    rows=list(csv.DictReader((DATA/'self_repetition_episodes.csv').open()))
    for r in rows:
        r['width']=int(r['width'])
        r['value']=float(r['value']) if r['value'] else None
        r['eligible_messages']=int(r['eligible_messages']) if r['eligible_messages'] else 0
    results=[];coverage=[];contrasts=[]
    for minimum in [3,4]:
        s=analyze_rows([r for r in rows if r['eligible_messages']>=minimum])
        results.extend([r|dict(min_messages=minimum) for r in s['cells'] if r['panel']=='common' and r['level']=='all'])
        coverage.extend([r|dict(min_messages=minimum) for r in s['coverage']])
        contrasts.extend([r|dict(min_messages=minimum) for r in s['contrasts']])
    result=dict(interpretation='Exploratory length-conditioned subset, not selected by off repetition or persona differences. Require the same minimum messages within every included episode; retain questions with eligible data for all five settings. This post-treatment restriction changes the population and is not a causal estimate. Sources can disappear; do not compare its source mix directly with the main aggregate.',cells=results,coverage=coverage,contrasts=contrasts)
    write_json(DATA/'long_trace_repetition.json',result)
    write_csv(DATA/'long_trace_repetition.csv',flatten(results))
    for r in results:
        if r['width']==40:print(r['role'],r['min_messages'],r['arm'],r['tasks'],r['mean'],r['source_counts'],flush=True)

if __name__=='__main__':main()
