import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa.systest import SysTestRunner, SysTestSuite, UWA_PASS, UWA_FAIL, UWA_ERROR
from skeletonSysTest import SkeletonSysTest

class SysTestRunnerTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.stRunner = SysTestRunner()
        self.inputFiles = [os.path.join("input","TempDiffusion.xml")]
        self.skelTest1 = SkeletonSysTest(self.inputFiles,
            "output/SkeletonTest1",
            statusToReturn=UWA_PASS("testPass"), nproc=1)
        self.skelTest2 = SkeletonSysTest(self.inputFiles, 
            "output/SkeletonTest2",
            statusToReturn=UWA_FAIL("testFail"), nproc=1)
        self.skelTest3 = SkeletonSysTest(self.inputFiles,
            "output/SkeletonTestSub",
            statusToReturn=UWA_ERROR("testError"), nproc=1)
        self.skelTest4 = SkeletonSysTest(self.inputFiles,
            "output/SkeletonTestSub",
            statusToReturn=UWA_PASS("testPass2"), nproc=1)

    def tearDown(self):
        self.stRunner = None
        shutil.rmtree(self.basedir)

    def test_runTest(self):
        skelTest = SkeletonSysTest(self.inputFiles, "output/SkeletonTest1",
            statusToReturn=UWA_PASS("testPass"), nproc=1)
        testResult = self.stRunner.runTest(skelTest)
        self.assertEqual(testResult.statusStr, UWA_PASS.statusStr)
        skelTest = SkeletonSysTest(self.inputFiles, "output/SkeletonTest2",
            statusToReturn=UWA_FAIL("testFail"), nproc=1)
        testResult = self.stRunner.runTest(skelTest)
        self.assertEqual(testResult.statusStr, UWA_FAIL.statusStr)
    
    def test_runSuite(self):
        skelSuite = SysTestSuite("StgFEM", "RegressionTests", 
            sysTests=[self.skelTest1, self.skelTest2])
        testResults = self.stRunner.runSuite(skelSuite)
        self.assertEqual(len(testResults), 2)
        self.assertEqual(testResults[0].statusStr, UWA_PASS.statusStr)
        self.assertEqual(testResults[1].statusStr, UWA_FAIL.statusStr)

    def test_runSuite_withSubs(self):
        skelSuite = SysTestSuite("StgFEM", "RegressionTests", 
            sysTests=[self.skelTest1, self.skelTest2])
        subSuite = SysTestSuite("StgFEM", "RegressionTests-sub")
        skelSuite.addSubSuite(subSuite)
        subSuite.sysTests.append(self.skelTest3)
        testResults = self.stRunner.runSuite(skelSuite)
        self.assertEqual(len(testResults), 3)
        self.assertEqual(testResults[0].statusStr, UWA_PASS.statusStr)
        self.assertEqual(testResults[1].statusStr, UWA_FAIL.statusStr)
        self.assertEqual(testResults[2].statusStr, UWA_ERROR.statusStr)

    def test_runSuite_subOnly(self):
        subSuite1 = SysTestSuite("StgFEM", "RegressionTests-sub1",
            sysTests=[self.skelTest1, self.skelTest2])
        subSuite2 = SysTestSuite("StgFEM", "RegressionTests-sub2",
            sysTests=[self.skelTest2, self.skelTest3])
        masterSuite = SysTestSuite("StgFEM", "RegressionTests",
            subSuites=[subSuite1, subSuite2])
        testResults = self.stRunner.runSuite(masterSuite)
        self.assertEqual(len(testResults), 4)
        self.assertEqual(testResults[0].statusStr, UWA_PASS.statusStr)
        self.assertEqual(testResults[1].statusStr, UWA_FAIL.statusStr)
        self.assertEqual(testResults[2].statusStr, UWA_FAIL.statusStr)
        self.assertEqual(testResults[3].statusStr, UWA_ERROR.statusStr)

    def test_runTests(self):
        sysTests = [self.skelTest1, self.skelTest2]
        testResults = self.stRunner.runTests(sysTests)
        self.assertEqual(len(testResults), 2)
        self.assertEqual(testResults[0].statusStr, UWA_PASS.statusStr)
        self.assertEqual(testResults[1].statusStr, UWA_FAIL.statusStr)
    
    def test_runSuites(self):
        suite1 = SysTestSuite("StgFEM", "RegressionTests", 
            sysTests=[self.skelTest1, self.skelTest2])
        subSuite = SysTestSuite("StgFEM", "RegressionTests-sub")
        suite1.addSubSuite(subSuite)
        subSuite.sysTests.append(self.skelTest3)
        suite2 = SysTestSuite("StgFEM", "PerformanceTests",
            sysTests=[self.skelTest4])
        suite3 = SysTestSuite("PICellerator", "RegressionTests",
            sysTests=[self.skelTest2, self.skelTest4])
        testResults = self.stRunner.runSuites([suite1, suite2, suite3])

def suite():
    suite = unittest.TestSuite()
    #suite.addTest(unittest.makeSuite(SysTestRunnerTestCase, 'test'))
    suite.addTest(SysTestRunnerTestCase("test_runSuites"))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
