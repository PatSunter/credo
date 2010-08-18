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

import os
import shutil
import tempfile
import unittest

from credo.io.stgfreq import FreqOutput
import credo.io.stgfreq as stgfreq

class StgFreqTestCase(unittest.TestCase):
    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.stgFreq = FreqOutput("./sampleData")
        self.tSteps = [2, 4, 6, 8, 10]
        self.timeVals = [0.0125, 0.0375, 0.0625, 0.0875, 0.1125]
        self.VRMSVals = [3, 3.2, 3.8, 3.4, 2.6]

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_getHeaders(self):
        headers = self.stgFreq.getHeaders()
        self.assertEqual(headers, ['Timestep','Time','VRMS'])
        self.assertEqual(self.stgFreq.headerColMap, {'Timestep':0, 'Time':1,
            'VRMS':2})

    def test_getAllRecords(self):
        records = self.stgFreq.getAllRecords()
        for ii in range(0,5):
            self.assertEqual(records[ii][0], self.tSteps[ii])
            self.assertAlmostEqual(records[ii][1], self.timeVals[ii])
            self.assertAlmostEqual(records[ii][2], self.VRMSVals[ii])
    
    def test_getValueAtStep(self):
        self.stgFreq.populateFromFile()
        time4 = self.stgFreq.getValueAtStep("Time", 4)
        self.assertAlmostEqual(time4, 0.0375)
        VRMS2 = self.stgFreq.getValueAtStep("VRMS", 2)
        self.assertAlmostEqual(VRMS2, 3)
    
    def test_getRecordDictAtStep(self):
        self.stgFreq.populateFromFile()
        recordDict = self.stgFreq.getRecordDictAtStep(6)
        self.assertEqual(recordDict, {'Timestep':6,'Time':0.0625,"VRMS":3.8})

    def test_finalStep(self):
        self.assertEqual(10, self.stgFreq.finalStep())
    
    def test_getValuesArray(self):
        valArray = self.stgFreq.getValuesArray('Time')
        for ii, val in enumerate(valArray):
            self.assertAlmostEqual(val, self.timeVals[ii])
    
    def test_getTimeStepsArray(self):
        timeStepsArray = self.stgFreq.getTimeStepsArray()
        for ii, step in enumerate(timeStepsArray):
            self.assertEqual(step, self.tSteps[ii])

    def test_getMin(self):
        for headerName, testList in [('Time', self.timeVals),
                ('VRMS', self.VRMSVals)]:
            minVal, minStep = self.stgFreq.getMin(headerName)
            calcMin = min(testList)
            calcIndex = testList.index(calcMin)
            self.assertAlmostEqual(minVal, calcMin)
            self.assertEqual(minStep, self.tSteps[calcIndex])

    def test_getMax(self):
        for headerName, testList in [('Time', self.timeVals),
                ('VRMS', self.VRMSVals)]:
            maxVal, maxStep = self.stgFreq.getMax(headerName)
            #print "max for header '%s' calc to be %f at step %d"\
            #    % (headerName, maxVal, maxStep)
            calcMax = max(testList)
            calcIndex = testList.index(calcMax)
            self.assertAlmostEqual(maxVal, calcMax)
            self.assertEqual(maxStep, self.tSteps[calcIndex])

    def test_getMean(self):
        meanVal = self.stgFreq.getMean('VRMS')
        calcMean = sum(self.VRMSVals, 0.0) / len(self.VRMSVals)
        self.assertAlmostEqual(meanVal, calcMean)

    def test_getReductionOps(self):
        for headerName, testList in [('Time', self.timeVals),
                ('VRMS', self.VRMSVals)]:
            lastVal, lastStep = self.stgFreq.getReductionOp(headerName,
                stgfreq.last)
            calcLast = testList[-1]
            calcIndex = len(testList)-1
            self.assertAlmostEqual(lastVal, calcLast)
            self.assertEqual(lastStep, self.tSteps[calcIndex])
        for headerName, testList in [('Time', self.timeVals),
                ('VRMS', self.VRMSVals)]:
            firstVal, firstStep = self.stgFreq.getReductionOp(headerName,
                stgfreq.first)
            calcFirst = testList[0]
            calcIndex = 0
            self.assertAlmostEqual(firstVal, calcFirst)
            self.assertEqual(firstStep, self.tSteps[calcIndex])

    def test_plotOverTime(self):
        self.stgFreq.plotOverTime("Time", show=False, path="output/Plots")
        self.stgFreq.plotOverTime("VRMS", show=False, path="output/Plots")
    
    def test_printAllMinMax(self):
        self.stgFreq.printAllMinMax()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StgFreqTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
