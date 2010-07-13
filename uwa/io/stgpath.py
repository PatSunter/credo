"""
This module is for accessing and working with StGermain-related paths.
"""

import os
import glob
import shutil
import inspect

STG_BINDIRKEY = 'STG_BINDIR'

def getVerifyStgExePath(exeName):
    """For a given executable name (eg "StGermain"), return the full path
    name of that executable (in the path given by the STG_BINDIR env variable).
    """
    stgPath = getStgBinPath()
    fullExePath = os.path.join(stgPath, exeName)
    if not os.path.exists(fullExePath):
        raise IOError("Error, in %s(): executable requested %s doesn't" \
            " exist/not valid in StGermain binary path (%s)." % \
            (inspect.stack()[0][3], exeName, stgPath))

    return fullExePath    

def getStgBinPath():
    """Get the path of StGermain binaries (given by env variable STG_BINDIR)."""
    try:
        stgBinPath=os.environ[STG_BINDIRKEY]
    except KeyError, keyE:
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

# TODO
# getStgStandardXMLPath
# SearchInStandardXMLPath (or is this in XML)

def moveAllToTargetPath(startPath, targetPath, fileExt):
    """Move all files with extension `fileExt` from `startPath` to
    `targetPath` - automatically over-writing any existing files with
    identical names."""
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)
    for fname in glob.glob(os.path.join(startPath, "*."+fileExt)):
        target = os.path.join(targetPath, os.path.basename(fname))
        if (os.path.exists(target)): os.remove(target)
        shutil.move(fname, targetPath)
