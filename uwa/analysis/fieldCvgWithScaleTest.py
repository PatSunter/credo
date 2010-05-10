from lxml import etree

from uwa.io import stgcvg
import uwa.analysis.fields as fields

# The criteria of convergence: first is cvg rate, second is correlation
defFieldScaleCvgCriterions = {
    'VelocityField':(1.6,0.99),
    'PressureField':(0.9,0.99),
    'StrainRateField':(0.85,0.99) }

# For each field
# Check all the necessary convergence files available
# Get the final error vs analytic soln value for each res

# Then apply the convergence check algorithm to each of these.

#def convergenceCheck( resSets, compareResults ):
#    f


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

class FieldCvgWithScaleTest:
    def __init__(self, fieldsToTest=None,
            testCvgFunc=testAllCvgWithScale,
            fieldScaleCvgCrits=defFieldScaleCvgCriterions):
        self.testCvgFunc = testCvgFunc
        self.fieldScaleCvgCrits = fieldScaleCvgCrits
        self.fieldsToTest = fieldsToTest
        self.fTests = None

    def attachOps(self, modelRun):
        self.fTests = fields.FieldTestsInfo()
        if self.fieldsToTest == None:
            self.fTests.readFromStgXML(modelRun.modelInputFiles)
        else:
            for fieldName in self.fieldsToTest:
                self.fTests.add(fields.FieldTest(fieldName))
        modelRun.analysis['fieldTests'] = self.fTests

    def check(self, resSet, resultsSet):

        # NB: could store this another way in model info?
        lenScales = []
        for runI, mResult in enumerate(resultsSet):
            cvgIndex = stgcvg.genConvergenceFileIndex(mResult.outputPath)
            # a bit hacky, need to redesign cvg stuff?
            cvgInfo = cvgIndex[self.fTests.fields.keys()[0]]
            lenScales.append(stgcvg.getRes(cvgInfo.filename))

        fTests = self.fTests
        fieldErrorData = {} 
        for fieldName in self.fTests.fields.keys():
            fTest = fTests.fields[fieldName]
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
        ftNode = etree.SubElement(parentNode, 'fieldCvgWithScaleTest')
        ftNode.attrib['fromXML']=str(self.fTests.fromXML)
        fListNode = etree.SubElement(ftNode, 'fields')
        for fName in self.fTests.fields.keys():
            fNode = etree.SubElement(ftNode, 'field', name=fName)
