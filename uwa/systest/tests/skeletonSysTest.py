
from uwa.systest.api import SysTest, UWA_PASS, UWA_FAIL
from uwa.modelsuite import ModelSuite

class SkeletonSysTest(SysTest):
    """A Skeleton system test class, used for testing."""

    description = "Skeleton system test."

    def __init__(self, inputFiles, outputPathBase,
            statusToReturn, nproc=1,
            paramOverrides=None, solverOpts=None, nameSuffix=None):
        SysTest.__init__(self, inputFiles, outputPathBase, nproc,
            paramOverrides, solverOpts, "Skeleton", nameSuffix)        
        self.statusToReturn = statusToReturn    
    
    def genSuite(self):
        # an empty suite
        self.mSuite = ModelSuite(outputPathBase=self.outputPathBase)
        return self.mSuite
    
    def checkResultValid(self, resultsSet):
        pass

    def getStatus(self, resultsSet):
        self.testStatus = self.statusToReturn
        return self.testStatus
    
    def _writeXMLCustomSpec(self, specNode):
        pass
