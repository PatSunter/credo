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

    def runTests(self, sysTests, projName=None, suiteName=None,
            printSummary=True):
        """Run all tests in the sysTests list.
        Will also save all appropriate XMLs (as discussed in :meth:`.runTest`)
        and print a summary of results."""
        results = []
        testTotal = len(sysTests)
        for testI, sysTest in enumerate(sysTests):
            print "Running System test %d/%d, with name '%s':" \
                % (testI+1, testTotal, sysTest.testName)
            results.append(self.runTest(sysTest))
        if printSummary:
            self.printResultsSummary(sysTests, results, projName, suiteName)
        return results
    
    def runSuite(self, suite, runSubSuites=True, subSuiteMode=False):
        """Runs a suite of system tests, and prints results.
        The suite may contain sub-suites, which will also be run by default.
        
        .. note:: Currently, just returns a flat list of results, containing
           results of all tests and all sub-suites. Won't change this into
           a hierarchy of results by sub-suite, unless really necessary."""

        results = []
        testTotal = len(suite.sysTests)
        subSuitesTotal = len(suite.subSuites)
        subText = "Sub-" if subSuiteMode else ""
        print "Running System Test %sSuite for Project '%s', named '%s',"\
            " containing %d direct tests and %d sub-suites:"\
            % (subText, suite.projectName, suite.suiteName, testTotal,
             subSuitesTotal)
        # TODO: start Suite summary XML
        if testTotal > 0:
            results += self.runTests(suite.sysTests, suite.projectName,
                suite.suiteName)
            # TODO: update XML with results
        if runSubSuites and subSuitesTotal > 0:
            subSuiteResults = []
            for subSuite in suite.subSuites:
                subResults = self.runSuite(subSuite, subSuiteMode=True)
                subSuiteResults.append(subResults)
            for subResults in subSuiteResults:
                results += subResults
            self.printSuiteTotalsShortSummary(results, suite.projectName,
                suite.suiteName)
        return results

    def printSuiteTotalsShortSummary(self, results, projName, suiteName):
        """Prints a short summary, useful for suites with sub-suites."""
        print "-"*80
        print "UWA System Tests total for '%s' suite '%s' and sub-suites:"\
            % (projName, suiteName)
        sumsDict, failIndices, errorIndices = self.getResultsTotals(results)
        self.printResultsLine(sumsDict)
        print "-"*80

    def printResultsSummary(self, sysTests, results, 
            projName=None, suiteName=None):
        """Print a textual summary of the results of running a set of sys
        tests."""
        self.checkResultsSysTestsLength(sysTests, results)
        print "-"*80
        headerDetail = ""
        if projName is not None:
            headerDetail += ", project '%s'" % projName
        if suiteName is not None:
            headerDetail += ", suite '%s'" % suiteName
        print "UWA System Tests results summary%s:" % headerDetail
        self.printResultsDetails(sysTests, results)
        print "-"*80

    def printResultsDetails(self, sysTests, results):    
        sumsDict, failIndices, errorIndices = self.getResultsTotals(results)
        self.printResultsLine(sumsDict)

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

    def getResultsTotals(self, results):
        sums = {"Pass":0, "Fail":0, "Error":0}
        failIndices = []
        errorIndices = []
        for resI, result in enumerate(results):
            sums[result.statusStr] += 1
            if isinstance(result, UWA_FAIL): failIndices.append(resI)
            if isinstance(result, UWA_ERROR): errorIndices.append(resI)
        return sums, failIndices, errorIndices    

    def printResultsLine(self, sumsDict):
        totalResults = sum(sumsDict.values())
        print "Ran %d system tests," % (totalResults),
        print "with %d passes, %d fails, and %d errors" \
            % (sumsDict["Pass"], sumsDict["Fail"], sumsDict["Error"])

    def checkResultsSysTestsLength(self, sysTests, results):
        if len(sysTests) != len(results):
            raise ValueError("The sysTests and results args must be"\
                " same length, but sysTests of len %d vs results of"\
                " len %d" % (len(sysTests), len(results)))

