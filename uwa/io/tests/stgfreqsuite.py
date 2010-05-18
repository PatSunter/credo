import os
import shutil
import tempfile
import unittest

from uwa.io.stgfreq import FreqOutput

class StgFreqTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        self.stgFreq = FreqOutput("./output")
        self.expTimeVals = [0.0125, 0.0375, 0.0625, 0.0875, 0.1125]

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_getHeaders(self):
        headers = self.stgFreq.getHeaders()
        self.assertEqual(headers, ['Timestep','Time'])
        self.assertEqual(self.stgFreq.headerColMap, {'Timestep':0,'Time':1})

    def test_getAllRecords(self):
        records = self.stgFreq.getAllRecords()
        self.assertEqual(records[0], [2, self.expTimeVals[0]])
        self.assertEqual(records[1], [4, self.expTimeVals[1]])
        self.assertEqual(records[2], [6, self.expTimeVals[2]])
        self.assertEqual(records[3], [8, self.expTimeVals[3]])
        self.assertEqual(records[4], [10, self.expTimeVals[4]])
    
    def test_getValueAtStep(self):
        self.stgFreq.populateFromFile()
        time4 = self.stgFreq.getValueAtStep(4, "Time")
        self.assertEqual( time4, 0.0375)
    
    def test_getRecordDictAtStep(self):
        self.stgFreq.populateFromFile()
        recordDict = self.stgFreq.getRecordDictAtStep(6)
        self.assertEqual(recordDict, {'Timestep':6,'Time':0.0625})

    def test_finalStep(self):
        self.assertEqual(10, self.stgFreq.finalStep())
    
    def test_getValuesArray(self):
        valArray = self.stgFreq.getValuesArray('Time')
        for ii, val in enumerate(valArray):
            self.assertAlmostEqual(val, self.expTimeVals[ii])

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StgFreqTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
