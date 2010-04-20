import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa.io.stgcvg import CvgFileInfo
import uwa.analysis
from uwa.analysis.fields import FieldTest, FieldTestsInfo, FieldResult

class AnalysisFieldsTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_checkFieldConvergence(self):
        fTest = FieldTest('TemperatureField', tol=3e-2)
        cvgFileInfo = CvgFileInfo("./output/CosineHillRotate-analysis.cvg")
        cvgFileInfo.dofColMap[0]=1
        fRes = fTest.checkFieldConvergence(cvgFileInfo)
        self.assertEqual(fRes.fieldName, fTest.name)
        self.assertEqual(fRes.tol, fTest.tol)
        self.assertEqual(fRes.dofErrors[0], 0.00612235812)

    def testConvergence(self):
        fieldTests = FieldTestsInfo()
        fTest = FieldTest('TemperatureField', tol=3e-2)
        fieldTests.add(fTest)
        fResults = fieldTests.testConvergence('./output')
        self.assertEqual(len(fResults), 1)
        self.assertEqual(fResults[0].fieldName, fTest.name)
        self.assertEqual(fResults[0].tol, fTest.tol)
        self.assertEqual(fResults[0].dofErrors[0], 0.00612235812)

    def test_checkErrorsWithinTol(self):
        fRes = FieldResult('TemperatureField', 0.3, [0.1,0.2])
        self.assertTrue(fRes.checkErrorsWithinTol())
        fRes = FieldResult('TemperatureField', 0.3, [0.4,0.2])
        self.assertFalse(fRes.checkErrorsWithinTol())

    def test_addFieldTest(self):
        fieldTests = FieldTestsInfo()
        self.assertEqual(fieldTests.fields, {})
        fieldTests.setAllTols(0.02)
        self.assertEqual(fieldTests.fields, {})
        tempFT = FieldTest('TemperatureField')
        fieldTests.add(tempFT)
        velFT = FieldTest('VelocityField')
        fieldTests.add(velFT)
        self.assertEqual(fieldTests.fields, {'TemperatureField':tempFT,\
            'VelocityField':velFT})

    def test_setAllFieldTolerances(self):
        fieldTests = FieldTestsInfo()
        fieldTests.setAllTols(0.02)
        tempFT = FieldTest('TemperatureField')
        velFT = FieldTest('VelocityField', 0.07)
        fieldTests.fields = {'TemperatureField':tempFT, 'VelocityField':velFT} 
        fieldTol = 3e-2
        fieldTests.setAllTols(fieldTol)
        for fieldTest in fieldTests.fields.values():
            self.assertEqual(fieldTest.tol, fieldTol)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AnalysisFieldsTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
