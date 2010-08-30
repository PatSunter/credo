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

import credo.modelrun

class JobRunner:
    def __init__(self):
        pass

    def setup(self):
        """Does any necessary setup checks to run models.
        
        By default, does nothing - sub-classes need to override."""
        pass

    def getStGermainExeStr(self):
        """Get the string used to execute StGermain."""
        raise NotImplementedError("Error, virtual func on base class")   

    def constructStGermainRunCommand(self, modelRun, extraCmdLineOpts=None):
        runExe = self.getStGermainExeStr()
        stgRunStr = "%s " % (runExe)
        for inputFile in modelRun.modelInputFiles:    
            stgRunStr += inputFile+" "
        if modelRun.analysisXML:
            stgRunStr += modelRun.analysisXML+" "

        stgRunStr += credo.modelrun.getParamOverridesAsStr(
            modelRun.paramOverrides)
        if modelRun.solverOpts:
            #TODO: perhaps encapsulate this using OO in a solverOpts class
            stgRunStr += " -options_file %s" % modelRun.solverOpts
        if extraCmdLineOpts:
            stgRunStr += " "+extraCmdLineOpts
        return stgRunStr 

    def runModel(self, modelRun, extraCmdLineOpts=None, dryRun=False,
            maxRunTime=None):
        """Run the specified modelRun, and return a 
        :class:`~credo.modelresult.ModelResult` recording the results of
        the run.

        :param modelRun: the :class:`~credo.modelrun.ModelRun` to be run.
        :keyword extraCmdLineOpts: if specified, these extra cmd line opts will
           be passed through on the command line to the run, extra to any
           :attr:`.ModelRun.simParams` or :attr:`.ModelRun.paramOverrides`.
        :keyword dryRun: If set to True, just print out what *would* be run,
           but don't actually run anything."""

        raise NotImplementedError("Error, virtual func on base class")   
