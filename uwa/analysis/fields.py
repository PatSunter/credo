import os
import math
from lxml import etree

from uwa.analysis import AnalysisOperation
from uwa.io import stgxml, stgcvg
import uwa.analysis.stats as stats

class FieldComparisonOp:
    '''Class for maintaining info about a single field test'''
    def __init__(self, fieldName):
        self.name = fieldName

    def writeInfoXML(self, parentNode):
        return etree.SubElement(parentNode, 'field', name=self.name)

    def getResult(self, modelResult):
        '''Gets the result of the operator on the given fields.'''
        cvgIndex = stgcvg.genConvergenceFileIndex(modelResult.outputPath)
        try:
            cvgFileInfo = cvgIndex[self.name]
        except KeyError:     
            # TODO: create a new exception type here?
            raise KeyError("Field '%s' not found in the known list of"\
                " convergence results (%s) for model run '%s'"\
                % (self.name, cvgIndex.keys(),modelResult.modelName))
        dofErrors = stgcvg.getDofErrors_ByDof(cvgFileInfo, steps="last")
        fieldResult = FieldComparisonResult(self.name, dofErrors)
        fieldResult.cvgFileInfo = cvgFileInfo
        return fieldResult


class FieldComparisonResult:
    '''Simple class for storing UWA FieldComparisonOp Results'''
    XML_INFO_TAG = "fieldResult"
    XML_INFO_LIST_TAG = "fieldResults"

    def __init__(self, fieldName, dofErrors):
        self.fieldName = fieldName
        self.dofErrors = []
        # Allow the user to pass in just a single error value result for
        # simple fields
        if isinstance(dofErrors, int):
            dofErrors = [dofErrors]

        for errorStr in dofErrors:
            self.dofErrors.append(float(errorStr))
        
        self.cvgFileInfo = None
        self.plottedCvgFile = None
    
    def writeInfoXML(self, fieldResultsNode):
        '''Writes information about a FieldComparisonResult into an existing,
         open XML doc node'''
        fr = etree.SubElement(fieldResultsNode, self.XML_INFO_TAG)
        fr.attrib['fieldName'] = self.fieldName
        if self.plottedCvgFile:
            fr.attrib['plottedCvgFile'] = self.plottedCvgFile
        for dofIndex in range(len(self.dofErrors)):
            dr = etree.SubElement(fr, 'dofResult')
            dr.attrib['dof'] = str(dofIndex)
            dr.attrib['error'] = str(self.dofErrors[dofIndex])
    
    def plotCvgOverTime(self, save=True, show=False, dofIndex=None, path="."):
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print "Error, to use UWA built-in plot functions, please "\
                " install the matplotlib python library."
            return    
        
        assert self.cvgFileInfo

        dofErrorsArray = stgcvg.getDofErrors_ByDof(self.cvgFileInfo)

        numDofs = len(self.dofErrors)

        if dofIndex is not None:
            dofRange = [0]
            dofIndices = [dofIndex]
        else:
            dofRange = range(numDofs)    
            dofIndices = range(numDofs)
            
        plt.subplots_adjust(wspace=0.4)

        for dofI in dofRange:
            plt.subplot(1,len(dofRange),dofI+1)
            plot = plt.plot(dofErrorsArray[dofIndices[dofI]])
            # TODO: only the within tolerance test should add this.
            #plt.axhline(y=self.tol, label='tolerance', linewidth=3, color='r')

            plt.xlabel("Timestep")
            # TODO: title should change depending on analytic or reference
            plt.ylabel("Dof %d: Error vs analytic soln" % dofIndices[dofI])
            # Only display the title once on left
            if len(dofRange) == 1:
                plt.title("Convergence of field '%s' with analytic solution,"\
                    " for DOF %d" % (self.fieldName, dofIndices[dofI]))
            else:
                if dofI == 0:
                    plt.suptitle("Convergence of field '%s' with analytic"\
                        " solution" % (self.fieldName), fontsize=14)
                plt.title("DOF %d" % dofI)

        if save:
            filename = path+os.sep+self.fieldName+"-cvg.png"
            plt.savefig(filename, format="png")
            self.plottedCvgFile = filename
        if show: plt.show()

    def checkWithinTol(self, tol):
        for dofError in self.dofErrors:
            if dofError > tol: return False
        return True    

class FieldComparisonList(AnalysisOperation):
    '''Class for maintaining and managing a list of field tests, including
     IO from StGermain XML files'''

    stgXMLCompType = 'FieldTest'
    stgXMLCompName = 'uwaFieldTester'
    # This component is unusual in that it needs a "pluginData" struct
    # separate to the actual component definition.
    stgXMLSpecName = 'pluginData'
    stgXMLSpecFList = 'NumericFields'
    stgXMLSpecRList = 'ReferenceFields'

    def __init__(self, fieldsList=None):
        self.fields = fieldsList
        if self.fields == None: self.fields = {}
        self.fromXML = False
        self.useReference = False
        self.referencePath = None
        self.testTimestep = 0

    def add(self, fieldTest):
        self.fields[fieldTest.name] = fieldTest    

    def writeInfoXML(self, parentNode):
        '''Writes information about this class into an existing, open XML
         doc node, in a child element'''

        if len(self.fields) == 0: return

        ftNode = etree.SubElement(parentNode, 'fieldTestsInfo')
        ftNode.attrib['fromXML']=str(self.fromXML)
        ftNode.attrib['useReference']=str(self.useReference)
        ftNode.attrib['referencePath']=str(self.referencePath)
        ftNode.attrib['testTimestep']=str(self.testTimestep)
        fListNode = etree.SubElement(ftNode, 'fields')
        for fTest in self.fields.values():
            fTest.writeInfoXML(fListNode)

    def writeStgDataXML(self, rootNode):
        '''Writes the necessary StGermain XML to enable these specified
         fields to be tested'''

        assert(self.fromXML == False)
        # If there are no fields to test, no need to write StGermain XML
        if len(self.fields) == 0: return

        # Append the component to component list
        compElt = stgxml.mergeComponent(rootNode, self.stgXMLCompName, \
            self.stgXMLCompType)
        # Create the plugin data
        pluginDataElt = etree.SubElement(rootNode, stgxml.structTag, \
            name=self.stgXMLSpecName, mergeType="replace")
        xmlFieldTestsList = self.fields.keys()
        # This is necessary due to format of this list in the FieldTest plugin:
        # <FieldName> <# of analytic func> - both as straight params
        ii=0
        for index in range(1,len(self.fields)*2,2):
            xmlFieldTestsList.insert(index, str(ii))
            ii+=1

        stgxml.writeParamList(pluginDataElt, self.stgXMLSpecFList, \
            xmlFieldTestsList)
        if self.useReference:
            stgxml.writeParamSet(pluginDataElt, {\
                'referenceSolutionFilePath':self.referencePath,\
                'useReferenceSolutionFromFile':self.useReference })
            stgxml.writeParamList(pluginDataElt, self.stgXMLSpecRList, \
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
        fieldTestDataEl = stgxml.getStruct(stgRoot, self.stgXMLSpecName)
        fieldTestListEl = stgxml.getList(fieldTestDataEl, self.stgXMLSpecFList)

        fieldTestEls = fieldTestListEl.getchildren()
        # As per the current spec, the field names are followed by an index 
        # of analytic solution
        ii = 0
        while ii < len(fieldTestEls):
            fieldName = fieldTestEls[ii].text
            self.fields[fieldName] = FieldComparisonOp(fieldName)
            # Skip the index
            ii+=1
            ii+=1
        # NB: not reading in all the other specifying stuff currently. Possibly
        # would be useful to do this in future.

        os.remove(ffile)

    def getAllResults(self, modelResult):
        fComps = self.fields.values()
        return [fCompOp.getResult(modelResult) for fCompOp in fComps]

#--------------------------------------
# Functions below useful for doing convergence analysis with length scale

def getFieldScaleCvgData_SingleCvgFile(cvgFilePath):
    '''A utility function for generating necessary fieldErrorData for a
    multi-res convergence analysis, assuming it's all stored in the same 
    convergence file (the default approach of the legacy SYS tests)'''
    cvgIndex = stgcvg.genConvergenceFileIndex(cvgFilePath)
    fieldErrorData = {}
    for fieldName, cvgFileInfo in cvgIndex.iteritems():
        #NB: assumes all cvg files and all fields have same len scales.
        lenScales = stgcvg.getRes(cvgFileInfo.filename)
        dofErrors = stgcvg.getDofErrors_ByDof(cvgFileInfo)
        fieldErrorData[fieldName] = dofErrors
    return lenScales, fieldErrorData

def calcFieldCvgWithScale(fieldName, lenScales, dofErrors):
    '''Gets the convergence and correlation of a field with resolution
    (taking the log10 of both).
    
    lenScales argument should simply be an array of length scales for the
    different runs.
    dofErrors must be a list, for each dof of the field, of the error
    vs some expected solution at the corresponding length scale.

    returns a list of tuples, one per dof, where each tuple contains:
    (convergence rate, pearson correlation) over the set of scales.
    ''' 

    print "Testing convergence for field '%s'" % fieldName
    #print "Length scales are %s" % lenScales
    #print "Dof errors for %d dofs are %s" % (len(dofErrors), dofErrors)
    scaleLogs = map(math.log10, lenScales)
    convResults = []
    for errorArray in dofErrors:
        errLogs = map(math.log10, errorArray)
        cvgRate, intercept, rSq = stats.linreg(scaleLogs, errLogs)
        pearsonCorr = math.sqrt(rSq)
        convResults.append((cvgRate, pearsonCorr))
    return convResults        

