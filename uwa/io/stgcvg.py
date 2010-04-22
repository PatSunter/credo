import os
import glob
import linecache

'''A Module for dealing with StGermain Convergence files, produced by the
FieldTester Component.'''

CVG_EXT='cvg'
CVG_HEADER_LINESTART='#'

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

# TODO: the files below could perhaps be converted to an O-O representation,
# where operations are performed on a CVG file, and support e.g. slice notation?

def getCheckStepsRange(cvgFile, steps):
    lineTot = sum(1 for line in cvgFile)
    cvgFile.seek(0)

    # Given every 2nd line is a header
    stepTot = lineTot/2

    if steps == 'all':
        stepRange = range(0,stepTot)
    elif steps == 'last':
        stepRange = [stepTot-1]
    elif type(steps) == tuple:
        if len(steps) != 2 or type(steps[0]) != int or type(steps[1]) != int:
            raise TypeError("If arg 'steps' is a tuple, should be only two"\
                " numbers.")
                
        start,end = steps

        if start < 0:
            raise ValueError("Error, 'steps' init number less than 0")
        if end > stepTot:
            raise ValueError("Error, 'steps' finish number %d "\
                "greater than number of steps in the given file (%d)" % \
                (end, stepTot))

        stepRange = range(start,end)
    else:
        raise TypeError("arg 'steps' must be either 'all', 'last', or a tuple"\
            " of start and ending numbers")

    return stepRange        


def getDofErrorsForStep(cvgFileInfo, stepNum):
    # Given every 2nd line is a header, need to handle these
    lineNum = stepNum*2+1
    # The linecache.getline function indexes file lines from 1, hence
    # adjustment below
    line = linecache.getline(cvgFileInfo.filename, lineNum+1) 
    if line == "":
        raise IOError("Couldn't read step %d (line %d) from '%s'" %
            (stepNum, lineNum, cvgFileInfo.filename))
    elif line[0] == CVG_HEADER_LINESTART:
        # Should have avoided header lines
        raise IOError("Trying to read step %d (line %d) from '%s'"
            " unexpectedly indexed to a header line" %
            (stepNum, lineNum, cvgFileInfo.filename))

    colVals = line.split()

    dofErrorsForStep = []
    for dof, colIndex in cvgFileInfo.dofColMap.iteritems():
        errorStr = colVals[colIndex]
        dofErrorsForStep.append(float(errorStr))
    
    return dofErrorsForStep


# Question: should we use Numeric for this? - as performance for very large
#  CVG files could be a bit ordinary
def getDofErrors_ByDof(cvgFileInfo, steps='all'):
    '''For a given cvgFileInfo, get the errors in the specified dof from
    the specified file, indexed primarily by Dof.
    The 'steps' arg can be either 'all' (for all timesteps), 'last',
    or a tuple specifying range.
    If only one step result is asked for, the dofs are returned as a
    simple 1D array.'''

    cvgFile = open(cvgFileInfo.filename,"r")

    stepRange = getCheckStepsRange(cvgFile, steps)

    dofErrors = []
    numDofs = len(cvgFileInfo.dofColMap)
    for ii in range(numDofs): dofErrors.append([])

    if len(stepRange) == 1:
        dofErrors = getDofErrorsForStep(cvgFileInfo, stepRange[0])
    else:
        for stepNum in stepRange:
            dofErrorsStep = getDofErrorsForStep(cvgFileInfo, stepNum)
            for dofI in range(numDofs):
                dofErrors[dofI].append(dofErrorsStep[dofI])
            
    cvgFile.close()
    return dofErrors


def getDofErrors_ByStep(cvgFileInfo, steps='all'):
    '''For a given cvgFileInfo, get the errors in the specified dof from
    the specified file - for each timestep, indexed primarily by Timestep.
    The 'steps' arg can be either 'all' (for all timesteps), 'last',
    or a tuple specifying range.
    If only one step result is asked for, the dofs are returned as a
    simple 1D array.'''

    cvgFile = open(cvgFileInfo.filename,"r")

    stepRange = getCheckStepsRange(cvgFile, steps)

    dofErrors = []
    numDofs = len(cvgFileInfo.dofColMap)

    if len(stepRange) == 1:
        dofErrors = getDofErrorsForStep(cvgFileInfo, stepRange[0])
    else:
        for stepNum in stepRange:
            dofErrorsStep = getDofErrorsForStep(cvgFileInfo, stepNum)
            dofErrors.append(dofErrorsStep)
            
    cvgFile.close()
    return dofErrors
