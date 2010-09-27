##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA

"""This module allows the running of a whole suite of related 
:class:`~credo.modelrun.ModelRun` s, and managing and analysing their results
as a consistent set.

The key class in this module is the :class:`.ModelSuite`.

For example usage, see the CREDO documentation Examples section,
:ref:`credo-examples`, e.g. :ref:`credo-examples-raytay-run-suite`.

This class also performs a key role in the System tests provided in the
:mod:`credo.systest` module.
"""

import copy
import os, glob
import itertools
import operator
import csv

import credo
from credo import modelrun as mrun
from credo import modelresult as mres

# The below is for Python 2.5 compatibility
try:
    import itertools
    product = itertools.product
except AttributeError:
    import credo.utils
    product = credo.utils.productCalc

class StgXMLVariant:
    """A class that can be added to a :class:`.ModelSuite` to help 
    auto-generate a suite of ModelRuns to perform, where a particular
    parameter is being varied over a certain range.
    
    .. attribute:: paramPath
    
       The value to use when over-riding the parameter in a StGermain
       dictionary, using the StGermain command line format.
       
       E.g. Setting "gravity" would override the gravity parameter in
       the dictionary, whereas setting to 
       "components.initialConditionsShape.startX" would override the
       startX parameter, within the initialConditionsShape component.
       
    .. attribute:: paramRange
    
       A list, containing the values that the parameter should be varied
       over. E.g. [0,1,2], or [5.6, 7.8, 9.9]. Needs to be of the correct
       type for the particular parameter. The Python 
       `range() <http://docs.python.org/library/functions.html#range>`_
       function can be useful in generating such a list."""

    def __init__(self, paramPath, paramRange):
        self.paramPath = paramPath
        self.paramRange = paramRange
    
    def applyToModel(self, modelRun, ii):
        """Apply the ii-th value in the attr:`.paramRange` to a particular
        :class:`~credo.modelrun.ModelRun`."""
        modelRun.paramOverrides[self.paramPath] = self.paramRange[ii]
    
    def cmdLineStr(self, ii):
        """Return the command-line string to apply this value."""
        return credo.io.stgcmdline.paramStr(self.paramPath, self.paramRange[ii])

    def applyToModelGenerator(self, modelRun):
        """Creates a Python Generator for applying parameters to
        Apply the ii-th value in the attr:`.paramRange` to a particular
        :class:`~credo.modelrun.ModelRun`."""
        for paramVal in self.paramRange:
            modelRun.paramOverrides[self.paramPath] = paramVal
            yield modelRun
    
    def valLen(self):
        """Returns the length of the list of parameter values to vary
        specified in :attr:`.paramRange`."""
        return len(self.paramRange)
    
    def valStr(self, ii):
        """Return a string version of the ii-th parameter value."""
        paramVal = self.paramRange[ii]
        if type(paramVal) == float:
            valStr = "%g" % paramVal
        else:
            valStr = str(paramVal)
        return valStr

def getParamValuesIter(modelVariants, iterGen):
    """Given a list of model variants and an iterator generator function
    (eg itertools.izip or itertools.product) to use, generates
    a specific iterator that can be used on the modelVariants to obtain
    the actual param values."""
    paramIter = iterGen(*map(operator.attrgetter('paramRange'),
        modelVariants.itervalues()))
    return paramIter

def getParamValues(modelVariants, iterGen):
    """Shortcut to create a list of param values using
    :func:`.getParamValuesIter`"""
    paramIter = getParamValuesIter(modelVariants, iterGen)
    return list(paramIter)

def getVariantIndicesIter(modelVariants, iterGen):
    """Given a list of model variants and iterator generator function to use,
    generates an iterator of indices into the modelVariants list."""
    variantLens = [mv.valLen() for mv in modelVariants.itervalues()]
    indexIterator = iterGen(*map(range, variantLens))
    return indexIterator

def getVariantNameDicts(modelVariants, indicesIt):
    """Generates a list of dictionaries of parameters to be modified for each
    model run, given a list of :class:`.StgXMLVariant` and an iterator into
    them (e.g. generated by :func:`.getVariantIndicesIter`.
    """
    paramDicts = []
    modelVarList = modelVariants.values()
    for indexSet in indicesIt:
        newDict = {}
        for mvI, mvEntry in enumerate(modelVariants.iteritems()):
            mvName, modelVar = mvEntry
            paramVal = modelVar.paramRange[indexSet[mvI]]
            newDict[mvName] = paramVal
        paramDicts.append(newDict)
    return paramDicts    

def getVariantParamPathDicts(modelVariants, indicesIt):
    """Generates a list of dictionaries of parameters to be modified for each
    model run, given a list of :class:`.StgXMLVariant` and an iterator into
    them (e.g. generated by :func:`.getVariantIndicesIter`.
    """
    paramDicts = []
    for indexSet in indicesIt:
        newDict = {}
        for mvI, modelVar in enumerate(modelVariants.itervalues()):
            paramVal = modelVar.paramRange[indexSet[mvI]]
            newDict[modelVar.paramPath] = paramVal
        paramDicts.append(newDict)
    return paramDicts

def getVariantCmdLineOverrides(modelVariants, indicesIt):
    """Generates a list of strings to use at cmd line for each
    model run, given a list of :class:`.StgXMLVariant` and an iterator into
    them (e.g. generated by :func:`.getVariantIndicesIter`.
    """
    overrideCmdLines = []
    for indexSet in indicesIt:
        overStrs = [] 
        for mvI, modelVar in enumerate(modelVariants.itervalues()):
            overStrs.append(modelVar.cmdLineStr(indexSet[mvI]))
        overrideCmdLines.append(" ".join(overStrs))
    return overrideCmdLines

def getDefaultSubdir(modelVariants, paramIndices):
    subDirName = ""
    varTexts = []
    for mvI, mvEntry in enumerate(modelVariants.iteritems()):
        mvName, modelVar = mvEntry
        valStr = modelVar.valStr(paramIndices[mvI])
        varTexts.append("%s_%s" % (mvName, valStr))
    subDirName = "-".join(varTexts)
    return subDirName

def getDefaultSubdirs(modelVariants, indicesIt):
    subDirs = []
    for indexSet in indicesIt:
        subDirs.append(getDefaultSubdir(modelVariants, indexSet))
    return subDirs


class ModelSuite:
    '''A class for running a suite of Models (e.g. a group for profiling,
    or a System Test that requires multiple runs).
    
    The two main ways of using this class are:

    * Creating a :class:`.ModelSuite`, and then adding 
      :class:`~credo.modelrun.ModelRun` s to the suite using
      the :meth:`.addRun` method.
    * Creating a :class:`.ModelSuite`, and providing a
      :class:`~credo.modelrun.ModelRun` as a template, then adding 
      :class:`.StgXMLVariant` s to define what sort of parameter
      sweep should be performed. In this case, :meth:`.generateRuns()`
      needs to be called after all variants have been added.

    .. attribute:: outputPathBase

       The base path to use for saving model results under.

    .. attribute:: runs

       A list of :class:`~credo.modelrun.ModelRun` s to be run as part of the
       suite. See :meth:`.generateRuns` and :meth:`.addRun`.

    .. attribute:: runDescrips

       Short (eg 1 line) textual description for each ModelRun stored in the
       :attr:`.runs`.

    .. attribute:: runCustomOptSets

       Custom sets of options (to be used at the command line) associated 
       with each run in :attr:`.runs` (strings).
       
    .. attribute:: resultsList

       Initially `None`, after the suite has been run (using :meth:`.runAll`),
       saves a reference to all :class:`~credo.modelresult.ModelResult` s
       generated.

    .. attribute:: subOutputPathGenFunc
       
       If set, this function will be used to customise the model sub-path based
       on each modelRun.

    .. attribute:: templateMRun

       (Optional) setting this to an :class:`~credo.modelresult.ModelRun`
       means this run can be used as a "template" to add variants to, 
       and create a parameter sweep over this run.

       .. seealso: :meth:`.addVariant`, :meth:`generateRuns`, and
          :class:`.StgXMLVariant`.
    
    .. attribute:: modelVariants

       Set of :class:`.StgXMLVariant` s to apply to the template run in
       order to auto-generate a suite to vary certain parameters. See
       :attr:`.templateMRun` for more.

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
        """Add a model run to the list of those to be run.

        :param modelRun: A :class:`~credo.modelrun.ModelRun` to be added.
        :keyword runDescrip: An (optional) string describing the run.
        :keyword runCustomOpts: (optional) string of any custom options
          that should be passed through to StGermain, only for this run.
        :returns: the index of the newly added run in the modelRun list."""
        if not isinstance( modelRun, mrun.ModelRun ):
            raise TypeError("Error, given run not an instance of a"\
                " ModelRun" % runI)
        self.runs.append(modelRun)
        self.runDescrips.append(runDescrip)
        self.runCustomOptSets.append(runCustomOpts)
        # Return the index of the newly added run.
        return len(self.runs) - 1

    def cleanAllOutputPaths(self):
        '''Remove all files in each model's output path. Useful to get rid of
        results still there from previous jobs. Doesn't delete sub-directories,
        in case they are other model runs' results that should be ignored.'''
        startDir = os.getcwd()
        for modelRun in self.runs:
            os.chdir(modelRun.basePath)
            for filePath in glob.glob(os.path.join(modelRun.outputPath,"*")):
                if os.path.isfile(filePath):
                    os.unlink(filePath)
            os.chdir(startDir)

    def cleanAllLogFiles(self):
        """Remove all stdout and stderr files from each ModelRun's designated
        output and log paths."""
        startDir = os.getcwd()
        for modelRun in self.runs:
            os.chdir(modelRun.basePath)
            logFiles = [modelRun.getStdOutFilename(),
                modelRun.getStdErrFilename()]
            for fname in logFiles:
                if os.path.isfile(fname):
                    os.unlink(fname)
            os.chdir(startDir)

    def addVariant(self, name, modelVariant):
        """Add a :class:`.StgXMLVariant` to the list to be applied to a
        template run. See :attr:`.modelVariants`."""
        self.modelVariants[name] = modelVariant

    def generateRuns(self, iterGen=product):        
        """When using a template modelRun, will generate runs for the suite
        based on it. The generated runs are saved to 
        the :attr:`.runs` attribute ready to be run using :meth:`.runAll`.
        
        This requires that there are one or more :class:`.StgXMLVariant`
        recorded on the class already.

        :param iterGen: this determines what iterator strategy should be
          used to generate the runs. Defaults to a product, but a simple
          "zip" style can be achieved using the itertools.izip iterator
          generating function.
          See the Python :mod:`itertools` module for more.
        """

        assert self.templateMRun

        # Strategy used below is instead of iterating directly over the 
        # parameters we are applying to each run, create indices into the
        # modelVariants lists to work out which to apply for each run.
        indexIterator = getVariantIndicesIter(self.modelVariants, iterGen)

        for paramIndices in indexIterator:
            # First create a copy of the template model run
            newMRun = copy.deepcopy(self.templateMRun)
            # Now, apply each variant to it as appropriate
            for varI, modelVar in enumerate(self.modelVariants.itervalues()):
                modelVar.applyToModel(newMRun, paramIndices[varI])

            if self.subOutputPathGenFunc:
                subPath = self.subOutputPathGenFunc(modelRun)
            else:
                subPath = self.getOutputSubPath(paramIndices)

            newMRun.outputPath = os.path.join(self.outputPathBase, subPath)  
            self.runs.append(newMRun)
            self.runDescrips.append(subPath)
            self.runCustomOptSets.append(None)

    def getOutputSubPath(self, paramIndices):
        """Generate the standard output directory for a run with given
        paramIndices into the :attr:`.modelVariants` to be applied."""
        subPath = getDefaultSubdir(self.modelVariants, paramIndices)
        return subPath

    def writeAllModelRunXMLs(self):
        """Save an XML record of each ModelRun currently in :attr:`.runs`."""
        for runI, modelRun in enumerate(self.runs):
            modelRun.writeInfoXML()

    def writeAllModelResultXMLs(self):
        """Save an XML record of each ModelResult currently in
        :attr:`.resultsList`."""
        for runI, mResult in enumerate(self.resultsList):
            mResult.writeRecordXML()
            
    # TODO: here perhaps would be where we have tools to generate stats/plots
    # of various properties of the suite, e.g. memory usage? Or should
    # this be a capability of some sort of uber-results list?

def writeInputsOutputsToCSV(mSuite, iterGen, observablesDict, fname):
    """Write a CSV file, containing all the ModelVariants defined for a 
    ModelSuite, and also all the observables in the observablesDict.

    :param observablesDict: a dictionary of 'observables', each entry in
      the form 'obsName':[obsVals for each run], e.g. "vrms":[0.6, 0.8, 0.9].
    :param fname: file name of the CSV file to create, inside the model
      suite's base output path.
    
    .. note:: Could be a function on the ModelSuite?
    """  
    target = open(os.path.join(mSuite.outputPathBase, fname), "w" )
    wtr = csv.writer(target)
    wtr.writerow(mSuite.modelVariants.keys()+observablesDict.keys())
    indexIt = getVariantIndicesIter(mSuite.modelVariants, iterGen)
    varDicts = getVariantNameDicts(mSuite.modelVariants, indexIt)
    for varDict, observs in zip(varDicts, zip(*observablesDict.itervalues())):
        wtr.writerow(varDict.values()+list(observs))
    target.close()

def getModelResultsArray(baseName, baseDir):
    """Post-processing: given a base model name and base output directory,
    search this directory for model results, and read into a list of
    :class:`~credo.modelresult.ModelResult` . 

    .. note:: Needs more checking added.
    """
    modelResults = []
    for fName in os.listdir(baseDir):
        fullPath = os.path.join(baseDir, fName)
        if os.path.isdir(os.path.join(baseDir, fName)):
            dirName = fName
            modelResults.append(
                # TODO: Simtime of 0 is a hack here.
                mres.ModelResult("%s-%s" % (baseName, dirName), fullPath, 0))
                # TODO: other job meta info if possible?
    return modelResults
