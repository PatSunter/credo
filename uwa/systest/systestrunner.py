import os
import inspect

from uwa.systest.api import *

class SysTestRunner:

    def __init__(self, sysTests=[], nproc=1):
        self.sysTests = sysTests
        # Should this be over-rideable per test?
        self.nproc = nproc
    
    def addStdTest(self, testClass, inputFiles, **testOpts):
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
                
        # TODO: make the test name an input arg?
        if 'nproc' not in testOpts:
            testOpts['nproc']=self.nproc
        classStr = str(testClass).split('.')[-1]
        testName, ext = os.path.splitext(inputFiles[0])
        testName += "-"+classStr[0].lower()+classStr[1:]
        outputPath = 'output/' + testName + "-" + str(testOpts['nproc'])
        newSysTest = testClass(inputFiles, outputPath, **testOpts)
        self.sysTests.append(newSysTest)

    def runTest(self, sysTest):
        # Generate a suite of models to run as part of the test
        mSuite = sysTest.genSuite()

        mSuite.writeAllModelRunXMLs()
        suiteResults = mSuite.runAll()
        print "Checking test result:"
        testResult = sysTest.getStatus(suiteResults)
        mSuite.writeAllModelResultXMLs()

        print "Test result was %s" % testResult
        sysTest.writeInfoXML()
        return testResult

    def runAll(self):
        results = []
        for testI, sysTest in enumerate(self.sysTests):
            print "Running System test %d, with name '%s':" \
                % (testI, sysTest.testName)
            results.append(self.runTest(sysTest))
        
        self.printResultsSummary(self.sysTests, results)
    
    def printResultsSummary(self, sysTests, results):
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

