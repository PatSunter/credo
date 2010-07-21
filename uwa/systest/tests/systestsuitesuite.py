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
        self.stSuite.addStdTest(SkeletonSysTest, self.inputFiles, 
            statusToReturn=UWA_FAIL("testFail"), nproc=1)
        self.assertEqual(len(self.stSuite.sysTests), 2)
        secondTest = sysTestsList[1]
        self.assertTrue(isinstance(addedTest, SkeletonSysTest))
        self.assertEqual(addedTest.testType, "Skeleton")
        self.assertEqual(addedTest.inputFiles, self.inputFiles)
        self.assertEqual(addedTest.testStatus, None)
    
    def test_addSubSuite(self):
        subSuite1 = SysTestSuite("StgFEM", "RegressionTests-sub1")
        subSuite2 = SysTestSuite("StgFEM", "RegressionTests-sub2")
        self.stSuite.addSubSuite(subSuite1)
        self.stSuite.addSubSuite(subSuite2)
        self.assertEqual(len(self.stSuite.subSuites), 2)
        self.assertEqual(self.stSuite.subSuites[0], subSuite1)
        self.assertEqual(self.stSuite.subSuites[1], subSuite2)
        #Make sure don't get list confused etc
        self.assertRaises(TypeError, self.stSuite.addSubSuite,
            [subSuite1, subSuite2])

    def test_newSubSuite(self):
        subSuite1 = self.stSuite.newSubSuite("StgFEM", "RegressionTests-sub1")
        subSuite2 = self.stSuite.newSubSuite("StgFEM", "RegressionTests-sub2")
        self.assertEqual(len(self.stSuite.subSuites), 2)
        self.assertEqual(self.stSuite.subSuites[0], subSuite1)
        self.assertEqual(self.stSuite.subSuites[1], subSuite2)
        self.assertTrue(isinstance(self.stSuite.subSuites[0], SysTestSuite))
        self.assertTrue(isinstance(self.stSuite.subSuites[1], SysTestSuite))

    def test_addSubSuites(self):
        subSuite1 = SysTestSuite("StgFEM", "RegressionTests-sub1")
        subSuite2 = SysTestSuite("StgFEM", "RegressionTests-sub2")
        self.stSuite.addSubSuites([subSuite1, subSuite2])
        self.assertEqual(len(self.stSuite.subSuites), 2)
        self.assertEqual(self.stSuite.subSuites[0], subSuite1)
        self.assertEqual(self.stSuite.subSuites[1], subSuite2)
        # Now try add some tests to these suites
        self.stSuite.addStdTest(SkeletonSysTest, self.inputFiles, 
            statusToReturn=UWA_FAIL("testFail"), nproc=1)
        subSuite2.addStdTest(SkeletonSysTest, self.inputFiles, 
            statusToReturn=UWA_PASS("testPass"), nproc=1)
        self.assertEqual(len(self.stSuite.sysTests), 1)
        self.assertEqual(len(self.stSuite.subSuites[0].sysTests), 0)
        self.assertEqual(len(self.stSuite.subSuites[1].sysTests), 1)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SysTestSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
