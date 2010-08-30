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

# CREDOnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from credo import modelsuite as msuite
from credo.modelrun import ModelRun
from credo.modelsuite import ModelSuite, StgXMLVariant

# Skeleton classes
#class SkelModelRun(ModelRun):

class ModelSuiteTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())

    def tearDown(self):
        # TODO: tear down lxml document?
        shutil.rmtree(self.basedir)

    def test_variantGen(self):
        mRun1 = ModelRun("testRun1",["Input1.xml"],"./output/tr1")
        yRange = [-16000, -3000]
        zRange = [10000, 11000]
        stgI1 = StgXMLVariant("minY", yRange)
        stgI2 = StgXMLVariant("maxZ", zRange)

        for paramI in range(stgI1.varLen()):
            stgI1.applyToModel(mRun1, paramI)
            self.assertEqual(mRun1.paramOverrides['minY'],yRange[paramI])

        for paramI in range(stgI1.varLen()):
            stgI2.applyToModel(mRun1, paramI)
            self.assertEqual(mRun1.paramOverrides['maxZ'],zRange[paramI])

    def test_generateRuns(self):        
        mRun1 = ModelRun("testRun1",["Input1.xml"],"./output/tr1")
        mSuite = ModelSuite(os.path.join("output","genSuiteTest"),
            templateMRun = mRun1)

        yRange = [-16000, -3000]
        zRange = [10000, 11000]
        stgI1 = StgXMLVariant("minY", yRange)
        stgI2 = StgXMLVariant("maxZ", zRange)
        #TODO: just allow to add as a list?
        mSuite.addVariant("depthVary", stgI1)
        mSuite.addVariant("ZVary", stgI2)
        mSuite.generateRuns()
        self.assertEqual(len(mSuite.runs), len(yRange) * len(zRange))
        # These are indices into lists above, created manually for testing
        expIndices = [(0,0),(0,1),(1,0),(1,1)]
        for ii, expIndexTuple in enumerate(expIndices):
            yIndex, zIndex = expIndexTuple
            self.assertEqual(mSuite.runs[ii].paramOverrides['minY'],
                yRange[yIndex])
            self.assertEqual(mSuite.runs[ii].paramOverrides['maxZ'],
                zRange[zIndex])
            self.assertEqual(mSuite.runs[ii].outputPath,
                os.path.join("output", "genSuiteTest",
                "depthVary_%s-ZVary_%s" % (yRange[yIndex],zRange[zIndex])))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
