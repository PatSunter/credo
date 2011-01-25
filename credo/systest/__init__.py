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

"""
This module contains the System Testing functionality of CREDO. 

Working at a higher-level than the :mod:`credo.modelrun` and
:mod:`credo.analysis` modules, it is able to use their
capabilities to run system tests of scientific applications,
and communicate and record the results.

From a user perspective, doing an::

  from credo.systest import *

Should allow key functionality to be accessed: e.g. the 
:class:`credo.systest.systestrunner.SysTestRunner` class, and standard system
tests such as Analytic, Restart and Reference.

Examples of how to use this module are provided in the CREDO documentation,
see :ref:`credo-examples-systesting`.
"""

from credo.systest.api import *

from credo.systest.systestsuite import SysTestSuite
from credo.systest.systestrunner import SysTestRunner

# Import all the standard tests so they're available
from credo.systest.restart import RestartTest
from credo.systest.analytic import AnalyticTest
from credo.systest.analyticMultiRes import AnalyticMultiResTest
from credo.systest.reference import ReferenceTest
from credo.systest.highResReference import HighResReferenceTest
try:
    from credo.systest.imageReference import ImageReferenceTest
except ImportError:
    print "Warning, cannot import the ImageReferenceTest for"\
        " use since you don't have required libraries (PIL) installed."

# Import the benchmark test
from credo.systest.scibenchmark import SciBenchmarkTest

# import all test components here too so available for benchmark tests
from .fieldCvgWithScaleTest import FieldCvgWithScaleTest
from .fieldWithinTolTest import FieldWithinTolTest
from .imageCompTest import ImageCompTest
from .outputWithinRangeTest import OutputWithinRangeTest
