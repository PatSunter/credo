.. _credo-install:

********************************************
Installation & setup quickstart instructions
********************************************

As discussed in the introduction, the main way of distributing and
obtaining CREDO is as a core part of the *stgUnderworld* geophysics framework.

So setting up to use CREDO is very similar to setting up stgUnderworld,
except for some extra Python configuration at the conclusion.

Installing Dependencies and Options
===================================

CREDO has been designed to operate with just Python as a core dependency - other
libraries for more advanced functionality are optional, although are recommended
to use the full functionality.

Required- Python: 2.5 or 2.6
============================

CREDO is written to work with Python 2.5 or 2.6. One of these
versions should come
pre-installed on most Linux systems (including supercomputees), Mac OS
machines, and clusters. For Windows, you may need to download and install Python
yourself - check out the `Python website <http://www.python.org>`_ for
instructions and documentation.

NB: Python and scientific library "super set installs"
------------------------------------------------------

For users with a Mac machine or intending to run analysis on a cluster, you may
wish to consider one of the "scientific Python" distributions, which will
install Python, plus a large set of useful scientific libraries including those
mentioned below, as a group in one large install package. The idea is this takes
away some of the pain of individually installing these libraries, and making
sure you have compatible versions installed. Some of the leading
"install sets" of this type are:

* `SAGE Math <http://www.sagemath.org/>`_: SAGE is a collection of open source
  Python libraries, aiming to provide a free open source alternative to MATLAB
  etc. As well as the libraries, it provides a customised Python
  interpreter, that includes a more mathematical syntax for defining math
  functions etc.

* `Enthought Python Distribution <http://www.enthought.com/products/epd.php>`_:
  Enthought are a commercial company and provide their Python distribution with
  a per-user licence model, but also have an academic licence for trials of the
  software.

.. Note::
   we don't expressly recommend either of these packages at this time, but
   provide them as alternative options to the regular install process. 
   As mentioned above, they may be especially relevant to Mac machines,
   where installing several of the optional packages used by CREDO
   is non-trivial.

Optional Packages
-----------------

These packages are optional, they provide extra capabilities to CREDO such as
plotting and visualisation of output, but are not essential for running system
tests and doing basic analysis.

* **Matplotlib**: http://matplotlib.sourceforge.net:  A good plotting Library
  available in Python. CREDO has several functions/options to auto-create plots 
  of things of interest using Matplotlib.
* **NumPy** and **SciPy**: http://numpy.scipy.org/ and http://www.scipy.org/.
  These libraries are mature and provide efficient and effective interfaces for
  operating on Numerical data. CREDO doesn't use either explicitly
  currently, but they may be useful for doing custom analysis on
  StGermain data made available by CREDO.
* Visualisation: **ParaView** or **MayaVI**: http://www.paraview.org/,
  http://mayavi.sourceforge.net/: these two open-source visualisation packages,
  both based on the VTK toolkit, provide considerable capabilities for operating
  on the sorts of 2D and 3D datasets StGermain-based applications produce, and
  interact well with Python. We are considering providing explicit integration
  support for one or both of these packages in future.

Setting up CREDO - Temporary instructions for beta users
========================================================

The instructions below are for setting up to use the current beta release of
CREDO, |release|. In future the process will become more streamlined as part of
the normal process of configuring, building and installing stgUnderworld, but
for now follow these instructions to try out the beta version.

obtaining the CREDO-dev branch
------------------------------

The |release| release of CREDO is currently being developed on a branch of the
main stgUnderworld framework, called *credo-dev*. This is so it doesn't
interfere with the main-line of the stgUnderworld framework until ready
for a first production release.

To obtain this branch of the code for experimentation:

1. Check out the stgUnderworld codebase, from
   https://www.mcc.monash.edu.au/hg/stgUnderworld.
   (Check out instructions at the `Underworld download page <http://www.underworldproject.org/documentation/Releases.html#Bleeding_Edge_version>`_
   if unsure how to do this. We suggest you name the checked-out
   directory descriptively, e.g. stgUnderworldE-credoDev, which would use the
   following command::

    hg clone https://www.mcc.monash.edu.au/hg/stgUnderworld stgUnderworldE-credoDev

2. Update to the `uwa-dev` branch [#f1]_::

    cd ./stgUnderworldE-credoDev
    hg update uwa-dev

3. running obtainRepositories.py to download all the sub-packages,
   including CREDO::

    ./obtainRepositories.py --with-experimental=1

  * (You will have to submit your repository authentication details while
    cloning both CREDO, and Experimental.)
  * (We suggest you use the --with-experimental=1 flag, because the
    Experimental repository contains several examples of CREDO code.)

4. Verify you have obtained the credo-dev branch of each repository::

    ./identify-all.sh

5. Which should produce output such as the following (the numbers are not
   important and will depend on the particular revision you check out - the
   important thing is the *(uwa-dev)* beside each codebase except for CREDO)::

    02345d81430b (uwa-dev) .
    29f1a3b12768 (uwa-dev) tip ./config
    6e579efb9cba (uwa-dev) ./Experimental
    33ead9b1dd4a (uwa-dev) ./gLucifer
    bd690d648b46 (uwa-dev) ./PICellerator
    73a57163f45c (uwa-dev) ./StgDomain
    3f1ae708ca70 (uwa-dev) ./StGermain
    cfc1f5e5c316 (uwa-dev) tip ./StgFEM
    261e8602f34e (uwa-dev) tip ./Underworld
    204034be3ebf tip ./credo

6. Finally, configure and build the codebase as normal using scons, as detailed
   on the
   `Underworld website <http://www.underworldproject.org/documentation/CompileSCons.html#Compiling_the_Bleeding_Edge>`_.

You should now have a working version of the uwa-dev branch of the stgUnderworld
codebase installed.

.. _environment_setup:

Setting up your environment to use CREDO
----------------------------------------

.. note:: If you only intend to run CREDO System tests via SCons commands like
    `./scons.py check` (see :ref:`credo-examples-run-systest-scons`),
    then you don't need to read the section below, as CREDO is
    now integrated with SCons. However, the environment variables are needed
    if you want to run CREDO tests directly.

To run any CREDO scripts directly, you need to modify a couple of shell
environment variables.

These variables are:

=========== ==================================================================
Variable    Value to set to
=========== ==================================================================
PATH        needs to be extended with a reference to the credo/scripts
            directory in your checkout.
PYTHONPATH  needs to be extended to reference the main tree of CREDO python
            code (credo/credo)
STG_BASEDIR specifies the base directory that StGermain has been checked out
            to. Optional, can individually specify the variables below 
            instead if necessary.
STG_BINDIR  needs to specify the path that StGermain executables have been
            compiled and installed to. 
            For a default installation, you can just use STG_BASEDIR instead
            and CREDO will work out the binaries location within that.
STG_XMLDIR  needs to specify the path that StGermain standard XMLs are stored
            in when the code is compiled. 
            For a default installation, you can just use STG_BASEDIR instead
            and CREDO will work out the XMLs location within that.
=========== ==================================================================

The sections below will advise you how to set these up correctly.

Modifying the shell variables directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you would like to manually set up these environment variables, just first
work out the correct values, and set them in your shell. E.g. if your
stgUnderworld checkout with CREDO included was located at
~/AuScopeCodes/stgUnderworldE-credoDev, then in Bash you would type::

  export PATH=$PATH:~/AuScopeCodes/stgUnderworldE-credoDev/credo/scripts/  
  export PYTHONPATH=$PYTHONPATH:~/AuScopeCodes/stgUnderworldE-credoDev/credo/credo/  
  export STG_BINDIR=~/AuScopeCodes/stgUnderworldE-credoDev/build/bin/

You might like to then save these lines to a config file for when you log in.

Updating and sourcing the provided bash config file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternatively, a Bash script that does all the necessary exports once
you specify one single path, has been included as *updatePathsCREDO-dev.sh*
within the uwa-dev branch of the stgUnderworld repository.

So if you like, just modify the first line of this script so it points to the
base of your stgUnderworld checkout, e.g. again assuming you're main checkout is
at ~/AuScopeCodes/stgUnderworldE-credoDev, modify the first line so it reads::

  export REPOSBASE=~/AuScopeCodes/stgUnderworldE-credoDev
  export CREDO_DIR=$REPOSBASE
  export PATH=$PATH:$REPOSBASE/credo/scripts/
  export PYTHONPATH=$PYTHONPATH:$CREDO_DIR/credo 
  export STG_BINDIR=$REPOSBASE/build/bin

...and then just source this file into your environment each time you want to
start a session and use CREDO::

  source updatePathsCREDO-dev.sh 

you will then be ready to use CREDO.

Testing you're set up correctly to use CREDO
--------------------------------------------

It's easy to test if these environment variables have been set up correctly -
just open a Python script and test that you can import CREDO: ::

  psunter@auscope-02:~/AuScopeCodes/stgUnderworldE-credoDev-work$ python
  Python 2.6.4 (r264:75706, Dec  7 2009, 18:43:55) 
  [GCC 4.4.1] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import credo
  >>> 

No message is the expected result, it means the credo package was successfully
loaded.

If there's an error, you will see something like::

  [GCC 4.4.1] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import credo
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  ImportError: No module named credo
  >>> 

...which means you need to go back through the steps - most likely it's a
problem with the setup of the environment variables above.

.. rubric:: Footnotes

.. [#f1] We haven't renamed the branch from the original "uwa-dev" name of the 
   project, as this is a hassle in Mercurial.
