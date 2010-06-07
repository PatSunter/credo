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
        self.flatXMLDoc = etree.parse(os.path.join(self.dataPath, "flattenedModel.xml"))
        self.flatXMLRoot = self.flatXMLDoc.getroot()
        self.inXMLDoc = etree.parse(os.path.join(self.dataPath,
            "CosineHillRotateBC.xml"))
        self.inXMLRoot = self.inXMLDoc.getroot()
        self.testParamNode = etree.Element("param", name="dim")
        self.testParamNode.text = "2"

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_getParamNode(self):
        paramNode = stgxml.getParamNode(self.flatXMLRoot, "dim")
        self.assertEqual(paramNode.attrib['name'], "dim")
        self.assertEqual(paramNode.text, "2")
        paramNode = stgxml.getParamNode(self.inXMLRoot, "dim")
        self.assertEqual(paramNode.attrib['name'], "dim")
        # Whitespace not stripped automatically.
        self.assertEqual(paramNode.text.strip(), "2")
        paramNode = stgxml.getParamNode(self.flatXMLRoot, "voodoo")
        self.assertEqual(paramNode, None)

    def test_getListNode(self):
        listNode = stgxml.getListNode(self.flatXMLRoot, "FieldVariablesToCheckpoint")
        self.assertEqual(listNode.attrib['name'], "FieldVariablesToCheckpoint")
        self.assertEqual(listNode.text.strip(), "")
        self.assertEqual(len(listNode), 3)
        listNode = stgxml.getListNode(self.inXMLRoot, "plugins")
        self.assertEqual(listNode.attrib['name'], "plugins")
        self.assertEqual(listNode.text.strip(), "")
        self.assertEqual(len(listNode), 2)
        listNode = stgxml.getListNode(self.flatXMLRoot, "voodoo")
        self.assertEqual(listNode, None)

    def test_getStructNode(self):
        structNode = stgxml.getStructNode(self.flatXMLRoot, "velocityICs")
        self.assertEqual(structNode.attrib['name'], "velocityICs")
        self.assertEqual(structNode.text.strip(), "")
        self.assertEqual(len(structNode), 2)
        structNode = stgxml.getStructNode(self.inXMLRoot, "velocityICs")
        self.assertEqual(structNode.attrib['name'], "velocityICs")
        self.assertEqual(structNode.text.strip(), "")
        self.assertEqual(len(structNode), 2)
        structNode = stgxml.getStructNode(self.flatXMLRoot, "voodoo")
        self.assertEqual(structNode, None)

    def test_getParamValue(self):
        dimVal = stgxml.getParamValue(self.flatXMLRoot, "dim", int)
        self.assertEqual(dimVal, 2)
        # Should be able to cast as a string fine.
        dimVal = stgxml.getParamValue(self.flatXMLRoot, "dim", str)
        self.assertEqual(dimVal, "2")
        # Try to get non-existent
        noneVal = stgxml.getParamValue(self.flatXMLRoot, "voodoo", int)
        self.assertEqual(noneVal, None)
        # Try to get a struct 
        noneVal = stgxml.getParamValue(self.flatXMLRoot, "components", int)
        self.assertEqual(noneVal, None)
        noneVal = stgxml.getParamValue(self.flatXMLRoot, "temperatureBCs", int)
        self.assertEqual(noneVal, None)
        # Try from the non-flattened file
        dimVal = None
        dimVal = stgxml.getParamValue(self.inXMLRoot, "dim", int)
        self.assertEqual(dimVal, 2)
        dimVal = stgxml.getParamValue(self.flatXMLRoot, "dim", str)
        self.assertEqual(dimVal, "2")

    # Writing parameter tests
    def test_setMergeType(self):
        stgxml.setMergeType(self.testParamNode, 'append')
        self.assertEqual(self.testParamNode.attrib['mergeType'], 'append')
        stgxml.setMergeType(self.testParamNode, 'merge')
        self.assertEqual(self.testParamNode.attrib['mergeType'], 'merge')
        stgxml.setMergeType(self.testParamNode, 'replace')
        self.assertEqual(self.testParamNode.attrib['mergeType'], 'replace')
        self.assertRaises(ValueError, stgxml.setMergeType,
            self.testParamNode, 'FooFoo')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StgXMLTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
