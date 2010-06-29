"""Core API of the :mod:`uwa.systest` module.

This defines the two key classes of the model, :class:`.SysTest` and 
:class:`.TestComponent`, from which actual examples of System tests
or Test components need to inherit.
"""

import os
from xml.etree import ElementTree as etree
import uwa.modelrun as mrun
from uwa.io.stgxml import writeXMLDoc

class SysTestResult:
    """Class to represent an UWA system test result.

    .. attribute:: detailMsg

       detailed message of what happened during the test.

    .. attribute:: statusStr

       One-word status string summarising test result (eg 'Pass').
    """   

    detailMsg = None
    statusStr = None

    def __str__(self):
        return self.statusStr
    
    def printDetailMsg(self):
        if self.detailMsg:
            print self.detailMsg


class UWA_PASS(SysTestResult):
    '''Simple class to represent an UWA pass'''
    def __init__(self, passMsg):
        assert type(passMsg) == str
        self.statusStr = 'Pass'
        self.detailMsg = passMsg

class UWA_FAIL(SysTestResult):
    '''Simple class to represent an UWA failure'''
    def __init__(self, failMsg):
        assert type(failMsg) == str
        self.statusStr = 'Fail'
        self.detailMsg = failMsg
        
class UWA_ERROR(SysTestResult):
    '''Simple class to represent an UWA error'''
    def __init__(self, errorMsg):
        self.statusStr = 'Error'
        assert type(errorMsg) == str
        self.detailMsg = errorMsg


class SysTest:
    '''A class for managing SysTests in UWA. This is an abstract base
    class: you must sub-class it to create actual system test types.

    The SysTest is designed to interact with the 
    :class:`~uwa.systest.systestrunner.SysTestRunner` class, primarily by
    creating a :class:`~uwa.modelsuite.ModelSuite` on demand to run a set
    of ModelRuns required to do the test. It will then do a check that
    the results pass an expected metric:- generally by applying one or more
    :class:`~uwa.systest.api.TestComponent` classes.
    
    .. attribute:: testType

       records the "type" of the system test, as a string (e.g. "Analytic",
       or "SciBenchmark") - for printing purposes.
    
    .. attribute:: inputFiles

       StGermain XML files that define the Model to be tested.

    .. attribute:: testName

       The name of this test, generally auto-generated from other properties.
       
    .. attribute:: outputPathBase

       The "base" output path to store results of the test in. Results from
       individual Model Runs performed as part of running the test may also
       be stored in that directory, or in subdirectories of it.
    
    .. attribute:: testStatus

       Status of the test. Initially `None`, once the test has been run
       the :class:`.SysTestResult` generated will be saved here.

    .. attribute:: testComponents

       A list of any :class:`.TestComponent` classes used as part of 
       performing the test.
    
    .. attribute:: nproc

       Number of processors to be used for the test. See 
       :attr:`uwa.modelrun.ModelRun.nproc`.

    .. attribute:: paramOverrides

       Any model parameter overrides to be passed to ModelRuns performed
       as part of running the test - see
       :attr:`uwa.modelrun.ModelRun.paramOverrides`. Thus allow 
       customisation of the test properties.

    '''

    def __init__(self, inputFiles, outputPathBase, nproc, paramOverrides,
            testType):
        self.testType = testType
        # Be forgiving of user passing a single string rather than a list,
        # and correct for this.
        if isinstance(inputFiles, str):
            inputFiles = [inputFiles]
        self.inputFiles = inputFiles
        for iFile in self.inputFiles:
            if not os.path.exists(iFile):
                raise IOError("One of the given input files, '%s',"
                    " doesn't exist." % (iFile))
        self.testName, ext = os.path.splitext(inputFiles[0])
        self.testName += "-%sTest" % (testType[0].lower()+testType[1:])
        self.outputPathBase = outputPathBase
        self.testStatus = None
        self.testComponents = {}
        self.nproc = nproc 
        self.paramOverrides = paramOverrides

    def setup(self):
        '''For the setup phase of tests.
        Since not all tests need a setup phase, the default behaviour is to
        do nothing.'''
        pass

    def genSuite(self):
        """Virtual method: must return a :class:`uwa.modelsuite.ModelSuite`
        containing all models that need to be run to perform the test."""
        raise NotImplementedError("Error, base class")

    def checkResultValid(self, resultsSet):
        """Check that the given result set is "valid", i.e. exists, has 
        the right number of model results, and model results have necessary
        analysis ops associated with them to allow aspects of test to
        evaluate properly."""

    def getStatus(self, suiteResults):
        """Virtual method: after a suite of runs created by :meth:".genSuite"
        has been run, when this method is passed the results of the suite
        (as a list of :class:`uwa.modelresult.ModelResult`), it must decide
        and return the status of the test (as a :class:`.SysTestResult`).

        It also needs to save this status to :meth:`.testStatus`.
        """
        raise NotImplementedError("Error, base class")
        
    def defaultSysTestFilename(self):
        """Return the default system test XML record filename, based on
        properties of the systest (such as :attr:`.testName`)."""
        return 'SysTest-'+self.testName+'.xml'

    def writePreRunXML(self, outputPath="", filename="", prettyPrint=True):
        """Write the SysTest XML with as much information before the run as
        is possible. This includes general info about the test, and detailed
        specificiation of appropriate parameters and test components.
        
        :param outputPath: (opt) path the XML should be saved to.
        :param filename: (opt) filename within that path that should be used.
        :param prettyPrint: whether to indent the XML for better
          human-readability (pretty-printing).
        :returns: the name of the file written to.
        """
        baseNode = self._createXMLBaseNode()
        self._writeXMLDescription(baseNode)
        self._writeXMLSpecification(baseNode)
        self._writeXMLTestComponentPreRuns(baseNode)
        xmlDoc = etree.ElementTree(baseNode)
        outFileName = self._writeXMLDocToFile(xmlDoc, outputPath, filename)
        return outFileName
        
    def updateXMLWithResult(self, resultsSet, outputPath="", filename="", prettyPrint=True):
        """Given resultsSet, a set of model results (list of 
        :class:`~uwa.modelresult.ModelResult`), updates a Sys Test XML with
        the results of the test.
        If the XML file has the standard name, as defined by
        :meth:`.defaultSysTestFilename`, then it should be found automatically.

        Other arguments and return value same as for 
        :meth:`.writePreRunXML`.
        """
        baseNode, xmlDoc = self._getXMLBaseNodeFromFile(outputPath, filename)
        baseNode.attrib['status'] = str(self.testStatus)
        self._writeXMLResult(baseNode)
        self._updateXMLTestComponentResults(baseNode, resultsSet)
        outFileName = self._writeXMLDocToFile(xmlDoc, outputPath, filename)
        return outFileName

    def _createXMLBaseNode(self):
        """Create the base XML node for a Sys Test XML, in xml.etree format,
        and return it."""
        baseNode = etree.Element('StgSysTest')
        baseNode.attrib['type'] = self.testType
        baseNode.attrib['name'] = self.testName
        return baseNode

    def _resolveXMLOutputPathFilename(self, outputPath="", filename=""):   
        if filename == "":
            filename = self.defaultSysTestFilename()
        if outputPath == "":
            outputPath=self.outputPathBase
        outputPath+=os.sep
        return outputPath, filename

    def _writeXMLDocToFile(self, xmlDoc, outputPath, filename, prettyPrint=True):
        """Write the information in xmlDoc (in xml.etree format) to the filename
        given by outputPath and filename."""
        outputPath, filename = self._resolveXMLOutputPathFilename(
            outputPath, filename)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        outFilePath = os.path.join(outputPath, filename)
        outFile = open(outFilePath, 'w')
        writeXMLDoc(xmlDoc, outFile, prettyPrint)
        outFile.close()
        return outFilePath

    def _getXMLBaseNodeFromFile(self, outputPath="", filename=""):
        """Open the XML file in outputPath and given by filename (if these
        are empty strings, defaults are used), and return the base node
        from this file (in xml.etree format)."""
        outputPath, filename = self._resolveXMLOutputPathFilename(
            outputPath, filename)
        outFile = open(os.path.join(outputPath, filename), 'r+')
        parser = etree.XMLParser()
        # Note: we haven't removed blank spaces from the output
        # (xml.etree doesn't have an automatic option for this),
        # but that shouldn't pose a problem as no whitespace should
        # interfere with meaningful element text.
        xmlDoc = etree.parse(outFile, parser)
        baseNode = xmlDoc.getroot()
        return baseNode, xmlDoc

    def _writeXMLDescription(self, baseNode):
        """Writes the description of a test into an XML sub-node."""
        descNode = etree.SubElement(baseNode, 'description')
        descNode.text = self.description

    def _writeXMLSpecification(self, baseNode):
        """Function to write the test specification to baseNode (xml.etree)."""
        specNode = etree.SubElement(baseNode, 'testSpecification')
        
        ipListNode = etree.SubElement(specNode, 'inputFiles')
        for xmlFilename in self.inputFiles:
            fileNode = etree.SubElement(ipListNode, 'inputFile')
            fileNode.text = xmlFilename
        etree.SubElement(specNode, 'outputPathBase').text = self.outputPathBase

        nProcNode = etree.SubElement(specNode, "nproc")
        nProcNode.text = str(self.nproc)

        mrun.writeParamOverridesInfoXML(self.paramOverrides, specNode)
        try:
            self._writeXMLCustomSpec(specNode)   
        except AttributeError, ae:
            raise NotImplementedError("Please implement a "\
                " _writeXMLCustomSpec()"\
                " method for your SysTest subclass: %s" % ae )
            raise ae
    
    def _writeXMLCustomSpec(self, specNode):
        """Function to write the custom specification for a particular test
        type. Virtual method, to be implemented by sub-classes."""
        raise NotImplementedError("Abstract base class.")

    def _writeXMLTestComponentPreRuns(self, baseNode):
        """Write necessary info for all test components used by this 
        system test before a run (eg their specification info."""
        tcListNode = etree.SubElement(baseNode, 'testComponents')
        for tcName, testComponent in self.testComponents.iteritems():
            testComponent.writePreRunXML(tcListNode, tcName)

    def _updateXMLTestComponentResults(self, baseNode, resultsSet):
        """Update the XML info about each test component after a run
        (ie result info.)"""
        tcListNode = baseNode.find('testComponents')
        tcCompsAndXMLs = zip(self.testComponents.iterkeys(),
            self.testComponents.itervalues(),
            tcListNode.getchildren())
        for tcName, testComponent, testCompXMLNode in tcCompsAndXMLs:
            assert tcName == testCompXMLNode.attrib['name']
            assert testComponent.tcType == testCompXMLNode.attrib['type']
            testComponent.updateXMLWithResult(testCompXMLNode, resultsSet)

    def _writeXMLResult(self, baseNode):
        """Write the status of a test to the XML doc."""
        resNode = etree.SubElement(baseNode, 'testResult')
        resNode.attrib['status'] = str(self.testStatus)
        statusMsgNode = etree.SubElement(resNode, 'statusMsg')
        statusMsgNode.text = self.testStatus.detailMsg


class TestComponent:
    '''A class for TestComponents that make up an UWA System test/benchmark.
    Generally they will form part a list contained by a 
    :class:`.SysTest`.

    This is an abstract base class, individual test components must subclass
    from this interface.
    
    .. attribute:: tcStatus
    
       Status of this test component. Initially None, will be updated after
       the test component is evaluated to a :class:`.SysTestResult`.
       
    .. attribute:: tcType
    
       Type of the test component, as a (single world descriptive) string.'''

    def __init__(self, tcType):
        self.tcStatus = None
        self.tcType = tcType

    def attachOps(self, modelRun):
        '''Provided a modelRun (:class:`uwa.modelrun.ModelRun`)
        attaches any necessary analysis operations
        to that run in order to produce the results needed for the test.
        (see :attr:`uwa.modelrun.ModelRun.analysis`).'''
        raise NotImplementedError("Abstract base class.")

    def check(self, resultsSet):
        '''A function to check a set of results - returns True if the Test
        passes, False if not. Also updates the :attr:`.tcStatus` attribute.'''
        raise NotImplementedError("Abstract base class.")

    def writePreRunXML(self, parentNode, name):
        '''Function to write out info about the test component to an XML file,
        as a sub-tree of parentNode.'''
        tcNode = self._createBaseXMLNode(parentNode, name)
        self._writeXMLSpecification(tcNode)
    
    def _createBaseXMLNode(self, parentNode, name):
        '''Utility function when writing out info, should be called by 
        sub-classes at start of writeInfoXML definitions to follow
        convention of naming of XML node.'''
        tcNode = etree.SubElement(parentNode, 'testComponent')
        tcNode.attrib['name'] = name
        tcNode.attrib['type'] = self.tcType
        return tcNode
    
    def _writeXMLSpecification(self, tcNode):
        specNode = etree.SubElement(tcNode, 'specification')
        #Not currently any specification for all testComponents ... though may
        # be a fromXML param in future for example.
        self._writeXMLCustomSpec(specNode)
    
    def _writeXMLCustomSpec(self, specNode):
        raise NotImplementedError("Abstract base class.")

    def updateXMLWithResult(self, tcNode, resultsSet):
        """Updates a given XML node with the result of the test component,
        based on resultsSet."""
        tcNode.attrib['status'] = str(self.tcStatus)
        self._writeXMLResult(tcNode, resultsSet)
    
    def _writeXMLResult(self, tcNode, resultsSet):
        resNode = etree.SubElement(tcNode, 'result')
        resNode.attrib['status'] = str(self.tcStatus)
        statusMsgNode = etree.SubElement(resNode, 'statusMsg')
        statusMsgNode.text = self.tcStatus.detailMsg
        self._writeXMLCustomResult(resNode, resultsSet)
    
    def _writeXMLCustomResult(self, resNode, resultsSet):
        raise NotImplementedError("Abstract base class.")
