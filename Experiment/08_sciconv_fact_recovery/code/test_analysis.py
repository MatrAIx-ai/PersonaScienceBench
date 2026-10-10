"""Offline checks protecting the recovery definition and independent trial count."""
import unittest
from analyze import parse_fraction,task_means,analyze,ARMS
class RecoveryTests(unittest.TestCase):
    def test_native_fraction(self):
        self.assertEqual(parse_fraction(' 2 / 3 ',3),(2,3))
        self.assertEqual(parse_fraction('0/4',4),(0,4))
    def test_invalid_fraction(self):
        for value in ['1/0','4/3','-1/3','1.5/3','invalid','1/2/3']:
            with self.assertRaises(ValueError):parse_fraction(value)
        with self.assertRaises(ValueError):parse_fraction('2/3',4)
    def test_case_weighting(self):
        rows=[dict(case='a',domain='d',study_id='s',status='scored',recovery_share=x) for x in [0,1,1]]
        rows+=[dict(case='b',domain='d',study_id='t',status='scored',recovery_share=0)]
        t=task_means(rows,'recovery_share')
        self.assertEqual([r['episodes'] for r in t],[3,1])
        self.assertAlmostEqual(sum(r['value'] for r in t)/len(t),1/3)
    def test_invalid_judgement_excluded(self):
        self.assertEqual(task_means([dict(case='a',status='invalid_or_missing_saved_judgement',recovery_share=None)],'recovery_share'),[])
    def test_paired_identical_conditions(self):
        rows=[]
        for view in ['original','after_repair']:
            for trial,value in [(1,0.5),(2,1),(3,0)]:
                for arm in ARMS:
                    rows.append(dict(view=view,trial=trial,arm=arm,case='d/disambiguation/a',domain='d',study_id='a',mode='disambiguation',status='scored',facts_total=2,recovery_share=value,FRR=int(value==1),full_recovery=int(value==1),researcher_replies=2,reply_words_mean=5,question_limit_hit=0))
        result=analyze({'episodes':rows})
        for s in result['views']['original']['panels']['all']['paired_recovery_vs_off'].values():
            self.assertEqual(s['mean'],0);self.assertEqual(s['ci95'],[0,0]);self.assertEqual(s['episodes'],3)
if __name__=='__main__':unittest.main()
