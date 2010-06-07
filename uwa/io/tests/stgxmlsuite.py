import os
import tempfile
import unittest
import shutil

from uwa.io import stgxml
from lxml import etree

class StgXMLTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.dataPath = "sampleData/stgXML"
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_getParamValue(self):
        xmlDoc = etree.parse(os.path.join(self.dataPath, "flattenedModel.xml"))
        stgRoot = xmlDoc.getroot()
        dimVal = stgxml.getParamValue(stgRoot, "dim", int)
        self.assertEqual(dimVal, 2)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StgXMLTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
