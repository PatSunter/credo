import sys
import os
import inspect
import shutil
import glob
import uwa.analysis
from uwa.io import stgcvg

STG_BINDIRKEY = 'STG_BINDIR'

def getVerifyStgExePath(exeName):
    stgPath = getStgBinPath()
    fullExePath = os.path.join(stgPath, exeName)
    if not os.path.exists(fullExePath):
        raise IOError("Error, in %s(): executable requested %s doesn't" \
            " exist/not valid in StGermain binary path (%s)." % \
            (inspect.stack()[0][3], exeName, stgPath))

    return fullExePath    

def getStgBinPath():
    try:
        stgBinPath=os.environ[STG_BINDIRKEY]
    except KeyError as keyE:
        raise EnvironmentError("Error in %s(): since this script needs to"\
            " use StGermain" \
            " executables, please set the %s environment variable for use" \
            " within UWA.\n" \
            % (inspect.stack()[0][3], STG_BINDIRKEY))

    if not os.path.exists(stgBinPath):
        raise EnvironmentError("Error, in %s(): needed env variable %s is"\
            " set, but path it's" \
            " set to (%s) doesn't exist/not valid.\n" \
            % (inspect.stack()[0][3], STG_BINDIRKEY, stgBinPath))
    elif not os.path.exists(os.path.join(stgBinPath, 'StGermain')):
        raise EnvironmentError("Error, in %s(): needed env variable %s is"\
            " set, path it's set" \
            " to (%s) is valid, but doesn't contain a StGermain executable.\n"\
            % (inspect.stack()[0][3], STG_BINDIRKEY, stgBinPath))

    return stgBinPath    

def moveAllToOutputPath(runPath, outputPath, fileExt):
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    for fname in glob.glob(os.path.join(runPath, "*."+fileExt)):
        # These are convergence files, don't keep records of previous runs
        target = os.path.join(outputPath, os.path.basename(fname))
        if (os.path.exists(target)): os.remove(target)
        shutil.move(fname, outputPath)

def prepareOutputLogDirs(outputPath, logPath):
    # TODO: complete    
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    if not os.path.exists(logPath):
        os.makedirs(logPath)

def cleanupOutputLogDirs(outputPath, logPath):
    #TODO
    pass
