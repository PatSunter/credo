#!/usr/bin/env python

import getopt
import sys
import os

import uwa
from uwa.modelrun import ModelRun, SimParams
import uwa.analysis 
from uwa.analysis.fields import FieldTest

# This test will run a model for n timesteps, checkpointing half-way:- then
#  re-start the model mid way through, and check the values at the end are
#  the same.

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
nproc=1

# For a restart test, these are standard fields to be tested.
modelName+="-restartTest"
outputPath = 'output'+os.sep+modelName
standardFields = ['VelocityField','PressureField']
runSteps=20
assert runSteps % 2 == 0

print "Initial run:"
mRun = ModelRun(modelName+"-initial", inputFiles, outputPath, nproc=nproc)
initialOutputPath = outputPath+os.sep+"initial"
mRun.outputPath = initialOutputPath
mRun.simParams = SimParams(nsteps=runSteps, cpevery=runSteps/2, dumpevery=0)
mRun.cpFields = standardFields

mRun.writeModelRunXML(mRun)
uwa.prepareOutputLogDirs(mRun.outputPath, mRun.logPath)
# This will run the model, and also save basic results (e.g. walltime)
mRun.analysisXMLGen(mRun)
results = uwa.modelrun.runModel(mRun)
uwa.modelresult.writeModelResultsXML(results, path=mRun.outputPath)

print "Restart run:"
mRun.name = modelName+"-restart"
mRun.outputPath = outputPath+os.sep+"restart"
mRun.cpReadPath = initialOutputPath
# Note we could modify existing SimParams rather than create new, but below is
# probably easier
mRun.simParams = SimParams(nsteps=runSteps/2, cpevery=0, dumpevery=0, \
    restartstep=runSteps/2)
fTests = mRun.analysis['fieldTests']
fTests.testTimestep = runSteps
fTests.useReference = True
fTests.referencePath = initialOutputPath
defFieldTol = 1e-5
for fieldName in standardFields:
    fTests.add(FieldTest(fieldName, tol=defFieldTol))

uwa.writeModelRunXML(mRun)
mRun.analysisXML = uwa.modelrun.analysisXMLGen(mRun)
uwa.prepareOutputLogDirs(mRun.outputPath, mRun.logPath)
# This will run the model, and also save basic results (e.g. walltime)
results = uwa.modelrun.runModel(mRun)

print "Processing results"

# TODO: This step necessary since currently convergence files saved
# in directory of run may be better handled within the runModel
uwa.moveConvergenceResults(os.getcwd(), mRun.outputPath)
results.fieldResults = fTests.testConvergence(mRun.outputPath)

uwa.modelresult.writeModelResultsXML(results, path=mRun.outputPath)

#Now do any required post-processing, depending on type of script
uwa.cleanupOutputLogDirs(mRun.outputPath, mRun.logPath)
