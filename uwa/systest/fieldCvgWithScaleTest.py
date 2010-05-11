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

    for fieldName, cvgTestData in fieldErrorData.iteritems():
        dofErrors = cvgTestData
        fieldConv = fields.calcFieldCvgWithScale(fieldName, lenScales, dofErrors)
        reqCvgRate, reqCorr = fieldCvgCriterions[fieldName]
        for dofI, dofConv in enumerate(fieldConv):
            cvgRate, pearsonCorr = dofConv
            print "Field %s, dof %d - cvg rate %f, corr %f" \
                % (fieldName, dofI, cvgRate, pearsonCorr)
            #plt.plot(resLogs, errLogs)
            #plt.show()

            testStatus = True
            if cvgRate < reqCvgRate: 
                testStatus = False
                print "  -Bad! - cvg %f less than req'd %f for this field."\
                    % (cvgRate, reqCvgRate)

            if pearsonCorr < reqCorr:
                testStatus = False
                print "  -Bad! - corr %f less than req'd %f for this field."\
                    % (pearsonCorr, reqCorr)

            if testStatus: print "  -Good"
            else: overallResult = False
    
    return overallResult

class FieldCvgWithScaleTest(TestComponent):
    def __init__(self, fieldsToTest=None,
            testCvgFunc=testAllCvgWithScale,
            fieldScaleCvgCrits=defFieldScaleCvgCriterions):
        self.testCvgFunc = testCvgFunc
        self.fieldScaleCvgCrits = fieldScaleCvgCrits
        self.fieldsToTest = fieldsToTest
        self.fComps = None

    def attachOps(self, modelRun):
        self.fComps = fields.FieldTestsInfo()
        if self.fieldsToTest == None:
            self.fComps.readFromStgXML(modelRun.modelInputFiles)
        else:
            for fieldName in self.fieldsToTest:
                self.fComps.add(fields.FieldTest(fieldName))
        modelRun.analysis['fieldComparisons'] = self.fComps

    def check(self, resultsSet):
        # NB: could store this another way in model info?
        lenScales = []
        for runI, mResult in enumerate(resultsSet):
            cvgIndex = stgcvg.genConvergenceFileIndex(mResult.outputPath)
            # a bit hacky, need to redesign cvg stuff?
            cvgInfo = cvgIndex[self.fComps.fields.keys()[0]]
            lenScales.append(stgcvg.getRes(cvgInfo.filename))

        fComps = self.fComps
        fieldErrorData = {} 
        for fieldName in self.fComps.fields.keys():
            fComp = fComps.fields[fieldName]
            dofErrorsByRun = []
            # We need to index the dofErrors by run, then dofI, for cvg check
            for runI, mResult in enumerate(resultsSet):
                cvgIndex = stgcvg.genConvergenceFileIndex(mResult.outputPath)
                cvgInfo = cvgIndex[fieldName]
                # TODO: below really should be inside FieldComparison op.
                dofErrors = stgcvg.getDofErrors_ByDof(cvgInfo, steps="last")
                # A bit of a hack: need to store # of dofs per field better
                # (eg on FieldComparison op?)
                if runI == 0:
                    for dofI in range(len(dofErrors)):
                        dofErrorsByRun.append([])

                for dofI, dofError in enumerate(dofErrors):
                    dofErrorsByRun[dofI].append(dofError)

            fieldErrorData[fieldName] = dofErrorsByRun

        result = self.testCvgFunc(lenScales, fieldErrorData,
            self.fieldScaleCvgCrits)
        return result

    def writeInfoXML(self, parentNode):
        ftNode = self.createBaseXMLNode(parentNode, 'fieldCvgWithScaleTest')
        ftNode.attrib['fromXML']=str(self.fComps.fromXML)
        fListNode = etree.SubElement(ftNode, 'fields')
        for fName in self.fComps.fields.keys():
            fNode = etree.SubElement(fListNode, 'field', name=fName)
