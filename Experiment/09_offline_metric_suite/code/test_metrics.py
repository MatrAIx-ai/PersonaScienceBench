"""Meaningful offline invariants and exact enumeration checks."""
import unittest,itertools,json,sys
import numpy as np
from extract import pattern,DATA,ARMS,key
from analyze import failure_probabilities,repetition,task_values,summary
from self_repetition import normalize,reuse,messages
from word_repetition import tokenize

class MetricsTests(unittest.TestCase):
 def test_word_windows_allow_surrounding_edits(self):
  a=tokenize('alpha beta gamma delta')
  b=tokenize('Other: alpha, BETA gamma delta! Afterwards.')
  self.assertAlmostEqual(reuse([a,b],4)[0],100/3)
  self.assertEqual(reuse([a,a],4)[0],100)
  self.assertEqual(reuse([a,tokenize('alpha beta gamma changed')],4)[0],0)
 def test_word_tokenization_preserves_boundaries_and_scripts(self):
  self.assertNotEqual(tokenize('therapist'),tokenize('the rapist'))
  self.assertEqual(tokenize('हिंदी शब्द'),('हिंदी','शब्द'))
  self.assertEqual(tokenize('ПРИВЕТ мир'),('привет','мир'))
  words=tokenize('科学研究需要明确实验条件')
  self.assertEqual(''.join(words),'科学研究需要明确实验条件')
  self.assertGreater(len(words),1);self.assertTrue(any(len(w)>1 for w in words))
 def test_within_trace_repetition_has_no_self_comparison(self):
  a='abcdefghij';b='klmnopqrst'
  self.assertIsNone(reuse([a],4)[0])
  self.assertEqual(reuse([a,a],4)[0],100)
  self.assertEqual(reuse([a,b],4)[0],0)
  self.assertEqual(reuse([a,b,a],4)[0],50)
  # Repetition internal to a new message does not count as earlier-turn reuse.
  self.assertEqual(reuse([a,b*3],4)[0],0)
  self.assertIsNone(reuse(['a','b'],4)[0])
 def test_within_trace_unicode_and_role_isolation(self):
  self.assertEqual(normalize('ABC, DEF!'),normalize('abc def'))
  self.assertEqual(normalize('हिंदी'), 'हिंदी')
  self.assertEqual(normalize('Text\n> quoted content\n```code```'), 'text')
  events=[dict(type='researcher_question',payload={'question':'actor content'}),dict(type='researcher_reply',payload={'answer':'sim content'}),dict(type='final_specification',payload={'answer':'final artifact'})]
  out=messages(events,'sciconvbench')
  self.assertEqual(out['actor'],['actorcontent']);self.assertEqual(out['simulator'],['simcontent'])
 def test_pattern_ignores_prose_but_preserves_decisions(self):
  events=[{'type':'initial_request','payload':{'message':'hidden prose'}},{'type':'agent_handoff','payload':{'answer':'plan'}},{'type':'researcher_decision','payload':{'phase':'approach_review','action':'continue','interaction':'next_task','message':'feedback'}},{'type':'agent_handoff','payload':{'answer':'result'}},{'type':'researcher_decision','payload':{'phase':'result_review','action':'stop','interaction':'conclude'}}]
  seq,n=pattern(events,'bixbench');self.assertEqual(n,2);self.assertEqual(len(seq),3)
  other=json.loads(json.dumps(events));other[2]['payload']['message']='different language';self.assertEqual(pattern(other,'bixbench')[0],seq)
  other[2]['payload']['action']='stop';self.assertNotEqual(pattern(other,'bixbench')[0],seq)
  self.assertNotEqual(pattern([events[0],events[3],events[4],events[1],events[2]],'bixbench')[0],seq)
 def test_sciconv_length_sensitivity(self):
  ev=[{'type':'researcher_question'},{'type':'researcher_reply'},{'type':'final_specification'}]
  self.assertEqual(pattern(ev,'sciconvbench')[1],1)
  self.assertNotEqual(pattern(ev,'sciconvbench')[0],pattern(ev[:2]+ev,'sciconvbench')[0])
 def test_repetition_no_self_pairs(self):
  x=[dict(pattern_hash='a',interaction_length=1),dict(pattern_hash='b',interaction_length=2)]
  self.assertEqual(repetition(x,x,True),(0.,1));self.assertEqual(repetition(x,x,False),(50.,4))
  self.assertEqual(repetition(x[:1],x[:1],True),(None,0));self.assertEqual(repetition(x,x,True,True),(None,0))
 def test_allocation_matches_brute_force(self):
  off=[1,0,1];personas=[[1,0],[1],[0,1],[0]]
  for m in [1,2,3]:
   fo,fm=failure_probabilities(off,personas,m);by_subset=[]
   for inds in itertools.combinations(range(4),m):by_subset.append(np.mean([1-np.prod(x) for x in itertools.product(*[personas[i] for i in inds])]))
   self.assertAlmostEqual(fm,np.mean(by_subset));self.assertAlmostEqual(fo,np.mean([any(v==0 for v in x) for x in itertools.combinations(off,m)]))
 def test_task_not_episode_weighted(self):
  rows=[dict(source='x',task_id='a',study_id='a',family='f',score=v) for v in [0,0,0]]+[dict(source='x',task_id='b',study_id='b',family='f',score=100)]
  self.assertEqual(summary(task_values(rows,'score'))['mean'],50)
 def test_saved_data_consistency(self):
  snap=json.loads((DATA/'snapshot.json').read_text());s=json.loads((DATA/'summary.json').read_text())
  for name in ['scores','traces','recovery']:self.assertEqual(len(snap[name]),len({key(r) for r in snap[name]}))
  self.assertEqual(set(s['arms']),set(ARMS));self.assertEqual(len(snap['scores']),2200)
  for r in s['repetition']:
   if r['persona_i']==r['persona_j'] and r['persona_i'] in ARMS[3:]:self.assertIsNone(r['mean'])
   if r['mean'] is not None:self.assertTrue(-1e-10<=r['mean']<=100+1e-10)
  for r in s['failure_coverage']:
   if r['strategy'] in ['off','mixture'] and r['mean'] is not None:self.assertTrue(-1e-10<=r['mean']<=100+1e-10)
  old=json.loads((DATA.parents[1]/'08_sciconv_fact_recovery/data/snapshot.json').read_text())
  oldidx={(r['case'],r['arm'],r['trial']):r for r in old['episodes'] if r['view']=='original' and r.get('recovery_share') is not None}
  for r in snap['recovery']:
   k=(r['task_id'],r['arm'],r['trial'])
   if k in oldidx:self.assertAlmostEqual(r['recovery'],100*oldidx[k]['recovery_share'])
  # Source-level original native means reproduce the established saved analysis.
  prev=json.loads((DATA.parents[1]/'02_performance_and_fields/data/all_available/summary.json').read_text())
  for r in s['outcomes']:
   if r['metric']=='native_score' and r['level']=='source':
    v=prev['absolute']['original'][r['arm']]['source'][r['group']]
    if v['mean'] is None:self.assertIsNone(r['mean'])
    else:self.assertAlmostEqual(r['mean'],v['mean'])
 def test_individual_coverage_preserves_budget_and_baseline(self):
  s=json.loads((DATA/'summary.json').read_text())
  rows=s['persona_failure_coverage']
  for arm in ARMS:
   selected=[r for r in rows if r['arm']==arm]
   self.assertEqual([r['budget'] for r in selected],[1] if arm in ARMS[3:] else [1,2,3])
   self.assertTrue(all(r['tasks']==40 for r in selected))
   self.assertEqual(sorted(r['mean'] for r in selected),[r['mean'] for r in selected])
  for row in [r for r in rows if r['arm']==ARMS[0]]:
   original=next(r for r in s['failure_coverage'] if r['strategy']=='off' and r['budget']==row['budget'] and r['variant']=='primary' and r['level']=='source' and r['group']=='sciconvbench')
   self.assertAlmostEqual(row['mean'],original['mean'])
   np.testing.assert_allclose(row['ci95'],original['ci95'])
if __name__=='__main__':unittest.main()
