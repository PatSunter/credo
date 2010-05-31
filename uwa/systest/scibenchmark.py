import os
from lxml import etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun
from uwa.systest.api import SysTest, TestComponent, UWA_PASS, UWA_FAIL

class SciBenchmarkTest(SysTest):
    '''A Science benchmark test.
        This is an open-ended system test, designed for the user to add multiple
        test components which test the conditions of the benchmark.
        Contains extra capabilities to report more fully on the test result
        than a standard system test.'''

    description = '''Runs a user-defined science benchmark.'''

    def __init__(self, inputFiles, outputPathBase, nproc=1):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, "SciBenchmark")

    def addTestComponent(self, testComp, testCompName):
        if not issubclass(testComp, TestComponent):
            raise TypeError("Test component passed in to be added to"\
                " benchmark, '%s', not a subclass of TestComponent."\
                % (testComp))
        self.testComponents[testCompName] = testComp

    def writeXMLCustomSpec(self, specNode):
        # TODO: write stuff like paper references here?
        pass

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        mRun = ModelRun(self.testName, self.inputFiles,
            self.outputPathBase, nproc=self.nproc)

        for tComp in self.testComponents.itervalues():
            tComp.attachOps(mRun)
        mSuite.addRun(mRun, "Run the model needed for the benchmark.")
        return mSuite

    def checkResultValid(self, resultsSet):
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            pass

    def getStatus(self, resultsSet):
        self.checkResultValid(resultsSet)
        mResult = resultsSet[0]

        overallResult = True
        failedCompNames = []
        for tCompName, tComp in self.testComponents.iteritems():
            result = tComp.check(resultsSet)
            if not result:
                overallResult = False
                failedCompNames.append(tCompName)

        if overallResult:    
            testStatus = UWA_PASS("All aspects of the benchmark passed.")
        else:        
            testStatus = UWA_FAIL("The following components of the benchmark" \
                " failed: %s" % failedCompNames)

        self.testStatus = testStatus
        return testStatus
        
