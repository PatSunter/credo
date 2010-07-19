
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL

class SkeletonSysTest(SysTest):
    """A Skeleton system test class, used for testing."""

    description = "Skeleton system test."

    def __init__(self, inputFiles, outputPathBase, nproc=1,
            paramOverrides=None, solverOpts=None, nameSuffix=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Skeleton", nameSuffix)        
    
    def getSuite(self):
        self.mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        return mSuite
    
    def checkResultValid(self, resultsSet):
        pass

    def getStatus(self, resultsSet):
        testStatus = UWA_PASS("Skeleton test always passes.")
        self.testStatus = testStatus
        return testStatus
    
    def _writeXMLCustomSpec(self, specNode):
        pass
