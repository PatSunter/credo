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
import cPickle as pickle
import shutil
import tempfile
import unittest
import itertools

from credo import modelsuite as msuite
from credo.modelrun import ModelRun
from credo.modelsuite import ModelSuite, StgXMLVariant
import credo.modelsuite as msuite

# Skeleton classes
#class SkelModelRun(ModelRun):

class ModelSuiteTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.mRun1 = ModelRun("testRun1",["Input1.xml"],"./output/tr1")
        self.yRange = [-16000, -10000, -3000]
        self.zRange = [10000, 11000]
        self.stgI1 = StgXMLVariant("minY", self.yRange)
        self.stgI2 = StgXMLVariant("maxZ", self.zRange)

    def tearDown(self):
        # TODO: tear down lxml document?
        shutil.rmtree(self.basedir)

    def test_variantGen(self):
        for paramI in range(self.stgI1.varLen()):
            self.stgI1.applyToModel(self.mRun1, paramI)
            self.assertEqual(self.mRun1.paramOverrides['minY'],
                self.yRange[paramI])

        for paramI in range(self.stgI2.varLen()):
            self.stgI2.applyToModel(self.mRun1, paramI)
            self.assertEqual(self.mRun1.paramOverrides['maxZ'],
                self.zRange[paramI])

    def test_getVariantsDicts(self):
        varDicts = msuite.getVariantsDicts(itertools.izip,
            [self.stgI1, self.stgI2])
        self.assertEqual(len(varDicts), min(
            map(len, [self.yRange, self.zRange])))
        for ii, varDict in enumerate(varDicts):
            self.assertEqual(varDict['minY'], self.yRange[ii])
            self.assertEqual(varDict['maxZ'], self.zRange[ii])
            
        varDicts = msuite.getVariantsDicts(msuite.productCalc,
            [self.stgI1, self.stgI2])
        self.assertEqual(len(varDicts), (len(self.yRange) * len(self.zRange)))
        # Loop through and check the product has worked.
        for ii in range(len(self.yRange)):
            for jj in range(len(self.zRange)):
                entryI = ii * len(self.zRange) + jj
                varDict = varDicts[entryI]
                self.assertEqual(varDict['minY'], self.yRange[ii])
                self.assertEqual(varDict['maxZ'], self.zRange[jj])

    def test_variantsDict(self):    
        mSuite = ModelSuite(os.path.join("output","genSuiteTest"),
            templateMRun = self.mRun1)
        mSuite.addVariant("depthVary", self.stgI1)
        mSuite.addVariant("ZVary", self.stgI2)
        import pdb
        pbd.set_trace()
        varDict = mSuite.getVariantsDict(0)

    def test_generateRuns_product(self):        
        mSuite = ModelSuite(os.path.join("output","genSuiteTest"),
            templateMRun = self.mRun1)
        mSuite.addVariant("depthVary", self.stgI1)
        mSuite.addVariant("ZVary", self.stgI2)
        mSuite.generateRuns()
        self.assertEqual(len(mSuite.runs), len(self.yRange) * len(self.zRange))
        # These are indices into lists above, created manually for testing
        expIndices = [(0,0),(0,1),(1,0),(1,1)]
        for ii, expIndexTuple in enumerate(expIndices):
            yIndex, zIndex = expIndexTuple
            self.assertEqual(mSuite.runs[ii].paramOverrides['minY'],
                self.yRange[yIndex])
            self.assertEqual(mSuite.runs[ii].paramOverrides['maxZ'],
                self.zRange[zIndex])
            self.assertEqual(mSuite.runs[ii].outputPath,
                os.path.join("output", "genSuiteTest",
                "depthVary_%s-ZVary_%s" % (self.yRange[yIndex],
                    self.zRange[zIndex])))

    def test_generateRuns_izip(self):        
        mSuite = ModelSuite(os.path.join("output","genSuiteTest"),
            templateMRun = self.mRun1)

        mSuite.addVariant("depthVary", self.stgI1)
        mSuite.addVariant("ZVary", self.stgI2)
        mSuite.generateRuns(itertools.izip)
        self.assertEqual(len(mSuite.runs),
            min(len(self.yRange), len(self.zRange)))
        # These are indices into lists above, created manually for testing
        expIndices = [(0,0),(1,1)]
        for ii, expIndexes in enumerate(expIndices):
            yIndex, zIndex = expIndexes
            self.assertEqual(mSuite.runs[ii].paramOverrides['minY'],
                self.yRange[yIndex])
            self.assertEqual(mSuite.runs[ii].paramOverrides['maxZ'],
                self.zRange[zIndex])
            self.assertEqual(mSuite.runs[ii].outputPath,
                os.path.join("output", "genSuiteTest",
                "depthVary_%s-ZVary_%s" % (self.yRange[yIndex],
                    self.zRange[zIndex])))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
