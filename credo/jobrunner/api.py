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

from datetime import timedelta
import credo.modelrun
import credo.modelresult
from credo.io import stgcmdline
from credo.io import stgpath

class JobRunner:
    def __init__(self):
        self.runSuiteNonBlockingDefault = False

    def setup(self):
        """Does any necessary setup checks to run models.
        
        By default, does nothing - sub-classes need to override."""
        pass

    def submitRun(self, modelRun, prefixStr=None, extraCmdLineOpts=None,
            dryRun=False, maxRunTime=None):
        """Submit the job to be run.
        TODO: comment on parameters ...
        Returns: a jobMetaInfo (that can later be attached ... )
        """
        raise NotImplementedError("Error, virtual func on base class")

    def blockResult(self, modelRun, jobMetaInfo):
        """Block on a modelRun until the result is completed ...
        requires appropriate info to be passed in the jobMetaInfo object."""
        raise NotImplementedError("Error, virtual func on base class")

    # TODO: should the args be passed through as unnamed kwArgs,
        # then interpreted by submitRun?
    def runModel(self, modelRun, prefixStr=None, extraCmdLineOpts=None,
            dryRun=False, maxRunTime=None):
        """Run the specified modelRun, and return the ModelResult.

        :param modelRun: the :class:`~credo.modelrun.ModelRun` to be run.
        :keyword prefixStr: optional precursor string for running the model,
           e.g. for timing.
        :keyword extraCmdLineOpts: if specified, these extra cmd line opts will
           be passed through on the command line to the run, extra to any
           :attr:`.ModelRun.simParams` or :attr:`.ModelRun.paramOverrides`.
        :keyword dryRun: If set to True, just print out what *would* be run,
           but don't actually run anything.
        :keyword maxRunTime: maximum time (in seconds) a model should be
          allowed to run for before killing the job.
        :returns: A :class:`~credo.modelresult.ModelResult` recording
          the results of the run."""

        # TODO: handle dryRun at this level...?
        jobMetaInfo = self.submitRun(modelRun, prefixStr,
            extraCmdLineOpts, dryRun, maxRunTime)
        if dryRun is False:
            modelResult = self.blockResult(modelRun, jobMetaInfo)
            return modelResult
        else:
            return None

    def submitSuite(self, modelSuite, prefixStr=None, extraCmdLineOpts=None,
            dryRun=False, maxRunTime=None):
        """Submits each modelRun in a suite to be run, and returns a list
        of all jobMetaInfos for the submitted jobs."""
        jobMetaInfos = []
        for runI, modelRun in enumerate(modelSuite.runs):
            customOpts = modelSuite.getCustomOpts(runI, extraCmdLineOpts)
            jobMetaInfo = self.submitRun(modelRun, prefixStr, customOpts,
                dryRun, maxRunTime)    
            if jobMetaInfo:
                jobMetaInfos.append(jobMetaInfo)
        return jobMetaInfos
        
    def blockSuite(self, modelSuite, jobMetaInfos):    
        """Blocks on each ModelRun in a Suite, given a list of
        JobMetaInfos for each run."""
        modelSuite.resultsList = []
        for modelRun, jobMetaInfo in zip(modelSuite.runs, jobMetaInfos):
            # TODO: ideally if we implemented a "testResult" func, could
            #  loop through and poll/report as they complete,
            #  rather than just in sequential order ...
            result = self.blockResult(modelRun, jobMetaInfo)
            print "ModelRun '%s' complete." % modelRun.name
            assert isinstance(result, credo.modelresult.ModelResult)
            modelSuite.resultsList.append(result)
        return modelSuite.resultsList
    
    def runSuite(self, modelSuite, prefixStr=None, extraCmdLineOpts=None,
            dryRun=False, maxRunTime=None, runSuiteNonBlocking=None):
        """Run each ModelRun in the suite - with optional extra cmd line opts.
        Will also write XML records of each ModelRun and ModelResult in the 
        suite.

        Input arguments same as for :meth:`.runModel`.

        :returns: a reference to the :attr:`.resultsList` containing all
           the ModelResults generated."""

        print "Running the %d modelRuns specified in the suite" % \
            (len(modelSuite.runs))
    
        if runSuiteNonBlocking is None:
            runSuiteNonBlocking = self.runSuiteNonBlockingDefault

        if runSuiteNonBlocking:
            jobMetaInfos = self.submitSuite(modelSuite, prefixStr,
                extraCmdLineOpts, dryRun, maxRunTime)
            resultsList = self.blockSuite(modelSuite, jobMetaInfos)
            return resultsList
        else:
            modelSuite.resultsList = []
            for runI, modelRun in enumerate(modelSuite.runs):
                if not isinstance(modelRun, credo.modelrun.ModelRun):
                    raise TypeError("Error, stored run %d not an instance of a"\
                        " ModelRun" % runI)
                print "Doing run %d/%d (index %d), of name '%s':"\
                    % (runI+1, len(modelSuite.runs), runI, modelRun.name)
                print "ModelRun description: \"%s\"" % \
                    (modelSuite.runDescrips[runI])

                print "Running the Model (saving results in %s):"\
                    % (modelRun.outputPath)

                customOpts = modelSuite.getCustomOpts(runI, extraCmdLineOpts)
                result = self.runModel(modelRun, prefixStr, customOpts,
                    dryRun, maxRunTime)

                if dryRun == True: continue
                assert isinstance(result, credo.modelresult.ModelResult)
                modelSuite.resultsList.append(result)

        return modelSuite.resultsList


class ModelRunError(Exception):
    """Base class of ModelRunError exception hierarchy."""
    def __init__(self, modelName):
        self.modelName = modelName

class ModelRunRegularError(ModelRunError):
    """An Exception for when Models fail to run."""
    def __init__(self, modelName, retCode, stdOutFilename, stdErrFilename):
        ModelRunError.__init__(self, modelName)
        self.retCode = retCode
        self.stdOutFilename = stdOutFilename
        self.stdErrFilename = stdErrFilename
        self.tailLen = 20
        stdOutFile = open(stdOutFilename, "r")
        stdErrFile = open(stdErrFilename, "r")
        self.stdErrMsg = stdErrFile.read()
        # TODO: this is a bit inefficient and could be done with proper
        # tail function using seek etc.
        stdOutFileLines = stdOutFile.readlines()
        total = len(stdOutFileLines)
        start = 0
        if total > self.tailLen: start = total - self.tailLen
        self.stdOutFileTail = stdOutFileLines[start:]
        stdOutFile.close()
        stdErrFile.close()

    def __str__(self):
        return "Failed to run model '%s', ret code was %s\n"\
            "Std out and error logs saved to files %s and %s, "\
            "Std error msg was:\n%s\nLast %d lines of std out msg was:\n%s"\
            % (self.modelName, self.retCode,
                self.stdOutFilename, self.stdErrFilename, 
                self.stdErrMsg, self.tailLen,
                "".join(self.stdOutFileTail))


class ModelRunTimeoutError(ModelRunRegularError):
    """An Exception for when Models fail to run due to timing out.
    
    .. attribute:: maxRunTime
    
       maximum time to run that the model exceeded, in seconds.
    """
    def __init__(self, modelName, stdOutFilename, stdErrFilename,
            maxRunTime):
        ModelRunRegularError.__init__(self, modelName, None, stdOutFilename,
            stdErrFilename)
        self.maxRunTime = maxRunTime
    
    def __str__(self):
        return "Failed to run model '%s' due to timeout, max time was"\
            " %s\n"\
            "Std out and error logs saved to files %s and %s, "\
            "Std error msg was:\n%s\nLast %d lines of std out msg was:\n%s"\
            % (self.modelName, str(timedelta(seconds=self.maxRunTime)),
                self.stdOutFilename, self.stdErrFilename, 
                self.stdErrMsg, self.tailLen,
                "".join(self.stdOutFileTail))

class ModelRunLaunchError(ModelRunError):
    """An Exception for when Models fail to run due to being unable to launch
    the run process in some way.
    
    .. attribute:: runExecCmd
    
       command used to launch the job.
    """
    def __init__(self, modelName, runExecCmd, launchHint=None):
        ModelRunError.__init__(self, modelName)
        self.runExecCmd = runExecCmd
        self.launchHint = launchHint
    
    def __str__(self):
        retStr = "Failed to run model '%s' due to being unable to launch"\
            " run with command '%s'.\n"\
            % (self.modelName, self.runExecCmd)
        if self.launchHint is not None:
            retStr += " (%s)" % self.launchHint
        return retStr

