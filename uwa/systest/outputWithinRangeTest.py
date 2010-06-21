from xml.etree import ElementTree as etree

from uwa.systest.api import TestComponent, UWA_PASS, UWA_FAIL
import uwa.analysis.fields as fields

class OutputWithinRangeTest(TestComponent):
    '''Test component to check that a given output parameter 
    (found in the frequent output) is within a given range'''
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

    def writeXMLCustomSpec(self, specNode):
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
        # TODO: here we have to make sure the correct plugin is set to be
        # loaded .
        # Maybe with the aid of a lookup table of param->plugins?
        pass

    def check(self, resultsSet):
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
                if not self.withinTRange:
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
            self.tcStatus = UWA_FAIL(statusMsg)
        else:
            self.tcStatus = UWA_PASS(statusMsg)
        return overallResult

    def writeXMLCustomResult(self, resNode, resultsSet):
        avNode = etree.SubElement(resNode, 'actualValue')
        avNode.text = "%6e" % self.actualVal
        atNode = etree.SubElement(resNode, 'actualTime')
        atNode.text = "%6g" % self.actualTime
        wrNode = etree.SubElement(resNode, 'withinRange')
        wrNode.text = str(self.withinRange)

