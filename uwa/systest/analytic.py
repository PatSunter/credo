
import os

import uwa.systest
from uwa.systest.api import SysTest
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

    def __init__(self, inputFiles, outputPathBase):
        self.modelName, ext = os.path.splitext(inputFiles[0])
        self.modelName += "-analyticTest"
        self.inputFiles = inputFiles
        self.outputPathBase = outputPathBase

    def genSuite(self):
        mSuite = ModelSuite(outputPathParent=outputPath)
        self.mSuite = mSuite    

        mRun = mrun.ModelRun(self.modelName, self.inputFiles,
            self.outputPathBase, nproc=nproc)
        # For analytic test, read fields to analyse from the XML
        mRun.fTests = FieldTestsInfo()
        mRun.fTests.readFromStgXML(inputFiles)
        # Would be good to allow these to be over-ridden per field.
        mRun.fieldTests.setAllTols(defaultFieldTol)
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

        mRun = self.mSuite.runs[0]
        mResult = suiteResults[0]

        testStatus = UWA_PASS

        # This could be refactored quite a bit, should be done in modelRun
        fTests = mRun.analysis['fieldTests']
        mResult.fieldResults = fTests.testConvergence(mRun.outputPath)

        for fRes in mResult.fieldResults:
            result = fRes.checkErrorsWithinTol()
            if result == False:
                testStatus=UWA_FAIL
                break

        return testStatus
