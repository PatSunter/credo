import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa.io import stgcvg 
from uwa.io.stgcvg import CvgFileInfo

class StgCVGTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_genConvergenceFileIndex(self):
        #TODO: should write the actual test convergence files,
        # perhaps in set-up
        cvgInfoEmpty = stgcvg.genConvergenceFileIndex(".")
        self.assertEqual(cvgInfoEmpty, {})
        cvgInfo = stgcvg.genConvergenceFileIndex("./output")
        self.assertEqual(len(cvgInfo), 2)
        self.assertEqual(cvgInfo['TemperatureField'].filename, \
            './output/CosineHillRotate-analysis.cvg')
        self.assertEqual(cvgInfo['TemperatureField'].dofColMap, {0:1})
        self.assertEqual(cvgInfo['VelocityField'].filename, \
            './output/Analytic2-analysis.cvg')
        self.assertEqual(cvgInfo['VelocityField'].dofColMap, {0:1})

    def test_checkFieldConvergence(self):
        cvgFileInfo = CvgFileInfo("./output/CosineHillRotate-analysis.cvg")
        cvgFileInfo.dofColMap[0]=1
        dofErrors = stgcvg.getDofErrors_Final(cvgFileInfo)
        self.assertEqual(len(dofErrors), 1)
        self.assertEqual(dofErrors[0], 0.00612235812)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StgCVGTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
