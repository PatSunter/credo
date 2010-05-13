

class AnalysisOperation:
    '''Abstract base class for Analysis Operations in UWA: i.e. that require
    some analysis to be done during a ModelRun.'''
    
    def writeInfoXML(self, parentNode):
        '''Virtual method for writing Information XML about an analysis op.'''
        raise NotImplementedError("This is a virtual method and must be"
            " overwritten")       

    def writeStgDataXML(self, rootNode):
        '''Writes the necessary StGermain XML to require the analysis to take
        place'''
        raise NotImplementedError("This is a virtual method and must be"
            " overwritten")       

    def postRun(self, modelRun, runPath):
        '''Does any required post-run actions for this analysis op, e.g. moving
        generated files into the correct directory.'''
        raise NotImplementedError("This is a virtual method and must be"
            " overwritten")       
