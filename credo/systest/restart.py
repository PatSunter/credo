
import os
from xml.etree import ElementTree as etree

from credo.modelsuite import ModelSuite
from credo.modelrun import SimParams
from credo.systest.api import SysTest, CREDO_PASS, CREDO_FAIL
from credo.systest.fieldWithinTolTest import FieldWithinTolTest

class RestartTest(SysTest):
    '''A Restart System test.
       This case simply runs a given model for set number of steps,
       then restarts half-way through, and checks the same result is
       obtained. (Thus it's largely a regression test to ensure 
       checkpoint-restarting works for various types of models).
       Uses a :class:`~credo.systest.fieldWithinTolTest.FieldWithinTolTest`
       test component to perform the check.

       Optional constructor keywords:

       * fullRunSteps: number of steps to do the initial "full" run for.
         Must be a multiple of 2, so it can be restarted half-way through.
       * fieldsToTest: Which fields in the model should be compared with the
         reference solution.
       * defFieldTol: The default tolerance to be applied when comparing fields of
         interest between the restarted, and original solution.
         See also the FieldWithinTolTest's
         :attr:`~credo.systest.fieldWithinTolTest.FieldWithinTolTest.defFieldTol`.
       * fieldTols: a dictionary of tolerances to use when testing particular
         fields, rather than the default tolerance defined by 
         the defFieldTol argument.
          
       .. attribute:: fTestName

          Standard name to use for this test's field comparison TestComponent
          in the :attr:`~credo.systest.api.SysTest.testComponents` list.  
        '''

    fTestName = 'Restart compared with original'
    description = '''Runs a Model for a set number of timesteps,
        then restarts half-way, checking the standard fields are the
        same at the end for both the original and restart run.'''
    passMsg = "All fields on restart were within required"\
                " tolerance of full run at end."
    failMsg = "At least one field wasn't within tolerance"\
                " on restart run of original run."

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            fieldsToTest = ['VelocityField','PressureField'], fullRunSteps=20,
            defFieldTol=1e-5, fieldTols=None, 
            paramOverrides=None, solverOpts=None, nameSuffix=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Restart", nameSuffix)
        self.initialOutputPath = os.path.join(self.outputPathBase, "initial")
        self.restartOutputPath = os.path.join(self.outputPathBase, "restart")
        self.fieldsToTest = fieldsToTest
        self.fullRunSteps = fullRunSteps
        if self.fullRunSteps % 2 != 0:
            raise ValueError("fullRunSteps parameter must be even so restart"\
                " can occur half-way - but you provided %d." % (fullRunSteps))
        self.testComponents[self.fTestName] = FieldWithinTolTest(
            fieldsToTest=self.fieldsToTest, defFieldTol=defFieldTol,
            fieldTols=fieldTols,
            useReference=True,
            referencePath=self.initialOutputPath,
            testTimestep=self.fullRunSteps)

    def genSuite(self):
        """See base class :meth:`~credo.systest.api.SysTest.genSuite`.

        For this test, will create a suite containing 2 model runs:
        one to initally run the requested Model and save the results,
        and a 2nd to restart mid-way through, so that the results can
        be compared at the end."""
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        # Initial run
        initRun = self._createDefaultModelRun(self.testName+"-initial",
            self.initialOutputPath)
        initRun.simParams = SimParams(nsteps=self.fullRunSteps,
            cpevery=self.fullRunSteps/2, dumpevery=0)
        initRun.cpFields = self.fieldsToTest
        mSuite.addRun(initRun, "Do the initial full run and checkpoint"\
            " solutions.")
        # Restart run
        resRun = self._createDefaultModelRun(self.testName+"-restart",
            self.restartOutputPath)
        resRun.simParams = SimParams(nsteps=self.fullRunSteps/2,
            cpevery=0, dumpevery=0, restartstep=self.fullRunSteps/2)
        resRun.cpReadPath = self.initialOutputPath    
        fTests = self.testComponents[self.fTestName]
        fTests.attachOps(resRun)
        resRunI = mSuite.addRun(resRun, "Do the restart run and check results"\
            " at end match initial.")
        # Only test fields on the restart run
        self.setResIndicesToTest([resRunI])
        return mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~credo.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def _writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'fullRunSteps').text = str(self.fullRunSteps)
        # fieldTols
        fieldsToTestNode = etree.SubElement(specNode, 'fieldsToTest')
        for fieldName in self.fieldsToTest:
            fieldsNode = etree.SubElement(fieldsToTestNode, 'field',
                name=fieldName)
            
