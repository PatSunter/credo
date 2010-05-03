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
        self.testName, ext = os.path.splitext(inputFiles[0])
        self.testName += "-%sTest" % (testType[0].lower()+testType[1:])
        self.outputPathBase = outputPathBase
        self.testStatus = None
        self.testComponents = {}
        self.nproc = nproc 

    def setup():
        '''For the setup phase of tests. Since not all tests need a setup
        phase, the default behaviour is to do nothing.'''
        pass

    def genSuite():
        print "Error, base class"
        assert 0

    def getStatus(suiteResults):
        print "Error, base class"
        
    def defaultSysTestFilename(self):
        return 'SysTest-'+self.testName+'.xml'

    def writeInfoXML(self, outputPath="", filename="", prettyPrint=True):
        # Create the XML file, and standard tags
        # Write standard stuff like descriptions, etc

        if filename == "":
            filename = self.defaultSysTestFilename()
        if outputPath == "":
            outputPath=self.outputPathBase
        outputPath+=os.sep

        # create XML document
        root = etree.Element('StgSysTest')
        xmlDoc = etree.ElementTree(root)

        # write standard parts
        self.writeXMLStandardParts(root)
        # Call the sub-class to write the actual systest contents
        try:
            self.writeXMLContents(root)
        except AttributeError as ae:
            raise NotImplementedError("Please implement a writeXMLContents()"\
                " method for your SysTest subclass: %s" % ae )
            raise ae

        # Write the file
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        outFile = open(outputPath+filename, 'w')
        xmlDoc.write(outFile, pretty_print=prettyPrint)
        outFile.close()
        return outputPath+filename

    def writeXMLStandardParts(self, baseNode):
        baseNode.attrib['type'] = self.testType
        baseNode.attrib['name'] = self.testName
        baseNode.attrib['status'] = str(self.testStatus)
        descNode = etree.SubElement(baseNode, 'description')
        descNode.text = self.description

        ipListNode = etree.SubElement(baseNode, 'inputFiles')
        for xmlFilename in self.inputFiles:
            fileNode = etree.SubElement(ipListNode, 'inputFile')
            fileNode.text = xmlFilename
        etree.SubElement(baseNode, 'outputPathBase').text = self.outputPathBase

        nProcNode = etree.SubElement(baseNode, "nproc")
        nProcNode.text = str(self.nproc)

        cpListNode = etree.SubElement(baseNode, 'testComponents')
        for tcName, testComponent in self.testComponents.iteritems():
            testComponent.writeInfoXML(cpListNode)

    def writeResultXML(self):
        # TODO
        # StgSysTestResult
        # Basic info about the test
        # Update with the status
        # Print the status message
        # Print Model Results as a sub-set
        pass
