import math
import unittest
from synthetic_shift import weighted_quantile, vanilla_quantile, seed, ratio

class QuantileControls(unittest.TestCase):
    def test_known_unweighted_positive(self):
        self.assertEqual(vanilla_quantile([1,2,3,4],.4),3)
        self.assertEqual(weighted_quantile([1,2,3,4],[1]*4,1,.4),3)
    def test_infinity_boundary(self):
        self.assertTrue(math.isinf(weighted_quantile([1,2,3,4],[1]*4,10,.1)))
        self.assertTrue(math.isinf(vanilla_quantile([1,2],.1)))
    def test_test_atom_tamper_is_detected(self):
        # Deliberate mutant omits test weight from threshold; must disagree.
        mutant=sorted([1,2,3,4])[math.ceil(4*.9)-1]
        actual=weighted_quantile([1,2,3,4],[1]*4,10,.1)
        self.assertNotEqual(actual,mutant)
        self.assertEqual(mutant,4)
    def test_weight_association(self):
        self.assertEqual(weighted_quantile([30,10,20],[8,1,1],1,.4),30)
    def test_weight_scale_invariance(self):
        args=([1,2,3],[1,2,4],1,.4)
        self.assertEqual(weighted_quantile(*args), weighted_quantile(args[0],[w*17 for w in args[1]],17,.4))
    def test_ties(self):
        self.assertEqual(weighted_quantile([2,2,2],[1,1,1],1,.5),2)
    def test_invalid_inputs(self):
        for args in [([],[],1,.1),([1],[1,2],1,.1),([1],[0],1,.1),([1],[-1],1,.1),([1],[math.nan],1,.1),([1],[1],0,.1),([1],[1],1,0),([-1],[1],1,.1)]:
            with self.subTest(args=args), self.assertRaises(ValueError): weighted_quantile(*args)
    def test_ratio_expectation_one(self):
        for q in [.1,.5,.9]: self.assertAlmostEqual(.1*ratio(1,q,.1)+.9*ratio(0,q,.1),1)
    def test_seed_split(self):
        self.assertEqual(seed(1,0,'calibration'),seed(1,0,'calibration'))
        self.assertNotEqual(seed(1,0,'calibration'),seed(1,0,'no_shift'))
        self.assertNotEqual(seed(1,0,'calibration'),seed(1,1,'calibration'))

if __name__=='__main__': unittest.main(verbosity=2)
