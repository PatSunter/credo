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

# Generate a suite of models to run as part of the test
mSuite = anTest.genSuite()

#jobRunner = mpich2JobRunner()
suiteResults = mSuite.runAll() # pass in jobRunner
#suiteResults.writeAllXMLs(anTest.outputPath)

#testResult = anTest.getStatus(suiteResults)
#anTest.writeXML(anTest.outputPath)

#==================

# Multi-res ....

#from uwa.systest import AnalyticTest, MultiResTest
#import uwa.analysis

#sysTest = AnalyticMultiResCvgTest(xmlFiles, outputPath, cmdLineOpts, resSet,
#    uwa.analysis.DefaultMultiResChecker())

# Then as follows for normal tests...
