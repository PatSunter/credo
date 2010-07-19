import unittest

from uwa.systest.api import *

class SysTestResultTestCase(unittest.TestCase):
    def setUp(self):
        self.passMsg = "All fields passed."
        self.passResult = UWA_PASS(self.passMsg)
        self.failMsg = "One of the fields outside tolerance."
        self.failResult = UWA_FAIL(self.failMsg)
        self.errorMsg = "Model failed to run."
        self.errorResult = UWA_ERROR(self.errorMsg)

    def test_printBasic(self):
        resStr = "%s" % self.passResult
        self.assertEqual(resStr, UWA_PASS.statusStr)
        resStr = "%s" % self.failResult
        self.assertEqual(resStr, UWA_FAIL.statusStr)
        resStr = "%s" % self.errorResult
        self.assertEqual(resStr, UWA_ERROR.statusStr)

    def test_printDetailMsg(self):
        self.assertEqual(self.passResult.detailMsg, self.passMsg)
        self.assertEqual(self.failResult.detailMsg, self.failMsg)
        self.assertEqual(self.errorResult.detailMsg, self.errorMsg)

class SysTestNamesHandling(unittest.TestCase):
    def testGetStdTestName(self):
        self.assertRaises(TypeError, getStdTestName, "AnalyticTest",
            "Multigrid.xml", nproc=1)
        testNameSingle = getStdTestName("AnalyticTest", ["Multigrid.xml"],
            nproc=1, paramOverrides=None, solverOpts=None, nameSuffix=None)
        self.assertEqual(testNameSingle,
            "Multigrid-analyticTest-np1")    
        testNameMulti = getStdTestName("AnalyticTest", 
            ["Multigrid.xml", "Blah.xml"],
            nproc=1, paramOverrides=None, solverOpts=None, nameSuffix=None)
        self.assertEqual(testNameMulti, testNameSingle)
        testNameOvers = getStdTestName("AnalyticTest", 
            ["Multigrid.xml"],
            nproc=1, paramOverrides={"dim":3,"components.rheo.pert":45.6},
            solverOpts=None, nameSuffix=None)
        self.assertEqual(testNameOvers,
            "Multigrid-analyticTest-np1-pert-45_6-dim-3")    
        testNameSuffix = getStdTestName("AnalyticTest", 
            ["Multigrid.xml"],
            nproc=1, paramOverrides={"dim":3,"components.rheo.pert":45.6},
            solverOpts=None, nameSuffix="hipert")
        self.assertEqual(testNameSuffix,
            "Multigrid-analyticTest-np1-hipert")    

def suite():
    testResultSuite = unittest.TestSuite()
    testResultSuite.addTest(unittest.makeSuite(SysTestResultTestCase, 'test'))
    nameSuite = unittest.TestSuite()
    nameSuite.addTest(unittest.makeSuite(SysTestNamesHandling))
    multiSuite = unittest.TestSuite((testResultSuite, nameSuite))
    return multiSuite

if __name__ == '__main__':
    unittest.main()
