.. _uwa-install:

********************************************
Installation & setup quickstart instructions
********************************************

As discussed in the introduction, the main way of distributing and
obtaining UWA is as a core part of the *stgUnderworld* geophysics framework.

So setting up to use UWA is very similar to setting up stgUnderworld,
except for some extra Python configuration at the conclusion.

Temporary instructions for beta users
=====================================

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
PYTHON_PATH needs to be extended to reference the main tree of UWA python
            code (uwa/uwa)
STG_BINDIR  needs to specify the path that StGermain executables have been
            compiled and installed to.
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
