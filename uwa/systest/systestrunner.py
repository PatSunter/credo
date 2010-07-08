import os
import inspect

from uwa.systest.api import *

class SysTestRunner:
    """Class that manages and runs a set of :class:`~uwa.systest.api.SysTest`.

    For examples of how to use, see the UWA documentation, especially
    :ref:`uwa-examples-run-systest`.

    .. attribute:: sysTests

       List of system tests that should be run and reported upon. Generally
       shouldn't be accessed directly, recommend using :meth:`.addStdTest`
       to add to this list, and other methods to run and report on it.
    """

    def __init__(self, sysTests=None, nproc=1):
        if sysTests == None:
            self.sysTests = []
        else:    
            if not isinstance(sysTests, list):
                raise TypeError("Error, if the sysTests keyword is provided"\
                    " it must be a list of SysTests.")
            self.sysTests = sysTests
        # Should this be over-rideable per test?
        self.nproc = nproc
    
    def addStdTest(self, testClass, inputFiles, **testOpts):
        """Instantiate and add a "standard" system test type to the list
        of System tests to be run. (The "standard" refers to the user needing
        to have access to the module containing the system test type to be
        added, usually from a `from uwa.systest import *` statement.

        :param testClass: Python class of the System test to be added. This
          needs to be a sub-class of :class:`~uwa.systest.api.SysTest`.
        :param inputFiles: model input files to be passed through to the 
          System test when instantiated.
        :param `**testOpts`: any other keyword arguments the user wishes to
          passed through to the System test when it's instantiated.
          Can be used to customise a test."""

        if not inspect.isclass(testClass):
            raise TypeError("The testClass argument must be a type that's"\
                " a subclass of the UWA SysTest type. Arg passed in, '%s',"\
                " of type '%s', is not a Python Class." \
                % (testClass, type(testClass)))
        if not issubclass(testClass, SysTest):
            raise TypeError("The testClass argument must be a type that's"\
                " a subclass of the UWA SysTest type. Type passed in, '%s',"\
                " not a subclass of SysTest." \
                % (testClass))
                
        # If just given a single input file as a string, convert
        #  to a list (containing that single file).
        if isinstance(inputFiles, str): inputFiles = [inputFiles]
        # TODO: make the test name an input arg?
        if 'nproc' not in testOpts:
            testOpts['nproc']=self.nproc

        outputPath = self._getStdOutputPath(testClass, inputFiles, testOpts)

        newSysTest = testClass(inputFiles, outputPath, **testOpts)
        self.sysTests.append(newSysTest)

    def _getStdOutputPath(self, testClass, inputFiles, testOpts):
        """Get the standard name for the test's output path. Attempts to
        avoid naming collisions where reasonable."""
        classStr = str(testClass).split('.')[-1]
        testName, ext = os.path.splitext(inputFiles[0])
        testName += "-"+classStr[0].lower()+classStr[1:]
        outputPath = 'output/' + testName + "-np" + str(testOpts['nproc'])
        # This bit to avoid param override tests overriding std ones.
        if 'paramOverrides' in testOpts:
            paramOs = testOpts['paramOverrides']
            paramOsStr = ""
            paramKeys = paramOs.keys()
            paramKeys.sort()
            for paramName in paramKeys:
                paramVal = paramOs[paramName]
                # TODO: move this stuff into a library for managing Stg Command
                # line dict format.
                paramNameLast = paramName.split('.')[-1]
                paramValCanon = str(paramVal).replace(".","_")
                paramOsStr += "-%s-%s" % (paramNameLast, paramValCanon)
            outputPath += paramOsStr    

        return outputPath

    def runTest(self, sysTest):
        """Run a given sysTest, and return the 
        :class:`uwa.systest.api.SysTestResult` it produces.
        Usually sysTest should be from the attribute :attr:`.sysTests`.
        Will also write an XML record of the System test, and each ModelRun
        and ModelResult in the suite that made up the test."""
        mSuite = sysTest.genSuite()
        mSuite.cleanAllOutputPaths()
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

    def runAll(self):
        """Run all tests that have been added to the :attr:".sysTests" list.
        Will also save all appropriate XMLs (as discussed in :meth:`.runTest`)
        and print a summary of results."""
        results = []
        for testI, sysTest in enumerate(self.sysTests):
            print "Running System test %d, with name '%s':" \
                % (testI, sysTest.testName)
            results.append(self.runTest(sysTest))
        self.printResultsSummary(self.sysTests, results)
    
    def printResultsSummary(self, sysTests, results):
        """Print a textual summary of the results of running a set of sys
        tests."""
        if len(sysTests) != len(results):
            raise ValueError("The sysTests and results args must be"\
                " same length, but sysTests of len %d vs results of"\
                " len %d" % (len(sysTests), len(results)))
        
        print "-"*80
        print "UWA System Tests results summary:"
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

