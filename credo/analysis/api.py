"""This is the core interface for analysis operations in CREDO."""

# TODO: add some documentation about the archicture of AnalysisOps, and how this
# could be related/integrated with gLucifer.

class AnalysisOperation:
    '''Abstract base class for Analysis Operations in CREDO: i.e. that require
    some analysis to be done during a 
    :class:`~credo.modelrun.ModelRun`. All instances should provide at least
    this standard interface so that records of analysis can be stored.'''
    
    def writeInfoXML(self, parentNode):
        '''Virtual method for writing Information XML about an analysis op,
        that will be saved as a record of the analysis applied.'''

        raise NotImplementedError("This is a virtual method and must be"
            " overwritten")       

    def writeStgDataXML(self, rootNode):
        '''Writes the necessary StGermain XML to require the analysis to take
        place. This is likely to include creating and configuring Components,
        and adding them to the Components dictionary. See
        :mod:`credo.io.stgxml` for the interface for setting these up.'''

        raise NotImplementedError("This is a virtual method and must be"
            " overwritten")       

    def postRun(self, modelRun, runPath):
        '''Does any required post-run actions for this analysis op, e.g. moving
        generated files into the correct output directory. Is passed
        a reference to a :class:`~credo.modelrun.ModelRun`, so can use it's
        attributes such as :attr:`~credo.modelrun.ModelRun.outputPath`.'''

        raise NotImplementedError("This is a virtual method and must be"
            " overwritten")       
