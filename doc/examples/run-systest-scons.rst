.. _uwa-examples-run-systest-scons:

Running a test target, or test suite, via the SCons build system
----------------------------------------------------------------

UWA is now integrated with the SCons build system, so for project such as
Underworld it is now possible to run UWA System tests via SCons.

For this to work, it requires test maintainers to follow the directions in
:ref:`uwa-examples-run-systest-direct-importingReqs`, but you can follow
the instructions below without knowing the internal contents of suites.

Running a project-defined multi-suite test target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you invoke the SCons help for a project using UWA in it's base directory,
e.g. stgUnderworld, by typing::

  scons --help

the full list of check 'targets' for a project
will be printed. UWA has been set up to also work with the 
`PCU (Parallel C-Unit) <https://www.mcc.monash.edu.au/pcu-doc/>`_
unit testing suite also used by StGermain codes, so
that some testing targets can run both unit and system tests.

For example, the "check-lowres" target has been set up to run low-resolution
system test suites, so you can invoke this target by running from the
stgUnderworld base directory::

  scons check-lowres 

which will invoke a series of system tests.

  .. note:: You no longer need to run "./scons", as UWA now prints a summary
     using the standard scons executable.
  
The output printed after running this command should start with something like
the following::

  scons: Reading SConscript files ...
  Mkdir("./testLogs")
  Copy("build/config.log", "config.log")
  Copy("build/config.cfg", "config.cfg")
  scons: done reading SConscript files.
  scons: Building targets ...
  runSuites(["testLogs/lowresSuiteSummary.xml"], ["Underworld/SysTest/RegressionTests/testAll_lowres.py"])
  Importing suite for Underworld.SysTest.RegressionTests.testAll_lowres:
  Running the following system test suites:
   Project 'Underworld', suite 'RegressionTests-lowres'
  --------------------------------------------------------------------------------
  Running System Test Suite for Project 'Underworld', named 'RegressionTests-lowres', containing 30 direct tests and 0 sub-suites:
  Running System test 1/30, with name 'Anisotropic-referenceTest-np1-lowres':
  Writing pre-test info to XML
  Running the 1 modelRuns specified in the suite
  Doing run 1/1 (index 0), of name 'Anisotropic-referenceTest-np1-lowres':
  ModelRun description: "Run the model, and check results against previously generated reference solution."
  Generating analysis XML:
  Running the Model (saving results in output/Anisotropic-referenceTest-np1-lowres):
  Running model 'Anisotropic-referenceTest-np1-lowres' with command 'mpirun -np 1 /home/psunter/AuScopeCodes/stgUnderworldE-uwaDev-work/build/bin/StGermain /home/psunter/AuScopeCodes/stgUnderworldE-uwaDev-work/Underworld/SysTest/RegressionTests/Anisotropic.xml uwa-analysis.xml  --elementResI=10 --elementResJ=10 --elementResK=10' ...
  Model ran successfully (output saved to path output/Anisotropic-referenceTest-np1-lowres, std out & std error to log.
  Doing post-run tidyup:
  Checking test result:
  Field comp 'VelocityField' error within tol 0.01 of reference solution for all runs.
  Field comp 'PressureField' error within tol 0.01 of reference solution for all runs.

  Test result was Pass

..and so on through a series of test suites, concluding with::

  --------------------------------------------------------------------------------
  UWA System Tests results summary, project 'Underworld', suite 'RegressionTests-lowres':
  Ran 30 system tests, with 29 passes, 1 fails, and 0 errors
  Failures were:
   CylinderRiseThermal-referenceTest-np2-lowres: A Field was not within tolerance of reference soln.
  --------------------------------------------------------------------------------
  --------------------------------------------------------------------------------
  UWA System Tests summary for all project suites ran:
  ------
  Project 'Underworld':
   Suite 'RegressionTests-lowres': 30 tests, 29/1/0 passes/fails/errors
  30 tests, 29/1/0 passes/fails/errors
  ------
  ALL Projects Total:  30 tests, 29/1/0 passes/fails/errors
  --------------------------------------------------------------------------------
  scons: done building targets.

This gives you a summary of the results of the system test suite run. For check
targets that run across multiple projects, the final summary will show the
totals sorted by project, for example::

  --------------------------------------------------------------------------------
  UWA System Tests summary for all project suites ran:
  ------
  Project 'StgFEM':
   Suite 'PerformanceTests': 3 tests, 3/0/0 passes/fails/errors
  3 tests, 3/0/0 passes/fails/errors
  ------
  Project 'PICellerator':
   Suite 'PerformanceTests': 3 tests, 3/0/0 passes/fails/errors
  3 tests, 3/0/0 passes/fails/errors
  ------
  Project 'Underworld':
   Suite 'PerformanceTests': 16 tests, 16/0/0 passes/fails/errors
  16 tests, 16/0/0 passes/fails/errors
  ------
  ALL Projects Total:  22 tests, 22/0/0 passes/fails/errors
  --------------------------------------------------------------------------------

The test commands will also save an XML file, for parsing by the likes of
Bitten, summarising the results of the test suite run. These are saved in the
"testLogs" subdirectory. For example, after running the lowres suite above, the
testLogs directory will contain a file `testLogs/lowresSuiteSummary.xml`.

Running a single test suite via SCons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of running a whole set of system test suites, you may wish to run 
just a single suite. Of course this can be done directly as described in
:ref:`uwa-examples-run-systest-direct`, but we also have the facility to
do this at the base directory of a project via SCons.

The syntax for running individual suites is based on the Python import name of
the suite. This is based on it's position in the file tree, but with "."
replacing directory separators.

For example on a Linux system, if you wanted to run the PICellerator convergence
test suite as part of the stgUnderworld project, the file is located in the
subdirectory `PICellerator/SysTest/PerformanceTests/testAll.py`. In Python
import syntax, this becomes `PICellerator.SysTest.PerformanceTests.testAll`.

So invoking the following at the command line::

  scons PICellerator.SysTest.PerformanceTests.testAll

will cause that suite to be run, printing output as follows:

.. literalinclude:: SConsOutput/scons-PICellerator-suite.txt

..and an XML log of the suite results will also be created in the `testLogs`
directory: in this case called
`testLogs/PICellerator.SysTest.PerformanceTests.testAll.xml`.

.. TODO: would be good to have a section here about how to add System tests to a
   project, via SCons. Or perhaps in the appendix.
