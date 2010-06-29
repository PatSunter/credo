***********************************
UWA SysTest API
***********************************

.. automodule:: uwa.systest

:mod:`uwa.systest.api`
==========================

.. inheritance-diagram:: uwa.systest.api

.. automodule:: uwa.systest.api
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`uwa.systest.systestrunner`
================================

.. inheritance-diagram:: uwa.systest.systestrunner

.. automodule:: uwa.systest.systestrunner
   :members:
   :undoc-members:
   :show-inheritance:

Core System Test class implementations
======================================

UWA provides a set of core :class:`~uwa.systest.api.SysTest` instantations,
which supercede the functionality of the pre-existing test scripts system,
which are documented below.

The user can always add to this list, by defining new SysTest classes to use.

The most flexible of the set is the
:class:`~uwa.systest.scibenchmark.SciBenchmarkTest`, but this requires the
most customisation (i.e. generally can't be created in the short-hand form
of the other tests using the sysTestRunner's
:meth:`~uwa.systest.systestrunner.SysTestRunner.addStdTest` method).

.. inheritance-diagram:: uwa.systest.analytic
    uwa.systest.restart uwa.systest.reference uwa.systest.analyticMultiRes
    uwa.systest.scibenchmark

:mod:`uwa.systest.analytic`
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.analytic
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`uwa.systest.reference`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.reference
   :members:
   :undoc-members:

:mod:`uwa.systest.restart`
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.restart
   :members:
   :undoc-members:

:mod:`uwa.systest.analyticMultiRes`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.analyticMultiRes
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`uwa.systest.scibenchmark`
===============================

.. automodule:: uwa.systest.scibenchmark
   :members:
   :undoc-members:
   :show-inheritance:

Core TestComponent implementations
==================================

.. inheritance-diagram:: uwa.systest.fieldWithinTolTest
    uwa.systest.fieldCvgWithScaleTest uwa.systest.outputWithinRangeTest

:mod:`uwa.systest.fieldWithinTolTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.fieldWithinTolTest
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`uwa.systest.fieldCvgWithScaleTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.fieldCvgWithScaleTest
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`uwa.systest.outputWithinRangeTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: uwa.systest.outputWithinRangeTest
   :members:
   :undoc-members:
   :show-inheritance:

