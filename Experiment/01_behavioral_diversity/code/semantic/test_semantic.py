"""Check statistical formulas and simulator-then-actor event alignment."""
import unittest
import numpy as np
from analyze import pair_matrix,parse_events,within

class SemanticChecks(unittest.TestCase):
    def test_adjusted_manual_negative(self):
        # Identical finite samples have nonzero W but cross-pairs include matching
        # samples: negative excess is valid and must not be clipped.
        x=np.array([[1.,0.],[0.,1.]])
        m,w=pair_matrix([x,x],True)
        self.assertAlmostEqual(w[0],1)
        self.assertAlmostEqual(m[0,1],-.5)
        self.assertTrue(np.allclose(m,m.T));self.assertEqual(m[0,0],0)
    def test_separated_repeats(self):
        x=np.array([[1.,0.],[1.,0.]]);y=-x
        m,_=pair_matrix([x,y],True);self.assertAlmostEqual(m[0,1],2)
    def test_single_repeat_rejected(self):
        with self.assertRaises(ValueError):within(np.array([[1.,0.]]))
    def test_pairing_terminal_and_preintervention(self):
        def e(t,p):return {'type':t,'payload':p}
        events=[e('initial_request',{'message':'task'}),e('researcher_question',{'question':'before'}),e('researcher_reply',{'answer':'one'}),e('researcher_question',{'question':'response'}),e('researcher_reply',{'answer':'two'})]
        r,pre=parse_events(events)
        self.assertEqual(pre,1);self.assertEqual(len(r),2)
        self.assertEqual(r[0]['actor'],'response');self.assertIsNone(r[1]['actor'])
        self.assertEqual([x['round'] for x in r],[1,2])

if __name__=='__main__':unittest.main()
