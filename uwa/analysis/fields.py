from lxml import etree

import os

from uwa.analysis import AnalysisOperation
from uwa.io import stgxml, stgcvg
from uwa.modelresult import FieldResult

class FieldTest:
    '''Class for maintaining info about a single field test'''
    def __init__(self, fieldName, tol=None):
        self.name = fieldName
        self.tol = tol

    def writeInfoXML(self, parentNode):
        return etree.SubElement(parentNode, 'field', name=self.name, \
            tol=str(self.tol))

    def checkFieldConvergence(self, cvgFileInfo):
        '''Checks that for a given fieldTest, each of the Field's dofs is within the
        required tolerance. Needs to be passed a cvgFileInfo to know which
        convergence file to get information from'''

        #TODO: should we do some comparison with tolerance here?
        dofErrors = stgcvg.getDofErrors_Final(cvgFileInfo)

        fieldResult = FieldResult(self.name, self.tol, dofErrors)
        return fieldResult


class FieldTestsInfo(AnalysisOperation):
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

    def testConvergence(self, cvgFilePath):
        fieldTestsDict = self.fields

        # Note: ideally, we'd have some better way of knowing what these
        # analytic soln output files would be called - perhaps the
        # analytic plugins should create a meta report file that can
        # be parsed and read
        # TODO: should this be done in some sort of preparatory step
        cvgFileIndex = stgcvg.genConvergenceFileIndex(cvgFilePath)

        fieldResults = []
        for fieldTest in fieldTestsDict.values():
            assert fieldTest.name in cvgFileIndex
            cvgFileInfo = cvgFileIndex[fieldTest.name]
            fr = fieldTest.checkFieldConvergence(cvgFileInfo)
            fieldResults.append(fr)

        return fieldResults
