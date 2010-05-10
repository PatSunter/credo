#!/usr/bin/env python

import getopt
import sys
import os

#from uwa.modelrun import SuiteRunner
from uwa.systest.analyticMultiRes import AnalyticMultiResTest

# Temporary input processing
opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])

#For now just copy all args as input files
inputFiles = args
modelName, ext = os.path.splitext(args[0])
modelName += "-analyticTestMultiRes"
outputPath = 'output/'+modelName

resSet = [(10,10),(20,20),(30,30)]
resConvChecker = None

anTest = AnalyticMultiResTest(inputFiles, outputPath, resSet, nproc=1)

# Generate a suite of models to run as part of the test
mSuite = anTest.genSuite()

#jobRunner = mpich2JobRunner()
mSuite.writeAllModelRunXMLs()
suiteResults = mSuite.runAll() # pass in jobRunner
testResult = anTest.getStatus(suiteResults)
mSuite.writeAllModelResultXMLs()

print "Test result was %s" % testResult
anTest.writeInfoXML()
