"""
This module contains the System Testing functionality of UWA. 

Working at a higher-level than the :mod:`uwa.modelrun` and :mod:`uwa.analysis`
modules, it is able to use their capabilities to run system tests of 
StGermain-based codes, and communicate and record the results.

From a user perspective, doing an::

  from uwa.systest import *

Should allow key functionality to be accessed: e.g. the 
:class:`uwa.systest.systestrunner.SysTestRunner` class, and standard system
tests such as Analytic, Restart and Reference.

Examples of how to use this module are provided in the UWA documentation,
see :ref:`uwa-examples-systesting`.
"""

from uwa.systest.api import *

from uwa.systest.systestrunner import SysTestRunner
# Import all the standard tests so they're available
from uwa.systest.restart import RestartTest
from uwa.systest.analytic import AnalyticTest
from uwa.systest.analyticMultiRes import AnalyticMultiResTest
from uwa.systest.reference import ReferenceTest
# Import the benchmark
from uwa.systest.scibenchmark import SciBenchmarkTest
