import os
import sys
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
        # TODO A little hacky on the chdir - see api.py:183 comment
        startDir = os.getcwd()
        os.chdir(sysTest.runPath)
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
        os.chdir(startDir)
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

        :returns: a list of all results of the suite, and its sub-suites
        
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
    
    def runSuites(self, testSuites):
        """Runs a list of suites, and prints a big summary at the end.
        
        :returns: a list containing lists of results for each suite (results
          list in the same order as testSuites input argument).
        """
        print "Running the following system test suites:"
        for suite in testSuites:
            print " Project '%s', suite '%s'" % (suite.projectName,
                suite.suiteName)
        print "-"*80

        resultsLists = []
        for suite in testSuites:
            suiteResults = self.runSuite(suite)
            resultsLists.append(suiteResults)

        self.printSuiteResultsByProject(testSuites, resultsLists)
        return resultsLists

    def printSuiteResultsByProject(self, testSuites, resultsLists):
        """Utility function to print a set of suite results out, 
        categorised by project, in the order that the projects first
        appear in the results."""
        projOrder, projIndices = self._buildResultsProjectIndex(testSuites)
        suitesResults = zip(testSuites, resultsLists)
        print "-"*80
        print "UWA System Tests summary for all project suites ran:"
        print "------"
        totalSumsDict = {"Pass":0, "Fail":0, "Error":0}
        for projName in projOrder:
            print "Project '%s':" % projName
            projSumsDict = {"Pass":0, "Fail":0, "Error":0}
            for suiteI in projIndices[projName]:
                suite = testSuites[suiteI]
                print " Suite '%s':" % suite.suiteName,
                suiteResults = resultsLists[suiteI]
                sumsDict = self.getResultsTotals(suiteResults)[0]
                self._printResultsLineShort(sumsDict)
                for kw, sumVal in sumsDict.iteritems():
                    projSumsDict[kw] += sumVal
            self._printResultsLineShort(projSumsDict)
            print "------"
            for kw, sumVal in projSumsDict.iteritems():
                totalSumsDict[kw] += sumVal
        print "ALL Projects Total: ",
        self._printResultsLineShort(totalSumsDict)
        print "-"*80

    def printSuiteResultsOrderFound(self, testSuites, resultsLists):
        """Utility function to print a set of results in the order they
        were entered (not sub-categorised by project)."""
        print "-"*80
        print "UWA System Tests summary for all project suites ran:"
        totalSumsDict = {"Pass":0, "Fail":0, "Error":0}
        for ii, suite in enumerate(testSuites):
            print "'%s', '%s': " % (suite.projectName, suite.suiteName),
            suiteResults = resultsLists[ii]
            sumsDict = self.getResultsTotals(suiteResults)[0]
            totalResults = sum(sumsDict.values())
            self._printResultsLineShort(sumsDict)
            for kw, sumVal in sumsDict.iteritems():
                totalSumsDict[kw] += sumVal
        print "------"
        print "TOTAL: ",
        self._printResultsLineShort(totalSumsDict)
        print "-"*80

    def _buildResultsProjectIndex(self, testSuites):
        """Build index of projects and their indices into testSuites.
       :returns: dictionary where keys are project names, values are lists
       of indices into the testSuites list of results of that project."""
        projectsOrder = []
        projectIndices = {}
        for suiteI, suite in enumerate(testSuites):
            projName = suite.projectName    
            if projName not in projectsOrder: projectsOrder.append(projName)

            if projName not in projectIndices:
                projectIndices[projName] = [suiteI]
            else:
                projectIndices[projName].append(suiteI)

        return projectsOrder, projectIndices

    def printSuiteTotalsShortSummary(self, results, projName, suiteName):
        """Prints a short summary, useful for suites with sub-suites."""
        print "-"*80
        print "UWA System Tests total for '%s' suite '%s' and sub-suites:"\
            % (projName, suiteName)
        sumsDict, failIndices, errorIndices = self.getResultsTotals(results)
        self._printResultsLine(sumsDict)
        print "-"*80

    def printResultsSummary(self, sysTests, results, 
            projName=None, suiteName=None):
        """Print a textual summary of the results of running a set of sys
        tests."""
        self._checkResultsSysTestsLength(sysTests, results)
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
        """Prints details of which tests failed in a sub-suite."""
        sumsDict, failIndices, errorIndices = self.getResultsTotals(results)
        self._printResultsLine(sumsDict)

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
        """Gets the totals of a set of results, and returns, including
        indices of which results failed, and which were errors."""
        sums = {"Pass":0, "Fail":0, "Error":0}
        failIndices = []
        errorIndices = []
        for resI, result in enumerate(results):
            sums[result.statusStr] += 1
            if isinstance(result, UWA_FAIL): failIndices.append(resI)
            if isinstance(result, UWA_ERROR): errorIndices.append(resI)
        return sums, failIndices, errorIndices    

    def _printResultsLine(self, sumsDict):
        totalResults = sum(sumsDict.values())
        print "Ran %d system tests," % (totalResults),
        print "with %d passes, %d fails, and %d errors" \
            % (sumsDict["Pass"], sumsDict["Fail"], sumsDict["Error"])

    def _printResultsLineShort(self, sumsDict):
        totalResults = sum(sumsDict.values())
        print "%d tests, %d/%d/%d passes/fails/errors" \
            % (totalResults, sumsDict["Pass"], sumsDict["Fail"],
                sumsDict["Error"])

    def _checkResultsSysTestsLength(self, sysTests, results):
        if len(sysTests) != len(results):
            raise ValueError("The sysTests and results args must be"\
                " same length, but sysTests of len %d vs results of"\
                " len %d" % (len(sysTests), len(results)))


def runSuitesFromModules(suiteModNames, xmlOutputFilename):
    """Runs a set of System test suites, where suiteModNames is a list of 
    suites to import and run."""
    suites = []
    for modName in suiteModNames:
        print "Importing suite for %s:" % modName
        imp = __import__(modName)
        mod = sys.modules[modName]
        suites.append(mod.suite())
    testRunner = SysTestRunner()
    # TODO: pass in xmlOutputFilename to save record of this stuff
    testRunner.runSuites(suites)
