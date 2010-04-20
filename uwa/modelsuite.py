
import uwa
from uwa import modelrun as mrun
from uwa import modelresult as mres

class ModelSuite:
    '''A class for running a suite of Models (e.g. a group for profiling,
    or a System Test that requires multiple runs)'''

    def __init__(self):
        self.runs = []

    def runAll(self):
        '''Run each modelRun in the suite'''
        # NB: may want to pass in a jobRunner argument, to do the run

        resultsList=[]

        print "Running the %d modelRuns specified in the suite" % len(self.runs)
        for runI, run in enumerate(self.runs):
            assert isinstance( run, mrun.ModelRun )
            print "Doing run %d, of name '%s':" % (runI, run.name)
            print "Generating analysis XML:"
            mRun.analysisXML = mrun.analysisXMLGen(mRun)
            print "Running the Model:"
            result = mrun.runModel(mRun)
            assert isinstance( result, mres.ModelResult )
            # TODO: does this step need to be refactored/generalised?
            # I.E. into a "post-run cleanup" for all analysis ?
            print "Doing post-run tidyup:"
            uwa.moveConvergenceResults(os.getcwd(), mRun.outputPath)
            resultsList.append(result)

        return resultsList    
    
    # TODO: here would be where we have tools to generate stats/plots
    # of various properties of the suite, e.g. memory usage
