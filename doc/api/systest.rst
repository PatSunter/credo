***********************************
SysTest API
***********************************

.. automodule:: credo.systest

:mod:`credo.systest.api`
==========================

.. inheritance-diagram:: credo.systest.api

.. automodule:: credo.systest.api
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.systestrunner`
==================================

.. inheritance-diagram:: credo.systest.systestrunner

.. automodule:: credo.systest.systestrunner
   :members:
   :undoc-members:
   :show-inheritance:

Core System Test class implementations
======================================

CREDO provides a set of core :class:`~credo.systest.api.SysTest` instantations,
which supercede the functionality of the pre-existing test scripts system,
which are documented below.

The user can always add to this list, by defining new SysTest classes to use.

The most flexible of the set is the
:class:`~credo.systest.scibenchmark.SciBenchmarkTest`, but this requires the
most customisation (i.e. generally can't be created in the short-hand form
of the other tests using the sysTestRunner's
:meth:`~credo.systest.systestrunner.SysTestRunner.addStdTest` method).

.. inheritance-diagram:: credo.systest.analytic
    credo.systest.restart credo.systest.reference 
    credo.systest.analyticMultiRes credo.systest.highResReference
    credo.systest.scibenchmark

depending on whether you have the Python Imaging Library (PIL) installed,
you can also use the :class:`credo.systest.imageReference.ImageReferenceTest`
system test.

:mod:`credo.systest.analytic`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.analytic
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.reference`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.reference
   :members:
   :undoc-members:

:mod:`credo.systest.restart`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.restart
   :members:
   :undoc-members:

:mod:`credo.systest.analyticMultiRes`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.analyticMultiRes
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.imageReference`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.imageReference
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.scibenchmark`
=================================

.. automodule:: credo.systest.scibenchmark
   :members:
   :undoc-members:
   :show-inheritance:

Core TestComponent implementations
==================================

.. inheritance-diagram:: credo.systest.fieldWithinTolTest
    credo.systest.fieldCvgWithScaleTest credo.systest.outputWithinRangeTest

:mod:`credo.systest.fieldWithinTolTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.fieldWithinTolTest
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.fieldCvgWithScaleTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.fieldCvgWithScaleTest
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.outputWithinRangeTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.outputWithinRangeTest
   :members:
   :undoc-members:
   :show-inheritance:

:mod:`credo.systest.imageCompTest`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: credo.systest.imageCompTest
   :members:
   :undoc-members:
   :show-inheritance:
