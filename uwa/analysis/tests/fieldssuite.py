import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa.analysis.fields import FieldComparisonOp, FieldComparisonList
from uwa.analysis.fields import FieldComparisonResult
from uwa.modelresult import ModelResult

class AnalysisFieldsTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_getResult(self):
        mRes = ModelResult("test", './output/', 0)
        fComp = FieldComparisonOp('TemperatureField')
        fRes = fComp.getResult(mRes)
        self.assertEqual(fRes.fieldName, fComp.name)
        self.assertEqual(fRes.dofErrors[0], 0.00612235812)

    def test_getAllResults(self):
        mRes = ModelResult("test", './output', 0)
        fieldComps = FieldComparisonList()
        fComp = FieldComparisonOp('TemperatureField')
        fieldComps.add(fComp)
        fResults = fieldComps.getAllResults(mRes)
        self.assertEqual(len(fResults), 1)
        self.assertEqual(fResults[0].fieldName, fComp.name)
        self.assertEqual(fResults[0].dofErrors[0], 0.00612235812)

    def test_WithinTol(self):
        fRes = FieldComparisonResult('TemperatureField', [0.1,0.2])
        self.assertTrue(fRes.withinTol(0.3))
        fRes = FieldComparisonResult('TemperatureField', [0.4,0.2])
        self.assertFalse(fRes.withinTol(0.3))

    def test_addFieldComparisonOp(self):
        fieldCompares = FieldComparisonList()
        self.assertEqual(fieldCompares.fields, {})
        self.assertEqual(fieldCompares.fields, {})
        tempFT = FieldComparisonOp('TemperatureField')
        fieldCompares.add(tempFT)
        velFT = FieldComparisonOp('VelocityField')
        fieldCompares.add(velFT)
        self.assertEqual(fieldCompares.fields, {'TemperatureField':tempFT,\
            'VelocityField':velFT})

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AnalysisFieldsTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

