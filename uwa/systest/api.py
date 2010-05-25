import os
from lxml import etree

class SysTestResult:
    detailMsg = None
    statusStr = None

    def __str__(self):
        return self.statusStr
    
    def printDetailMsg(self):
        if detailMsg:
            print detailMsg

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
    class: you must sub-class it to create actual system test types.'''

    def __init__(self, inputFiles, outputPathBase, nproc, testType):
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

    def setup():
        '''For the setup phase of tests.
        Since not all tests need a setup phase, the default behaviour is to
        do nothing.'''
        pass

    def genSuite():
        raise NotImplementedError("Error, base class")

    def getStatus(suiteResults):
        raise NotImplementedError("Error, base class")
        
    def defaultSysTestFilename(self):
        return 'SysTest-'+self.testName+'.xml'

    def writePreRunXML(self, outputPath="", filename="", prettyPrint=True):
        # Create the XML file, and standard tags
        # Write standard stuff like descriptions, etc
        baseNode = self.createXMLBaseNode()
        self.writeXMLDescription(baseNode)
        self.writeXMLSpecification(baseNode)
        self.writeXMLTestComponentPreRuns(baseNode)
        xmlDoc = etree.ElementTree(baseNode)
        outFileName = self.writeXMLDocToFile(xmlDoc, outputPath, filename)
        return outFileName
        
    def updateXMLWithResult(self, resultsSet, outputPath="", filename="", prettyPrint=True):
        baseNode, xmlDoc = self.getXMLBaseNodeFromFile(outputPath, filename)
        baseNode.attrib['status'] = str(self.testStatus)
        self.writeXMLResult(baseNode)
        self.updateXMLTestComponentResults(baseNode, resultsSet)
        outFileName = self.writeXMLDocToFile(xmlDoc, outputPath, filename)
        return outFileName

    def createXMLBaseNode(self):
        baseNode = etree.Element('StgSysTest')
        baseNode.attrib['type'] = self.testType
        baseNode.attrib['name'] = self.testName
        return baseNode

    def resolveXMLOutputPathFilename(self, outputPath="", filename=""):   
        if filename == "":
            filename = self.defaultSysTestFilename()
        if outputPath == "":
            outputPath=self.outputPathBase
        outputPath+=os.sep
        return outputPath, filename

    def writeXMLDocToFile(self, xmlDoc, outputPath, filename, prettyPrint=True):
        outputPath, filename = self.resolveXMLOutputPathFilename(
            outputPath, filename)
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        outFilePath = os.path.join(outputPath, filename)
        outFile = open(outFilePath, 'w')
        xmlDoc.write(outFile, pretty_print=prettyPrint)
        outFile.close()
        return outFilePath

    def getXMLBaseNodeFromFile(self, outputPath="", filename=""):
        outputPath, filename = self.resolveXMLOutputPathFilename(
            outputPath, filename)

        outFile = open(os.path.join(outputPath, filename), 'r+')
        # use a custom parser to remove blank text, so the doc can be correctly
        # re-prettyPrinted when done (see 
        # http://codespeak.net/lxml/FAQ.html
        #  #why-doesn-t-the-pretty-print-option-reformat-my-xml-output
        parser = etree.XMLParser(remove_blank_text=True)
        xmlDoc = etree.parse(outFile, parser)
        baseNode = xmlDoc.getroot()
        return baseNode, xmlDoc

    def writeXMLDescription(self, baseNode):
        '''Writes the description of a test into an XML sub-node.'''
        descNode = etree.SubElement(baseNode, 'description')
        descNode.text = self.description

    def writeXMLSpecification(self, baseNode):
        '''Function to write the test specification.'''
        specNode = etree.SubElement(baseNode, 'testSpecification')
        
        ipListNode = etree.SubElement(specNode, 'inputFiles')
        for xmlFilename in self.inputFiles:
            fileNode = etree.SubElement(ipListNode, 'inputFile')
            fileNode.text = xmlFilename
        etree.SubElement(specNode, 'outputPathBase').text = self.outputPathBase

        nProcNode = etree.SubElement(specNode, "nproc")
        nProcNode.text = str(self.nproc)
        try:
            self.writeXMLCustomSpec(specNode)   
        except AttributeError as ae:
            raise NotImplementedError("Please implement a writeXMLCustomSpec()"\
                " method for your SysTest subclass: %s" % ae )
            raise ae
    
    def writeXMLCustomSpec(self, specNode):
        '''Function to write the custom specification for a particular test
        type.'''
        raise NotImplementedError("Abstract base class.")

    def writeXMLTestComponentPreRuns(self, baseNode):
        tcListNode = etree.SubElement(baseNode, 'testComponents')
        for tcName, testComponent in self.testComponents.iteritems():
            testComponent.writePreRunXML(tcListNode)

    def updateXMLTestComponentResults(self, baseNode, resultsSet):
        tcListNode = baseNode.find('testComponents')
        tcCompsAndXMLs = zip(self.testComponents.itervalues(),
            tcListNode.iterchildren())
        for testComponent, testCompXMLNode in tcCompsAndXMLs:
            assert testComponent.tcName == testCompXMLNode.attrib['name']
            testComponent.updateXMLWithResult(testCompXMLNode, resultsSet)

    def writeXMLResult(self, baseNode):
        resNode = etree.SubElement(baseNode, 'testResult')
        resNode.attrib['status'] = str(self.testStatus)
        statusMsgNode = etree.SubElement(resNode, 'statusMsg')
        statusMsgNode.text = self.testStatus.detailMsg


class TestComponent:
    '''A class for TestComponents that make up an UWA System test/benchmark.

    This is an abstract base class, individual test components must subclass
    from this interface.'''

    def __init__(self, name):
        self.tcStatus = None
        self.tcName = name

    def attachOps(self, modelRun):
        '''Takes in a model run, and attaches any necessary analysis operations
        to that run in order to produce the results needed for the test.'''
        raise NotImplementedError("Abstract base class.")

    def check(self, resultsSet):
        '''A function to check a set of results - returns True if the Test
        passes, False if not.'''
        raise NotImplementedError("Abstract base class.")

    def writePreRunXML(self, parentNode):
        '''Function to write out info about the system test to an XML file,
        as a sub-tree of parentNode.'''
        tcNode = self.createBaseXMLNode(parentNode)
        self.writeXMLSpecification(tcNode)
    
    def createBaseXMLNode(self, parentNode):
        '''Utility function when writing out info, should be called by 
        sub-classes at start of writeInfoXML definitions to follow
        convention of naming of XML node.'''
        tcNode = etree.SubElement(parentNode, 'testComponent', name=self.tcName)
        return tcNode
    
    def writeXMLSpecification(self, tcNode):
        specNode = etree.SubElement(tcNode, 'specification')
        #Not currently any specification for all testComponents ... though may
        # be a fromXML param in future for example.
        self.writeXMLCustomSpec(specNode)
    
    def writeXMLCustomSpec(self, specNode):
        raise NotImplementedError("Abstract base class.")

    def updateXMLWithResult(self, tcNode, resultsSet):
        tcNode.attrib['status'] = str(self.tcStatus)
        self.writeXMLResult(tcNode, resultsSet)
    
    def writeXMLResult(self, tcNode, resultsSet):
        resNode = etree.SubElement(tcNode, 'result')
        resNode.attrib['status'] = str(self.tcStatus)
        statusMsgNode = etree.SubElement(resNode, 'statusMsg')
        statusMsgNode.text = self.tcStatus.detailMsg
        self.writeXMLCustomResult(resNode, resultsSet)
    
    def writeXMLCustomResult(self, resNode, resultsSet):
        raise NotImplementedError("Abstract base class.")
