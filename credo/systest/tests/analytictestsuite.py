import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from credo.systest.analytic import AnalyticTest

class AnalyticTestTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir,
                #self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')
        self.sysTest = AnalyticTest("TestModel.xml", "./output/analyticTest")

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_checkGenSuite(self):
        # TODO
        mrSuite = self.sysTest.genSuite()
        self.fail("Not written yet")

    def test_checkResultValid(self):
        # TODO
        self.fail("Not written yet")

    def test_getStatus(self):
        # TODO
        self.fail("Not written yet")

    def test_writeXML(self):
        # TODO
        self.fail("Not written yet")

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AnalyticTestTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
