.. _uwa-install:

********************************************
Installation & setup quickstart instructions
********************************************

As discussed in the introduction, the main way of distributing and
obtaining UWA is as a core part of the *stgUnderworld* geophysics framework.

So setting up to use UWA is very similar to setting up stgUnderworld,
except for some extra Python configuration at the conclusion.

Installing Dependencies and Options
===================================

UWA has been designed to operate with just Python as a core dependency - other
libraries for more advanced functionality are optional, although are recommended
to use the full functionality.

Required- Python: 2.5 or 2.6
============================

UWA is written to work with Python 2.5 or 2.6. One of these versions should come
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
   where installing several of the optional packages used by UWA is non-trivial.

Optional Packages
-----------------

These packages are optional, they provide extra capabilities to UWA such as
plotting and visualisation of output, but are not essential for running system
tests and doing basic analysis.

* **Matplotlib**: http://matplotlib.sourceforge.net:  A good plotting Library
  available in Python. UWA has several functions/options to auto-create plots 
  of things of interest using Matplotlib.
* **NumPy** and **SciPy**: http://numpy.scipy.org/ and http://www.scipy.org/.
  These libraries are mature and provide efficient and effective interfaces for
  operating on Numerical data. UWA doesn't use either explicitly currently, but
  they may be useful for doing custom analysis on StGermain data made available
  by UWA.
* Visualisation: **ParaView** or **MayaVI**: http://www.paraview.org/,
  http://mayavi.sourceforge.net/: these two open-source visualisation packages,
  both based on the VTK toolkit, provide considerable capabilities for operating
  on the sorts of 2D and 3D datasets StGermain-based applications produce, and
  interact well with Python. We are considering providing explicit integration
  support for one or both of these packages in future.

Setting up UWA - Temporary instructions for beta users
======================================================

The instructions below are for setting up to use the current beta release of
UWA, 0.1.0 . In future the process will become more streamlined as part of
the normal process of configuring, building and installing stgUnderworld, but
for now follow these instructions to try out the beta version.

obtaining the UWA-dev branch
----------------------------

The 0.1.0 version of UWA is currently being developed on a branch of the main
stgUnderworld framework, called *uwa-dev*. This is so it doesn't interfere with
the main-line of the stgUnderworld framework until ready for a first production
release.

To obtain this branch of the code for experimentation:

1. Check out the stgUnderworld codebase, from
   https://www.mcc.monash.edu.au/hg/stgUnderworld.
   (Check out instructions at the `Underworld download page <http://www.underworldproject.org/documentation/Releases.html#Bleeding_Edge_version>`_
   if unsure how to do this. We suggest you name the checked-out
   directory descriptively, e.g. stgUnderworldE-uwaDev, which would use the
   following command::

    hg clone https://www.mcc.monash.edu.au/hg/stgUnderworld stgUnderworldE-uwaDev

2. Update to the uwa-dev branch::

    cd ./stgUnderworldE-uwaDev
    hg update uwa-dev

3. running obtainRepositories.py to download all the sub-packages, including UWA::

    ./obtainRepositories.py --with-experimental=1

  * (You will have to submit your repository authentication details while
    cloning both UWA, and Experimental.)
  * (We suggest you use the --with-experimental=1 flag, because the Experimental
    repository contains several examples of UWA code.)

4. Verify you have obtained the uwa-dev branch of each repository::

    ./identify-all.sh

5. Which should produce output such as the following (the numbers are not
   important and will depend on the particular revision you check out - the
   important thing is the *(uwa-dev)* beside each codebase except for UWA)::

    02345d81430b (uwa-dev) .
    29f1a3b12768 (uwa-dev) tip ./config
    6e579efb9cba (uwa-dev) ./Experimental
    33ead9b1dd4a (uwa-dev) ./gLucifer
    bd690d648b46 (uwa-dev) ./PICellerator
    73a57163f45c (uwa-dev) ./StgDomain
    3f1ae708ca70 (uwa-dev) ./StGermain
    cfc1f5e5c316 (uwa-dev) tip ./StgFEM
    261e8602f34e (uwa-dev) tip ./Underworld
    204034be3ebf tip ./uwa

6. Finally, configure and build the codebase as normal using scons, as detailed
   on the
   `Underworld website <http://www.underworldproject.org/documentation/CompileSCons.html#Compiling_the_Bleeding_Edge>`_.

You should now have a working version of the uwa-dev branch of the stgUnderworld
codebase installed.

.. _environment_setup:

Setting up your environment to use UWA
--------------------------------------

Currently in UWA version 0.1.0, UWA is not integrated with the `SCons
<http://www.scons.org/>`_ build system used by the rest of stgUnderworld.

So to run any of the examples, you need to modify a couple of shell environment
variables directly, to use the UWA code directly from its source directory in
uwa.

These variables are:

=========== ==================================================================
Variable    Value to set to
=========== ==================================================================
PATH        needs to be extended with a reference to the uwa/scripts directory
            in your checkout.
PYTHONPATH  needs to be extended to reference the main tree of UWA python
            code (uwa/uwa)
STG_BASEDIR specifies the base directory that StGermain has been checked out
            to. Optional, can individually specify the variables below 
            instead if necessary.
STG_BINDIR  needs to specify the path that StGermain executables have been
            compiled and installed to. 
            For a default installation, you can just use STG_BASEDIR instead
            and UWA will work out the binaries location within that.
STG_XMLDIR  needs to specify the path that StGermain standard XMLs are stored
            in when the code is compiled. 
            For a default installation, you can just use STG_BASEDIR instead
            and UWA will work out the XMLs location within that.
=========== ==================================================================

The sections below will advise you how to set these up correctly.

Modifying the shell variables directly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you would like to manually set up these environment variables, just first
work out the correct values, and set them in your shell. E.g. if your
stgUnderworld checkout with UWA included was located at
~/AuScopeCodes/stgUnderworldE-uwaDev, then in Bash you would type::

  export PATH=$PATH:~/AuScopeCodes/stgUnderworldE-uwaDev/uwa/scripts/  
  export PYTHONPATH=$PYTHONPATH:~/AuScopeCodes/stgUnderworldE-uwaDev/uwa/uwa/  
  export STG_BINDIR=~/AuScopeCodes/stgUnderworldE-uwaDev/build/bin/

You might like to then save these lines to a config file for when you log in.

Updating and sourcing the provided bash config file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternatively, a Bash script that does all the necessary exports once
you specify one single
path, has been included as *updatePathsUWA-dev.sh* within the uwa-dev branch of
the stgUnderworld repository.

So if you like, just modify the first line of this script so it points to the
base of your stgUnderworld checkout, e.g. again assuming you're main checkout is
at ~/AuScopeCodes/stgUnderworldE-uwaDev, modify the first line so it reads::

  export REPOSBASE=~/AuScopeCodes/stgUnderworldE-uwaDev
  export UWA_DIR=$REPOSBASE
  export PATH=$PATH:$REPOSBASE/uwa/scripts/
  export PYTHONPATH=$PYTHONPATH:$UWA_DIR/uwa 
  export STG_BINDIR=$REPOSBASE/build/bin

...and then just source this file into your environment each time you want to
start a session and use UWA::

  source updatePathsUWA-dev.sh 

you will then be ready to use UWA.

Testing you're set up correctly to use UWA
------------------------------------------

It's easy to test if these environment variables have been set up correctly -
just open a Python script and test that you can import UWA: ::

  psunter@auscope-02:~/AuScopeCodes/stgUnderworldE-uwaDev-work$ python
  Python 2.6.4 (r264:75706, Dec  7 2009, 18:43:55) 
  [GCC 4.4.1] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import uwa
  >>> 

No message is the expected result, it means the uwa package was successfully
loaded.

If there's an error, you will see something like::

  [GCC 4.4.1] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> import uwa
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  ImportError: No module named uwa
  >>> 

...which means you need to go back through the steps - most likely it's a
problem with the setup of the environment variables above.
