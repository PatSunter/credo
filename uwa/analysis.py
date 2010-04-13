from uwa.modelrun import ModelRun
from uwa.modelresult import FieldResult

import os
import glob

CVG_EXT='cvg'

class CvgFileInfo:
    '''A simple class to store info about what fields map to what 
     convergence files'''
    def __init__(self, filename):
        self.filename=filename
        # the dofInfo is just a dict mapping dof number to column number
        self.dofColMap={}

# TODO: perhaps this first should be a method of the ModelRun
def testConvergence(modelRun):
    fieldTestsDict = modelRun.fieldTests.fields

    # Note: ideally, we'd have some better way of knowing what these
    # analytic soln output files would be called - perhaps the
    # analytic plugins should create a meta report file that can
    # be parsed and read
    cvgFileIndex = genConvergenceFileIndex(modelRun.outputPath)

    fieldResults = []
    for fieldTest in fieldTestsDict.values():
        assert fieldTest.name in cvgFileIndex
        fieldResults.append(checkFieldConvergence(fieldTest, cvgFileIndex[fieldTest.name]))

    return fieldResults

def genConvergenceFileIndex(path):
    '''Returns a dictionary relating field names to convergence files, for 
     all .cvg files in the given path'''
    
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

def checkFieldConvergence(fieldTest, cvgFileInfo):
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

    #TODO: should we do some comparison with tolerance here?

    fieldResult = FieldResult(fieldTest.name, fieldTest.tol, dofErrors)
    return fieldResult
