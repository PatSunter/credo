import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa.systest import *

class SysTestRunnerTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.stRunner = SysTestRunner(nproc=1)

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_printResultsSummary(self):
        sysTests = [RestartTest(["Multigrid.xml"],"./output"),
            RestartTest("Multigrid2.xml","./output"),
            RestartTest("Multigrid3.xml","./output"),
            RestartTest("Multigrid4.xml","./output") ]
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
