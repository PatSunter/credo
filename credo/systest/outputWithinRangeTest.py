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

from xml.etree import ElementTree as etree

from credo.systest.api import TestComponent, CREDO_PASS, CREDO_FAIL

class OutputWithinRangeTest(TestComponent):
    '''Test component to check that a given output parameter 
    (found in the frequent output) is within a given range, and
    optionally also that this occurs within a given set of model times.
    
    .. seealso:: :mod:`credo.io.stgfreq`.

    .. attribute:: outputName

       The name of the model observable to check, as it's recorded in the
       Frequent Output file. E.g. "Vrms".

    .. attribute:: reductionOp

       The reduction operation to perform in choosing where the value should
       be checked.
       Simple examples using Python built-ins could be:

       * `max() <http://docs.python.org/library/functions.html#max>`_
         - the Maximum value
       * `min() <http://docs.python.org/library/functions.html#min>`_
         - the Minimum value

       .. seealso:: :func:`credo.io.stgfreq.FreqOutput.getReductionOp`  

    .. attribute:: allowedRange

       The allowed range for the paramter to fall into for the test to pass.
       A tuple of (min,max) form.

    .. attribute:: tRange

       (Optional) determines if a secondary check should be performed, that
       the parameters value checked (eg max) also fell within a given range
       of model simulation times as a (min,max) tuple. If `None`, this 
       secondary check won't be performed.
       
    .. attribute:: actualVal

       After the check is performed, the actual value of the parameter is 
       recorded here.

    .. attribute:: actualTime

       After the check is performed, records the model sim time at which the 
       parameters chosen property (eg max or min) occurred.

    .. attribute:: withinRange

       After the check is performed, records a Bool saying whether
       the test component passed.
    '''

    def __init__(self, outputName, reductionOp, allowedRange,  
            tRange=None):
        TestComponent.__init__(self, "outputWithinRange")
        self.outputName = outputName
        self.reductionOp = reductionOp
        self.allowedRange = allowedRange
        self.tRange = tRange
        self.actualVal = None
        self.actualTime = None
        self.withinRange = None

    def _writeXMLCustomSpec(self, specNode):
        etree.SubElement(specNode, 'outputName', value=self.outputName)
        etree.SubElement(specNode, 'reductionOp', value=str(self.reductionOp))
        etree.SubElement(specNode, 'allowedRange-min',
            value=str(self.allowedRange[0]))
        etree.SubElement(specNode, 'allowedRange-max',
            value=str(self.allowedRange[1]))
        if self.tRange:
            etree.SubElement(specNode, 'tRange-min',
                value=str(self.tRange[0]))
            etree.SubElement(specNode, 'tRange-max',
                value=str(self.tRange[1]))
                

    def attachOps(self, modelRun):
        """Implements base class
        :meth:`credo.systest.api.TestComponent.attachOps`.
        
        .. note:: Currently does nothing. Intend to make it ensure the
           correct plugin is set to be loaded (to make sure observable
           is generated in FrequentOutput.dat)."""
        # TODO: here we have to make sure the correct plugin is set to be
        # loaded .
        # Maybe with the aid of a lookup table of param->plugins?
        pass

    def check(self, resultsSet):
        """Implements base class
        :meth:`credo.systest.api.TestComponent.check`."""
        self.actualVal = None
        self.withinRange = None
        statusMsg = ""
        numRuns = len(resultsSet)
        overallResult = True
        for runI, mResult in enumerate(resultsSet):
            mResult.readFrequentOutput()
            self.actualVal, actualTimeStep = mResult.freqOutput.getReductionOp(
                self.outputName, self.reductionOp)
            self.actualTime = mResult.freqOutput.getValueAtStep('Time',
                actualTimeStep)
            self.withinRange = (self.allowedRange[0] <= self.actualVal \
                <= self.allowedRange[1])

            if not self.withinRange:
                if numRuns > 1:
                    statusMsg += "For run %d out of %d: " % (runI, numRuns)
                statusMsg += "Model output '%s' value %g not within"\
                    " required range (%g,%g)."\
                    % (self.outputName, self.actualVal, self.allowedRange[0],\
                        self.allowedRange[1])
                overallResult = False    
            elif self.tRange:
                tMin, tMax = self.tRange
                withinTRange = (tMin <= self.actualTime <= tMax)
                if not withinTRange:
                    if numRuns > 1:
                        statusMsg += "For run %d out of %d: " % (runI, numRuns)
                    statusMsg += "Model output '%s' value %g within"\
                        " required range (%g,%g), but time at which this"\
                        " occurred (%s) not within req'd range (%g,%g)."\
                        % (self.outputName, self.actualVal,\
                            self.allowedRange[0], self.allowedRange[1],\
                            self.actualTime, self.tRange[0], self.tRange[1])
                    overallResult = False        

        if overallResult:
            statusMsg += "Model output '%s' value %g within"\
                " required range (%g,%g) for all runs."\
                % (self.outputName, self.actualVal, self.allowedRange[0],\
                    self.allowedRange[1])

        print statusMsg
        if overallResult == False:
            self.tcStatus = CREDO_FAIL(statusMsg)
        else:
            self.tcStatus = CREDO_PASS(statusMsg)
        return overallResult

    def _writeXMLCustomResult(self, resNode, resultsSet):
        avNode = etree.SubElement(resNode, 'actualValue')
        avNode.text = "%6e" % self.actualVal
        atNode = etree.SubElement(resNode, 'actualTime')
        atNode.text = "%6g" % self.actualTime
        wrNode = etree.SubElement(resNode, 'withinRange')
        wrNode.text = str(self.withinRange)

