import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa import modelrun as mrun
from uwa import modelresult as mres

class ModelRunTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_writeModelRunXML(self):
        nproc = 2
        modelRun = mrun.ModelRun('TestModel', ["testModel.xml"], \
            'output/testModel', nproc)
        modelRun.simParams = mrun.SimParams(nsteps=5, cpevery=10)
        mrun.writeModelRunXML(modelRun)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelRunTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
