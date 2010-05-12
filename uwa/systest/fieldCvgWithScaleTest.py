from lxml import etree

from uwa.systest.api import TestComponent
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
        if result == False:
            overallResult = False
    return overallResult    

def testCvgWithScale(fieldName, lenScales, dofErrors, fieldCvgCriterion):
    fieldConv = fields.calcFieldCvgWithScale(fieldName, lenScales, dofErrors)
    reqCvgRate, reqCorr = fieldCvgCriterion
    dofStatuses = []
    for dofI, dofConv in enumerate(fieldConv):
        cvgRate, corr = dofConv
        print "Field %s, dof %d - cvg rate %f, corr %f" \
            % (fieldName, dofI, cvgRate, corr)
        #plt.plot(resLogs, errLogs)
        #plt.show()

        dofTestStatus = True
        if cvgRate < reqCvgRate: 
            dofTestStatus = False
            print "  -Bad! - cvg %f less than req'd %f for this field."\
                % (cvgRate, reqCvgRate)
        if corr < reqCorr:
            dofTestStatus = False
            print "  -Bad! - corr %f less than req'd %f for this field."\
                % (corr, reqCorr)
        if dofTestStatus: print "  -Good"
        dofStatuses.append(dofTestStatus)
    
    if False in dofStatuses: return False
    else: return True

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
        self.testCvgFunc = testCvgFunc
        self.fieldCvgCrits = fieldCvgCrits
        self.fieldsToTest = fieldsToTest
        self.fComps = None

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
        results = []
        for fCompOp in self.fComps.fields.itervalues():
            dofErrors = getDofErrorsByRun(fCompOp, resultsSet)
            fResult = self.testCvgFunc(fCompOp.name, lenScales, dofErrors,
                self.fieldCvgCrits[fCompOp.name])
            results.append(fResult)

        if False in results: return False
        else: return True

    def writeInfoXML(self, parentNode):
        ftNode = self.createBaseXMLNode(parentNode, 'fieldCvgWithScaleTest')
        ftNode.attrib['fromXML']=str(self.fComps.fromXML)
        fListNode = etree.SubElement(ftNode, 'fields')
        for fName in self.fComps.fields.keys():
            fNode = etree.SubElement(fListNode, 'field', name=fName)

    def getLenScales(self, resultsSet):
        lenScales = []
        for runI, mResult in enumerate(resultsSet):
            cvgIndex = stgcvg.genConvergenceFileIndex(mResult.outputPath)
            # a bit hacky, need to redesign cvg stuff, esp len scales??
            cvgInfo = cvgIndex[self.fComps.fields.keys()[0]]
            lenScales.append(stgcvg.getRes(cvgInfo.filename))        
        return lenScales    
