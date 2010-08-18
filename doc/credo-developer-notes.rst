.. _credo-developer-notes:

****************************************
Notes for CREDO developers / maintainers
****************************************

Coding standards / style guides
===============================

On recommendation of the majority of Python tutorials out there, we are
following the standard Python style guide, at
http://www.python.org/dev/peps/pep-0008/.

Some of the notable things here are:

* Use *4 spaces* for indentation, instead of tabs (obviously crucial to be
  consistent about this in Python, since indenting whitespace is used to
  control blocks.
* Spaces around assignment symbols, =, but not between brackets and arguments.

Where we 'break' any of these rules in the package, we'll document this here.

Testing framework
=================

Currently, we use the Python
`Unittest <http://docs.python.org/library/unittest.html>`_ framework.
Tests are mainly organised per file (module), rather than per class.

It's important to write unit tests for all new classes and to maintain and
improve the suite for existing ones. Unittest is pretty easy to use and is well
documented.
