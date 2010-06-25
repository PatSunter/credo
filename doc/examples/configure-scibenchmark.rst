.. _uwa-examples-configure-scibenchmark:

Running and configuring Scientific Benchmark Tests
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Sci Benchmark testing interface for UWA is still being developed, but
essentially requires the user to write a Python script to configure and run
a particular benchmark. This interface was chosen since benchmarks generally
require more detailed specification and configuration than standard system
tests.

The one example benchmark so far is testing a Rayleigh Taylor model can perform
as required by the Van Keken benchmark:

.. include:: ../../../Underworld/InputFiles/uwa-rayTayBenchmark.py
   :literal:

As the code shows, once you set up a SciBenchmarkTest, you need to then add
TestComponents that check that the model to be run actually passes some
benchmark conditions. In this case, we're checking that the Vrms output into the
FrequentOutput.txt each timestep has a maximum value within a specified range,
within a specified time range.

