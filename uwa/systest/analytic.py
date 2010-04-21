
import os
from lxml import etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun
import uwa.systest
from uwa.systest.api import SysTest
from uwa.analysis import fields

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

    defaultFieldTol = 3e-2    

    def __init__(self, inputFiles, outputPathBase, nproc=1):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, "Analytic")
        self.testComponents['fieldTests'] = fields.FieldTestsInfo()

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        mRun = ModelRun(self.testName, self.inputFiles,
            self.outputPathBase, nproc=self.nproc)
        # For analytic test, read fields to analyse from the XML
        fTests = self.testComponents['fieldTests']
        fTests.readFromStgXML(self.inputFiles)
        # Would be good to allow these to be over-ridden per field.
        fTests.setAllTols(self.defaultFieldTol)
        # TODO: currently need to over-ride here...
        mRun.analysis['fieldTests'] = fTests
        mSuite.addRun(mRun, "Run the model and generate analytic soln.")

        return mSuite

    def checkResultValid(self, resultsSet):
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def getStatus(self, resultsSet):
        self.checkResultValid(resultsSet)

        #TODO: fact it has to reference a saved set of suite results 
        # suggests a not-so-good coupling. 
        # Perhaps more a structure of TestComponents, that generate
        #  Analytic updates to be added to the model runs?
        mResult = resultsSet[0]

        testStatus = None

        # This could be refactored quite a bit, should be done in modelRun
        fTests = self.testComponents['fieldTests']
        mResult.fieldResults = fTests.testConvergence(mResult.outputPath)

        for fRes in mResult.fieldResults:
            result = fRes.checkErrorsWithinTol()
            if result == False:
                testStatus = uwa.systest.UWA_FAIL("Field '%s' not within"
                    " tolerance %d" % (fRes.fieldName, fRes.tol))
                break

        if testStatus == None:
            testStatus = uwa.systest.UWA_PASS("All fields were within required"\
                " tolerance %d of analytic solution at end of run." % fRes.tol )
        self.testStatus = testStatus
        return testStatus
        
    def writeXMLContents(self, baseNode):
        pass
