from lxml import etree

import os
import glob

from uwa import stgxml
from uwa.modelresult import FieldResult

CVG_EXT='cvg'

class FieldTest:
    '''Class for maintaining info about a single field test'''
    def __init__(self, fieldName, tol=None):
        self.name = fieldName
        self.tol = tol

    def writeInfoXML(self, parentNode):
        return etree.SubElement(parentNode, 'field', name=self.name, \
            tol=str(self.tol))

# TODO: class Analysis that all must inherit from, with std methods such as
#  writeInfoXML, writeStgXML, etc ?

class FieldTestsInfo:
    '''Class for maintaining and managing a list of field tests, including
     IO from StGermain XML files'''

    stgFTComp_Type = 'FieldTest'
    stgFTComp_Name = 'uwaFieldTester'
    stgFTSpecName = 'pluginData'
    stgFTSpec_FList = 'NumericFields'
    stgFTSpec_RList = 'ReferenceFields'

    def __init__(self, fieldsList=None):
        self.fields = fieldsList
        if self.fields == None: self.fields = {}
        self.fromXML = False
        self.useReference = False
        self.referencePath = None
        self.testTimestep = 0

    def add(self, fieldTest):
        self.fields[fieldTest.name] = fieldTest    

    def setAllTols(self, fieldTol):
        for fieldTest in self.fields.values():
            fieldTest.tol = fieldTol

    def writeInfoXML(self, parentNode):
        '''Writes information about this class into an existing, open XML
         doc node, in a child element'''

        if len(self.fields) == 0: return

        ftNode = etree.SubElement(parentNode, 'fieldTestsInfo')
        ftNode.attrib['fromXML']=str(self.fromXML)
        ftNode.attrib['useReference']=str(self.useReference)
        ftNode.attrib['referencePath']=str(self.referencePath)
        ftNode.attrib['testTimestep']=str(self.testTimestep)
        fListNode = etree.SubElement(parentNode, 'fields')
        for fTest in self.fields.values():
            fTest.writeInfoXML(fListNode)

    def writeStgDataXML(self, rootNode):
        '''Writes the necessary StGermain XML to enable these specified
         fields to be tested'''

        assert(self.fromXML == False)
        # If there are no fields to test, no need to write StGermain XML
        if len(self.fields) == 0: return

        # Append the component to component list
        compElt = stgxml.mergeComponent(rootNode, self.stgFTComp_Name, \
            self.stgFTComp_Type)

        # Create the plugin data
        pluginDataElt = etree.SubElement(rootNode, stgxml.structTag, \
            name=self.stgFTSpecName, mergeType="replace")
        xmlFieldTestsList = self.fields.keys()
        # This is necessary due to format of this list in the FieldTest plugin:
        # <FieldName> <# of analytic func> - both as straight params
        ii=0
        for index in range(1,len(self.fields)*2,2):
            xmlFieldTestsList.insert(index, str(ii))
            ii+=1

        stgxml.writeParamList(pluginDataElt, self.stgFTSpec_FList, \
            xmlFieldTestsList)
        if self.useReference:
            stgxml.writeParamSet(pluginDataElt, {\
                'referenceSolutionFilePath':self.referencePath,\
                'useReferenceSolutionFromFile':self.useReference })
            stgxml.writeParamList(pluginDataElt, self.stgFTSpec_RList, \
                self.fields.keys())

        stgxml.writeParamSet(pluginDataElt, {\
            'IntegrationSwarm':'gaussSwarm',\
            'ConstantMesh':'constantMesh',\
            'testTimestep':self.testTimestep,\
            'ElementMesh':'linearMesh',\
            'normaliseByAnalyticSolution':'True',\
            'context':'context',\
            'appendToAnalysisFile':'True'})
    
    def readFromStgXML(self, inputFilesList):
        '''Read in the list of fields that have already been specified to 
         be tested from a set of StGermain input files. Useful when e.g. 
         working with an Analytic Solution plugin'''
        self.fromXML = True

        # create a flattened file
        ffile=stgxml.createFlattenedXML(inputFilesList)

        # Necessary, because the parser will prefix this this to tag names
        stgNSText = stgxml.stgNSText

        xmlDoc = etree.parse(ffile)
        stgRoot = xmlDoc.getroot()

        # Go and grab necessary info from XML file
        fieldTestDataEl = stgxml.getStruct(stgRoot, self.stgFTSpecName)
        fieldTestListEl = stgxml.getList(fieldTestDataEl, self.stgFTSpec_FList)

        fieldTestEls = fieldTestListEl.getchildren()
        # As per the current spec, the field names are followed by an index 
        # of analytic solution
        ii = 0
        while ii < len(fieldTestEls):
            fieldName = fieldTestEls[ii].text
            self.fields[fieldName] = FieldTest(fieldName)
            # Skip the index
            ii+=1
            ii+=1

        os.remove(ffile)


class CvgFileInfo:
    '''A simple class to store info about what fields map to what 
     convergence files'''
    def __init__(self, filename):
        self.filename=filename
        # the dofInfo is just a dict mapping dof number to column number
        self.dofColMap={}

# TODO: probably should be a method of the FieldTestsInfo?
def testConvergence(fieldTestsInfo, cvgFilePath):
    fieldTestsDict = fieldTestsInfo.fields

    # Note: ideally, we'd have some better way of knowing what these
    # analytic soln output files would be called - perhaps the
    # analytic plugins should create a meta report file that can
    # be parsed and read
    cvgFileIndex = genConvergenceFileIndex(cvgFilePath)

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
