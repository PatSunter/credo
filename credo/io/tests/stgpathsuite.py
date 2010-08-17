import os
import tempfile
import unittest
import shutil
import glob

from credo.io import stgpath
from xml.etree import ElementTree as etree

class StgPathTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        os.environ['STG_BASEDIR'] = os.path.abspath(
            os.path.join('..', '..', '..', '..'))

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_checkAllXMLInputFilesExist(self):
        sampleXMLs = glob.glob(os.path.join("sampleData", "stgXML", "*.xml"))
        try:
            stgpath.checkAllXMLInputFilesExist(sampleXMLs)
        except IOError:
            self.fail("Shouldn't produce IO error")
        self.assertRaises(IOError, stgpath.checkAllXMLInputFilesExist, ["boo"])
    
    def test_convertLocalXMLFilesToAbsPaths(self):
        sampleXMLsOrig = glob.glob(os.path.join(
            "sampleData", "stgXML", "*.xml")) 
        sampleXMLsTest = sampleXMLsOrig[:]
        stgpath.convertLocalXMLFilesToAbsPaths(sampleXMLsTest,
            "Underworld/SysTests")
        self.assertEqual(sampleXMLsOrig, sampleXMLsTest)   

    def test_convertLocalXMLFilesToAbsPaths_ConvertNeeded(self):
        testCallingPath = "Underworld/SysTests"
        sampleXMLsOrig = glob.glob(os.path.join(
            "sampleData", "stgXML", "*.xml"))
        sampleXMLsOrig.append(os.path.join("rel","notExist.xml"))    
        sampleXMLsTest = sampleXMLsOrig[:]
        stgpath.convertLocalXMLFilesToAbsPaths(sampleXMLsTest, testCallingPath)
        self.assertEqual(sampleXMLsOrig[:-1], sampleXMLsTest[:-1])   
        self.assertEqual(sampleXMLsTest[-1], 
            os.path.join(testCallingPath, "rel", "notExist.xml"))

# TODO: more tests required!

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StgPathTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
