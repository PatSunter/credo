.. _uwa-architecture:

*****************************************
Core UWA Architecture
*****************************************

.. Class diagrams, using matplotlib extensions

**UWA**'s core architecture for analysis is the ModelRun and ModelResult
hierarchy, shown below:

.. inheritance-diagram:: uwa.modelrun

.. inheritance-diagram:: uwa.modelresult

The *SystemTest* and *SysTestRunner* are the core API for running System tests.

.. inheritance-diagram:: uwa.systest.api

.. inheritance-diagram:: uwa.systest.systestrunner

Some actual examples of System tests are:

.. inheritance-diagram:: uwa.systest.api uwa.systest.analytic
    uwa.systest.restart uwa.systest.reference uwa.systest.analyticMultiRes
    :parts: 1


