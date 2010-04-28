
import os
from lxml import etree

from uwa.modelsuite import ModelSuite
from uwa.modelrun import ModelRun, SimParams
import uwa.systest
from uwa.systest.api import SysTest
from uwa.analysis import fields

# TODO: have a factory for these to register with, in the API?

class ReferenceTest(SysTest):
    '''A Reference System test.
        This case simply runs a given model for a set number of steps,
        then checks the resultant solution matches within a tolerance
        of a previously-generated reference solution.'''

    description = '''Runs a Model for a set number of timesteps,
        then checks the specified fields match a previously-generated
        reference solution.'''

    defaultFieldTol = 1e-2

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            fieldsToTest = ['VelocityField','PressureField'], runSteps=20,
            createRefSolnMode=False ):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, "Reference")
        self.testComponents['fieldTests'] = fields.FieldTestsInfo()
        self.expectedSolnPath = "expected" + os.sep + self.testName
        self.fieldsToTest = fieldsToTest
        self.runSteps = runSteps

    def setup(self):
        '''Do a run to create the reference solution to use.'''

        print "Running the model to create a reference solution after %d"\
            " steps, and saving in dir '%s'" % \
            (self.runSteps, self.expectedSolnPath)
        mRun = ModelRun(self.testName+"-createReference", self.inputFiles,
            self.expectedSolnPath, nproc=self.nproc)
        mRun.simParams = SimParams(nsteps=self.runSteps, cpevery=self.runSteps,
            dumpevery=0)
        mRun.cpFields = self.fieldsToTest    
        import uwa.modelrun as modelrun
        mRun.writeInfoXML()
        mRun.analysisXMLGen()
        result = modelrun.runModel(mRun)
        # It's conceivable this could be useful, if we store results about
        # e.g. solver solution times etc.
        import uwa.modelresult as modelresult
        modelresult.writeModelResultsXML(result, path=mRun.outputPath)

    # TODO: a pre-check phase - check the reference dir exists?

    def genSuite(self):
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        # Set up a field test to check between the two runs
        # TODO: should this be in genSuite, or in constructor, or in a
        # 'configure tests' phase (that could be easily over-ridden?)
        fTests = self.testComponents['fieldTests']
        fTests.testTimestep = self.runSteps
        fTests.useReference = True
        fTests.referencePath = self.expectedSolnPath
        for fieldName in self.fieldsToTest:
            fTests.add(fields.FieldTest(fieldName, tol=self.defaultFieldTol))

        # Normal mode
        mRun = ModelRun(self.testName, self.inputFiles,
            self.outputPathBase, nproc=self.nproc)
        mRun.simParams = SimParams(nsteps=self.runSteps,
            cpevery=0, dumpevery=0)
        # TODO: this copying not ideal....
        mRun.analysis['fieldTests'] = fTests
        mSuite.addRun(mRun, "Run the model, and check results against "\
            "previously generated reference solution.")

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

        fTests = self.testComponents['fieldTests']
        fieldResults = fTests.testConvergence(self.outputPathBase)

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
