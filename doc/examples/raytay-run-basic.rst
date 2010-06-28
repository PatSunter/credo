.. _uwa-examples-raytay-run-basic:

Using UWA to run and analyse a Rayleigh-Taylor problem in Underworld
--------------------------------------------------------------------

This examples shows how to use UWA to run a simple single Underworld job, and
perform some basic post-processing on the results, such as getting relevant
values from the FrequentOutput.dat, and plotting observables of interest.

Setup
"""""

The script to run a Rayleigh Taylor model is as included below, currently in the
Underworld/InputFiles directory:

.. literalinclude:: ../../../Underworld/InputFiles/uwa-rayTayBasic.py
   :linenos:

The script above the `#-----------------` comment line is setting up and running
the model, and that below it is for doing some simple post-processing and
analysis of the result.

Essentially, what we are doing is setting up a ModelRun to run the
"RayleighTaylorBenchmark.xml" model, with some small customisations to some of
the parameters. We also specify to save information about the model run via the
:meth:`~uwa.modelrun.ModelRun.writeInfoXML` method and
:meth:`~uwa.modelresult.writeModelResultsXML` function.

.. seealso:: Modules :mod:`uwa.modelrun` and :mod:`uwa.modelresult`

Looking at the post-processing in more detail:

.. literalinclude:: ../../../Underworld/InputFiles/uwa-rayTayBasic.py
   :language: python
   :lines: 20-

We first use the :meth:`~uwa.modelresult.ModelResult.readFrequentOutput()`
method to read the FrequentOutput.dat results into memory and make them
accessible through UWA, bound to a `freqOutput` attribute of the mRes object.
We are then able to use various methods of this 
:class:`uwa.io.stgfreq.FreqOutput` class to query the Frequent Output for
properties of interest - in this case the maximum value of the "Vrms" property,
the time this occurred. We also use the plotOverTime() method to plot and save a
graph of the value of Vrms over time in the model.

.. seealso:: The :class:`uwa.io.stgfreq.FreqOutput` class, especially the
   :meth:`~uwa.io.stgfreq.FreqOutput.plotOverTime` method.

Outputs
"""""""

Running this script at the terminal produces::

  Running model 'RayTay-basicBenchmark' with command 'mpirun -np 1 /home/psunter/AuScopeCodes/stgUnderworldE-uwaDev-work/build/bin/StGermain RayleighTaylorBenchmark.xml uwa-analysis.xml  --gravity=1 > logFile.txt' ...
  Model ran successfully.
  Maximum value of Vrms was 0.000365, at time 64

Where the last line is the result of our post-processing query.

.. _uwa-examples-raytay-run-basic-plot:

If you have Matplotlib installed, it will also produce a pop-up window showing
the graph of VRMS against time, something like that shown below:

.. image:: ./RayTayBasic/Vrms-timeSeries.png

In the script above you can see the output path requested for the model was
`./output/raytay-scibench-uwa-basic`.

.. _uwa-examples-raytay-run-basic-outputdir:

If you have a look at the contents of the directory, as well all of the
standard output that an Underworld run saves [#f1]_, you'll see
several things specific to UWA:

* An `uwa-analysis.xml` file, recording a summary StGermain format XML of
  over-rides or new components created to complete the required analysis
  specified in the UWA script;
* `ModelRun-RayTay-basicBenchmark.xml` and 
  `ModelResult-RayTay-basicBenchmark.xml` files, which keep a record of what
  UWA was asked to run and the result it produced
* `Vrms-timeSeries.png`, a saved copy of the image shown above [#f2]_.

The contents of the ModelRun and ModelResult XML files should look something
like the below:

.. literalinclude:: ./RayTayBasic/ModelRun-RayTay-basicBenchmark.xml

... and: 

.. literalinclude:: ./RayTayBasic/ModelResult-RayTay-basicBenchmark.xml

You will see that they save essential quantities about the run requested and the
result [#f3]_.  

.. rubric:: Footnotes

.. [#f1] such as FrequentOutput.dat, and a record of the flattened XML produced
   by the run as `input.xml`. For more on these, see the Underworld manual.
.. [#f2] Note it's possible not to save these images, by passing `save=False` as
   a keyword argument to the plotOverTime method 
   (see :meth:`~uwa.io.stgfreq.FreqOutput.plotOverTime`).
.. [#f3] Note: in future, we plan to provide the capability to read in a
   ModelResult.xml file into UWA, which will create a ModelResult object for 
   post-processing. However as yet this capability isn't included.
