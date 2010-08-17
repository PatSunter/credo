"""
This module contains the System Testing functionality of CREDO. 

Working at a higher-level than the :mod:`credo.modelrun` and :mod:`credo.analysis`
modules, it is able to use their capabilities to run system tests of 
StGermain-based codes, and communicate and record the results.

From a user perspective, doing an::

  from credo.systest import *

Should allow key functionality to be accessed: e.g. the 
:class:`credo.systest.systestrunner.SysTestRunner` class, and standard system
tests such as Analytic, Restart and Reference.

Examples of how to use this module are provided in the CREDO documentation,
see :ref:`credo-examples-systesting`.
"""

from credo.systest.api import *

from credo.systest.systestrunner import SysTestRunner
# Import all the standard tests so they're available
from credo.systest.restart import RestartTest
from credo.systest.analytic import AnalyticTest
from credo.systest.analyticMultiRes import AnalyticMultiResTest
from credo.systest.reference import ReferenceTest
# Import the benchmark
from credo.systest.scibenchmark import SciBenchmarkTest
