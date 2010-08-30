##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA

# CREDOnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from lxml import etree

from credo import modelresult as mres
from credo.modelresult import ModelResult, JobMetaInfo

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
        results.writeRecordXML(prettyPrint=True)

    def test_updateModelResultsXMLFieldInfo(self):
        modName = 'TestModel'
        results = mres.ModelResult(modName, "./output", 2.07)
        resFile = results.writeRecordXML(
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
