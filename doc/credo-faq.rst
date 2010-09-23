.. _credo-faq:

*********
CREDO FAQ
*********

Problems running tests
======================

When I try to run a CREDO system test script get an "ImportError" message
-------------------------------------------------------------------------

This problem is usually because you haven't add the directory containing
the CREDO Python source to your PYTHONPATH. See :ref:`environment_setup`
for the various ways to do this.

Problem with parallel system tests, a CVGReadError occurs trying to read CVGs
-----------------------------------------------------------------------------

Q: I have a problem running parallel CREDO system tests, along the lines
of being unable to parse Field convergence results, where it brings up an
exception message along the lines of:
"credo.io.stgcvg.CVGReadError: Error, couldn't read expected error" ...

A: This problem is often caused by using an "mpirun" or "mpiexec"
not corresponding to the MPI library you compiled the code with. Not doing
this (eg running the code with OpenMPI that you compiled with MPICH2)
can result in annoying parallel bugs  e.g. corruptions when writing
output files, which among other things throw off the CREDO system
testing now included with the code.

What are the ways of dealing with this?

1. On clusters using the "module" system, just make sure you load the
   same modules when running the code (eg in PBS scripts) as when you
   compiled it.
2. Make sure your PATH system environment variable is set up
   correctly so that "mpirun" will launch the correct version you
   compiled with. (You can test this by running 'which mpirun'). It's a
   good idea to set this up in your login scripts, e.g. .bashrc.
3. For CREDO specifically, you can set the environment variable
   MPI_RUN_COMMAND to tell it to use a custom mpirun/mpiexec rather than
   the default one in your PATH. (E.g. setting
   MPI_RUN_COMMAND="/usr/local/packages/mpich2-1.2.1p1-debug/bin/".) 
