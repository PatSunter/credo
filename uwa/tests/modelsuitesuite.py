# UWAnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa import modelsuite as msuite
from uwa.modelrun import ModelRun
from uwa.modelsuite import ModelSuite

# Skeleton classes
#class SkelModelRun(ModelRun):

class ModelSuiteTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.mSuite = ModelSuite()

    def tearDown(self):
        # TODO: tear down lxml document?
        shutil.rmtree(self.basedir)

    def test_runAll(self):
        results = self.mSuite.runAll()
        self.assertEqual(results,[])
        # Now add some runs
        mRun1 = ModelRun("testRun1",["Input1.xml"],"./output/tr1")
        mRun2 = ModelRun("testRun2",["Input2.xml"],"./output/tr2")
        self.mSuite.addRun(mRun1, "Initial run")
        self.mSuite.addRun(mRun2, "Second run")
        results = self.mSuite.runAll()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
