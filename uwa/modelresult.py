from lxml import etree
import os

class ModelResult:
    '''A class to keep records about the results of a StgDomain/Underworld
     model run'''

    XML_INFO_TAG = 'StgModelResult'

    def __init__(self, modelName, simtime):
        self.modelName = modelName
        self.jobMetaInfo = JobMetaInfo(simtime)
        self.fieldResults = []

    def recordFieldResult(self, fieldName, tol, errors):
        '''Records the info required for a FieldResult in the array of
         stored FieldResults kept by the ModelResult. Returns a reference
         to the just-added FieldResult.'''
        fieldResult = FieldResult(fieldName, tol, errors)
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
        self.simtime = float(simtime)

    def writeInfoXML(self, xmlNode):
        '''Writes information about this class into an existing, open
         XML doc node'''
        jmNode = etree.SubElement(xmlNode, self.XML_INFO_TAG)
        etree.SubElement(jmNode, 'simtime').text = str(self.simtime)


#TODO: move into Analysis for fields.
class FieldResult:
    '''Simple class for storing UWA FieldResults'''
    XML_INFO_TAG = "fieldResult"
    XML_INFO_LIST_TAG = "fieldResults"

    def __init__(self, fieldName, tol, dofErrors):
        self.fieldName = fieldName
        self.tol = float(tol)
        self.dofErrors = []
        # Allow the user to pass in just a single error value result for
        # simple fields
        if isinstance(dofErrors, int):
            dofErrors = [dofErrors]

        for errorStr in dofErrors:
            self.dofErrors.append(float(errorStr))
    
    def writeInfoXML(self, fieldResultsNode):
        '''Writes information about a FieldResult into an existing,
         open XML doc node'''
        fr = etree.SubElement(fieldResultsNode, self.XML_INFO_TAG)
        fr.attrib['fieldName'] = self.fieldName
        fr.attrib['tol'] = str(self.tol)
        for dofIndex in range(len(self.dofErrors)):
            dr = etree.SubElement(fr, 'dofResult')
            dr.attrib['dof'] = str(dofIndex)
            dr.attrib['error'] = str(self.dofErrors[dofIndex])

# Key XML tags

def writeModelResultsXML(modelResult, path="", filename="", prettyPrint=True):
    mres = modelResult
    assert isinstance(mres, ModelResult)
    if filename == "":
        filename = defaultModelResultFilename(mres.modelName)
    if path != "":
        path+=os.sep
        if not os.path.exists(path):
            os.makedirs(path)

    # Write extra model results, e.g.
    # create model file
    mrNode = etree.Element(modelResult.XML_INFO_TAG)
    xmlDoc = etree.ElementTree(mrNode)
    etree.SubElement(mrNode, 'modelName').text = mres.modelName
    mres.jobMetaInfo.writeInfoXML(mrNode)
    if (mres.fieldResults):
        fieldResultsNode = etree.SubElement(mrNode,
            FieldResult.XML_INFO_LIST_TAG)
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
    fieldResultsNode = xmlDoc.find(FieldResult.XML_INFO_LIST_TAG)
    # It may not exist, if there were no field results already,
    # in which case grab existing
    if fieldResultsNode is None:
        fieldResultsNode = etree.SubElement(root, FieldResult.XML_INFO_LIST_TAG)
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

