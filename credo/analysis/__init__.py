
"""
The CREDO Analysis module is to group together tools for analysis of the
results of Underworld models: for use in both individual user scripts, and as
part of system testing (see :mod:`credo.systest`).

For analysis operations that are designed to be added to
:class:`~credo.modelrun.ModelRun` instances, and possibly used as part of
system testing, these should inherit from
:class:`~credo.analysis.api.AnalysisOperation`.
There are also several functions
that can be used to access and post-process Underworld results in a more direct
manner, using the :mod:`credo.io` interface.

For examples of using the analysis operations with models, see the 
:ref:`credo-examples-analysis` section of the documentation.
"""

from credo.analysis.api import *
