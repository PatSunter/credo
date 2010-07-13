
import os
from xml.etree import ElementTree as etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import SimParams
import uwa.modelrun as modelrun
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL, getStdTestNameBasic
from uwa.systest.fieldWithinTolTest import FieldWithinTolTest

class ReferenceTest(SysTest):
    '''A Reference System test.
       This case simply runs a given model for a set number of steps,
       then checks the resultant solution matches within a tolerance
       of a previously-generated reference solution. Uses a
       :class:`~uwa.systest.fieldWithinTolTest.FieldWithinTolTest`
       test component to perform the check.

       Optional constructor keywords:

       * runSteps: number of steps the reference solution should run for.
       * fieldsToTest: Which fields in the model should be compared with the
         reference solution.
       * defFieldTol: The default tolerance to be applied when comparing fields of
         interest to the reference solution.
         See also the FieldWithinTolTest's
         :attr:`~uwa.systest.fieldWithinTolTest.FieldWithinTolTest.defFieldTol`.
       * fieldTols: a dictionary of tolerances to use when testing particular
         fields, rather than the default tolerance as set in the defFieldTol
         argument.
          
       .. attribute:: fTestName

          Standard name to use for this test's field comparison TestComponent
          in the :attr:`~uwa.systest.api.SysTest.testComponents` list.'''

    description = '''Runs a Model for a set number of timesteps,
        then checks the specified fields match a previously-generated
        reference solution.'''

    fTestName = 'Reference Solution compare'

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            fieldsToTest = ['VelocityField','PressureField'], runSteps=20,
            defFieldTol=1e-2, fieldTols=None, paramOverrides=None,
            solverOpts=None, expPathPrefix="expected", nameSuffix=None ):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Reference", nameSuffix)
        testNameBasic = getStdTestNameBasic(self.testType+"Test", inputFiles)
        self.expectedSolnPath = os.path.join(expPathPrefix, testNameBasic)
        self.fieldsToTest = fieldsToTest
        self.runSteps = runSteps
        self.testComponents[self.fTestName] = FieldWithinTolTest(
            fieldsToTest=self.fieldsToTest, defFieldTol=defFieldTol,
            fieldTols=fieldTols,
            useReference=True,
            referencePath=self.expectedSolnPath,
            testTimestep=self.runSteps)

    def setup(self):
        '''Do a run to create the reference solution to use.'''

        print "Running the model to create a reference solution after %d"\
            " steps, and saving in dir '%s'" % \
            (self.runSteps, self.expectedSolnPath)
        mRun = self._createDefaultModelRun(self.testName+"-createReference",
            self.expectedSolnPath)
        mRun.simParams = SimParams(nsteps=self.runSteps, cpevery=self.runSteps,
            dumpevery=0)
        mRun.cpFields = self.fieldsToTest
        mRun.writeInfoXML()
        mRun.analysisXMLGen()
        result = modelrun.runModel(mRun)
        # It's conceivable this could be useful, if we store results about
        # e.g. solver solution times etc.
        import uwa.modelresult as modelresult
        modelresult.writeModelResultsXML(result, path=mRun.outputPath)

    # TODO: a pre-check phase - check the reference dir exists?

    def genSuite(self):
        """See base class :meth:`~uwa.systest.api.SysTest.genSuite`.

        For this test, just a single model run is needed, to run
        the model and compare against the reference solution."""
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        # Normal mode
        mRun = self._createDefaultModelRun(self.testName, self.outputPathBase)
        mRun.simParams = SimParams(nsteps=self.runSteps,
            cpevery=0, dumpevery=0)
        fTests = self.testComponents[self.fTestName]
        fTests.attachOps(mRun)
        mSuite.addRun(mRun, "Run the model, and check results against "\
            "previously generated reference solution.")
        return mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~uwa.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def getStatus(self, resultsSet):
        """See base class :meth:`~uwa.systest.api.SysTest.getStatus`."""
        self.checkResultValid(resultsSet)
        fTests = self.testComponents[self.fTestName]
        result = fTests.check(resultsSet)
        if result:
            testStatus = UWA_PASS("All fields were within required"\
                " tolerance of reference soln at end of run." )
        else:
            testStatus = UWA_FAIL("A Field was not within"\
                " tolerance of reference soln.")
        self.testStatus = testStatus
        return testStatus
        
    def _writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'runSteps').text = str(self.runSteps)
        # fieldTols
        fieldsToTestNode = etree.SubElement(specNode, 'fieldsToTest')
        for fieldName in self.fieldsToTest:
            fieldsNode = etree.SubElement(fieldsToTestNode, 'field',
                name=fieldName)    
