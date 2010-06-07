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
    
    def test_getElementType(self):
        # Regular params syntax
        testNode = etree.Element(stgxml.STG_PARAM_TAG, name="dim")
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_PARAM_TAG)
        testNode = etree.Element(stgxml.STG_LIST_TAG, name="test")
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_LIST_TAG)
        testNode = etree.Element(stgxml.STG_STRUCT_TAG, name="test")
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_STRUCT_TAG)
        # bad case
        testNode = etree.Element("sillyTag", name="test")
        self.assertRaises(ValueError, stgxml.getElementType, testNode)

        # Element params syntax
        testNode = etree.Element(stgxml.STG_ELEMENT_TAG,
            type=stgxml.STG_PARAM_TAG, name="dim")
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_PARAM_TAG)
        testNode = etree.Element(stgxml.STG_ELEMENT_TAG,
            type=stgxml.STG_LIST_TAG, name="test")
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_LIST_TAG)
        testNode = etree.Element(stgxml.STG_ELEMENT_TAG,
            type=stgxml.STG_STRUCT_TAG, name="test")
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_STRUCT_TAG)
        # bad cases
        testNode = etree.Element(stgxml.STG_ELEMENT_TAG, name="test")
        self.assertRaises(ValueError, stgxml.getElementType, testNode)
        testNode = etree.Element(stgxml.STG_ELEMENT_TAG,
            type="sillyType", name="test")
        self.assertRaises(ValueError, stgxml.getElementType, testNode)

        # Special params - should be recognised
        testNode = etree.Element(stgxml.STG_IMPORT_TAG)
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_LIST_TAG)
        testNode = etree.Element(stgxml.STG_PLUGINS_TAG)
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_LIST_TAG)
        testNode = etree.Element(stgxml.STG_COMPONENTS_TAG)
        self.assertEqual(stgxml.getElementType(testNode), stgxml.STG_STRUCT_TAG)

    def test_getNodeFromStrSpec(self):
        # Try all kinds of combinations of good and bad input
        # Basic elements - good cases
        node = stgxml.getNodeFromStrSpec(self.flatXMLRoot, "dim")
        self.assertEqual(node.attrib['name'], "dim")
        self.assertEqual(node.attrib['type'], stgxml.STG_PARAM_TAG)
        self.assertEqual(node.text, "2")
        node = stgxml.getNodeFromStrSpec(self.flatXMLRoot, "velocityICs")
        self.assertEqual(node.attrib['name'], "velocityICs")
        self.assertEqual(node.attrib['type'], stgxml.STG_STRUCT_TAG)
        # Basic elements - bad cases
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "voodoo")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, ".velocityICs")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "..")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, ".[")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, ".[]")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "[]55")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "[].")
        # TODO: figure out how to handle these below - allowable on recursion,
        # but not from the root.
        #self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
        #    self.flatXMLRoot, "[]")
        #self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
        #    self.flatXMLRoot, "[0]")
        
        # Struct recursion - good cases
        node = stgxml.getNodeFromStrSpec(self.flatXMLRoot, "velocityICs.type")
        self.assertEqual(node.attrib['name'], "type")
        self.assertEqual(node.attrib['type'], stgxml.STG_PARAM_TAG)
        self.assertEqual(node.text, "CompositeVC")
        node = stgxml.getNodeFromStrSpec(self.flatXMLRoot,
            "velocityICs.vcList")
        self.assertEqual(node.attrib['name'], "vcList")
        self.assertEqual(node.attrib['type'], stgxml.STG_LIST_TAG)
        # Struct recursion - bad cases
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.voodoo")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.[")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.]")

        # Struct - list recursion - good cases
        node = stgxml.getNodeFromStrSpec(
            self.flatXMLRoot, "velocityICs.vcList[0]")
        self.assertEqual(node.attrib['type'], stgxml.STG_STRUCT_TAG)
        self.assertTrue('name' not in node.attrib)
        self.assertEqual(node[0].text, "AllNodesVC")
        # Struct - list recursion - bad cases
        # In this case, list is only of length 1.
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[1]")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[455]")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[455")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[455]voodoo")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[455]voodoo.jabbar")
        self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
            self.flatXMLRoot, "velocityICs.vcList[.]")
        # TODO: Special case - probably need a "listAppendMode" flag to decide
        #  if this is ok or not
        #self.assertRaises(ValueError, stgxml.getNodeFromStrSpec,
        #    self.flatXMLRoot, "velocityICs.vcList[]")

        # Deep recursion - good cases
        node = stgxml.getNodeFromStrSpec(
            self.flatXMLRoot, "temperatureBCs.vcList[0].Shape")
        self.assertEqual(node.attrib['type'], stgxml.STG_PARAM_TAG)
        self.assertEqual(node.attrib['name'], "Shape")
        self.assertEqual(node.text, "initialConditionShape")
        node = stgxml.getNodeFromStrSpec(
            self.flatXMLRoot, "temperatureBCs.vcList[0].variables")
        self.assertEqual(node.attrib['name'], "variables")
        self.assertEqual(node.attrib['type'], stgxml.STG_LIST_TAG)
        node = stgxml.getNodeFromStrSpec(
            self.flatXMLRoot, "temperatureBCs.vcList[0].variables[0]")
        self.assertEqual(node.attrib['type'], stgxml.STG_STRUCT_TAG)
        self.assertTrue('name' not in node.attrib)
        self.assertEqual(node[0].text, "temperature")
        node = stgxml.getNodeFromStrSpec(
            self.flatXMLRoot, "temperatureBCs.vcList[0].variables[0].value")
        self.assertEqual(node.attrib['type'], stgxml.STG_PARAM_TAG)
        self.assertEqual(node.attrib['name'], "value")
        self.assertEqual(node.text, "Temperature_CosineHill")
        # Deep recursion - bad cases
        # TODO
        
        # TODO: test this sort of stuff in CosineHillRotate.xml (maybe in a for
        # loop)

            

    # Writing things out tests
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
