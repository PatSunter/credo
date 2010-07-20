import os
import inspect

from uwa.systest.api import *

class SysTestRunner:
    """Class that runs a set of :class:`~uwa.systest.api.SysTest`, usually
    collected into :class:`~uwa.systest.api.SysTestSuite` collections.

    For examples of how to use, see the UWA documentation, especially
    :ref:`uwa-examples-run-systest`.
    """

    def __init__(self):
        return

    def runTest(self, sysTest):
        """Run a given sysTest, and return the 
        :class:`uwa.systest.api.SysTestResult` it produces.
        Will also write an XML record of the System test, and each ModelRun
        and ModelResult in the suite that made up the test."""
        mSuite = sysTest.genSuite()
        mSuite.cleanAllOutputPaths()
        mSuite.cleanAllLogFiles()
        print "Writing pre-test info to XML"
        sysTest.writePreRunXML()
        mSuite.writeAllModelRunXMLs()
        suiteResults = mSuite.runAll()
        print "Checking test result:"
        testResult = sysTest.getStatus(suiteResults)
        mSuite.writeAllModelResultXMLs()
        print "Test result was %s" % testResult
        outFilePath = sysTest.updateXMLWithResult(suiteResults)
        print "Saved test result to %s" % (outFilePath)
        return testResult

    def runTests(self, sysTests, projName=None, suiteName=None):
        """Run all tests in the sysTests list.
        Will also save all appropriate XMLs (as discussed in :meth:`.runTest`)
        and print a summary of results."""
        results = []
        testTotal = len(sysTests)
        for testI, sysTest in enumerate(sysTests):
            print "Running System test %d/%d, with name '%s':" \
                % (testI+1, testTotal, sysTest.testName)
            results.append(self.runTest(sysTest))
        self.printResultsSummary(sysTests, results, projName, suiteName)
        return results
    
    def runSuite(self, suite):
        testTotal = len(suite.sysTests)
        print "Running System Test Suite for Project '%s', named '%s',"\
            " containing %d tests:"\
            % (suite.projectName, suite.suiteName, testTotal)
        # TODO: start Suite summary XML
        results = self.runTests(suite.sysTests, suite.projectName,
            suite.suiteName)
        # TODO: update XML with results
        return results

    def printResultsSummary(self, sysTests, results, 
            projName=None, suiteName=None):
        """Print a textual summary of the results of running a set of sys
        tests."""
        if len(sysTests) != len(results):
            raise ValueError("The sysTests and results args must be"\
                " same length, but sysTests of len %d vs results of"\
                " len %d" % (len(sysTests), len(results)))
        
        print "-"*80
        headerDetail = ""
        if projName is not None:
            headerDetail += ", project '%s'" % projName
        if suiteName is not None:
            headerDetail += ", suite '%s'" % suiteName
        print "UWA System Tests results summary%s:" % headerDetail
        print "Ran %d system tests," % (len(results)),

        sums = {"Pass":0, "Fail":0, "Error":0}
        failIndices = []
        errorIndices = []
        for resI, result in enumerate(results):
            sums[result.statusStr] += 1
            if isinstance(result, UWA_FAIL): failIndices.append(resI)
            if isinstance(result, UWA_ERROR): errorIndices.append(resI)
        
        print "with %d passes, %d fails, and %d errors" \
            % (sums["Pass"], sums["Fail"], sums["Error"])

        if len(failIndices) > 0:
            print "Failures were:"
            for fI in failIndices:
                print " %s: %s" % (sysTests[fI].testName,
                    results[fI].detailMsg)

        if len(errorIndices) > 0:
            print "Errors were:"
            for eI in errorIndices:
                print " %s: %s" % (sysTests[eI].testName,
                    results[eI].detailMsg)
        print "-"*80

