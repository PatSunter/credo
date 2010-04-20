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
    fullExePath = stgPath+os.sep+exeName
    if not os.path.exists(fullExePath):
        print "Error, in %s(): executable requested %s doesn't" \
            " exist/not valid in StGermain binary path (%s)." % \
            (inspect.stack()[0][3], exeName, stgPath)
        raise IOError

    return fullExePath    

def getStgBinPath():
    try:
        stgBinPath=os.environ[STG_BINDIRKEY]
    except KeyError as keyE:
        print "Error in %s(): since this script needs to use StGermain" \
            " executables, please set the %s environment variable for use" \
            " within UWA.\n" \
            % (inspect.stack()[0][3], STG_BINDIRKEY)
        key = keyE
        sys.exit(2)

    if not os.path.exists(stgBinPath):
        print "Error, in %s(): needed env variable %s is set, but path it's" \
            " set to (%s) doesn't exist/not valid.\n" \
            % (inspect.stack()[0][3], STG_BINDIRKEY, stgBinPath)
        sys.exit(2)    
    elif not os.path.exists(stgBinPath+os.sep+'StGermain'):
        print "Error, in %s(): needed env variable %s is set, path it's set" \
            " to (%s) is valid, but doesn't contain a StGermain executable.\n"\
            % (inspect.stack()[0][3], STG_BINDIRKEY, stgBinPath)
        sys.exit(2)    

    return stgBinPath    

def moveConvergenceResults(path, outputPath):

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    for fname in glob.glob(path+os.sep+"*."+stgcvg.CVG_EXT):
        # These are convergence files, don't keep records of previous runs
        target=outputPath+os.sep+os.path.basename(fname)
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
