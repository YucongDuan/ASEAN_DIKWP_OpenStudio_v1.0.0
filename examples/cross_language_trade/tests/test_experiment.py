import unittest
from experiment import compare
class SemanticTests(unittest.TestCase):
    def pair(self):
        return ({'entity':'lot1','purpose':'compare','quantity':1000,'unit':'kg'}, {'entity':'lot1','purpose':'compare','quantity':1,'unit':'tonne'})
    def test_unit_equivalence(self):
        a,b=self.pair();self.assertEqual(compare(a,b)['status'],'equivalent')
    def test_purpose_change(self):
        a,b=self.pair();b['purpose']='send';self.assertIn('purpose',compare(a,b)['differences'])
    def test_unknown_unit(self):
        a,b=self.pair();b['unit']='crate';self.assertEqual(compare(a,b)['status'],'unresolved')
    def test_currency(self):
        a,b=self.pair();a['currency']='CNY';b['currency']='VND';self.assertEqual(compare(a,b)['status'],'mismatch')
    def test_nonfinite(self):
        a,b=self.pair();a['quantity']=float('nan');self.assertRaises(ValueError,compare,a,b)
if __name__=='__main__': unittest.main()
