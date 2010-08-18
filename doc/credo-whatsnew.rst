.. _credo-whatsnew:

*******************
What's new in CREDO
*******************

This page summarises what's new in each CREDO version.

(See the files in the "changelogs" sub-directory of the CREDO distribution for
full ChangeLogs based on Mercurial commits.)

new in credo-0.1.1
==================

The main changes in this version were:

* Change from all tests being directly attached to a 
  :class:`~credo.systest.systestrunner.SysTestRunner` class, to ability
  to define :class:`~credo.systest.api.SysTestSuite` classes
  that could then be run by
  the SysTestRunner. This makes it possible to better control running of
  multiple suites, and also makes the interface closer to Python's
  Unittest module.

* Setting up of conventions so CREDO Suites can be both imported and run as
  part of a collection, or run directly. See
  :ref:`credo-examples-run-systest-direct-importingReqs`.

* Much better integration with SCons, so the user doesn't have to set up special
  environment variables if you just wish to run tests via SCons, and also are
  able to generate proper reports on the different suites that were run. See
  :ref:`credo-examples-run-systest-scons`.

* Several small but useful interface improvements when defining suites and 
  system tests, including:

  * the ability to define a suffix to append to the output directory
    of model runs and sys test suites.
  * The ability to define a solverOpts file to use for each run, that contains
    options to customise the PETSc solver.
  * Making sure the stdout and stderr logs of system tests and models are saved
    properly.
  * Checking that the input files specified for a model are defined correctly.  

* Improved the :mod:`credo.systest.fieldCvgWithScaleTest` module considerably, 
  to be more modular, and also better handle fields that don't have a
  convergence criterion specified. Default criterion were also added for
  common recovered fields (eg recovered Pressure).

* Created a new :mod:`credo.io.stgpath` module, which contains several useful
  path-manipulation utilities.

* Testing of CREDO: improved the unit tests of CREDO itself, so the majority of
  testing dirs now have a "testAll.py" script that runs all the other tests.
