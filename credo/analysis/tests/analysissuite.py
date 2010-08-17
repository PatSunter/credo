# CREDOnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

import credo.analysis

class AnalysisTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')

    def tearDown(self):
        shutil.rmtree(self.basedir)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AnalysisTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
