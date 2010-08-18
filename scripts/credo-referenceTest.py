#!/usr/bin/env python
##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA

import getopt
import sys
import os

#from credo.modelrun import SuiteRunner
from credo.systest.reference import ReferenceTest

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
