import os
from lxml import etree
import inspect

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


class SysTestRunner:

    def __init__(self, sysTests=[], nproc=1):
        self.sysTests = sysTests
        # Should this be over-rideable per test?
        self.nproc = nproc
    
    def addStdTest(self, testClass, inputFiles, **testOpts):
        if not inspect.isclass(testClass):
            raise TypeError("The testClass argument must be a type that's"\
                " a subclass of the UWA SysTest type. Arg passed in, '%s',"\
                " of type '%s', is not a Python Class." \
                % (testClass, type(testClass)))
        if not issubclass(testClass, SysTest):
            raise TypeError("The testClass argument must be a type that's"\
                " a subclass of the UWA SysTest type. Type passed in, '%s',"\
                " not a subclass of SysTest." \
                % (testClass))
                
        classStr = str(testClass).split('.')[-1]
        testName, ext = os.path.splitext(inputFiles[0])
        testName += "-"+classStr[0].lower()+classStr[1:]
        outputPath = 'output/' + testName
        # TODO: make the test name an input arg?
        newSysTest = testClass(inputFiles, outputPath, nproc=self.nproc)
        self.sysTests.append(newSysTest)

    def runTest(self, sysTest):
        # Generate a suite of models to run as part of the test
        mSuite = sysTest.genSuite()

        mSuite.writeAllModelRunXMLs()
        suiteResults = mSuite.runAll()
        print "Checking test result:"
        testResult = sysTest.getStatus(suiteResults)
        mSuite.writeAllModelResultXMLs()

        print "Test result was %s" % testResult
        sysTest.writeInfoXML()
        return testResult

    def runAll(self):
        results = []
        for testI, sysTest in enumerate(self.sysTests):
            print "Running System test %d, with name '%s':" \
                % (testI, sysTest.testName)
            results.append(self.runTest(sysTest))
        
        self.printResultsSummary(results)
    
    def printResultsSummary(self, results):
        print "UWA System Tests results summary:"
        print "Ran %d system tests, " % (len(results)),

        #


class SysTest:
    '''A class for managing SysTests in UWA. This is an abstract base
    class: you must sub-class it to create actual system test types.'''

    def __init__(self, inputFiles, outputPathBase, nproc, testType):
        self.testType = testType
        self.testName, ext = os.path.splitext(inputFiles[0])
        self.testName += "-%sTest" % (testType[0].lower()+testType[1:])
        self.inputFiles = inputFiles
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
