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


"""Collection of utility functions for plotting interesting aspects of models
"""

#!/usr/bin/env python

import os
import operator as op
import credo
try:
    # For why we use Agg backend, see
    # http://matplotlib.sourceforge.net/faq/howto_faq.html#matplotlib-in-a-web-application-server
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print "Error, to use CREDO built-in plot functions, please "\
        " install the matplotlib python library."

def getValsFromAllRuns(mResults, outputName):
    resVals = [mRes.freqOutput.getValuesArray(outputName) for mRes in mResults]
    return resVals

def plotOverAllRuns(mResults, outputName, depName='Timestep', show=False,
        save=True, path=".", labelNames=True):
    """Create a plot of values over multiple runs."""    
    resVals = getValsFromAllRuns(mResults, outputName)
    depVals = getValsFromAllRuns(mResults, depName)
    plot = plt.clf()   # Start by clearing any pre-existing figure
    for ii, mRes in enumerate(mResults):
        lab = "%d" % ii
        if labelNames == True: lab += ": %s" % mRes.modelName
        plt.plot(depVals[ii], resVals[ii], label=lab)
    plt.xlabel(depName)
    plt.ylabel(outputName)
    plt.legend(loc='best', prop={'size':'small'})
    plt.title("Output parameter '%s' over %s"\
        % (outputName, depName))
    if save:
        if not os.path.exists(path):
            os.makedirs(path)
        for fmt in ['svg', 'png']:
            filename = os.path.join(path,
                outputName+"-multiRunTimeSeries.%s" % fmt)
            plt.savefig(filename, format=fmt, dpi=120)
    if show: plt.show()
    return plt

def parseUnixTimeElapsed(timeElapsedStr):
    secStrs = timeElapsedStr.split(":")
    if len(secStrs) == 2:
        hours = 0
        mins = int(secStrs[0])
        secs = float(secStrs[1])
    elif len(secStrs) == 3:
        hours = int(secStrs[0])
        mins = int(secStrs[1])
        secs = float(secStrs[2])
    else:
        raise ValueError("Error, time elapsed string given, '%s',"\
            "doesn't conform to Unix time command's elapsed string format."\
            % timeElapsedStr)
    return hours * (60*60) + mins * 60 + secs        
        

def getSpeedups(mRuns, mResults, profilerName=None):
    if profilerName == None:
        #TODO: get a default
        profilerName = "UnixTimeCmd"
    resList = []
    for mRun, mRes in zip(mRuns, mResults):
        nProc = mRun.jobParams["nproc"]
        wallTimeStr = mRes.jobMetaInfo.performance[profilerName]['walltime']
        wallTime = parseUnixTimeElapsed(wallTimeStr)
        resList.append((nProc, wallTime))
    lowestProcEntry = min(resList)
    lowestProc = lowestProcEntry[0]
    lowestTime = lowestProcEntry[1]
    #NB: if lowestProc == 1 (often will be), then serialTime == lowestTime
    serialTime = lowestTime * lowestProc
    speedups = [serialTime / res[1] for res in resList]
    return speedups

def plotSpeedups(mRuns, mResults, profiler=None, show=False,
        save=True, path=".", showIdeal=True):
    """Plot the speedup of a set of mResults, by processor."""
    nprocs = [mRun.jobParams["nproc"] for mRun in mRuns]
    speedups = getSpeedups(mRuns, mResults, profiler)
    plot = plt.clf()   # Start by clearing any pre-existing figure
    plt.xlabel("# procs")
    plt.ylabel("speedup")
    #plt.legend(loc='best', prop={'size':'small'})
    plt.plot(nprocs, speedups, "o:", label="actual")
    if showIdeal == True:
        idealProcs = [1, nprocs[-1]]
        idealSpeedup = [1, nprocs[-1]]
        plt.plot(idealProcs, idealSpeedup, "g-", label="ideal")
    plt.ylim(ymin=0)
    plt.title("Parallel Speedup for given runs.")
    plt.legend(loc='best', prop={'size':'small'})
    if save:
        if not os.path.exists(path):
            os.makedirs(path)
        for fmt in ['svg', 'png']:
            filename = os.path.join(path,
                "speedups.%s" % fmt)
            plt.savefig(filename, format=fmt, dpi=120)
    if show: plt.show()
    return plt
