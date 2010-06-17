#!/usr/bin/env python

import getopt
import sys
import os

#from uwa.modelrun import SuiteRunner
from uwa.systest.analytic import AnalyticTest

# Temporary input processing
opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])

#For now just copy all args as input files
inputFiles = args
modelName, ext = os.path.splitext(args[0])
modelName += "-analyticTest"
outputPath = 'output/'+modelName

anTest = AnalyticTest(inputFiles, outputPath, nproc=1)
anTest.writePreRunXML()

# Generate a suite of models to run as part of the test
mSuite = anTest.genSuite()

#jobRunner = mpich2JobRunner()
mSuite.writeAllModelRunXMLs()
suiteResults = mSuite.runAll() # pass in jobRunner
testResult = anTest.getStatus(suiteResults)
mSuite.writeAllModelResultXMLs()

print "Test result was %s" % testResult
savedFile = anTest.updateXMLWithResult(suiteResults)
print "(Wrote record of result to %s)" % (savedFile)
