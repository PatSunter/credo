import os
from xml.etree import ElementTree as etree

from uwa.modelsuite import ModelSuite
from uwa.systest.api import SysTest, TestComponent, UWA_PASS, UWA_FAIL

class SciBenchmarkTest(SysTest):
    '''A Science benchmark test.
        This is an open-ended system test, designed for the user to add multiple
        :class:`~uwa.systest.api.TestComponent` s to,
        which test the conditions of the benchmark.
        Contains extra capabilities to report more fully on the test result
        than a standard system test.
        
        See the examples section of the UWA documentation,
        :ref:`uwa-examples-scibenchmarking`, for examples of sci benchmarking
        in practice.'''

    description = '''Runs a user-defined science benchmark.'''

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            paramOverrides=None, solverOpts=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, 
            paramOverrides, solverOpts, "SciBenchmark")

    def addTestComponent(self, testComp, testCompName):
        """Add a testComponent (:class:`~uwa.systest.api.TestComponent`)
        with name testCompName to the list of test
        components to be applied as part of determining if the benchmark
        has passed."""
        if not isinstance(testComp, TestComponent):
            raise TypeError("Test component passed in to be added to"\
                " benchmark, '%s', not an instance of a TestComponent."\
                % (testComp))
        self.testComponents[testCompName] = testComp

    def _writeXMLCustomSpec(self, specNode):
        # TODO: write stuff like paper references here?
        pass

    def genSuite(self):
        """See base class :meth:`~uwa.systest.api.SysTest.genSuite`.
        
        By default will create just a single model run.

        .. note:: for Benchmarks that involve running a suite of models, this 
           API may need re-thinking. Or else a separate SciBenchmarkSuite
           class could be added.
        """
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        mRun = self._createDefaultModelRun(self.testName, self.outputPathBase)
        for tComp in self.testComponents.itervalues():
            tComp.attachOps(mRun)
        mSuite.addRun(mRun, "Run the model needed for the benchmark.")
        return mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~uwa.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            pass

    def getStatus(self, resultsSet):
        """See base class :meth:`~uwa.systest.api.SysTest.getStatus`."""
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
        
