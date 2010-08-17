"""This module allows recording and post-processing of the results of running
a StGermain-based application.

The primary interface is via the :class:`~credo.modelrun.ModelRun` class.

.. seealso:: :mod:`credo.modelrun`."""

from xml.etree import ElementTree as etree
import os

from credo.io import stgfreq
from credo.io.stgxml import writeXMLDoc
from credo.analysis import fields

class ModelResult:
    """A class to keep records about the results of a StgDomain/Underworld
     model run. These are normally produced as a result of running a
     :class:`~credo.modelrun.ModelRun`. 

     .. note:: In future, we intend to add the ability to create a ModelResult
        class by reading in an XML file specifying output directory, etc.

     .. attribute:: modelName

        Name of the Model that was run.

     .. attribute:: outputPath

        Path to the output results the ModelRun produced.

     .. attribute:: jobMetaInfo

        A :class:`.JobMetaInfo`, recording information about the run such as
        time taken, Memory usage etc.

     .. attribute:: fieldResults

        A list of FieldComparisonResult objects.

        .. note:: is a legacy of early design of CREDO to allow construction of
           XML files from pre-existing sys test scripts, may be removed soon.

     .. attribute:: freqOutput

        Initially `None`, if :meth:`.readFrequentOutput` is called, this will
        be populated with a reference to a :class:`credo.io.stgfreq.FreqOutput`
        class, to allow post-processing of info in the Frequent Output file
        saved as part of the model run.

     """

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
        """Opens and reads in info from the Frequent Output file produced
        as part of the run, and saves to the attribute :attr:`.freqOutput`.

        .. seealso: :class:`credo.io.stgfreq.FreqOutput` for info on how to
           use this attribute once created."""
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
    memory usage, etc.

    .. attribute:: simtime

       Simulated time the model ran for.
    '''

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
    """Write an XML record of a :class:`.ModelResult`."""
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
            fields.FieldComparisonResult.XML_INFO_LIST_TAG)
        for fieldResult in mres.fieldResults:
            fieldResult.writeInfoXML(fieldResultsNode)

    # Write the file, default name if filename provided is empty
    outFile = open(path+filename, 'w')
    writeXMLDoc(xmlDoc, outFile, prettyPrint)
    outFile.close()
    return path+filename


def updateModelResultsXMLFieldInfo(filename, newFieldResult, prettyPrint=True):
    """Update an existing XML record of a :class:`.ModelResult` with info
    about a particular fieldResult."""
    assert filename != ""

    xmlDoc = etree.parse(filename)
    root = xmlDoc.getroot()
    
    # Because we just grabbed a reference to the root, the find will
    # look relative to the root
    fieldResultsNode = xmlDoc.find(fields.FieldComparisonResult.XML_INFO_LIST_TAG)
    # It may not exist, if there were no field results already,
    # in which case grab existing
    if fieldResultsNode is None:
        fieldResultsNode = etree.SubElement(root, fields.FieldComparisonResult.XML_INFO_LIST_TAG)
    else:
        # TODO: Check the field to add is not in the list already
        pass

    newFieldResult.writeInfoXML(fieldResultsNode)

    # Write the file, default name if filename provided is empty
    outFile = open(filename, 'w')
    writeXMLDoc(xmlDoc, outFile, prettyPrint)
    outFile.close()

def defaultModelResultFilename(modelName):
    """Get the default filename to use, based on the model name of a
    particular model."""
    return 'ModelResult-'+modelName+'.xml'

