
import os
from lxml import etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun, SimParams
import uwa.systest
from uwa.systest.api import SysTest
from uwa.analysis import fields

# TODO: have a factory for these to register with, in the API?

class RestartTest(SysTest):
    '''A Restart System test.
        This case simply runs a given model for set number of steps,
        then restarts half-way through, and checks the same result is
        obtained. (Thus it's largely a regression test to ensure 
        checkpoint-restarting works for various types of models).
        '''

    description = '''Runs a Model for a set number of timesteps,
        then restarts half-way, checking the standard fields are the
        same at the end for both the original and restart run.'''

    defaultFieldTol = 1e-5

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            fieldsToTest = ['VelocityField','PressureField'], fullRunSteps=20 ):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, "Restart")
        self.testComponents['fieldTests'] = fields.FieldTestsInfo()
        self.initialOutputPath = self.outputPathBase+os.sep+"initial"
        self.restartOutputPath = self.outputPathBase+os.sep+"restart"
        self.fieldsToTest = fieldsToTest
        self.fullRunSteps = fullRunSteps
        if self.fullRunSteps % 2 != 0:
            raise ValueError("fullRunSteps parameter must be even so restart"\
                " can occur half-way - but you provided %d." % (fullRunSteps))

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        # Initial run
        initRun = ModelRun(self.testName+"-initial", self.inputFiles,
            self.initialOutputPath, nproc=self.nproc)
        initRun.simParams = SimParams(nsteps=self.fullRunSteps,
            cpevery=self.fullRunSteps/2, dumpevery=0)
        initRun.cpFields = self.fieldsToTest
        mSuite.addRun(initRun, "Do the initial full run and checkpoint solutions.")

        # Restart run
        resRun = ModelRun(self.testName+"-restart", self.inputFiles,
            self.restartOutputPath, nproc=self.nproc)
        resRun.simParams = SimParams(nsteps=self.fullRunSteps/2,
            cpevery=0, dumpevery=0, restartstep=self.fullRunSteps/2)
        resRun.cpReadPath = self.initialOutputPath    

        # Set up a field test to check between the two runs
        # TODO: should this be in genSuite, or in constructor, or in a
        # 'configure tests' phase (that could be easily over-ridden?)
        fTests = self.testComponents['fieldTests']
        fTests.testTimestep = self.fullRunSteps
        fTests.useReference = True
        fTests.referencePath = self.initialOutputPath
        for fieldName in self.fieldsToTest:
            fTests.add(fields.FieldTest(fieldName, tol=self.defaultFieldTol))

        # TODO: this copying not ideal....
        resRun.analysis['fieldTests'] = fTests
        mSuite.addRun(resRun, "Do the restart run and check results at end"\
            " match initial.")

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

        testStatus = None

        # This could be refactored quite a bit, should be done in modelRun
        fTests = self.testComponents['fieldTests']
        fieldResults = fTests.testConvergence(self.restartOutputPath)

        for fRes in fieldResults:
            result = fRes.checkErrorsWithinTol()
            if result == False:
                testStatus = uwa.systest.UWA_FAIL("Field '%s' not within"
                    " tolerance %d" % (fRes.fieldName, fRes.tol))
                break

        if testStatus == None:
            testStatus = uwa.systest.UWA_PASS("All fields were within required"\
                " tolerance %d at end of run." % fRes.tol )
        self.testStatus = testStatus
        return testStatus
        
    def writeXMLContents(self, baseNode):
        pass
