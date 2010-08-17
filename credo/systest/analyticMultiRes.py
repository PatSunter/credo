import os
from xml.etree import ElementTree as etree

from uwa.modelsuite import ModelSuite
import uwa.modelrun as mrun
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL
from uwa.systest.fieldCvgWithScaleTest import FieldCvgWithScaleTest

class AnalyticMultiResTest(SysTest):
    '''A Multiple Resolution system test.
       This test can be used to convert any existing system test that
       analyses fields, to check that the error between the analytic
       solution fields and the actual results improves at the required
       rate as the model resolution is increased. Uses a
       :class:`~uwa.systest.fieldCvgWithScaleTest.FieldCvgWithScaleTest`
       test component to perform the check.

       Optional constructor keywords:

       * resSet: a list of resolutions to use for the test, as tuples.
         E.g. to specify testing at 10x10 res then 20x20, resSet would
         be [(10,10), (20,20)]
       
       .. attribute:: resSet

          Set of resolutions to use, as described for the resSet keyword
          to the constructor.
       '''

    description = '''Runs an existing test with multiple resolutions.'''
    passMsg = "The solution compared to the analytic result"\
		    " converged as expected with increasing resolution for all fields."
    failMsg = "One of the fields failed to converge as expected."

    def __init__(self, inputFiles, outputPathBase, resSet, nproc=1,
            paramOverrides=None, solverOpts=None, nameSuffix=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "AnalyticMultiResConvergence",
            nameSuffix)
        self.resSet = resSet
        cvgChecker = FieldCvgWithScaleTest()
        self.testComponents['fieldConvChecker'] = cvgChecker

    def genSuite(self):
        """See base class :meth:`~uwa.systest.api.SysTest.genSuite`.

        The generated suite will contain model runs all with the same model
        XML files, but with increasing resolution as specified by the 
        :attr:`.resSet` attribute.
        """
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        
        # For analytic conv test, read fields to analyse from the XML
        cvgChecker = self.testComponents['fieldConvChecker']

        for res in self.resSet:
            resStr = mrun.strRes(res)
            modelName = self.testName+'-'+resStr
            mRun = self._createDefaultModelRun(modelName,
                os.path.join(self.outputPathBase, resStr))
            customOpts = mrun.generateResOpts(res)
            cvgChecker.attachOps(mRun)
            mSuite.addRun(mRun, "Run the model at res "+resStr, customOpts)

        return mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~uwa.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def _writeXMLCustomSpec(self, specNode):
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

        
