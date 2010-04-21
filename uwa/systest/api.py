
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
    statusStr = 'Pass'

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

    def __init__(self, sysTest):
        # Nothing for the base class
        pass
        self.sysTest = sysTest
    
    def runTest(self):
        # Generate a suite of models to run as part of the test
        mSuite = sysTest.genSuite()

        suiteResults = mSuite.runAll()
        suiteResults.writeAllXMLs(sysTest.outputPath)

        testResult = sysTest.getStatus(suiteResults)
        sysTest.writeXML(sysTest.outputPath)
       

class SysTest:
    def genSuite():
        print "Error, base class"
        assert 0

    def getStatus(suiteResults):
        print "Error, base class"
        
    def writeXML(outputPath):    
        # Create the XML file, and standard tags
        # Write standard stuff like descriptions, etc
        writeXMLContexts(outputPath)
        # Write any necessary closing stuff, write the file

    def writeXMLContents(outputPath):
        # Write the contents of this particular test
        print "Error, base class"

