"""Offline within-conversation word n-gram reuse, with dictionary Han segmentation."""
import json
import logging
import re
import unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version
import jieba
import regex
from extract import ROOT,BASE,DATA,ARMS,sha,write_json,write_csv
from self_repetition import messages,reuse,analyze_rows
from analyze import flatten

WINDOWS=(1,2,3,4)
PRIMARY=4
jieba.setLogLevel(logging.ERROR)
SEGMENTER=jieba.Tokenizer()
SEGMENTER.tmp_dir='/tmp'


def tokenize(text):
    text=re.sub(r'```.*?```','',text,flags=re.S)
    text=re.sub(r'^\s*>.*$','',text,flags=re.M)
    text=unicodedata.normalize('NFKC',text).casefold().replace('’',"'")
    tokens=[]
    for span in regex.split(r'(\p{Script=Han}+)',text):
        if not span:continue
        if regex.fullmatch(r'\p{Script=Han}+',span):
            tokens.extend(SEGMENTER.cut(span,HMM=False))
        else:
            tokens.extend(regex.findall(r"[\p{L}\p{M}\p{N}]+(?:'[\p{L}\p{M}\p{N}]+)*",span))
    return tuple(tokens)


def extract_one(trace):
    meta={k:trace[k] for k in ['source','task_id','study_id','family','arm','trial']}
    if trace.get('exclusion') is not None:
        return [meta|dict(role=role,width=n,value=None,exclusion=trace['exclusion']) for role in ['simulator','actor'] for n in WINDOWS],[]
    raw=(ROOT/trace['trace_path']).read_bytes();assert sha(raw)==trace['sha256']
    events=[json.loads(line) for line in raw.splitlines() if line.strip()]
    rows=[];turns=[]
    for role,texts in messages(events,trace['source'],normalizer=tokenize).items():
        for n in WINDOWS:
            value,eligible,parts=reuse(texts,n)
            rows.append(meta|dict(role=role,width=n,value=value,exclusion=None if value is not None else 'fewer_than_two_length_eligible_messages',messages=len(texts),eligible_messages=eligible,scored_turns=len(parts),word_tokens=sum(map(len,texts)),trace_sha256=trace['sha256']))
            turns.extend([meta|dict(role=role,width=n,**r) for r in parts])
    return rows,turns


def report(s):
    from report import table,cell
    chosen=lambda role,n:[r for r in s['cells'] if r['role']==role and r['width']==n and r['panel']=='common' and r['level']=='all']
    lines=['# Word-based within-conversation repetition','',
           'Current panel A uses exact four-word sequences separately for simulator and actor. This revision was requested after viewing the character-based results; it is exploratory. The 40-character analysis remains available in SELF_REPETITION.md and the prior figure is archived under revisions/v5_character_matching/. No new model calls or embeddings.','',
           '## Definition','',
           'For every later length-eligible message, slide a four-token window one token at a time. A window matches if its ordered token tuple occurred in an earlier message of the same role and conversation. Divide matched windows by all current-message windows, then average eligible later turns. The first eligible message only provides history; within-current-message repetition alone is not counted. Exact token equality is required: no stemming, synonym matching or semantic comparison. Short phrases can match despite surrounding edits.','',
           'Tokens: remove code fences and Markdown blockquote lines; Unicode NFKC and casefold. Han-script spans use jieba 0.42.1 dictionary segmentation with HMM=False; other spans use Unicode letter/mark/number runs with internal apostrophes retained. Punctuation/whitespace separate words, so word boundaries are preserved. Hindi combining marks and Cyrillic letters are retained. Stopwords and numbers are retained. No tokenizer model inference or translation. Tokenization and language differences still affect comparability; Chinese dictionary words are approximations, not guaranteed linguistic segmentation.','',
           '## Aggregation and interpretation','',
           'Average turns within episode, eligible trials within question, questions within benchmark, then benchmarks equally. Retain a common five-setting question panel separately for each role/window size. Require at least two messages containing enough tokens; unavailable is not zero. CIs use 20,000 source-study bootstrap draws conditional on saved trials. Paired contrasts compare question means; available repeat counts differ. The four-word choice was fixed before this extraction; two- and three-word results are sensitivities. Unigram reuse is provided as vocabulary reuse, which naturally includes recurring scientific terms and function words and should not be called conversational stagnation.','',
           table(['Role','Words/window','Common questions','Sources'],[[r['role'],r['width'],r['questions'],json.dumps(r['source_counts'],sort_keys=True)] for r in s['coverage']]),'']
    for role in ['simulator','actor']:
        lines.extend(['## '+role.capitalize()+' — four-word repetition','',table(['Setting','Repeated word windows % [95% CI]','Paired Δ vs off (pp)'],[[r['arm'].replace('candidate_','').replace('persona_off','Off'),cell(r),'Reference' if r['arm']==ARMS[0] else cell(next(c for c in s['contrasts'] if c['arm']==r['arm'] and c['role']==role and c['width']==PRIMARY))] for r in chosen(role,PRIMARY)]),''])
    lines.extend(['## Window-size sensitivity','',table(['Role','Words/window','Off','155','001','003','046'],[[role,n,*[f"{r['mean']:.3f}" for r in chosen(role,n)]] for role in ['simulator','actor'] for n in WINDOWS]),'',
                  'These are different definitions and can have different eligible turns/questions. Four-word and 40-character rates are not interchangeable. Higher measured overlap under shorter phrases does not imply more mode collapse. Required scientific vocabulary, stock politeness and legitimate fact restatement can contribute; paraphrases remain undetected. Persona language, output length and dialogue duration can confound comparisons. Intervals are pointwise; no new significance claims or persona ranking are selected from the sensitivities.','',
                  '[Figure](figures/metric_suite.pdf) · [Notebook](metric_suite.ipynb). Source tables are data/word_repetition_{episodes,turns,cases,cells,contrasts}.csv. Snapshots contain numeric values and hashes, not transcripts or word strings.','',
                  'Reproduce with `OPENBLAS_NUM_THREADS=1 .venv/bin/python Experiment/09_offline_metric_suite/code/word_repetition.py`. Dictionary/version provenance is in data/word_repetition_summary.json.'])
    (BASE/'WORD_REPETITION.md').write_text('\n'.join(lines)+'\n')


def main():
    SEGMENTER.initialize()
    snap=json.loads((DATA/'snapshot.json').read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:pieces=list(pool.map(extract_one,snap['traces']))
    rows=[r for a,_ in pieces for r in a];turns=[r for _,b in pieces for r in b]
    s=analyze_rows(rows,windows=WINDOWS)
    dictionary=Path(jieba.__file__).parent/'dict.txt'
    s['method']=dict(primary_window=PRIMARY,window_unit='word tokens',sensitivity_windows=[2,3],vocabulary_reuse_window=1,jieba_version=version('jieba'),regex_version=version('regex'),dictionary_sha256=sha(dictionary.read_bytes()),segmentation='Han: jieba HMM=False; other scripts: Unicode L/M/N runs, internal apostrophes retained',matching='exact ordered token tuple; previous same-role messages within episode only',weighting='equal questions within source, equal represented-source weights; available trials averaged within question',source_sha256=sha((DATA/'snapshot.json').read_bytes()),inference_calls=0)
    write_json(DATA/'word_repetition_summary.json',s)
    for name,rr in [('episodes',rows),('turns',turns),('cases',s['cases']),('cells',s['cells']),('contrasts',s['contrasts'])]:write_csv(DATA/f'word_repetition_{name}.csv',flatten(rr))
    report(s)
    print(json.dumps(s['coverage'],indent=2),flush=True)
    for r in s['cells']:
        if r['width']==PRIMARY and r['panel']=='common' and r['level']=='all':print(r['role'],r['arm'],r['mean'],r['ci95'],flush=True)


if __name__=='__main__':main()
