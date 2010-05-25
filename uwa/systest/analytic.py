import os
from lxml import etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL
from uwa.systest.fieldWithinTolTest import FieldWithinTolTest

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
    fTestName = 'fieldWithinTol'

    def __init__(self, inputFiles, outputPathBase, nproc=1, fieldTols=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, "Analytic")
        self.testComponents[self.fTestName] = FieldWithinTolTest(
            defFieldTol=self.defaultFieldTol, fieldTols=fieldTols)

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        mRun = ModelRun(self.testName, self.inputFiles,
            self.outputPathBase, nproc=self.nproc)
        # For analytic test, read fields to analyse from the XML
        fTests = self.testComponents[self.fTestName]
        fTests.attachOps(mRun)
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
        mResult = resultsSet[0]
        fTests = self.testComponents[self.fTestName]
        result = fTests.check(resultsSet)
        if result:    
            testStatus = UWA_PASS("All fields were within required"\
                " tolerance of analytic solution at end of run." )
        else:        
            testStatus = UWA_FAIL("At least one Field not within"
                " tolerance of analytic soln.")
        # NB: should the ftest component now be able to do this?
        # Or is it appropriate to control from here?
        #for fRes in mResult.fieldResults:
        #    fRes.plotOverTime(show=False, path=mResult.outputPath)
        self.testStatus = testStatus
        return testStatus
        
    def writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'defaultFieldTol').text = \
            str(self.defaultFieldTol)   
