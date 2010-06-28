.. _uwa-examples:

**************************
Examples of how to use UWA
**************************

The sections below should help given an overview of how to use UWA, through
worked examples.

The :ref:`uwa-examples-systesting` section explains how to use UWA to run and
set-up the basic system tests of a StGermain code that supercede the previous
system testing scripts.

The :ref:`uwa-examples-analysis` section shows examples of how to configure
and run Underworld runs using UWA, and analyse/post-process the results.
This is for custom analysis, rather than for addition to the automated
testing system.

Finally the :ref:`uwa-examples-scibenchmarking` section shows the more complex
use-case of the code, where scientific benchmarks are set up:
generally requiring
both analysis-style set-up of models to run, while also using the system
testing features to allow automated regular running of this benchmark.

.. Note::
   UWA is designed in such a manner that it should be possible to readily
   convert analysis scripts into repeatable system tests, and after
   reading examples of all the sections above you should have a handle
   on how to go about this.

.. _uwa-examples-systesting:

Using UWA for System Testing of StGermain-based codes such as Underworld
========================================================================

.. toctree::

   examples/run-systest.rst

.. _uwa-examples-analysis:

Doing Model analysis with UWA
=============================

.. toctree::
   :maxdepth: 1

   examples/raytay-run-basic.rst
   examples/raytay-run-suite.rst

.. _uwa-examples-scibenchmarking:

Scientific Benchmarking using UWA
=================================

.. toctree::
   :maxdepth: 1

   examples/configure-scibenchmark.rst
