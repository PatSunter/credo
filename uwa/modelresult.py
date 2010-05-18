from lxml import etree
import os

from uwa.io import stgfreq
from uwa.analysis import fields

class ModelResult:
    '''A class to keep records about the results of a StgDomain/Underworld
     model run'''

    XML_INFO_TAG = 'StgModelResult'

    def __init__(self, modelName, outputPath, simtime):
        self.modelName = modelName
        self.outputPath = outputPath
        # TODO: ideally should the jobrunner pass this in?
        # TODO: Sim time not really a job meta info
        self.jobMetaInfo = JobMetaInfo(simtime)
        self.fieldResults = []
        self.freqOutput = None

    def readFrequentOutput(self):
        self.freqOutput = stgfreq.FreqOutput(self.outputPath)    

    # TODO: is this function still appropriate?
    def recordFieldResult(self, fieldName, tol, errors):
        '''Records the info required for a FieldResult in the array of
         stored FieldResults kept by the ModelResult. Returns a reference
         to the just-added FieldResult.'''
        fieldResult = fields.FieldComparisonResult(fieldName, errors)
        self.fieldResults.append(fieldResult)
        return fieldResult

# TODO: can the below just be collapsed into a dictionary? Then have
# standard write facilities.
# Or maybe sub-class from dict, and just add some parameter checking.
class JobMetaInfo:
    '''A simple class for recording meta info about a job, such as walltime,
    memory usage, etc'''
    XML_INFO_TAG = "jobMetaInfo"

    def __init__(self, simtime):
        if simtime is None:
            self.simtime = "unknown"
        else:     
            self.simtime = float(simtime)

    def writeInfoXML(self, xmlNode):
        '''Writes information about this class into an existing, open
         XML doc node'''
        jmNode = etree.SubElement(xmlNode, self.XML_INFO_TAG)
        etree.SubElement(jmNode, 'simtime').text = str(self.simtime)

# Key XML tags

def writeModelResultsXML(modelResult, path="", filename="", prettyPrint=True):
    mres = modelResult
    assert isinstance(mres, ModelResult)
    if filename == "":
        filename = defaultModelResultFilename(mres.modelName)
    if path == "":
        path = modelResult.outputPath
    else:
        path += os.sep
        if not os.path.exists(path): os.makedirs(path)

    # Write extra model results, e.g.
    # create model file
    mrNode = etree.Element(modelResult.XML_INFO_TAG)
    xmlDoc = etree.ElementTree(mrNode)
    etree.SubElement(mrNode, 'modelName').text = mres.modelName
    etree.SubElement(mrNode, 'outputPath').text = mres.outputPath
    mres.jobMetaInfo.writeInfoXML(mrNode)
    if (mres.fieldResults):
        fieldResultsNode = etree.SubElement(mrNode,
            fields.FieldResult.XML_INFO_LIST_TAG)
        for fieldResult in mres.fieldResults:
            fieldResult.writeInfoXML(fieldResultsNode)

    # Write the file, default name if filename provided is empty
    outFile = open(path+filename, 'w')
    xmlDoc.write(outFile, pretty_print=prettyPrint)
    outFile.close()
    return path+filename


def updateModelResultsXMLFieldInfo(filename, newFieldResult, prettyPrint=True):
    assert filename != ""

    xmlDoc = etree.parse(filename)
    root = xmlDoc.getroot()
    
    # Because we just grabbed a reference to the root, the find will
    # look relative to the root
    fieldResultsNode = xmlDoc.find(fields.FieldResult.XML_INFO_LIST_TAG)
    # It may not exist, if there were no field results already,
    # in which case grab existing
    if fieldResultsNode is None:
        fieldResultsNode = etree.SubElement(root, fields.FieldResult.XML_INFO_LIST_TAG)
    else:
        # TODO: Check the field to add is not in the list already
        pass

    newFieldResult.writeInfoXML(fieldResultsNode)

    # Write the file, default name if filename provided is empty
    outFile = open(filename, 'w')
    xmlDoc.write(outFile, pretty_print=prettyPrint)
    outFile.close()

def defaultModelResultFilename(modelName):
    return 'ModelResult-'+modelName+'.xml'

