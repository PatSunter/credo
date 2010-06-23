.. _uwa-intro:

*****************************************
Introduction to UWA (UnderWorld Analysis)
*****************************************

.. An introductory document about UWA.

**UWA** (UnderWorld Analysis) is a Python toolkit for system testing,
benchmarking and analysis of Modelling tools based on the StGermain
framework, such as *Underworld*.

It is distributed with the *stgUnderworld* open source framework, but in future
it's planned that it will be able to be obtained, installed and run
independently.

Core design goals
=================

UWA's core design goals are to:

* Support the effective development, inquiry and maintenance of a suite
  of benchmarks that test the scientific features, numerical accuracy, and
  computational performance of StGermain-based codes.
* Significantly enhance the ease and effectiveness of performing scientific
  analysis of the results of StGermain modelling applications.

Both these tasks are possible using a combination of command lines and custom
3rd party tools, both proprietary and open source - but the goal of UWA is to
provide an integrated system that makes doing both of them to a high level
much easier and clearer - and also in a readily repeatable manner so that
the status of a code as it evolves can be readily checked (e.g. as part of
a continuous integration system).

To meet these goals, we chose the *Python* scripting and programming language,
explained more in the :ref:`uwa-why_python` section below.

.. Would be good to footnote some stuff in the paragraph above.


How UWA fits into the workflow of using the Underworld modelling code
=====================================================================


.. image:: _static/UWAnalysis-detail.*
   :scale: 70 %


Benchmarking of Underworld and other StGermain applications
===========================================================

..  (Harvest from the specification, and Bec's paper). And also some
  examples of the Wiki pages.

There has long been an interest in a more systematic way of testing both
the software performance, and scientific/numerical reliability of the
StgUnderworld code – for example the issue was explored in Rebecca
Farrington's paper presented at the APAC05 conference.

.. TODO Ref above

The benefits of getting such a system operational would be as follows:

* A clear and up-to-date record of the performance and reliability of the
  code to present to scientists interested in using it or comparing it
  to similar codes. The chosen benchmarks would be of a “scope” of much
  more interest to modellers and scientists than the detailed unit
  and integration tests.
* A definitive record to examine the changing performance of the code over
  time, which has always been a big concern among the existing research
  community using the code;
* As a corollary to the above, the system would give the development
  team a clear and timely warning if a design change accidentally
  negatively affected performance or accuracy – which has been a
  problem in the past.
* The ability to use the science benchmark suite and framework
  to quickly evaluate the performance of Stg-Underworld on new
  hardware systems, to assist purchasing decisions and new collaborators.
* The goal would be to automate as much as possible the regular
  collection of these benchmarks (initally proposed as weekly),
  assessment of them, and publishing of them on-line in a succinct
  and meaningful form (IE with key metrics emphasised, and linked
  to clear definitions of the benchmark problem).

Scientific analysis of computational codes - core capabilities
==============================================================

A discussion of the basic sorts of things we need to do - eg testing outputs,
fields.

.. _uwa-why_python:

Language choice - why Python?
=============================

The UWA code is written in the dynamic scripting and programming language
**Python**. Python was chosen as the implementation language because of:

* It's ability to run in either interactive or scripted mode:- and thus
  facilitate either scripted, repeatable workflows, or interactive exploration;
* The fact that it's clear, concise syntax and high level of abstraction is
  recommended for human developer productivity - while computationally
  intensive tasks can be performed in compiled languages and libraries (such as
  Underworld itself).
* The fact that it's a highly portable language between operating systems and
  architectures.
* The increasingly stable, feature-rich and wide-ranging set of open source
  packages for mathematical and scientific analysis in Python, such as 
  `SciPy <http://www.scipy.org/>`_, Numeric, Matplotlib, SAGE, Paraview,
  and MayaVI.

.. Something about not preventing users from using 3rd-part tools, libs
  afterwards - in this case, UWA helps access data in needed format.
