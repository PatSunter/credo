.. _uwa-examples:

**************************
Examples of how to use UWA
**************************

Running one or more standard system tests in the repository
===========================================================

This is a fairly simple use-case, for those who are used to already running
system tests in stgUnderworld. UWA provides a similar top-level interface to the
previous SYS scripts system.

To start off with, make sure the necessary environment variables necessary to
run UWA have been set up, as detailed in :ref:`environment_setup`.

Then check out one of the test suite files in a SysTest directory within the
code. We'll show in this example StgFEM/SysTest/RegressionTests/testAll-new.py:

.. include:: ../../StgFEM/SysTest/RegressionTests/testAll-new.py
   :literal:

This Python script uses UWA to run 3 system tests, and process their results. To
see it in practice, cd to that directory and then run the script (since it's set
as executable, you don't need to invoke Python explicitly). You should see
output starting with::

  psunter@auscope-02:~/AuScopeCodes/stgUnderworldE-uwaDev-work/StgFEM/SysTest/RegressionTests$ ./testAll-new.py 
  Running System test 0, with name 'Multigrid-restartTest':
  Writing pre-test info to XML
  Running the 2 modelRuns specified in the suite
  Doing run 1/2 (index 0), of name 'Multigrid-restartTest-initial':
  ModelRun description: "Do the initial full run and checkpoint solutions."
  Generating analysis XML:

and finishing with::

  --------------------------------------------------------------------------------
  UWA System Tests results summary:
  Ran 3 system tests, with 2 passes, 1 fails, and 0 errors
  Failures were:
   CosineHillRotateBC-analyticTest: At least one Field not within tolerance of analytic soln.
  --------------------------------------------------------------------------------

(Note that the failure is deliberate in the testing stages).

The following sections will explain how the file is set up, and show what the different sections do.

Importing UWA and creating a testRunner object
----------------------------------------------

To explain the first few lines of the script, as shown below::

  #!/usr/bin/env python
  from uwa.systest import *

  testRunner = SysTestRunner()

The first denotes the file as an executable script, using Python.

The next imports everything directly under the uwa.systest package for use in
the rest of the Python script - this is a convenience since all the objects
we'll need for the rest of the script, such as various types of System
test classes, are contained here.

The next line creates a SysTestRunner object to use for managing a test suite,
and assigns it to the name 'testRunner'.

Note that the SysTestRunner object definition was one of those we imported
with the preceding *import* statement. Currently the SysTestRunner takes no
options, in future versions we
expect you'll be able to set paramaters or configure in more detail how the
tests should be run.  

Adding system tests to the suite, and configuring them
------------------------------------------------------

Let's look at the next few lines, which declare what tests to run, and add them
to the test suite::

  testRunner.addStdTest(RestartTest, ["Multigrid.xml"],
      paramOverrides={"maxZ":2.5})
  testRunner.addStdTest(ReferenceTest, ["Multigrid.xml"])
  testRunner.addStdTest(AnalyticTest, ["CosineHillRotateBC.xml"],
      fieldTols={'TemperatureField':1e-8})

Each line is invoking the *addStdTest* method of the SysTestRunner object, to
add a system test of a particular type to the suite.

The addStdTest method uses a special shorthand to add tests to the suite, to
save some of the work from the uses in this high-level interface. It's arguments
are:

* Test class: the class of test you're adding. Generally this should be one of
  the standard set imported above, i.e. RestartTest, ReferenceTest,
  AnalyticTest, or AnalyticMultiResTest.
* XML file name(s): list of XML files that make up the model to be used in the
  test. If in the common case this is just one top-level XML file, a single
  string instead of a list is ok.
* Any over-riding options you wish to pass to the test.

So looking at the simplest case first, we can see the 2nd test added to the
suite of our example::

  testRunner.addStdTest(ReferenceTest, ["Multigrid.xml"])

... means that a ReferenceTest (test against a reference solution) is being
added, for the model contained in Multigrid.xml, with no special options.

In the case of over-riding parameters to the tests, there are 2 main categories:

#. Passing parameters that customise the model itself (paramOverrides)
#. Passing parameters that modify the nature of the test.

Let's look at an example of the first of these categories::

  testRunner.addStdTest(RestartTest, ["Multigrid.xml"],
      paramOverrides={"maxZ":2.5})

... this line means that a RestartTest on the Multigrid.xml model is being added
to the suite, with the model being modified by over-riding the "maxZ" parameter
from whatever is specified in the XML file, to 2.5 .

Here, the paramOverrides option is a dictionary of overrides to perform exactly
the same as described in the section for running a single analysis model through
UWA below.

Let's now look at a case where parameters that over-ride default properties of
how the test is applied are specified::

  testRunner.addStdTest(AnalyticTest, ["CosineHillRotateBC.xml"],
      fieldTols={'TemperatureField':1e-8})

Here, we're creating an AnalyticTest (compare against analytic solution), for
the CosineHillRotateBC.xml model. Additionally, this test is instructed to use a
tolerance of 1e-8 when testing the TemperatureField generated by the model
against the analytic solution, rather than the default value.

There are several other options you can use to over-ride the default behaviour
of system tests, please refer to the API section on System Tests for more. The
principle is the same for all of these regarding SysTestRunner suites though:
just specify the options as you would to the constructor of an individual
SystemTest, and they will be passed through by the SysTestRunner.

.. TODO: would be good if some of this was in the API direct docos. And
   hyperlinking in to them

Getting the testRunner to run all tests
---------------------------------------

Finally, in the test script we need to call the SysTestRunner to run all the
system tests that've been associated with it::

  testRunner.runAll()

Which is what will actually trigger the running of the tests, and produce a
report of what happened both to the terminal, and in XML files.

Alternative: Running a single test from the command-line
--------------------------------------------------------

Alternatively to the above, scripts have been provided to allow you to run a
single system test from the command line prompt, just as you could with the SYS
scripts.

To do this, the relevant scripts are as follows:

=============================== =========================
Script Name                     Sys Test class it invokes
=============================== =========================
uwa-referenceTest.py            ReferenceTest
uwa-restartTest.py              RestartTest
uwa-analyticTest.py             AnalyticTest
uwa-analyticTestMultiResCvg.py  AnalyticMultiResTest
=============================== =========================

So for example, to run a RestartTest on the Multigrid.xml model, type::

  uwa-restartTest.py Multigrid.xml

... which will run the test.

.. TODO: include output

Running and configuring Scientific Benchmark Tests
==================================================

The Sci Benchmark testing interface for UWA is still being developed, but
essentially requires the user to write a Python script to configure and run
a particular benchmark. This interface was chosen since benchmarks generally
require more detailed specification and configuration than standard system
tests.

The one example benchmark so far is testing a Rayleigh Taylor model can perform
as required by the Van Keken benchmark:

.. include:: ../../Underworld/InputFiles/uwa-rayTayBenchmark.py
   :literal:

As the code shows, once you set up a SciBenchmarkTest, you need to then add
TestComponents that check that the model to be run actually passes some
benchmark conditions. In this case, we're checking that the Vrms output into the
FrequentOutput.txt each timestep has a maximum value within a specified range,
within a specified time range.

Doing Model analysis with UWA
=============================


