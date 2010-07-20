#!/usr/bin/env python

import glob
import unittest

def suite():
    testMods = [fName.rstrip(".py") for fName in glob.glob("*suite.py")]
    alltests = unittest.TestSuite()
    for module in map(__import__, testMods):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
