#!/usr/bin/env python

import getopt
import sys
import os

from uwa.modelrun import SuiteRunner
from uwa.systest import AnalyticTest

anTest = AnalyticTest( xmlFiles, outputPath, cmdLineOpts )

# Generate a suite of models to run as part of the test
mSuite = anTest.genSuite()

jobRunner = mpich2JobRunner()
suiteResults = mSuite.runSuite( jobRunner )
suiteResults.writeAllXMLs(anTest.outputPath)

testResult = anTest.getStatus(suiteResults)
anTest.writeXML(anTest.outputPath)

#==================

# Multi-res ....

from uwa.systest import AnalyticTest, MultiResTest
import uwa.analysis

sysTest = AnalyticMultiResCvgTest(xmlFiles, outputPath, cmdLineOpts, resSet,
    uwa.analysis.DefaultMultiResChecker())

# Then as follows for normal tests...
