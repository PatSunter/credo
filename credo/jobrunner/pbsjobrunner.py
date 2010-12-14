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
from credo.modelresult import ModelResult, JobMetaInfo
from credo.modelresult import getSimInfoFromFreqOutput

# Default amount of time to wait (sec) between polling model results
# when timeout active
DEF_WAIT_TIME = 1

# Allow MPI command to be used within PBS to be overriden by env var.
MPI_RUN_COMMAND = "MPI_RUN_COMMAND"
DEFAULT_MPI_RUN_COMMAND = "mpiexec"

PBS_STRING = "#!/bin/bash"

class PBSJobParams(JobParams):
    def __init__(self, jobNameLine="# ",
            nodeLine="# ", wallTimeLine="# ", queueLine="# "):
        self.jobNameLine = jobNameLine
        self.nodeLine = nodeLine
        self.wallTimeLine = wallTimeLine
        self.queueLine = queueLine


class PBSJobMetaInfo(JobMetaInfo):
    def __init__(self):
        JobMetaInfo.__init__(self, 0)
        self.runType = "PBS"
        self.jobId = None


class PBSJobRunner(JobRunner):
    def __init__(self):
        JobRunner.__init__(self)
        # PBS Job Runners should by default submit all jobs first
        self.runSuiteNonBlockingDefault = True
        if MPI_RUN_COMMAND in os.environ:
            self.mpiRunCommand = os.environ[MPI_RUN_COMMAND]
        else:
            self.mpiRunCommand = DEFAULT_MPI_RUN_COMMAND

    def setup(self):
        # TODO: check pbs available and running, if necessary
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
        modelRunCommand = modelRun.constructModelRunCommand(extraCmdLineOpts)

        # Construct full run line
        mpiPart = "%s" % (self.mpiRunCommand)
        runCommand = " ".join([mpiPart, modelRunCommand])
        if prefixStr is not None:
            # NB: in the case of MPI runs, we prefix the prefixStr before MPI
            # command and args ... appropriate for things like timing stuff.
            runCommand = " ".join([prefixStr, runCommand])
        
        # TODO: fill out a dictionary of PBS commands with defaults ...
        # TODO: Create the PBS script
        pbsFilename = self._writePBSFile(modelRun, runCommand)        
        pbsSubCmd = "qsub "+pbsFilename

        # Run the run command, sending stdout and stderr to defined log paths
        print "Running model '%s' via PBS, using job name %s,"
            " with underlying MPI command '%s' ..."\
            % (modelRun.name, runCommand)

        # If we're only doing a dry run, return here.
        if dryRun == True:
            os.chdir(startDir)
            return None

        # Do the actual run
        # TODO: create PBS Stdout and pbsStdErr
        try:
            retCode = subprocess.call(pbsSubCmd, shell=False,
                stdout=qsubStdOut, stderr=qsubStdErr)
        except OSError:
            raise ModelRunLaunchError(modelRun.name, runAsArgs[0],
                "Error submitting PBS job, with command %s" % (pbsSubCmd))
        
        #TODO:
        # Parse the result, get the job number
        jobMetaInfo = PBSJobMetaInfo()
        jobMetaInfo.jobId = jobId
        return jobMetaInfo

    def _writePBSFile(self, modelRun, runCommand):
        jobParams = modelRun.jobParams
        #make the pbs file name
        proc = "%s" % (jobParams.nproc)
        pbsFileName = modelRun.name+"_proc_"+proc+".pbs"
        #add all necessary lines for a basic pbs- might need to modify
        # this slightly depending on what needs to go in
        f = open(pbsFileName, 'w') 
        f.write(PBS_STRING+"\n")
        #name line:
        jobNameLine = "%s " % (jobParams.jobNameLine)
        f.write(jobNameLine+"\n")
        # All the following can be rearranged to suit whatever cluster
        # this is running on
        #For example: vayu:
        #PBS -l walltime=00:10:00,ncpus=16,vmem=32000mb
        #The above can all be specified as the node line,
        # the rest is just written as comments
        #node line:
        nodeLine = "%s " % (jobParams.nodeLine)
        f.write(nodeLine+"\n")
        #wall time:
        wallTimeLine = "%s " % (jobParams.wallTimeLine)
        f.write(wallTimeLine+"\n")
        #queue:
        queueLine = "%s " % (jobParams.queueLine)
        f.write(queueLine+"\n")
        #export bash script vars:
        f.write("#PBS -V\n")
        #export UW
        # This is because some clusters require the full path to be specified
        # If this is the case, remember to
        # specify the full path for the output dir
        f.write("export UW="+pathUW+"\n")
        #export UWPATH
        f.write("export UWPATH=$UW\n")
        #cmd line:
        f.write(runCommand+"\n")
        f.close()
        return pbsFileName

    def blockResult(self, modelRun, jobMetaInfo):        
        # TODO
        # Check jobMetaInfo is of type PBS...
        # jobID = jobMetaInfo['jobId']
        # pollInterval = modelRun.jobParams.pollInterval
        # periodically based on pollInterval:
            # check PBS job output ... (eg using qstat on jobID)
            # Get server info ...
            # jobMetaInfo.dict['nodeInfo'] = nodeInfo
            # get retCode, timeOut.

        # Check status of run (eg error status)

        # TODO: archive PBS file in modelRun output directory.

        stdOutFilename = modelRun.getStdOutFilename()
        stdErrFilename = modelRun.getStdErrFilename()
        if timeOut == True:
            raise ModelRunTimeoutError(modelRun.name, stdOutFilename,
                stdErrFilename, modelRun.jobParams.maxRunTime)
        if retCode != 0:
            raise ModelRunRegularError(modelRun.name, retCode, stdOutFilename,
                stdErrFilename)
        else:
            absOutPath = os.path.join(modelRun.basePath, modelRun.outputPath)
            absLogPath = os.path.join(modelRun.basePath, modelRun.logPath)
            # TODO: Move and rename output and error files created by PBS,
            #  ... to stdOutFilename, stdErrFilename
            print "Model ran successfully (output saved to path %s, std out"\
                " & std error to %s." % (absOutPath, absLogPath)

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
        # Perhaps functions on jobMetaInfo?
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
