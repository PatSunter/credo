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
from credo.jobrunner.api import *
from credo.modelrun import JobParams
from credo.modelresult import ModelResult, JobMetaInfo
from credo.modelresult import getSimInfoFromFreqOutput

# Allow MPI command to be overriden by env var.
MPI_RUN_COMMAND = "MPI_RUN_COMMAND"
DEFAULT_MPI_RUN_COMMAND = "mpiexec"

class MPIJobParams(JobParams):
    def __init__(self):
        pass

class MPIJobMetaInfo(JobMetaInfo):
    def __init__(self):
        JobMetaInfo.__init__(self, 0)
        self.runType = "MPI"
        self.procHandle = None

class MPIJobRunner(JobRunner):
    def __init__(self):
        JobRunner.__init__(self)
        if MPI_RUN_COMMAND in os.environ:
            self.mpiRunCommand = os.environ[MPI_RUN_COMMAND]
        else:
            self.mpiRunCommand = DEFAULT_MPI_RUN_COMMAND

    def setup(self):
        # TODO: check mpd is running, if necessary
        pass

    def submitRun(self, modelRun, prefixStr=None, extraCmdLineOpts=None,
            dryRun=False, maxRunTime=None):
        """See :meth:`credo.jobrunner.api.JobRunner.submit`."""     

        # Navigate to the model's base directory
        startDir = os.getcwd()
        if modelRun.basePath != startDir:
            print "Changing to ModelRun's specified base path '%s'" % \
                (modelRun.basePath)
            os.chdir(modelRun.basePath)

        modelRun.checkValidRunConfig()
        modelRun.preRunPreparation()
        runCommand = self._getMPIRunCommandLine(modelRun, prefixStr,
            extraCmdLineOpts)

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
        stdOutFilename = modelRun.getStdOutFilename()
        stdErrFilename = modelRun.getStdErrFilename()
        try:
            stdOutFile = open(stdOutFilename, "w+")
            stdErrFile = open(stdErrFilename, "w+")
            procHandle = subprocess.Popen(runAsArgs, shell=False,
                stdout=stdOutFile, stderr=stdErrFile)
        except OSError:
            raise ModelRunLaunchError(modelRun.name, runAsArgs[0],
                "You can set the MPI_RUN_COMMAND env. variable to control"
                " the MPI command used.")

        jobMetaInfo = MPIJobMetaInfo()
        jobMetaInfo.procHandle = procHandle
        jobMetaInfo.stdOutFile = stdOutFile
        jobMetaInfo.stdErrFile = stdErrFile
        # TODO: record extra info in "provenance" dict of jobMetaInfo,
        #  eg hostname, run command used, prefix, etc...
        if modelRun.basePath != startDir:
            print "Restoring initial path '%s'" % \
                (startDir)
            os.chdir(startDir)
        return jobMetaInfo

    def _getMPIRunCommandLine(self, modelRun, prefixStr, extraCmdLineOpts):
        modelRunCommand = modelRun.constructModelRunCommand(extraCmdLineOpts)
        # Construct full run line
        mpiPart = "%s -np %d" % (self.mpiRunCommand, modelRun.jobParams.nproc)
        runCommand = " ".join([mpiPart, modelRunCommand])
        if prefixStr is not None:
            # NB: in the case of MPI runs, we prefix the prefixStr before MPI
            # command and args ... appropriate for things like timing stuff.
            runCommand = " ".join([prefixStr, runCommand])
        return runCommand

    def blockResult(self, modelRun, jobMetaInfo):        
        # CHeck jobMetaInfo is of type MPI ...
        maxRunTime = modelRun.jobParams.maxRunTime
        pollInterval = modelRun.jobParams.pollInterval
        procHandle = jobMetaInfo.procHandle
        # jobParams

        # Navigate to the model's base directory
        startDir = os.getcwd()
        if modelRun.basePath != startDir:
            print "Changing to ModelRun's specified base path '%s'" % \
                (modelRun.basePath)
            os.chdir(modelRun.basePath)

        if maxRunTime == None or maxRunTime <= 0:    
            timeOut = False
            retCode = procHandle.wait()
        else:
            if pollInterval > maxRunTime: pollInterval = maxRunTime
            totalTime = 0
            timeOut = True
            while totalTime <= maxRunTime:
                time.sleep(pollInterval)
                totalTime += pollInterval
                retCode = procHandle.poll()
                if retCode is not None:
                    timeOut = False
                    break
            if timeOut:
                # At this point, we know the process has run too long.
                # From Python 2.6, change this to procHandle.kill()
                print "Error: passed timeout of %s, sending quit signal." % \
                    (str(timedelta(seconds=maxRunTime)))
                os.kill(procHandle.pid, signal.SIGQUIT)

        # Check status of run (eg error status)
        stdOutFilename = modelRun.getStdOutFilename()
        stdErrFilename = modelRun.getStdErrFilename()
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
        jobMetaInfo.stdOutFile.close()
        jobMetaInfo.stdErrFile.close()
        print "Doing post-run tidyup:"
        modelRun.postRunCleanup()

        # Construct a modelResult
        mResult = ModelResult(modelRun.name, absOutPath)
        # Now attach appropriate Job meta info
        try:
            tSteps, simTime = getSimInfoFromFreqOutput(modelRun.outputPath)
        except ValueError:
            # For now, allow runs that didn't create a freq output
            tSteps, simTime = None, None
        # get provenance info
        # attach provenance info
        # get performance info
        # attach performance info
        mResult.jobMetaInfo = jobMetaInfo

        if modelRun.basePath != startDir:
            print "Restoring initial path '%s'" % \
                (startDir)
            os.chdir(startDir)
        return mResult
