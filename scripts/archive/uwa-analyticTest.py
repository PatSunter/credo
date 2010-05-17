#!/usr/bin/env python

import getopt
import sys
import os

import uwa
from uwa import modelrun as mrun
from uwa import modelresult as mres
import uwa.analysis

defaultFieldTol = 3e-2

#process input args

#modelName, options = uwa.processInput(argv, argc)
# Keep allowing options file for now in default scripts:- though for a 
# custom script, user could easily write their own
#uwa.processOptionsFile(options, "./options.dat")

# This is where we create the key data structure, the mRun.
# It will be a key data structure storing info about the directories
# used, timestep, fields checkpointed, and be used in APIs to access info.

opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])

#For now just copy all args as input files
inputFiles = args
modelName, ext = os.path.splitext(args[0])
modelName += "-analyticTest"
# Do the following live on an options struct?
outputPath = 'output/'+modelName
nproc=1

mRun = mrun.ModelRun(modelName, inputFiles, outputPath, nproc=nproc)

# For analytic test, assume the user has specified what fields to analyse
# in the XML
# (In the background this will generate the flattened XML for the model)
fTests = mRun.analysis['fieldTests']
fTests.readFromStgXML(mRun.modelInputFiles)
# Set all field tolerances at once. Of course, should allow this to
# be over-ridden
mRun.analysis['fieldTests'].setAllTols(defaultFieldTol)
customOpts = "--pluginData.appendToAnalysisFile=True"

mRun.writeInfoXML()
# This will generate an additional XML to require StGermain/Underworld
# to do any requested extra analysis (eg compare fields), and run for
# the appropriate number of timesteps etc. It is stored on the mRun
# as a param named 'analysisXML'
mRun.analysisXMLGen()

uwa.prepareOutputLogDirs(mRun.outputPath, mRun.logPath)
# This will run the model, and also save basic results (e.g. walltime)
results = mrun.runModel(mRun, customOpts)

# TODO: This step necessary since currently convergence files saved in
# directory of run, may be better handled within the runModel
uwa.moveConvergenceResults(os.getcwd(), mRun.outputPath)

results.fieldResults = fTests.testConvergence(mRun.outputPath)
results.fieldResults[0].plotCvgOverTime(path=mRun.outputPath)
mres.writeModelResultsXML(results, path=mRun.outputPath)

#Now do any required post-processing, depending on type of script
uwa.cleanupOutputLogDirs(mRun.outputPath, mRun.logPath)
