import os
import glob

from lxml import etree

'''A Module for dealing with StGermain Convergence files, produced by the
FieldTester Component.'''

CVG_EXT='cvg'

class CvgFileInfo:
    '''A simple class to store info about what fields map to what 
     convergence files'''
    def __init__(self, filename):
        self.filename=filename
        # the dofInfo is just a dict mapping dof number to column number
        self.dofColMap={}

def genConvergenceFileIndex(path):
    '''Returns a dictionary relating field names to convergence file info
    classes, for all .cvg files in the given path'''
    
    # get list of all convergence files
    cvgFiles=glob.glob(path+os.sep+"*."+CVG_EXT)

    cvgFileDict = {}

    # for each file, read first line, and check field name
    for cvgFilename in cvgFiles:
        # Store in a dict structure, so we know file, field
        cvgFile = open(cvgFilename,"r")
        line=cvgFile.readline()
        cols=line.split()
        for colIndex in range(1,len(cols)):
            fieldCol=cols[colIndex]
            # The Field name is written with a number appended, the field
            # Degree of freedom
            assert fieldCol[-1].isdigit()
            # The -1 is because of the way FieldTest adds 1 to these
            fieldName = fieldCol[:-1]
            dofValue = int(fieldCol[-1]) - 1
            if (fieldName not in cvgFileDict):
                newCvgInfo = CvgFileInfo(cvgFilename)
                newCvgInfo.dofColMap[dofValue] = colIndex
                cvgFileDict[fieldName] = newCvgInfo
            else:
                cvgFileDict[fieldName].dofColMap[dofValue] = colIndex

        cvgFile.close()

    return cvgFileDict

def getDofErrors_Final(cvgFileInfo):
    '''For a given cvgFileInfo, get the errors in the specified dof from the
    specified file - just for final timestep (line) in file'''

    cvgFile = open(cvgFileInfo.filename,"r")

    # Just read the last line - this is last timestep that ran
    # NB: this could be done more efficiently using file.seek, if performance
    # becomes an issue with very large convergence files
    for line in cvgFile: pass
    colVals = line.split()

    dofErrors=[]
    for ii in range(len(cvgFileInfo.dofColMap)): dofErrors.append(0.0)

    for dof, colIndex in cvgFileInfo.dofColMap.iteritems():
        errorStr = colVals[colIndex]
        dofErrors[dof] = float(errorStr)

    cvgFile.close()

    return dofErrors
