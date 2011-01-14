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
from credo.systest.api import SysTest, TestComponent, CREDO_PASS, CREDO_FAIL
import credo.utils

class SciBenchmarkTest(SysTest):
    '''A Science benchmark test.
        This is an open-ended system test, designed for the user to add multiple
        :class:`~credo.systest.api.TestComponent` s to,
        which test the conditions of the benchmark.
        Contains extra capabilities to report more fully on the test result
        than a standard system test.
        
        See the examples section of the CREDO documentation,
        :ref:`credo-examples-scibenchmarking`, for examples of sci benchmarking
        in practice.'''

    description = '''Runs a user-defined science benchmark.'''

    def __init__(self, testName, outputPathBase,
            basePath=None, nproc=1, timeout=None):
        if basePath is None:
            # Since expect this class to be used directly,
            #  get calling path 1 levels up
            basePath = credo.utils.getCallingPath(1)
        SysTest.__init__(self, "SciBenchmark", testName, basePath, 
            outputPathBase, nproc, timeout)

    def addTestComp(self, testComp, testCompName):
        """Add a testComponent (:class:`~credo.systest.api.TestComponent`)
        with name testCompName to the list of test
        components to be applied as part of determining if the benchmark
        has passed."""
        if not isinstance(testComp, TestComponent):
            raise TypeError("Test component passed in to be added to"\
                " benchmark, '%s', not an instance of a TestComponent."\
                % (testComp))
        self.testComponents[testCompName] = testComp

    def _writeXMLCustomSpec(self, specNode):
        # TODO: write info about the modelRuns making up the suite ...
        #  or should this be a standard feature of all Sys tests writeups?
        # TODO: write stuff like paper references here?
        # TODO: does this need to be converted to an FP to allow
         # user to more easily over-ride? Or is that done via
         #  custom test components?
        pass

    def genSuite(self):
        """See base class :meth:`~credo.systest.api.SysTest.genSuite`.
        
        For Sci Benchmarks, simply return the suite of models the user
        has constructed and added themselves, after ensuring any
        necessary test component ops are attached."""
        if self.mSuite == None:
            raise AttributeError("Error: for SciBenchmark Tests, you as"\
                " the user need to configure and set the ModelSuite used"\
                " for the test and assign to the mSuite parameter.")
        for tComp in self.testComponents.itervalues():
            for mRun in self.mSuite.runs:
                tComp.attachOps(mRun)
        return self.mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~credo.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            pass

    def getStatus(self, resultsSet):
        """See base class :meth:`~credo.systest.api.SysTest.getStatus`."""
        self.checkResultValid(resultsSet)
        mResult = resultsSet[0]

        overallResult = True
        failedCompNames = []
        for tCompName, tComp in self.testComponents.iteritems():
            result = tComp.check(resultsSet)
            if not result:
                overallResult = False
                failedCompNames.append(tCompName)

        if overallResult:    
            testStatus = CREDO_PASS("All aspects of the benchmark passed.")
        else:        
            testStatus = CREDO_FAIL("The following components of the benchmark" \
                " failed: %s" % failedCompNames)

        self.testStatus = testStatus
        return testStatus
        
