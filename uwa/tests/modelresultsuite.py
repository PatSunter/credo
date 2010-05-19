# UWAnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from lxml import etree

from uwa import modelresult as mres
from uwa.modelresult import ModelResult, JobMetaInfo

class ModelResultTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w')
         # Useful for testing doc writing   
        self.xmlRoot = etree.Element(ModelResult.XML_INFO_TAG)
        self.xmlDoc = etree.ElementTree(self.xmlRoot)
        self.xmlFilename = os.path.join(self.basedir, "testOutput.xml")

    def tearDown(self):
        # TODO: tear down lxml document?
        shutil.rmtree(self.basedir)

    def test_WriteJobMetaInfo(self):
        simT = 10.7
        jmInfo = JobMetaInfo( simtime=simT )
        jmInfo.writeInfoXML(self.xmlRoot)
        childEls = self.xmlRoot.getchildren()
        self.assertEqual(len(childEls),1)
        jmEl = childEls[0]
        self.assertEqual(jmEl.tag, JobMetaInfo.XML_INFO_TAG)
        self.assertEqual(jmEl.text, None)
        jmChildren = jmEl.getchildren()
        self.assertEqual(len(jmChildren),1)
        self.assertEqual(jmChildren[0].tag,'simtime')
        self.assertEqual(jmChildren[0].text,str(simT))

    def test_writeModelResultsXML(self):
        results = mres.ModelResult('TestModel', "./output", 2.07)
        tol = 0.01
        results.recordFieldResult('VelocityField', tol, [3.5e-4, 4.4e-3])
        results.recordFieldResult('PressureField', tol, [3.5e-2])
        mres.writeModelResultsXML(results)

    def test_updateModelResultsXMLFieldInfo(self):
        modName = 'TestModel'
        results = mres.ModelResult(modName, "./output", 2.07)
        resFile = mres.writeModelResultsXML(results,\
            filename="ModelResult-TestModel-inc.xml")
        tol = 0.01
        fr = results.recordFieldResult('VelocityField', tol, [3.5e-4, 4.9e-2])
        mres.updateModelResultsXMLFieldInfo(resFile, fr)
        fr = results.recordFieldResult('PressureField', tol, [3.5e-2])
        mres.updateModelResultsXMLFieldInfo(resFile, fr)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ModelResultTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
