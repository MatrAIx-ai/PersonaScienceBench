"""Analysis-contract checks using isolated synthetic values, never figure data."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Experiment/shared'))
sys.path.insert(0,str(ROOT/'Experiment/01_behavioral_diversity/code'))
sys.path.insert(0,str(ROOT/'Experiment/02_performance_and_fields/code'))
from analysis_utils import summarize,paired
from analyze_behavior import script_features,normalized
from consolidate_performance import compatible,BRIDGE

class ContractTests(unittest.TestCase):
    def row(self,task,trial,arm,value):
        return dict(source='bixbench',task_id=task,study_id=task,trial=trial,arm=arm,value=value,status='scored',evaluator_version='native')

    def test_pair_before_averaging_incomplete_trials(self):
        rows=[self.row('a',1,'persona_off',0),self.row('a',2,'persona_off',100),self.row('a',1,'candidate_148',10)]
        s=summarize(paired(rows,'value','candidate_148'))
        self.assertEqual(s['mean'],10)
        self.assertEqual(s['episodes'],1)

    def test_repeats_do_not_reweight_tasks(self):
        rows=[self.row('a',t,'persona_off',0) for t in [1,2,3]]+[self.row('b',1,'persona_off',100)]
        s=summarize(rows)
        self.assertEqual(s['mean'],50)
        self.assertEqual(s['tasks'],2)
        self.assertEqual(s['episodes'],4)

    def test_missing_is_not_zero(self):
        rows=[self.row('a',1,'persona_off',None),self.row('b',1,'persona_off',100)]
        self.assertEqual(summarize(rows)['mean'],100)

    def test_shared_study_moves_together(self):
        rows=[self.row('a',1,'persona_off',0),self.row('b',1,'persona_off',100)]
        for row in rows:row['study_id']='one-study'
        s=summarize(rows)
        self.assertEqual(s['studies'],1)
        self.assertEqual(s['ci95'],[50,50])

    def test_asi_version_filter_is_strict(self):
        good=dict(source='asibench',evaluator_version=BRIDGE,status='scored')
        old=dict(good,evaluator_version='legacy')
        self.assertTrue(compatible(good,good))
        self.assertFalse(compatible(good,old))
        self.assertFalse(compatible(old,old))
        self.assertFalse(compatible(good,good,exclude_asi=True))

    def test_script_and_template_rules(self):
        self.assertIsNone(script_features('short')['script'])
        self.assertEqual(script_features('科学研究数据分析实验方法结果讨论'*4)['script'],'CJK')
        self.assertEqual(normalized('ＨＥＬＬＯ, World! ```private code```'),'helloworld')

if __name__=='__main__':unittest.main()
