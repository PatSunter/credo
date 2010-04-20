
def AnalyticMultiResTest(SysTest):
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
