
import os
from xml.etree import ElementTree as etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun, SimParams
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL
from uwa.systest.fieldWithinTolTest import FieldWithinTolTest

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
    fTestName = 'Restart compared with original'

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            fieldsToTest = ['VelocityField','PressureField'], fullRunSteps=20,
            fieldTols=None, paramOverrides={}):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, "Restart")
        self.initialOutputPath = os.path.join(self.outputPathBase, "initial")
        self.restartOutputPath = os.path.join(self.outputPathBase, "restart")
        self.fieldsToTest = fieldsToTest
        self.fullRunSteps = fullRunSteps
        if self.fullRunSteps % 2 != 0:
            raise ValueError("fullRunSteps parameter must be even so restart"\
                " can occur half-way - but you provided %d." % (fullRunSteps))
        self.testComponents[self.fTestName] = FieldWithinTolTest(
            fieldsToTest=self.fieldsToTest, defFieldTol=self.defaultFieldTol,
            fieldTols=fieldTols,
            useReference=True,
            referencePath=self.initialOutputPath,
            testTimestep=self.fullRunSteps)

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        # Initial run
        initRun = ModelRun(self.testName+"-initial", self.inputFiles,
            self.initialOutputPath, nproc=self.nproc,
            paramOverrides=self.paramOverrides)
        initRun.simParams = SimParams(nsteps=self.fullRunSteps,
            cpevery=self.fullRunSteps/2, dumpevery=0)
        initRun.cpFields = self.fieldsToTest
        mSuite.addRun(initRun, "Do the initial full run and checkpoint"\
            " solutions.")
        # Restart run
        resRun = ModelRun(self.testName+"-restart", self.inputFiles,
            self.restartOutputPath, nproc=self.nproc,
            paramOverrides=self.paramOverrides)
        resRun.simParams = SimParams(nsteps=self.fullRunSteps/2,
            cpevery=0, dumpevery=0, restartstep=self.fullRunSteps/2)
        resRun.cpReadPath = self.initialOutputPath    
        fTests = self.testComponents[self.fTestName]
        fTests.attachOps(resRun)
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
        fTests = self.testComponents[self.fTestName]
        # We are only interested in checking the restart run
        result = fTests.check([resultsSet[1]])
        if result:
            testStatus = UWA_PASS("All fields on restart were within required"\
                " tolerance of full run at end." )
        else:        
            testStatus = UWA_FAIL("At least one field wasn't within tolerance"\
                " on restart run of original run")
        self.testStatus = testStatus
        return testStatus
        
    def writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'fullRunSteps').text = str(self.fullRunSteps)
        etree.SubElement(specNode, 'defaultFieldTol').text = \
            str(self.defaultFieldTol)
        # fieldTols
        fieldsToTestNode = etree.SubElement(specNode, 'fieldsToTest')
        for fieldName in self.fieldsToTest:
            fieldsNode = etree.SubElement(fieldsToTestNode, 'field',
                name=fieldName)
            
