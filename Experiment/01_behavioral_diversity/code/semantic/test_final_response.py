import unittest
from itertools import product
import numpy as np
from final_response import kernel,direct_components,quadratic_samples,holm

class FinalResponseChecks(unittest.TestCase):
 def setUp(self):
  rng=np.random.default_rng(19);self.x=rng.normal(size=(5,4));self.y=rng.normal(size=(5,4))
  self.x/=np.linalg.norm(self.x,axis=1,keepdims=True);self.y/=np.linalg.norm(self.y,axis=1,keepdims=True)
 def test_all_label_swaps_equal_direct_distances(self):
  k=kernel(self.x,self.y)
  for signs in product([-1,1],repeat=5):
   signs=np.array(signs);x=np.where(signs[:,None]>0,self.x,self.y);y=np.where(signs[:,None]>0,self.y,self.x)
   b,wi,wj=direct_components(x,y)
   self.assertAlmostEqual(float(signs@k@signs/20),b-(wi+wj)/2,places=12)
 def test_bootstrap_duplicate_question_exclusion(self):
  ids=np.array([0,0,2,3,3]);w=np.bincount(ids,minlength=5);k=kernel(self.x,self.y)
  pairs=[(a,b) for a in ids for b in ids if a!=b]
  expected=np.mean([k[a,b] for a,b in pairs])
  actual=quadratic_samples(w[None,:],k)[0]/(len(ids)**2-sum(w*w))
  self.assertAlmostEqual(actual,expected,places=12)
 def test_holm_and_identical_personas(self):
  np.testing.assert_allclose(holm([.03,.001,.2,.02]),[.06,.004,.2,.06])
  np.testing.assert_array_equal(kernel(self.x,self.x),np.zeros((5,5)))
if __name__=='__main__':unittest.main()
