##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA


import os
from xml.etree import ElementTree as etree

from credo.modelsuite import ModelSuite
from credo.modelrun import SimParams
import credo.modelrun as modelrun
from credo.systest.api import SysTest, CREDO_PASS, CREDO_FAIL, getStdTestNameBasic
from credo.systest.fieldWithinTolTest import FieldWithinTolTest

class ReferenceTest(SysTest):
    '''A Reference System test.
       This case simply runs a given model for a set number of steps,
       then checks the resultant solution matches within a tolerance
       of a previously-generated reference solution. Uses a
       :class:`~credo.systest.fieldWithinTolTest.FieldWithinTolTest`
       test component to perform the check.

       Optional constructor keywords:

       * runSteps: number of steps the reference solution should run for.
       * fieldsToTest: Which fields in the model should be compared with the
         reference solution.
       * defFieldTol: The default tolerance to be applied when comparing fields of
         interest to the reference solution.
         See also the FieldWithinTolTest's
         :attr:`~credo.systest.fieldWithinTolTest.FieldWithinTolTest.defFieldTol`.
       * fieldTols: a dictionary of tolerances to use when testing particular
         fields, rather than the default tolerance as set in the defFieldTol
         argument.
          
       .. attribute:: fTestName

          Standard name to use for this test's field comparison TestComponent
          in the :attr:`~credo.systest.api.SysTest.testComponents` list.'''

    fTestName = 'Reference Solution compare'
    description = '''Runs a Model for a set number of timesteps,
        then checks the specified fields match a previously-generated
        reference solution.'''
    passMsg = "All fields were within required tolerance of reference"\
        " soln at end of run."
    failMsg = "A Field was not within tolerance of reference soln."

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            fieldsToTest = ['VelocityField','PressureField'], runSteps=20,
            defFieldTol=1e-2, fieldTols=None, paramOverrides=None,
            solverOpts=None, expPathPrefix="expected", nameSuffix=None,
            timeout=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Reference", nameSuffix, timeout)
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
        import credo.modelresult as modelresult
        modelresult.writeModelResultsXML(result, path=mRun.outputPath)

    # TODO: a pre-check phase - check the reference dir exists?

    def genSuite(self):
        """See base class :meth:`~credo.systest.api.SysTest.genSuite`.

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
        """See base class :meth:`~credo.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    def _writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'runSteps').text = str(self.runSteps)
        # fieldTols
        fieldsToTestNode = etree.SubElement(specNode, 'fieldsToTest')
        for fieldName in self.fieldsToTest:
            fieldsNode = etree.SubElement(fieldsToTestNode, 'field',
                name=fieldName)    
