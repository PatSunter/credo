#!/usr/bin/env python

import getopt
import sys
import os

#from uwa.modelrun import SuiteRunner
from uwa.systest.restart import RestartTest

# Temporary input processing
opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])

#For now just copy all args as input files
inputFiles = args
modelName, ext = os.path.splitext(args[0])
modelName += "-restartTest"
outputPath = 'output/'+modelName

restartTest = RestartTest(inputFiles, outputPath, nproc=1)
restartTest.writePreRunXML()

# Generate a suite of models to run as part of the test
mSuite = restartTest.genSuite()

#jobRunner = mpich2JobRunner()
mSuite.writeAllModelRunXMLs()
suiteResults = mSuite.runAll() # pass in jobRunner
print "Checking test result:"
testResult = restartTest.getStatus(suiteResults)
mSuite.writeAllModelResultXMLs()

print "Test result was %s" % testResult
savedFile = restartTest.updateXMLWithResult(suiteResults)
print "(Wrote record of result to %s)" % (savedFile)
