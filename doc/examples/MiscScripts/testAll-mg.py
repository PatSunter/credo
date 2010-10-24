#!/usr/bin/env python
import os
from credo.systest import *
from testAll import testSuite

# Customise to run each test with Multigrid options
mgSetup = "MultigridEXPERI.xml"
mgOpts = "options-uzawa-mg.opt"
for sysTest in testSuite.sysTests:
    sysTest.testName += "-mg"
    sysTest.outputPathBase += "-mg"
    sysTest.inputFiles.append(mgSetup)
    sysTest.solverOpts = mgOpts

if __name__ == "__main__":
    testRunner = SysTestRunner()
    testRunner.runSuite(testSuite)
