#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.abspath("uwa"))
from uwa.systest import *

os.environ['STG_BASEDIR'] = os.getcwd()

lowResTests = [
    "Underworld.SysTest.RegressionTests.testAll_lowres"]

cvgTests = [
    "StgFEM.SysTest.PerformanceTests.testAll",
    "PICellerator.SysTest.PerformanceTests.testAll",
    "Underworld.SysTest.PerformanceTests.testAll"]

suites = []
for modName in cvgTests:
    print "Importing suite for %s:" % modName
    #The two-stage import process is required, see the Python doc page on
    # __import__ for more.
    __import__(modName)
    mod = sys.modules[modName]
    suites.append(mod.suite())

if __name__ == "__main__":
    testRunner = SysTestRunner()
    testRunner.runSuites(suites)
