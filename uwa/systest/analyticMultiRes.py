import os
from lxml import etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun
import uwa.modelrun as mrun
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL
from uwa.systest.fieldCvgWithScaleTest import FieldCvgWithScaleTest

class AnalyticMultiResTest(SysTest):
    '''A Multiple Resolution system test.
        This test can be used to convert any existing system test that
        analyses fields, to check that the convergence improves as res.
        improves'''

    description = '''Runs an existing test with multiple resolutions.'''

    def __init__(self, inputFiles, outputPathBase, resSet, nproc=1 ):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            "AnalyticMultiResConvergence")
        self.resSet = resSet
        cvgChecker = FieldCvgWithScaleTest()
        self.testComponents['fieldConvChecker'] = cvgChecker

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        
        # For analytic conv test, read fields to analyse from the XML
        cvgChecker = self.testComponents['fieldConvChecker']

        for res in self.resSet:
            resStr = mrun.strRes(res)
            outputPath = os.path.join(self.outputPathBase, resStr)
            modelName = self.testName+'-'+resStr
            mRun = mrun.ModelRun(modelName, self.inputFiles, outputPath,
                nproc=self.nproc)
            customOpts = mrun.generateResOpts(res)
            cvgChecker.attachOps(mRun)
            mSuite.addRun(mRun, "Run the model at res "+resStr, customOpts)

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

        testStatus = UWA_PASS("The solution compared to the analytic result"\
		    " converged as expected with increasing resolution for all fields")
        fConvChecker = self.testComponents['fieldConvChecker']
        result = fConvChecker.check(resultsSet)
        if result == False:
            testStatus = UWA_FAIL("One of the fields failed to converge as"\
                " expected")
        self.testStatus = testStatus
        return testStatus

    def writeXMLCustomSpec(self, specNode):
        resSetNode = etree.SubElement(specNode, "resSet")
        for res in self.resSet:
            resNode = etree.SubElement(resSetNode, "res")
            resNode.attrib['x'] = str(res[0])
            resNode.attrib['y'] = str(res[1])
            if len(res) == 3:
                resNode.attrib['z'] = str(res[2])
        #TODO: if we allow user to choose/override convergence checking
        # algorithm
        #cvgFuncNode = etree.SubElement(specNode, "cvgFunc")
        #cvgFuncNode.attrib['name']
        #cvgFuncNode.attrib['module'] = inspect.getmodule(cvgFunc)

        
