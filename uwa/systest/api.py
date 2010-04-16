
class SysTestRunner:

    def __init__(self, sysTest):
        # Nothing for the base class
        pass
        self.sysTest = sysTest
    
    def runTest(self):
        # Generate a suite of models to run as part of the test
        mSuite = sysTest.genSuite()

        suiteResults = mSuite.runSuite()
        suiteResults.writeAllXMLs(sysTest.outputPath)

        testResult = sysTest.getStatus(suiteResults)
        sysTest.writeXML(sysTest.outputPath)
       

class SysTest:
    def __init__():
        

    def genSuite():
        print "Error, base class"
        assert 0

    def getStatus( suiteResults ):
        print "Error, base class"
        
    def writeXML( outputPath ):    
        # Create the XML file, and standard tags
        # Write standard stuff like descriptions, etc
        print "Error, base class"

    def writeXMLContents( outputPath ):
        # Write the contents of this particular test

