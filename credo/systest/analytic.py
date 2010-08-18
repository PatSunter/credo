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
from credo.systest.api import SysTest, CREDO_PASS, CREDO_FAIL
from credo.systest.fieldWithinTolTest import FieldWithinTolTest

class AnalyticTest(SysTest):
    '''An Analytic System test.
       This case requires the user to have configured the XML correctly
       to load an anlytic soln, and compare it to the correct fields.
       Will check that each field flagged to be analysed is within
       the expected tolerance. Uses a
       :class:`~credo.systest.fieldWithinTolTest.FieldWithinTolTest`
       test component to perform the check.
       
       Optional constructor keywords:

       * defFieldTol: The default tolerance to be applied when comparing fields of
         interest to the analytic solution.
         See also the FieldWithinTolTest's
         :attr:`~credo.systest.fieldWithinTolTest.FieldWithinTolTest.defFieldTol`.
       * fieldTols: a dictionary of tolerances to use when testing particular
         fields, rather than the default tolerance defined by 
         the defFieldTol argument.
          
       .. attribute:: fTestName

          Standard name to use for this test's field comparison TestComponent
          in the :attr:`~credo.systest.api.SysTest.testComponents` list.
        '''

    fTestName = 'Analytic Solution compare'
    description = '''Runs a Model that has a defined analytic solution,
        and checks the outputted fields are within a given error tolerance
        of that analytic solution.'''
    passMsg = "All fields were within required tolerance of analytic"\
        " solution at end of run."
    failMsg = "At least one Field not within tolerance of analytic soln."

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            defFieldTol=3e-2, fieldTols=None, 
            paramOverrides=None, solverOpts=None, nameSuffix=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Analytic", nameSuffix)
        self.testComponents[self.fTestName] = FieldWithinTolTest(
            defFieldTol=defFieldTol, fieldTols=fieldTols)

    def genSuite(self):
        """See base class :meth:`~credo.systest.api.SysTest.genSuite`.

        For this test, just a single model run is needed, to run
        the model and compare against the analytic solution."""
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite

        mRun = self._createDefaultModelRun(self.testName, 
            self.outputPathBase)
        # For analytic test, read fields to analyse from the XML
        fTests = self.testComponents[self.fTestName]
        fTests.attachOps(mRun)
        mSuite.addRun(mRun, "Run the model and generate analytic soln.")

        return mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~credo.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check fieldresults exists, and is right length
            # Check each fieldResult contains correct fields
            pass

    # NB: Possible custom result plotting
    # Or is it appropriate to control from here?
    #for fRes in mResult.fieldResults:
    #    fRes.plotOverTime(show=False, path=mResult.outputPath)

    def _writeXMLCustomSpec(self, specNode):
        pass
