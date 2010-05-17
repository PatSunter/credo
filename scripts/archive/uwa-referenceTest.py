#!/usr/bin/env python

import getopt
import sys
import os

import uwa
from uwa.modelrun import ModelRun, SimParams
from uwa.analysis.fields import FieldTest

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
modelName += "-referenceTest"
# Do the following live on an options struct?
outputPath = 'output'+os.sep+modelName
expectedPath = 'expected'+os.sep+modelName
nproc=1

mRun = ModelRun(modelName, inputFiles, outputPath, nproc=nproc)

# TODO: responsibility of SystemTest class?
createReference = False
# For a reference test, these are standard fields to be tested.
standardFields = ['VelocityField','PressureField']
runSteps=10

if createReference:
    mRun.outputPath = expectedPath
    mRun.simParams = SimParams(nsteps=runSteps, cpevery=runSteps, dumpevery=0)
    mRun.cpFields = standardFields
else:
    mRun.simParams = SimParams(nsteps=runSteps, cpevery=0, dumpevery=0)
    fTests = mRun.analysis['fieldTests']
    fTests.testTimestep = runSteps
    fTests.useReference = True
    fTests.referencePath = expectedPath
    defFieldTol = 1e-2
    for fieldName in standardFields:
        fTests.add(FieldTest(fieldName, tol=defFieldTol))

mRun.writeInfoXML()

# This will generate an additional XML to require StGermain/Underworld to do
# any requested extra analysis (eg compare fields), and run for the
# appropriate number of timesteps etc.
mRun.analysisXMLGen()

uwa.prepareOutputLogDirs(mRun.outputPath, mRun.logPath)

# This will run the model, and also save basic results (e.g. walltime)
results = uwa.modelrun.runModel(mRun)

if not createReference:
    # TODO: This step necessary since currently convergence files saved
    # in directory of run may be better handled within the runModel
    uwa.moveConvergenceResults(os.getcwd(), mRun.outputPath)

    results.fieldResults = fTests.testConvergence(outputPath)

    uwa.modelresult.writeModelResultsXML(results, path=mRun.outputPath)

    #Now do any required post-processing, depending on type of script
    uwa.cleanupOutputLogDirs(mRun.outputPath, mRun.logPath)
