from xml.etree import ElementTree as etree

from uwa.systest.api import TestComponent, UWA_PASS, UWA_FAIL
from uwa.io import stgcvg
import uwa.analysis.fields as fields

# The criteria of convergence: first is cvg rate, second is correlation
defFieldScaleCvgCriterions = {
    'VelocityField':(1.6,0.99),
    'PressureField':(0.9,0.99),
    'StrainRateField':(0.85,0.99) }

def testAllCvgWithScale(lenScales, fieldErrorData, fieldCvgCriterions):    
    overallResult = True
    for fieldName, dofErrors in fieldErrorData.iteritems():
        result = testCvgWithScale(fieldName, lenScales, dofErrors,
            fieldCvgCriterions[fieldName])
        meetsReq = result[0]
        if meetsReq == False:
            overallResult = False
    return overallResult    

def testCvgWithScale(fieldName, lenScales, dofErrors, fieldCvgCriterion):
    '''Tests that for a given field, set of length scales of different runs,
    and list of dofErrors (indexed by Dof, then run) - that they converge
    according to the given fieldCvgCriterion.
    
    Returns: result of test (Bool), then a list indexed by dof, giving a tuple
    of (cvgRate, correlation) of that dof.'''

    fieldConv = fields.calcFieldCvgWithScale(fieldName, lenScales, dofErrors)
    reqCvgRate, reqCorr = fieldCvgCriterion
    dofStatuses = []

    for dofI, dofConv in enumerate(fieldConv):
        cvgRate, corr = dofConv
        print "Field %s, dof %d - cvg rate %6g, corr %6f" \
            % (fieldName, dofI, cvgRate, corr)
        #plt.plot(resLogs, errLogs)
        #plt.show()

        dofTestStatus = True
        if cvgRate < reqCvgRate: 
            dofTestStatus = False
            print "  -Bad! - cvg %6g less than req'd %6g for this field."\
                % (cvgRate, reqCvgRate)
        if corr < reqCorr:
            dofTestStatus = False
            print "  -Bad! - corr %6g less than req'd %6g for this field."\
                % (corr, reqCorr)
        if dofTestStatus: print "  -Good"
        dofStatuses.append(dofTestStatus)
    
    if False in dofStatuses:
        return False, fieldConv
    else: 
        return True, fieldConv

def getNumDofs(fComp, mResult):
    '''Hacky utility function to get the number of dofs of an fComp, by
    checking the result. Need to do this smarter/neater.'''
    fCompRes = fComp.getResult(mResult)
    return len(fCompRes.dofErrors)

def getDofErrorsByRun(fComp, resultsSet):
    '''For a given field comparison op, get all the dof errors from a set of
    runs, indexed primarily by run index'''

    # A bit of a hack: need to store # of dofs per field better somewhere
    numDofs = getNumDofs(fComp, resultsSet[0])
    dofErrorsByRun = [[] for ii in range(numDofs)]

    # We need to index the dofErrors by run, then dofI, for cvg check
    for runI, mResult in enumerate(resultsSet):
        fCompRes = fComp.getResult(mResult)

        for dofI, dofError in enumerate(fCompRes.dofErrors):
            dofErrorsByRun[dofI].append(dofError)

    return dofErrorsByRun


class FieldCvgWithScaleTest(TestComponent):
    def __init__(self, fieldsToTest = None,
            testCvgFunc = testCvgWithScale,
            fieldCvgCrits = defFieldScaleCvgCriterions):
        TestComponent.__init__(self, "fieldCvgWithScaleTest")
        self.testCvgFunc = testCvgFunc
        self.fieldCvgCrits = fieldCvgCrits
        self.fieldsToTest = fieldsToTest
        # TODO: would be good to check here that the fieldsToTest have
        # cvg info provided in the  fieldCvgCrits dict. However becuase we
        # allow fieldsToTest=None to mean "read from XML", can't always
        # do this just yet.
        self.fComps = None
        self.fErrorsByRun = {}
        self.fCvgMeetsReq = {}
        self.fCvgResults = {}

    def attachOps(self, modelRun):
        self.fComps = fields.FieldComparisonList()
        if self.fieldsToTest == None:
            self.fComps.readFromStgXML(modelRun.modelInputFiles)
        else:
            for fieldName in self.fieldsToTest:
                self.fComps.add(fields.FieldComparisonOp(fieldName))
        modelRun.analysis['fieldComparisons'] = self.fComps

    def check(self, resultsSet):
        # NB: could store this another way in model info?
        lenScales = self.getLenScales(resultsSet)    
        self.fErrorsByRun = {}
        self.fCvgMeetsReq = {}
        self.fCvgResults = {}

        for fName, fCompOp in self.fComps.fields.iteritems():
            self.fErrorsByRun[fName] = getDofErrorsByRun(fCompOp, resultsSet)
            fResult = self.testCvgFunc(fName, lenScales,
                self.fErrorsByRun[fName], self.fieldCvgCrits[fName])
            self.fCvgMeetsReq[fName] = fResult[0]
            self.fCvgResults[fName] = fResult[1]

        if False in self.fCvgResults.itervalues():
            statusMsg = "TODO"
            self.tcStatus = UWA_FAIL(statusMsg)
            return False
        else:
            statusMsg = "The solution compared to the %s result converged"\
                " as expected with increasing resolution for all fields."\
                % (self.fComps.getCmpSrcString())
            self.tcStatus = UWA_PASS(statusMsg)
            return True

    def writeXMLCustomSpec(self, specNode):
        if self.fComps == None:
            raise AttributeError("Unable to write XML for this TestComponent"\
                " until attachOps() has been called, and have been able to"\
                " read the model XML to find out name of fields to test.")
        etree.SubElement(specNode, 'fromXML', value=str(self.fComps.fromXML))
        fListNode = etree.SubElement(specNode, 'fields')
        for fName in self.fComps.fields.keys():
            fieldCvgCrit = self.fieldCvgCrits[fName]
            fNode = etree.SubElement(fListNode, 'field')
            fNode.attrib['name'] = fName
            fNode.attrib['cvgRate'] = cvgRate=str(fieldCvgCrit[0])
            fNode.attrib['corr'] = str(fieldCvgCrit[1])

    def writeXMLCustomResult(self, resNode, resultsSet):
        frNode = etree.SubElement(resNode, 'fieldResultDetails')
        lenScales = self.getLenScales(resultsSet)    
        for fName, fComp in self.fComps.fields.iteritems():
            fieldNode = etree.SubElement(frNode, "field", name=fName)
            fieldNode.attrib['cvgMeetsReq'] = str(self.fCvgMeetsReq[fName])
            for dofI, dofErrorsByRun in enumerate(self.fErrorsByRun[fName]):
                dofNode = etree.SubElement(fieldNode, "dof")
                dofNode.attrib["num"] = str(dofI)
                dofCvgResult = self.fCvgResults[fName][dofI]
                dofNode.attrib['cvgrate'] = "%8.6f" % dofCvgResult[0]
                dofNode.attrib['correlation'] = "%8.6f" % dofCvgResult[1]
                #TODO run name? and overall result?
                runEsNode = etree.SubElement(dofNode, "runErrors")
                for runI, dofError in enumerate(dofErrorsByRun):
                    dofErrorNode = etree.SubElement(runEsNode, "dofError")
                    dofErrorNode.attrib['run_number'] = str(runI+1)
                    dofErrorNode.attrib['lenScale'] = "%8.6e" % (lenScales[runI])
                    dofErrorNode.attrib["error"] = "%6e" % dofError


    def getLenScales(self, resultsSet):
        lenScales = []
        for runI, mResult in enumerate(resultsSet):
            cvgIndex = stgcvg.genConvergenceFileIndex(mResult.outputPath)
            # a bit hacky, need to redesign cvg stuff, esp len scales??
            cvgInfo = cvgIndex[self.fComps.fields.keys()[0]]
            lenScales.append(stgcvg.getRes(cvgInfo.filename))        
        return lenScales    
