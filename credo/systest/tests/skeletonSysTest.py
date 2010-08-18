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


from credo.systest.api import SysTest, CREDO_PASS, CREDO_FAIL
from credo.modelsuite import ModelSuite

class SkeletonSysTest(SysTest):
    """A Skeleton system test class, used for testing."""

    description = "Skeleton system test."

    def __init__(self, inputFiles, outputPathBase,
            statusToReturn, nproc=1,
            paramOverrides=None, solverOpts=None, nameSuffix=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Skeleton", nameSuffix)        
        self.statusToReturn = statusToReturn    
    
    def genSuite(self):
        # an empty suite
        self.mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        return self.mSuite
    
    def checkResultValid(self, resultsSet):
        pass

    def getStatus(self, resultsSet):
        self.testStatus = self.statusToReturn
        return self.testStatus
    
    def _writeXMLCustomSpec(self, specNode):
        pass
