
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
        self.modelName, ext = os.path.splitext(inputFiles[0])
        self.modelName += "-analyticTest"
        self.inputFiles = inputFiles
        self.outputPathBase = outputPathBase
        self.testStatus = None
        self.nproc = nproc

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        mRun = ModelRun(self.modelName, self.inputFiles,
            self.outputPathBase, nproc=self.nproc)
        # For analytic test, read fields to analyse from the XML
        fTests = mRun.analysis['fieldTests']
        fTests.readFromStgXML(self.inputFiles)
        # Would be good to allow these to be over-ridden per field.
        fTests.setAllTols(self.defaultFieldTol)
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
        mRun = self.mSuite.runs[0]
        mResult = resultsSet[0]

        testStatus = uwa.systest.UWA_PASS()

        # This could be refactored quite a bit, should be done in modelRun
        fTests = mRun.analysis['fieldTests']
        mResult.fieldResults = fTests.testConvergence(mRun.outputPath)

        for fRes in mResult.fieldResults:
            result = fRes.checkErrorsWithinTol()
            if result == False:
                testStatus=uwa.systest.UWA_FAIL("Field '%s' not within"
                    " tolerance %d" % (fRes.fieldName, fRes.tol))
                break

        self.status = testStatus
        return testStatus
        
    def writeXMLContents(self, baseNode):
        descNode = etree.SubElement(baseNode, 'description')
        descNode.text = self.description
        analysisNode = etree.SubElement(baseNode, 'testComponents')
        mRun = self.mSuite.runs[0]
        fTests = mRun.analysis['fieldTests']
        fTests.writeInfoXML(analysisNode)
        status = etree.SubElement(baseNode, 'status')
