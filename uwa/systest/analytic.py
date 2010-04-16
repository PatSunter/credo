
import uwa.analysis

# TODO: have a factory for these to register with, in the API?

class AnalyticTest(SysTest):
    '''An Analytic System test.
        This case requires the user to have configured the XML correctly
        to load an anlytic soln, and compare it to the correct fields.
        Will check that each field flagged to be analysed is within
        the expected tolerance'''

    description = '''Runs a Model that has a defined analytic solution,
        and checks the outputted fields are within a given error tolerance
        of that analytic solution.'''

    def __init__( inputFiles, outputPath ):
        self.modelName, ext = os.path.splitext(firstInputFile)
        self.modelName += "-analyticTest"
        self.fieldTests = FieldTestsInfo()
        self.

    def configureTests(self):
        # Have this as a separate method, to allow multi-res guy to override.
        # For analytic test, read fields to analyse from the XML
        self.fieldTests.readFromStgXML(inputFiles)
        # Would be good to allow these to be over-ridden per field.
        self.fieldTests.setAllTols(defaultFieldTol)

    def genSuite(self):
        mSuite = ModelSuite( outputPathParent=outputPath )
        mRun = mrun.ModelRun(self.modelName, inputFiles, outputPath,
            nproc=nproc)
        # TODO: how do we attach the know-how for any additional XML to be 
        # Generated for the ModelRun, related specifically to the test?
        mSuite.addRun("analysis", "Run the model and generate analytic soln.",\
            mRun)
        return mSuite

    def checkResultValid(suiteResults):
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in suiteResults:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def getStatus(suiteResults):
        self.checkResultValid(suiteResults)
        mResult = suiteResults[0]

        testStatus = UWA_PASS

        # This could be refactored quite a bit, should be done in modelRun
        cvgFileIndex = genConvergenceFileIndex(modelRun.outputPath)
        uwa.analysis.testConvergence(mRun)

        fieldResults = []
        for fieldTest in self.fieldTests.fields:
            assert fieldTest.name in cvgFileIndex
            fieldResults.append(checkFieldConvergence(fieldTest, \
                cvgFileIndex[fieldTest.name]))

        fTests = self.fieldTests.fields.values()
        for ii in range(len(fTests)):
            fTest = fTests[ii]
            result = fTest.checkResultWithinTol(mResult.fieldResult[ii])
            if result = False:
                testStatus=UWA_FAIL

            self.fieldConvergences[ii] = result

    return testStatus

################################

def MultiResTest(sysTest):
    '''A Multiple Resolution system test.

        This test can be used to convert any existing system test that
        analyses fields, to check that the convergence improves as res.
        improves'''

    description = '''Runs an existing test with multiple resolutions.'''

    def __init__( outputPath, innerTest, resSet, resConvChecker ):
        assert isinstance(innerTest, SysTest)
        self.innerTest = innerTest
        self.modelName = innerTest+"-multiResCvg"
        self.resSet = resSet
        self.resConvChecker = resConvChecker

    def configureTests(self):
        # Have this as a separate method, to allow multi-res guy to override.
        # For analytic test, read fields to analyse from the XML
        self.fieldTests.readFromStgXML(inputFiles)
        # Would be good to allow these to be over-ridden per field.
        self.fieldTests.setAllTols(defaultFieldTol)

    def genSuite(self):
        mSuite = ModelSuite( outputPathParent=outputPath )
        
        mRun = mrun.ModelRun(self.modelName, inputFiles, outputPath,
            nproc=nproc)

        for res in self.resSet:
            # TODO: how do we attach the know-how for any additional XML to be 
            # Generated for the ModelRun, related specifically to the test?
            mRun.outputPath += os.sep+mrun.strRes(res)
            customOpts = mrun.generateResOpts(res)
            mSuite.addRun("analysis", "Run the model at res"+mrun.strRes(res),
                mRun, customOpts)

        return mSuite

    def checkResultValid(suiteResults):
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in suiteResults:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def getStatus(suiteResults):
        self.checkResultValid(suiteResults)
        mResult = suiteResults[0]

        testStatus = UWA_PASS

        result = self.resConvChecker.check( self.resSet, self.suiteResults )
        if result == False:
            testStatus = UWA_FAIL

    return testStatus
