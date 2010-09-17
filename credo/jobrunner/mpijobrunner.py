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
import signal
import subprocess
import time
import shlex
from datetime import timedelta
from credo.modelresult import ModelResult, getSimInfoFromFreqOutput
from credo.jobrunner.api import *
from credo.io import stgpath

# Default amount of time to wait (sec) between polling model results
# when timeout active
DEF_WAIT_TIME = 2

# Allow MPI command to be overriden by env var.
MPI_RUN_COMMAND = "MPI_RUN_COMMAND"

class MPIJobRunner(JobRunner):
    def __init__(self):
        if MPI_RUN_COMMAND in os.environ:
            self.mpiRunCommand = os.environ[MPI_RUN_COMMAND]
        else:
            self.mpiRunCommand = "mpirun"

    def setup(self):
        # TODO: check mpd is running, if necessary
        pass

    def getStGermainExeStr(self):
        return stgpath.getVerifyStgExePath("StGermain")

    def runModel(self, modelRun, extraCmdLineOpts=None, dryRun=False,
            maxRunTime=None):
        """See :meth:`credo.jobrunner.api.JobRunner.runModel`."""     

        # Navigate to the model's base directory
        startDir = os.getcwd()
        if modelRun.basePath != startDir:
            print "Changing to ModelRun's specified base path '%s'" % \
                (modelRun.basePath)
            os.chdir(modelRun.basePath)

        stgpath.checkAllXMLInputFilesExist(modelRun.modelInputFiles)

        # Pre-run checks for validity - e.g. at least one input file,
        # nproc is sensible value
        if modelRun.simParams:
            modelRun.simParams.checkValidParams()
            modelRun.simParams.checkNoDuplicates(modelRun.paramOverrides.keys())
        if modelRun.solverOpts:
            modelRun.checkSolverOptsFile()

        # Do necessary pathing preparation
        modelRun.prepareOutputLogDirs()

        # Now create the XML file for custom analysis commands
        modelRun.analysisXMLGen()
        stgRunStr = self.constructStGermainRunCommand(modelRun,
            extraCmdLineOpts)

        stdOutFilename = modelRun.getStdOutFilename()
        stdErrFilename = modelRun.getStdErrFilename()
        stdOutFile = open(stdOutFilename, "w+")
        stdErrFile = open(stdErrFilename, "w+")

        # Construct full run line
        mpiPart = "%s -np %d " % (self.mpiRunCommand, modelRun.jobParams.nproc)
        runCommand = mpiPart + stgRunStr

        # Run the run command, sending stdout and stderr to defined log paths
        print "Running model '%s' via MPI with command '%s' ..."\
            % (modelRun.name, runCommand)

        # If we're only doing a dry run, return here.
        if dryRun == True:
            os.chdir(startDir)
            return None

        # Do the actual run
        # NB: We will split the arguments and run directly rather than in 
        # "shell mode":- this allows us to kill all sub-processes properly if
        # necessary.
        runAsArgs = shlex.split(runCommand)
        try:
            p = subprocess.Popen(runAsArgs, shell=False, stdout=stdOutFile,
                stderr=stdErrFile)
        except OSError:
            raise ModelRunLaunchError(modelRun.name, runAsArgs[0],
                "You can set the MPI_RUN_COMMAND env. variable to control"
                " the MPI command used.")

        if maxRunTime == None or maxRunTime <= 0:    
            timeOut = False
            retCode = p.wait()
        else:
            waitTime = DEF_WAIT_TIME if DEF_WAIT_TIME < maxRunTime \
                else maxRunTime
            totalTime = 0
            timeOut = True
            while totalTime <= maxRunTime:
                time.sleep(waitTime)
                totalTime += waitTime
                retCode = p.poll()
                if retCode is not None:
                    timeOut = False
                    break
            if timeOut:
                # At this point, we know the process has run too long.
                # From Python 2.6, change this to p.kill()
                print "Error: passed timeout of %s, sending quit signal." % \
                    (str(timedelta(seconds=maxRunTime)))
                os.kill(p.pid, signal.SIGQUIT)

        # Check status of run (eg error status)
        if timeOut == True:
            raise ModelRunTimeoutError(modelRun.name, stdOutFilename,
                stdErrFilename, maxRunTime)
        if retCode != 0:
            raise ModelRunRegularError(modelRun.name, retCode, stdOutFilename,
                stdErrFilename)
        else:
            # Taking advantage of os.path.join functionality to automatically
            #  over-ride later absolute paths.
            absOutPath = os.path.join(modelRun.basePath, modelRun.outputPath)
            absLogPath = os.path.join(modelRun.basePath, modelRun.logPath)
            print "Model ran successfully (output saved to path %s, std out"\
                " & std error to %s." % (absOutPath, absLogPath)

        # Now tidy things up after the run.
        stdOutFile.close()
        stdErrFile.close()
        print "Doing post-run tidyup:"
        modelRun.postRunCleanup()

        # Construct a modelResult
        # TODO: Maybe should construct just a basic ModelResult, and provide
        # a function on it to populate data structures from file.
        try:
            tSteps, simTime = getSimInfoFromFreqOutput(modelRun.outputPath)
        except ValueError:
            # For now, allow runs that didn't create a freq output
            tSteps, simTime = None, None

        mResult = ModelResult(modelRun.name, absOutPath, simTime)

        if modelRun.basePath != startDir:
            print "Restoring initial path '%s'" % \
                (startDir)
            os.chdir(startDir)
        
        # TODO: perhaps should return info on stdout and stderr?
        return mResult
