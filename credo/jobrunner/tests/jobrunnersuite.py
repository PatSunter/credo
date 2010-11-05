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
import shutil
import tempfile
import unittest

from credo.modelrun import ModelRun
from credo.modelresult import ModelResult
from credo.modelsuite import ModelSuite
from credo.jobrunner.api import JobRunner
#from skeletonClasses import SkeletonModelRun, SkeletonModelSuite

class SkeletonModelRun(ModelRun):
    def __init__(self, name, outputPath):
        self.name = name
        self.outputPath = outputPath
    pass

class SkeletonModelResult(ModelResult):
    def __init__(self, modelName):
        self.modelName = modelName
    pass

class SkeletonModelSuite(ModelSuite):
    def __init__(self):
        self.runs = []
        self.resultsList = []

class TestJobRunner(JobRunner):
    """A basic JobRunner, but with the runModel overridden to just print info."""
    def runModel(self, modelRun, prefixStr=None,
            extraCmdLineOpts=None, dryRun=False, maxRunTime=None):
        if dryRun is True:
            print "Called to run modelRun %s" % (modelRun.name)
            runOptsDict = {
                'prefixStr':prefixStr,
                'extraCmdLineOpts':extraCmdLineOpts,
                'dryRun':dryRun,
                'maxRunTime':maxRunTime}
            return None
        else:
            return SkeletonModelResult(modelRun.name)

class JobRunnerTestCase(unittest.TestCase):
    def setUp(self):
        self.jobRunner = TestJobRunner()
        self.skelMRun1 = SkeletonModelRun("skelMRun1", "output/test1")
        self.skelMRun2 = SkeletonModelRun("skelMRun2", "output/test2")
        self.skelMSuite = SkeletonModelSuite()
        self.skelMSuite.runs = [self.skelMRun1, self.skelMRun2]
        self.skelMSuite.runDescrips = ["skelMRun1 run", 
            "skelMRun2 run"]
        self.skelMSuite.runCustomOptSets = [
            "petscOpts1",
            "petscOpts2"]

    def tearDown(self):
        pass

    def test_runSuite(self):
        # Try with dryRun set to True, should be no results
        extraCmdLineOpts = "extraCmdLineOpts=1"
        results = self.jobRunner.runSuite(self.skelMSuite,
            extraCmdLineOpts=extraCmdLineOpts, dryRun=True, maxRunTime=200)
        self.assertEqual(len(results), 0)    
        # Try with dryRun set to False
        results = self.jobRunner.runSuite(self.skelMSuite,
            extraCmdLineOpts=extraCmdLineOpts, dryRun=False, maxRunTime=200)
        self.assertEqual(len(results), len(self.skelMSuite.runs))    
        for resI, res in enumerate(results):
            self.assertTrue(isinstance(res, ModelResult))
            self.assertEqual(res.modelName, self.skelMSuite.runs[resI].name)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JobRunnerTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
