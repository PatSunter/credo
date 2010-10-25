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
from xml.etree import ElementTree as etree

from credo.modelsuite import ModelSuite
from credo.modelrun import SimParams
import credo.jobrunner
from . import api
from credo.systest.imageCompTest import ImageCompTest

class ImageReferenceTest(api.SysTest):
    '''An image comparison against Reference System test.
    To do this, creates a set of several 
    :class:`~credo.systest.imageCompTest.ImageCompTest` Test Components for
    each image you wish to test.

    Optional contructor keywords:
    
    * runSteps: Number of steps the model should be run for before
       comparing images.
    * defImageTol: Default tolerance to use when comparing images (as a tuple
       as required by :func:`credo.analysis.images.compare`).
    * imageTols: If provided, must be a dictionary mapping image names to 
       tolerances to use when checking.
    * expPathPrefix: Directory to look for expected image file runs.   
    '''

    description = '''Runs a Model for a set number of timesteps,
        then checks the specified images match previously-generated
        ones within given tolerances.'''
    passMsg = "All images were within required tolerance of reference"\
        " ones at end of run."
    failMsg = "An image was not within tolerance of reference version."

    def __init__(self, inputFiles, outputPathBase,
            imagesToTest, nproc=1, runSteps=20, defImageTol=(1e-2, 1e-2),
            imageTols=None, paramOverrides=None,
            solverOpts=None, basePath=None, expPathPrefix="expected",
            nameSuffix=None, timeout=None):
        api.SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "ImageReference", 
            basePath, nameSuffix, timeout)
        testNameBasic = api.getStdTestNameBasic(self.testType+"Test",
            inputFiles)
        self.expectedSolnPath = os.path.join(expPathPrefix, testNameBasic)
        self.imagesToTest = imagesToTest
        assert isinstance(self.imagesToTest, list)
        self.runSteps = runSteps
        self.defImageTol = defImageTol
        self.imageTols = imageTols
        if self.imageTols is not None:
            assert isinstance(self.imageTols, dict)
        for ii, imageFilename in enumerate(self.imagesToTest):
            if self.imageTols is not None and imageFilename in self.imageTols:
                imageTol = self.imageTols[imageFilename]
            else:
                imageTol = self.defImageTol
            testName = 'Image(s) Reference Solution compare - %s' \
                % imageFilename
            self.testComponents[testName] = ImageCompTest(imageFilename,
                imageTol, refPath=self.expectedSolnPath)

    def setup(self):
        '''Do a run to create the reference images to use.'''

        print "Running the model to create reference images after %d"\
            " steps, and saving in dir '%s'" % \
            (self.runSteps, self.expectedSolnPath)
        mRun = self._createDefaultModelRun(self.testName+"-createReference",
            self.expectedSolnPath)
        mRun.simParams = SimParams(nsteps=self.runSteps, cpevery=0,
            dumpevery=self.runSteps)
        for imageComp in self.testComponents.itervalues():
            imageComp.attachOps(mRun)
        mRun.writeInfoXML()
        jobRunner = credo.jobrunner.defaultRunner()
        result = jobRunner.runModel(mRun)
        # Now check the required images were actually created
        for imageComp in self.testComponents.itervalues():
            refImageFilename = os.path.join(self.expectedSolnPath,
                imageComp.imageFilename)
            if not os.path.exists(refImageFilename):
                raise api.SysTestSetupError("After running model to generate"\
                    " reference image for image '%s', image file doesn't"\
                    " exist. Check your Model's XML that it's set to"\
                    " generate the image correctly, and/or the image filename"\
                    " you specified in your test is correct."\
                    % refImageFilename)
                
        result.writeRecordXML()

    # TODO: a pre-check phase - check the reference dir exists?

    def genSuite(self):
        """See base class :meth:`~credo.systest.api.SysTest.genSuite`.

        For this test, just a single model run is needed, to run
        the model and compare against the reference solution."""
        mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        self.mSuite = mSuite
        # Normal mode
        mRun = self._createDefaultModelRun(self.testName, self.outputPathBase)
        mRun.simParams = SimParams(nsteps=self.runSteps,
            cpevery=0, dumpevery=self.runSteps)
        for imageComp in self.testComponents.itervalues():
            imageComp.attachOps(mRun)
        mSuite.addRun(mRun, "Run the model, and check images against "\
            "previously generated reference images.")
        return mSuite

    def checkResultValid(self, resultsSet):
        """See base class :meth:`~credo.systest.api.SysTest.checkResultValid`."""
        # TODO check it's a result instance
        # check number of results is correct
        for mResult in resultsSet:
            # Check right images are present
            pass

    def _writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'runSteps').text = str(self.runSteps)
        imagesToTestNode = etree.SubElement(specNode, 'imagesToTest')
        for imageName in self.imagesToTest:
            imageNode = etree.SubElement(imagesToTestNode, 'image',
                name=imageName)
