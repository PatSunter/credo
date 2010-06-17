#!/usr/bin/env python

import getopt
import sys
import os

#from uwa.modelrun import SuiteRunner
from uwa.systest.reference import ReferenceTest

# Temporary input processing
opts, args = getopt.getopt(sys.argv[1:], "hs", ["help","setup"])

# Temp process options
setupMode = False
for optTuple in opts:
    if optTuple[0] == "--setup":
        setupMode = True

#For now just copy all args as input files
inputFiles = args
modelName, ext = os.path.splitext(args[0])
modelName += "-referenceTest"
outputPath = 'output/'+modelName

refTest = ReferenceTest(inputFiles, outputPath, nproc=1)

if setupMode == True:
    print "Running in setup mode only:"
    refTest.setup()
    print "Setup completed, exiting."
    sys.exit()

refTest.writePreRunXML()

# Generate a suite of models to run as part of the test
mSuite = refTest.genSuite()

#jobRunner = mpich2JobRunner()
mSuite.writeAllModelRunXMLs()
suiteResults = mSuite.runAll() # pass in jobRunner
print "Checking test result:"
testResult = refTest.getStatus(suiteResults)
mSuite.writeAllModelResultXMLs()

print "Test result was %s" % testResult
savedFile = refTest.updateXMLWithResult(suiteResults)
print "(Wrote record of result to %s)" % (savedFile)
