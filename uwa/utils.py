"""A module for general utility functions in UWA, that don't clearly fit
into other modules."""

import os

def productCalc(*args, **kwds):
    """Basic implementation of itertools.product from Python 2.6:
    For Python 2.5 backward compatibility.
    productCalc('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    productCalc(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    """
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
