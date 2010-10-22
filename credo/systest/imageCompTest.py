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

from credo.systest.api import TestComponent, CREDO_PASS, CREDO_FAIL
import credo.analysis.images as imageAnalysis

class ImageCompTest(TestComponent):
    """Checks whether an image produced by the run (eg by gLucifer)
    is within a given "tolerance" of an expected image.

    """
    DEFAULT_TOLS = (0.01, 0.01)
    DEFAULT_REFPATH = os.path.join('.', 'expected')

    def __init__(self, imageFilename,
            tol=None,
            refPath=None,
            genPath=None):
        TestComponent.__init__(self, "imagesWithinTol")
        self.imageFilename = imageFilename
        if tol is not None:
            self.tol = tol
        else:
            self.tol = self.DEFAULT_TOLS
        if refPath is not None:
            self.refPath = refPath
        else:
            self.refPath = self.DEFAULT_REFPATH
        if genPath is not None:
            self.genPath = genPath
        else:
            # in this case, we will read from the model's output dir.
            self.genPath = None
        self.imageResults = None
        self.imageErrors = None

    def attachOps(self, modelRun):
        """Implements base class
        :meth:`credo.systest.api.TestComponent.attachOps`."""
        # Nothing to do here - requires that the user has defined their
        # model XMLs correctly to generate the images.

    def check(self, resultsSet):
        """Implements base class
        :meth:`credo.systest.api.TestComponent.check`."""
        self.imageResults = []
        self.imageErrors = []
        statusMsg = ""
        numRuns = len(resultsSet)
        overallResult = True
        for runI, mResult in enumerate(resultsSet):
            refImageFname = os.path.join(self.refPath, self.imageFilename)
            if self.genPath is not None:
                genPath = self.genPath
            else:
                genPath = mResult.outputPath
            genImageFname = os.path.join(genPath, self.imageFilename)
            imageErrors = imageAnalysis.compare(
                refImageFname, genImageFname)
            imageResult = [diff <= tol for diff, tol in \
                zip(imageErrors, self.tol)]
            if False in imageResult:
                if numRuns > 1:
                    statusMsg += "For run %d out of %d: " % (runI, numRuns)
                statusMsg += "Image comp for image file '%s' errors %s not "\
                    " within tol %s of reference image\n"\
                    % (self.imageFilename, imageErrors, self.tol)
                overallResult = False    
            
            self.imageResults.append(imageResult)
            self.imageErrors.append(imageErrors)

        if False not in self.imageResults:
            statusMsg += "Image comp error within tolerances %s"\
                " of ref image for all runs.\n"\
                % (str(self.tol))

        print statusMsg
        if overallResult == False:
            self.tcStatus = CREDO_FAIL(statusMsg)
        else:
            self.tcStatus = CREDO_PASS(statusMsg)
        return overallResult

    def _writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'imageFilename').text = self.imageFilename
        tolNode = etree.SubElement(specNode, 'tol')
        for ii, tolComp in enumerate(self.tol):
            etree.SubElement(tolNode, str(ii)).text = str(tolComp)
        etree.SubElement(specNode, 'refPath').text = self.refPath
        if self.genPath is not None:
            etree.SubElement(specNode, 'genPath').text = self.genPath

    def _writeXMLCustomResult(self, resNode, resultsSet):
        irNode = etree.SubElement(resNode, 'imageResults')
        for runI, imageRes in enumerate(self.imageResults):
            runNode = etree.SubElement(irNode, "run")
            runNode.attrib['number'] = str(runI+1) 
            runNode.attrib['withinTol'] = str(imageRes)
            errorsNode = etree.SubElement(runNode, "imgErrors")
            for compI, compError in enumerate(self.imageErrors[runI]):
                eNode = etree.SubElement(errorsNode, "compError")
                eNode.attrib["num"] = str(compI)
                eNode.attrib["error"] = "%6e" % compError
                eNode.attrib["withinTol"] = str(compError <= self.tol[compI]) 
