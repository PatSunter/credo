# UWAnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa import modelsuite as msuite
from uwa.modelsuite import ModelSuite

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
        # TODO - perhaps add skeleton classes
        self.fail("Need to write")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelSuiteTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
