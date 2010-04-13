# UWAnalysis Unit test

import os
import cPickle as pickle
import shutil
import tempfile
import unittest

from uwa import modelrun as mrun
from uwa import modelresult as mres
from uwa.modelrun import FieldTestsInfo

class UwaTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        #os.makedirs(os.path.join(self.basedir,self.results_dir,'StGermain'))
            #self.results_xml = open(os.path.join(self.basedir, self.results_dir, 'StGermain', 'TEST-FooSuite.xml'), 'w' )

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_writeModelRunXML(self):
        nproc = 2
        modelRun = mrun.ModelRun( 'TestModel', ["testModel.xml"], 'output/testModel', nproc )
        modelRun.simParams = mrun.SimParams( nsteps=5, cpevery=10 )
        mrun.writeModelRunXML( modelRun )

    def test_writeModelResultsXML(self):
        results = mres.ModelResult( 'TestModel', 2.07 )
        tol = 0.01
        results.recordFieldResult( 'VelocityField', tol, [3.5e-4, 4.4e-3] )
        results.recordFieldResult( 'PressureField', tol, [3.5e-2] )
        mres.writeModelResultsXML( results )

    def test_updateModelResultsXMLFieldInfo(self):
        modName = 'TestModel'
        results = mres.ModelResult( modName, 2.07 )
        resFile = mres.writeModelResultsXML( results, filename="ModelResult-TestModel-inc.xml" )
        tol = 0.01
        fr = results.recordFieldResult( 'VelocityField', tol, [3.5e-4, 4.9e-2] )
        mres.updateModelResultsXMLFieldInfo( resFile, fr )
        fr = results.recordFieldResult( 'PressureField', tol, [3.5e-2] )
        mres.updateModelResultsXMLFieldInfo( resFile, fr )

    def test_addFieldTest(self):
        fieldTests = FieldTestsInfo()
        self.assertEqual( fieldTests.fields, {} )
        fieldTests.setAllTols( 0.02 )
        self.assertEqual( fieldTests.fields, {} )
        tempFT = mrun.FieldTest( 'TemperatureField' )
        fieldTests.add( tempFT )
        velFT = mrun.FieldTest( 'VelocityField' )
        fieldTests.add( velFT )
        self.assertEqual( fieldTests.fields, {'TemperatureField':tempFT,'VelocityField':velFT} )

    def test_setAllFieldTolerances(self):
        fieldTests = FieldTestsInfo()
        fieldTests.setAllTols( 0.02 )
        tempFT = mrun.FieldTest( 'TemperatureField' )
        velFT = mrun.FieldTest( 'VelocityField', 0.07 )
        fieldTests.fields = {'TemperatureField':tempFT, 'VelocityField':velFT} 
        fieldTol = 3e-2
        fieldTests.setAllTols( fieldTol )
        for fieldTest in fieldTests.fields.values():
            self.assertEqual( fieldTest.tol, fieldTol )

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UwaTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
