import os
import shutil
import tempfile
import unittest

from uwa.systest import SysTestSuite, UWA_PASS, UWA_FAIL, UWA_ERROR
from skeletonSysTest import SkeletonSysTest

class SysTestSuiteTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.stSuite = SysTestSuite("StgFEM", "RegressionTests")
        self.inputFiles = [os.path.join("input","TempDiffusion.xml")]

    def tearDown(self):
        self.stSuite = None
        shutil.rmtree(self.basedir)

    def test_addStdTest(self):
        self.stSuite.addStdTest(SkeletonSysTest, self.inputFiles, 
            statusToReturn=UWA_PASS("testPass"), nproc=1)
        sysTestsList = self.stSuite.sysTests
        self.assertEqual(len(self.stSuite.sysTests), 1)
        addedTest = sysTestsList[0]
        self.assertTrue(isinstance(addedTest, SkeletonSysTest))
        self.assertEqual(addedTest.testType, "Skeleton")
        self.assertEqual(addedTest.inputFiles, self.inputFiles)
        self.assertEqual(addedTest.testStatus, None)
        # TODO: add another test to suite


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysTestSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
