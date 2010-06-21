"""A library of useful stats functions for analysis operations.

The aim is for simple functions to be able to run without further dependencies
... with more advanced stats libraries from the likes of SciPy being able to be
loaded at the user's discretion."""

from math import sqrt

def linreg(X, Y):
    """
    Summary
        Linear regression of y = ax + b

    Usage
        real, real, real = linreg(list, list)

    Returns coefficients to the regression line "y=ax+b" from x[] and y[], and R^2 Value

    (Obtained from From
    http://www.answermysearches.com/how-to-do-a-simple-linear-regression-in-python/124/)
    Useful for field analysis, e.g. when applied to a list of length scales
    & field errors, to calculate convergence info, such as
    :func:`uwa.analysis.fields.calcFieldCvgWithScale`.
    """
    if len(X) != len(Y):  raise ValueError, 'unequal length'
    N = len(X)
    Sx = Sy = Sxx = Syy = Sxy = 0.0
    for x, y in map(None, X, Y):
        Sx = Sx + x
        Sy = Sy + y
        Sxx = Sxx + x*x
        Syy = Syy + y*y
        Sxy = Sxy + x*y
    det = Sxx * N - Sx * Sx
    a, b = (Sxy * N - Sy * Sx)/det, (Sxx * Sy - Sx * Sxy)/det
    meanerror = residual = 0.0
    for x, y in map(None, X, Y):
        meanerror = meanerror + (y - Sy/N)**2
        residual = residual + (y - a * x - b)**2
    RR = 1 - residual/meanerror
    #ss = residual / (N-2)
    #Var_a, Var_b = ss * N / det, ss * Sxx / det
    #print "y=ax+b"
    #print "N= %d" % N
    #print "a= %g \\pm t_{%d;\\alpha/2} %g" % (a, N-2, sqrt(Var_a))
    #print "b= %g \\pm t_{%d;\\alpha/2} %g" % (b, N-2, sqrt(Var_b))
    #print "R^2= %g" % RR
    #print "s^2= %g" % ss
    return a, b, RR
