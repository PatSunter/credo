
import copy
import os, glob
import itertools

import uwa
from uwa import modelrun as mrun
from uwa import modelresult as mres

class StgXMLVariant:
    def __init__(self, paramPath, paramRange):
        self.paramPath = paramPath
        self.paramRange = paramRange
    
    def applyToModel(self, modelRun, ii):
        modelRun.paramOverrides[self.paramPath] = self.paramRange[ii]

    def applyToModelGenerator(self, modelRun):
        for paramVal in self.paramRange:
            modelRun.paramOverrides[self.paramPath] = paramVal
            yield modelRun
    
    def varLen(self):
        """Returns the length of the list of variables"""
        return len(self.paramRange)
    
    def varStr(self, ii):
        return str(self.paramRange[ii])


class ModelSuite:
    '''A class for running a suite of Models (e.g. a group for profiling,
    or a System Test that requires multiple runs).
    
    .. attribute:: subOutputPathGenFunc
       
       If set, this function will be used to customise the model sub-path based
       on each modelRun.

    '''

    def __init__(self, outputPathBase, templateMRun=None):
        self.outputPathBase = outputPathBase
        self.runs = []
        self.runDescrips = []
        self.runCustomOptSets = []
        self.resultsList = []
        self.subOutputPathGenFunc = None
        self.templateMRun = templateMRun
        self.modelVariants = {}

    def addRun(self, modelRun, runDescrip=None, runCustomOpts=None):
        if not isinstance( modelRun, mrun.ModelRun ):
            raise TypeError("Error, given run not an instance of a"\
                " ModelRun" % runI)
        self.runs.append(modelRun)
        self.runDescrips.append(runDescrip)
        self.runCustomOptSets.append(runCustomOpts)

    def cleanAllOutputPaths(self):
        '''Remove all files in each model's output path. Useful to get rid of
        results still there from previous jobs. Doesn't delete sub-directories,
        in case they are other model runs results that should be ignored.'''
        for modelRun in self.runs:
            for filePath in glob.glob(os.path.join(modelRun.outputPath,"*")):
                if os.path.isfile(filePath):
                    os.unlink(filePath)

    def addVariant(self, name, modelVariant):
        self.modelVariants[name] = modelVariant

    def generateRuns(self):        
        '''When using a template modelRun, will generate runs for the suite
        based on it, and any run variants set.'''

        # TODO: exception check
        assert self.templateMRun

        variantLens = [variant.varLen() for variant in
            self.modelVariants.itervalues()]
        for paramIndices in itertools.product(*map(range, variantLens)):
            # First create a copy of the template model run
            newMRun = copy.deepcopy(self.templateMRun)
            # Now, apply each variant to it as appropriate
            for varI, variantGen in enumerate(self.modelVariants.itervalues()):
                paramI = paramIndices[varI]
                variantGen.applyToModel(newMRun, paramI)

            # Now build the output path for this modelRun
            if self.subOutputPathGenFunc:
                subPath = self.subOutputPathGenFunc(modelRun)
            else:    
                subPath = ""
                for varI, variantEntry in enumerate(
                        self.modelVariants.iteritems()):    
                    varName, variantGen = variantEntry
                    paramI = paramIndices[varI]
                    if subPath != "": subPath += "-"
                    subPath += "%s_%s" % (varName, variantGen.varStr(paramI))

            newMRun.outputPath = os.path.join(self.outputPathBase, subPath)  
            self.runs.append(newMRun)
            self.runDescrips.append(subPath)
            self.runCustomOptSets.append(None)

    def runAll(self, extraCmdLineOpts=None, dryRun=False):
        '''Run each modelRun in the suite - with optional extra cmd line opts'''
        # NB: may want to pass in a jobRunner argument, to do the run

        print "Running the %d modelRuns specified in the suite" % len(self.runs)
        for runI, modelRun in enumerate(self.runs):
            if not isinstance(modelRun, mrun.ModelRun):
                raise TypeError("Error, stored run %d not an instance of a"\
                    " ModelRun" % runI)
            print "Doing run %d/%d (index %d), of name '%s':"\
                % (runI+1, len(self.runs), runI, modelRun.name)
            print "ModelRun description: \"%s\"" % (self.runDescrips[runI])
            print "Generating analysis XML:"
            modelRun.analysisXMLGen()
            print "Running the Model (saving results in %s):"\
                % (modelRun.outputPath)
            customOpts = None
            if self.runCustomOptSets[runI]:
                customOpts = self.runCustomOptSets[runI]
            if extraCmdLineOpts:
                if customOpts == None: customOpts = ""
                customOpts += extraCmdLineOpts
            result = mrun.runModel(modelRun, customOpts, dryRun)
            if dryRun == True: continue
            assert isinstance( result, mres.ModelResult )
            print "Doing post-run tidyup:"
            modelRun.postRunCleanup(os.getcwd())
            self.resultsList.append(result)

        return self.resultsList    
    
    def writeAllModelRunXMLs(self):
        for runI, modelRun in enumerate(self.runs):
            modelRun.writeInfoXML(outputPath=modelRun.outputPath)

    def writeAllModelResultXMLs(self):
        for runI, result in enumerate(self.resultsList):
            mres.writeModelResultsXML(result, path=self.runs[runI].outputPath)
            
    # TODO: here would be where we have tools to generate stats/plots
    # of various properties of the suite, e.g. memory usage
