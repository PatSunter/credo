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
import cPickle as pickle
import shutil
import tempfile
import unittest

import credo.analysis.images as imageOps

class AnalysisImagesTestCase(unittest.TestCase):

    def setUp(self):
        self.basedir = os.path.realpath(tempfile.mkdtemp())
        imgPath = os.path.join("input", "testImages")
        self.imageFname1 = os.path.join(imgPath, "window.00001.png")
        self.imageFname1_dup = os.path.join(imgPath, "window.00001_dup.png")
        self.imageFname2 = os.path.join(imgPath, "window.00002.png")

    def tearDown(self):
        shutil.rmtree(self.basedir)

    def test_compare(self):
        diffs = imageOps.compare(self.imageFname1, self.imageFname1_dup)
        self.assertAlmostEqual(diffs[0], 0)
        self.assertAlmostEqual(diffs[1], 0)
        diffs = imageOps.compare(self.imageFname1, self.imageFname2)
        self.assertTrue(0 < diffs[0] < 0.011)
        self.assertTrue(0 < diffs[1] < 0.002)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AnalysisImagesTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

