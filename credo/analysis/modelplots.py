##  Copyright (C), 2010, Monash University
##  Copyright (C), 2010, Victorian Partnership for Advanced Computing (VPAC)
##  
##  This file is part of the CREDO library.
##  Developed as part of the Simulation, Analysis, Modelling program of 
##  AuScope Limited, and funded by the Australian Federal Government's
##  National Collaborative Research Infrastructure Strategy (NCRIS) program.
##
##  This library is free software; you can redistribute it and/or
##  modify it under the terms of the GNU Lesser General Public
##  License as published by the Free Software Foundation; either
##  version 2.1 of the License, or (at your option) any later version.
##
##  This library is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public
##  License along with this library; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
##  MA  02110-1301  USA


"""Collection of utility functions for plotting interesting aspects of models
"""

#!/usr/bin/env python

import os
import credo
try:
    # For why we use Agg backend, see
    # http://matplotlib.sourceforge.net/faq/howto_faq.html#matplotlib-in-a-web-application-server
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    print "Error, to use CREDO built-in plot functions, please "\
        " install the matplotlib python library."

def getValsFromAllRuns(mResults, outputName):
    resVals = [mRes.freqOutput.getValuesArray(outputName) for mRes in mResults]
    return resVals

def plotOverAllRuns(mResults, outputName, depName='Timestep', show=False,
        save=True, path=".", labelNames=True):
    """Create a plot of values over multiple runs."""    
    resVals = getValsFromAllRuns(mResults, outputName)
    depVals = getValsFromAllRuns(mResults, depName)
    plot = plt.clf()   # Start by clearing any pre-existing figure
    for ii, mRes in enumerate(mResults):
        lab = "%d" % ii
        if labelNames == True: lab += ": %s" % mRes.modelName
        plt.plot(depVals[ii], resVals[ii], label=lab)
    plt.xlabel(depName)
    plt.ylabel(outputName)
    plt.legend(loc='best', prop={'size':'small'})
    plt.title("Output parameter '%s' over %s"\
        % (outputName, depName))
    if save:
        if not os.path.exists(path):
            os.makedirs(path)
        for fmt in ['svg', 'png']:
            filename = os.path.join(path,
                outputName+"-multiRunTimeSeries.%s" % fmt)
            plt.savefig(filename, format=fmt, dpi=120)
    if show: plt.show()
    return plt
