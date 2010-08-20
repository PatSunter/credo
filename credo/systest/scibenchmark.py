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

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            paramOverrides=None, solverOpts=None, nameSuffix=None,
            timeout=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc, 
            paramOverrides, solverOpts, "SciBenchmark", nameSuffix, timeout)

    def addTestComponent(self, testComp, testCompName):
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
        # TODO: write stuff like paper references here?
        pass

    def genSuite(self):
        """See base class :meth:`~credo.systest.api.SysTest.genSuite`.
        
        By default will create just a single model run.

        .. note:: for Benchmarks that involve running a suite of models, this 
           API may need re-thinking. Or else a separate SciBenchmarkSuite
           class could be added.
        """
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        mRun = self._createDefaultModelRun(self.testName, self.outputPathBase)
        for tComp in self.testComponents.itervalues():
            tComp.attachOps(mRun)
        mSuite.addRun(mRun, "Run the model needed for the benchmark.")
        return mSuite

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
        
