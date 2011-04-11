
Provenance info
===============

* use the standard "Platform" module to harvest basic info about the
  platform used (eg architecture)
  http://docs.python.org/library/platform.html

Performance measurement
=======================

* Simple cross-platform timers:
  http://coreygoldberg.blogspot.com/2009/12/python-accurate-cross-platform-timers.html
* Note we can record the process ID in subprocess, using pid
  http://docs.python.org/library/subprocess.html

While processes are running:

* (Unix only, maybe not Mac): 
* Use 'psutil', BSD-licenced code. Is cross-platform, works on 2.4 - 3. See:

  * http://code.google.com/p/psutil/
  * http://pypi.python.org/pypi/psutil

* So most likely:

  * Just use basic timing by defualt
  * Query memory max etc using process module.
  * Write interfaces to harvest better info out of PETSc.

More powerful HPC-oriented tools:

 * Simple way to get cores info on Unix: http://phacker.org/2010/09/07/find-out-number-of-cores-cpus-for-a-linux-system/
 * HWLOC, produces pretty pics: http://www.open-mpi.org/projects/hwloc/
 * PADB, for parallel job inspection: http://padb.pittman.org.uk/
   (Eg could display some cool info on a job as it progresses)
 * SIGAR, http://support.hyperic.com/display/SIGAR/Home
 * ClusterNumbers, http://sourceforge.net/projects/cluster-numbers/
   
   * Written direct in Python
   * Specifically for running ranges of benchmarks, and comparing/reporting.
   * (May be worth examining for architecture information)

General:

* http://stackoverflow.com/questions/276052/how-to-get-current-cpu-and-ram-usage-in-python
* http://phacker.org/ (A nice page for using Python in Computational settings)
* http://matt.eifelle.com/2008/10/16/monitoring-cpu-usage-in-multithreaded-applications/ (creates nice graphs)
* http://stackoverflow.com/questions/3830658/check-memory-usage-of-subprocess-in-python
* http://www.vrplumber.com/programming/runsnakerun/
* http://stackoverflow.com/questions/1777556/alternatives-to-gprof/1779343#1779343

Log/Notes
=========

7/4/2011:

* Have now got "platform" info being logged to XML
* And included in PDF/RST reports
* Also showing CPU times in reports
  (The latter needs to be refactored, as part of some sort of standard
   reporting/plotting API in CREDO, that can then be used in a much more
   modular way).

TODO next:

* BUG: fix the jobMetaInfo writing to XML, so that hte MPI part isn't
   separated from the parent class part (need to think about XML design here)
* Add an API for saving performance info to the ModelResult JobMetaInfo;
* Really, the jobMetaInfo should be saved into the modelResult
  * And separate the jobMetaInfo from necessary "jobHandle" to be passed
    around to store MPI, PBS relevant stuff.
* Investigate best way to save time and memory usage here...

 * Use the relevant plugins in StGermain and parse freq output? (eg CPU_Time)
 * Just do a simple implementation and use the "time" function?
 * Or one of the more advanced methods used above?


