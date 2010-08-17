# UWAnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa import modelsuite as msuite
from uwa.modelrun import ModelRun
from uwa.modelsuite import ModelSuite, StgXMLVariant

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

    def test_runAll(self):
        mSuite = ModelSuite(os.path.join("output","suiteTest"))
        results = mSuite.runAll()
        self.assertEqual(results,[])
        # Now add some runs
        mRun1 = ModelRun("testRun1",["Input1.xml"],"./output/tr1")
        mRun2 = ModelRun("testRun2",["Input2.xml"],"./output/tr2")
        mSuite.addRun(mRun1, "Initial run")
        mSuite.addRun(mRun2, "Second run")
        #TODO: some sort of --pretend or --dry-run mode?
        #results = self.mSuite.runAll()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
