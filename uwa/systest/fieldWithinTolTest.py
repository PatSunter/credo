from lxml import etree

from uwa.systest.api import TestComponent
from uwa.io import stgcvg
import uwa.analysis.fields as fields

class FieldWithinTolTest(TestComponent):
    def __init__(self, fieldsToTest=None,
            defFieldTol=0.01,
            fieldTols=None,
            useReference=False,
            referencePath=None,
            testTimestep=0
            ):
        self.fieldsToTest = fieldsToTest
        self.defFieldTol = defFieldTol
        self.fieldTols = fieldTols
        self.fComps = fields.FieldTestsInfo()
        self.fComps.useReference = useReference
        self.fComps.referencePath = referencePath
        self.fComps.testTimestep = testTimestep

    def attachOps(self, modelRun):
        if self.fieldsToTest == None:
            self.fComps.readFromStgXML(modelRun.modelInputFiles)
        else:
            for fieldName in self.fieldsToTest:
                self.fComps.add(fields.FieldTest(fieldName))
        modelRun.analysis['fieldComparisons'] = self.fComps

    def getTolForField(self, fieldName):
        if (self.fieldTols is not None) and fieldName in self.fieldTols:
            fieldTol = self.fieldTols[fieldName]
        else:
            fieldTol = self.defFieldTol
        return fieldTol

    def check(self, resultsSet):
        fieldResults = {}

        fComps = self.fComps
        for fieldName in self.fComps.fields.keys():
            fieldResults[fieldName] = True
            fComp = fComps.fields[fieldName]
            fieldTol = self.getTolForField(fieldName)
            for runI, mResult in enumerate(resultsSet):
                cvgIndex = stgcvg.genConvergenceFileIndex(mResult.outputPath)
                cvgInfo = cvgIndex[fieldName]
                dofErrors = stgcvg.getDofErrors_ByDof(cvgInfo, steps="last")
                for dofError in dofErrors:
                    if dofError > fieldTol:
                        fieldResults[fieldName] = False
                        if len(resultsSet) > 0:
                            print "For run %d out of %d" % runI, len(resultsSet)
                        print "Field '%s' error of %f not within tol %f"\
                            % (fieldName, dofError, fieldTol)
                        break
                if fieldResults[fieldName] == False:
                    break

            if fieldResults[fieldName]:
                print "Field '%s' error within tol %f." % (fieldName, fieldTol)

        if False in fieldResults: result = False
        else: result = True

        return result

    def writeInfoXML(self, parentNode):
        ftNode = self.createBaseXMLNode(parentNode, 'fieldWithinTol')
        ftNode.attrib['fromXML']=str(self.fComps.fromXML)
        fListNode = etree.SubElement(ftNode, 'fields')
        for fName in self.fComps.fields.keys():
            fNode = etree.SubElement(fListNode, 'field', name=fName)
