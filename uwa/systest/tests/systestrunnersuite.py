import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa.systest import SysTestRunner, UWA_PASS, UWA_FAIL, UWA_ERROR
from skeletonSysTest import SkeletonSysTest

class SysTestRunnerTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.stRunner = SysTestRunner()
        self.inputFiles = [os.path.join("input","TempDiffusion.xml")]

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_printResultsSummary(self):
        sysTests = [SkeletonSysTest(self.inputFiles[0],"./output"),
            SkeletonSysTest(self.inputFiles[0],"./output"),
            SkeletonSysTest(self.inputFiles[0],"./output"),
            SkeletonSysTest(self.inputFiles[0],"./output") ]
        results = [UWA_PASS("Good"), 
            UWA_PASS("Excellent test"),
            UWA_FAIL("Fields outside tolerance"),
            UWA_ERROR("Job failed to run")]
        self.stRunner.printResultsSummary(sysTests, results)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysTestRunnerTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
